from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import SEED_DEMO, UNIVERSITY_EMAIL, UNIVERSITY_PASSWORD
from .models import Evidence, Profession, ProfessionSkill, Skill, User, now
from .security import hash_password

SKILLS = [
    ("Python dasturlash", "practical"), ("SQL va ma'lumotlar bazalari", "practical"),
    ("Algoritmlar va ma'lumotlar tuzilmasi", "academic"), ("Git va versiyalarni boshqarish", "digital"),
    ("Web API (REST) ishlab chiqish", "practical"), ("HTML/CSS/JavaScript", "practical"),
    ("Ma'lumotlarni tahlil qilish", "practical"), ("Statistika asoslari", "academic"),
    ("Vizualizatsiya (grafik va dashboard)", "digital"), ("Ingliz tili (texnik)", "academic"),
    ("Jamoada ishlash", "personal"), ("Muloqot va taqdimot", "personal"),
    ("Vaqtni boshqarish", "personal"), ("Tanqidiy fikrlash", "personal"),
    ("Axborot xavfsizligi asoslari", "digital"), ("Loyihalarni boshqarish", "personal"),
]

PROFESSIONS = {
    "Junior Python Developer": ("Python va web backend bo'yicha boshlang'ich lavozim", {
        "Python dasturlash": (4, 3), "SQL va ma'lumotlar bazalari": (3, 2),
        "Algoritmlar va ma'lumotlar tuzilmasi": (3, 2), "Git va versiyalarni boshqarish": (3, 2),
        "Web API (REST) ishlab chiqish": (3, 2), "Ingliz tili (texnik)": (3, 1), "Jamoada ishlash": (3, 1)}),
    "Data Analyst": ("Ma'lumotlarni tahlil qilish va hisobot tayyorlash", {
        "Ma'lumotlarni tahlil qilish": (4, 3), "SQL va ma'lumotlar bazalari": (4, 3),
        "Statistika asoslari": (3, 2), "Vizualizatsiya (grafik va dashboard)": (3, 2),
        "Python dasturlash": (3, 2), "Muloqot va taqdimot": (3, 1), "Tanqidiy fikrlash": (3, 1)}),
    "Frontend Developer": ("Web interfeyslar yaratish", {
        "HTML/CSS/JavaScript": (4, 3), "Git va versiyalarni boshqarish": (3, 2),
        "Web API (REST) ishlab chiqish": (3, 2), "Jamoada ishlash": (3, 1),
        "Ingliz tili (texnik)": (3, 1), "Vaqtni boshqarish": (2, 1)}),
}


def seed(db: Session) -> None:
    if not db.scalar(select(Skill.id).limit(1)):
        for n, c in SKILLS:
            db.add(Skill(name=n, category=c))
        db.flush()
        by_name = {s.name: s for s in db.scalars(select(Skill))}
        for title, (desc, reqs) in PROFESSIONS.items():
            p = Profession(title=title, description=desc)
            for sname, (lvl, w) in reqs.items():
                p.skills.append(ProfessionSkill(skill_id=by_name[sname].id, required_level=lvl, weight=w))
            db.add(p)
        db.commit()

    if UNIVERSITY_EMAIL and UNIVERSITY_PASSWORD and not db.scalar(select(User).where(User.email == UNIVERSITY_EMAIL.lower())):
        db.add(User(email=UNIVERSITY_EMAIL.lower(), name="Universitet (ekspert)", role="university",
                    password_hash=hash_password(UNIVERSITY_PASSWORD)))
        db.commit()

    if SEED_DEMO and not db.scalar(select(User).where(User.email == "student@demo.uz")):
        _demo(db)


def _demo(db: Session) -> None:
    pw = hash_password("demo1234")
    py = db.scalar(select(Profession).where(Profession.title == "Junior Python Developer"))
    uni = User(email="uni@demo.uz", name="Demo Universitet", role="university", password_hash=pw)
    hr = User(email="hr@demo.uz", name="Demo Kompaniya (HR)", role="employer", password_hash=pw)
    st = User(email="student@demo.uz", name="Demo Talaba", role="student", faculty="Dasturiy injiniring",
              profession_id=py.id if py else None, consent_employers=True, password_hash=pw)
    db.add_all([uni, hr, st])
    db.flush()
    s = {x.name: x for x in db.scalars(select(Skill))}
    rows = [
        ("Python dasturlash", "project", "Telegram bot loyihasi", "Python va aiogram bilan buyurtma qabul qiluvchi bot yozdim.", 3, "verified", 3),
        ("Git va versiyalarni boshqarish", "assignment", "Git topshirig'i", "Branch, merge va pull request bilan jamoaviy topshiriq.", 3, "verified", 3),
        ("Jamoada ishlash", "self", "O'zini baholash", "Kurs loyihalarida jamoada ishlaganman.", 3, "self", None),
        ("SQL va ma'lumotlar bazalari", "certificate", "SQL kursi sertifikati", "Onlayn kurs sertifikati.", 3, "pending", None),
    ]
    for sk, t, title, desc, lvl, status, vl in rows:
        db.add(Evidence(user_id=st.id, skill_id=s[sk].id, type=t, title=title, description=desc, claimed_level=lvl,
                        status=status, verified_level=vl, reviewer_id=uni.id if status == "verified" else None,
                        reviewed_at=now() if status == "verified" else None))
    db.commit()
