from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import ai, schemas, services
from .config import CORS_ORIGINS
from .db import Base, SessionLocal, engine, get_db
from .models import Evidence, Profession, ProfessionSkill, RoadmapItem, Skill, User
from .security import current_user, hash_password, make_token, require_role, verify_password
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="UniSkill AI API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Auth ----------
@app.post("/auth/register", response_model=schemas.TokenOut, status_code=201)
def register(body: schemas.RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Bu email allaqachon ro'yxatdan o'tgan")
    u = User(email=email, name=body.name.strip(), role=body.role, faculty=body.faculty,
             password_hash=hash_password(body.password))
    db.add(u)
    db.commit()
    return {"token": make_token(u), "user": u}


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == body.email.lower()))
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(401, "Email yoki parol noto'g'ri")
    return {"token": make_token(u), "user": u}


@app.get("/me", response_model=schemas.UserOut)
def me(user: User = Depends(current_user)):
    return user


@app.patch("/me", response_model=schemas.UserOut)
def update_me(body: schemas.MeUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    if "profession_id" in data and data["profession_id"] is not None and not db.get(Profession, data["profession_id"]):
        raise HTTPException(404, "Kasb topilmadi")
    if user.role != "student":
        data.pop("profession_id", None)
        data.pop("consent_employers", None)
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    return user


# ---------- Katalog ----------
@app.get("/skills", response_model=list[schemas.SkillOut])
def skills(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return db.scalars(select(Skill).order_by(Skill.category, Skill.name)).all()


@app.get("/professions", response_model=list[schemas.ProfessionOut])
def professions(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return db.scalars(select(Profession).order_by(Profession.title)).all()


@app.post("/professions", response_model=schemas.ProfessionOut, status_code=201)
def create_profession(
    body: schemas.ProfessionIn, user: User = Depends(require_role("employer", "university")), db: Session = Depends(get_db)
):
    """Ish beruvchi/universitet kasb talablari va kompetensiya mezonlarini kiritadi."""
    if db.scalar(select(Profession).where(Profession.title == body.title.strip())):
        raise HTTPException(409, "Bunday nomli kasb mavjud")
    ids = {r.skill_id for r in body.requirements}
    if len(ids) != len(body.requirements):
        raise HTTPException(422, "Bir kompetensiya ikki marta kiritilgan")
    found = set(db.scalars(select(Skill.id).where(Skill.id.in_(ids))))
    if found != ids:
        raise HTTPException(422, "Noma'lum kompetensiya ID")
    p = Profession(title=body.title.strip(), description=body.description, created_by=user.id)
    for r in body.requirements:
        p.skills.append(ProfessionSkill(skill_id=r.skill_id, required_level=r.required_level, weight=r.weight))
    db.add(p)
    db.commit()
    return p


# ---------- Talaba ----------
student_only = require_role("student")


@app.post("/evidence", response_model=schemas.EvidenceOut, status_code=201)
def add_evidence(body: schemas.EvidenceIn, user: User = Depends(student_only), db: Session = Depends(get_db)):
    if not db.get(Skill, body.skill_id):
        raise HTTPException(404, "Kompetensiya topilmadi")
    # O'zini baholash hech qachon tasdiq hisoblanmaydi va ekspert navbatiga tushmaydi.
    status = "self" if body.type == "self" else "pending"
    e = Evidence(user_id=user.id, status=status, **body.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@app.get("/evidence", response_model=list[schemas.EvidenceOut])
def my_evidence(user: User = Depends(student_only), db: Session = Depends(get_db)):
    return db.scalars(select(Evidence).where(Evidence.user_id == user.id).order_by(Evidence.created_at.desc())).all()


@app.delete("/evidence/{eid}", status_code=204)
def delete_evidence(eid: int, user: User = Depends(student_only), db: Session = Depends(get_db)):
    e = db.get(Evidence, eid)
    if not e or e.user_id != user.id:
        raise HTTPException(404, "Dalil topilmadi")
    if e.status == "verified":
        raise HTTPException(409, "Tasdiqlangan dalilni o'chirib bo'lmaydi")
    db.delete(e)
    db.commit()


@app.post("/evidence/{eid}/analyze", response_model=schemas.EvidenceOut)
def analyze(eid: int, user: User = Depends(student_only), db: Session = Depends(get_db)):
    e = db.get(Evidence, eid)
    if not e or e.user_id != user.id:
        raise HTTPException(404, "Dalil topilmadi")
    r = ai.analyze_evidence(e.skill.name, e.type, e.title, e.description, e.url, e.claimed_level)
    e.ai_level, e.ai_feedback = r["level"], r["feedback"]
    db.commit()
    return e


@app.get("/profile")
def profile(user: User = Depends(student_only), db: Session = Depends(get_db)):
    levels = services.skill_levels(db, user.id)
    out = []
    for s in db.scalars(select(Skill).order_by(Skill.category, Skill.name)):
        lv = levels.get(s.id)
        if lv:
            out.append({"skill": {"id": s.id, "name": s.name, "category": s.category}, **lv})
    return {"skills": out}


@app.get("/skill-gap")
def my_gap(user: User = Depends(student_only), db: Session = Depends(get_db)):
    return services.skill_gap(db, user)


@app.post("/roadmap/generate", response_model=list[schemas.RoadmapOut])
def gen_roadmap(user: User = Depends(student_only), db: Session = Depends(get_db)):
    if not user.profession_id:
        raise HTTPException(409, "Avval kasbiy maqsadni tanlang")
    services.generate_roadmap(db, user)
    return roadmap(user, db)


@app.get("/roadmap", response_model=list[schemas.RoadmapOut])
def roadmap(user: User = Depends(student_only), db: Session = Depends(get_db)):
    return db.scalars(select(RoadmapItem).where(RoadmapItem.user_id == user.id).order_by(RoadmapItem.position)).all()


@app.patch("/roadmap/{rid}", response_model=schemas.RoadmapOut)
def toggle_roadmap(rid: int, body: schemas.RoadmapPatch, user: User = Depends(student_only), db: Session = Depends(get_db)):
    r = db.get(RoadmapItem, rid)
    if not r or r.user_id != user.id:
        raise HTTPException(404, "Band topilmadi")
    r.done = body.done
    db.commit()
    return r


@app.get("/passport")
def my_passport(user: User = Depends(student_only), db: Session = Depends(get_db)):
    return {"student": {"name": user.name, "faculty": user.faculty}, "skills": services.passport(db, user)}


# ---------- Universitet / ekspert ----------
uni_only = require_role("university")


@app.get("/review/queue", response_model=list[schemas.ReviewItem])
def review_queue(_: User = Depends(uni_only), db: Session = Depends(get_db)):
    rows = db.scalars(select(Evidence).where(Evidence.status == "pending").order_by(Evidence.created_at)).all()
    return [
        schemas.ReviewItem(**schemas.EvidenceOut.model_validate(e).model_dump(), student_name=e.user.name,
                           student_faculty=e.user.faculty)
        for e in rows
    ]


@app.post("/review/{eid}", response_model=schemas.EvidenceOut)
def review(eid: int, body: schemas.ReviewIn, user: User = Depends(uni_only), db: Session = Depends(get_db)):
    e = db.get(Evidence, eid)
    if not e or e.status != "pending":
        raise HTTPException(404, "Tekshiruvga kutayotgan dalil topilmadi")
    if body.approve:
        e.status = "verified"
        e.verified_level = body.verified_level or e.claimed_level
    else:
        e.status = "rejected"
        e.verified_level = None
    e.reviewer_id, e.reviewer_note, e.reviewed_at = user.id, body.note, datetime.now(timezone.utc)
    db.commit()
    return e


@app.get("/university/analytics")
def analytics(_: User = Depends(uni_only), db: Session = Depends(get_db)):
    """Umumlashtirilgan va anonim natijalar: shaxsiy ma'lumot qaytarilmaydi."""
    students = db.scalars(select(User).where(User.role == "student")).all()
    total = len(students)
    gap_by_skill: dict[str, dict] = {}
    readiness, by_faculty = [], {}
    for st in students:
        g = services.skill_gap(db, st)
        if not g["profession"]:
            continue
        readiness.append(g["readiness"])
        f = by_faculty.setdefault(st.faculty or "Ko'rsatilmagan", [])
        f.append(g["readiness"])
        for it in g["items"]:
            d = gap_by_skill.setdefault(it["skill"]["name"], {"skill": it["skill"]["name"], "students": 0, "with_gap": 0, "avg_gap": 0})
            d["students"] += 1
            d["avg_gap"] += it["gap"]
            if it["gap"] > 0:
                d["with_gap"] += 1
    skills = []
    for d in gap_by_skill.values():
        d["avg_gap"] = round(d["avg_gap"] / d["students"], 2)
        skills.append(d)
    skills.sort(key=lambda x: (-x["avg_gap"], x["skill"]))
    ev = dict(db.execute(select(Evidence.status, func.count()).group_by(Evidence.status)).all())
    return {
        "students_total": total,
        "students_with_goal": len(readiness),
        "avg_readiness": round(sum(readiness) / len(readiness)) if readiness else 0,
        "by_faculty": [{"faculty": k, "students": len(v), "avg_readiness": round(sum(v) / len(v))} for k, v in sorted(by_faculty.items())],
        "top_gaps": skills[:10],
        "evidence": {"pending": ev.get("pending", 0), "verified": ev.get("verified", 0), "rejected": ev.get("rejected", 0)},
    }


# ---------- Ish beruvchi ----------
@app.get("/employer/candidates")
def candidates(profession_id: int, _: User = Depends(require_role("employer")), db: Session = Depends(get_db)):
    """Faqat rozilik bergan talabalar; faqat tasdiqlangan ko'nikmalar ko'rsatiladi."""
    prof = db.get(Profession, profession_id)
    if not prof:
        raise HTTPException(404, "Kasb topilmadi")
    out = []
    for st in db.scalars(select(User).where(User.role == "student", User.consent_employers.is_(True))):
        g = services.skill_gap(db, st, prof)
        out.append(
            {
                "id": st.id, "name": st.name, "faculty": st.faculty, "match": g["readiness"],
                "skills": [{"name": i["skill"]["name"], "required": i["required"], "verified": i["verified"]} for i in g["items"]],
            }
        )
    out.sort(key=lambda c: -c["match"])
    return {"profession": {"id": prof.id, "title": prof.title}, "candidates": out}
