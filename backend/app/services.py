from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Evidence, Profession, RoadmapItem, Skill, User


def skill_levels(db: Session, user_id: int) -> dict[int, dict]:
    """Har bir kompetensiya bo'yicha: tasdiqlangan daraja va da'vo qilingan daraja."""
    rows = db.scalars(select(Evidence).where(Evidence.user_id == user_id)).all()
    out: dict[int, dict] = {}
    for e in rows:
        d = out.setdefault(e.skill_id, {"verified": 0, "claimed": 0, "evidence": 0})
        d["evidence"] += 1
        if e.status == "verified":
            d["verified"] = max(d["verified"], e.verified_level or 0)
        elif e.status != "rejected":
            d["claimed"] = max(d["claimed"], e.claimed_level)
    return out


def skill_gap(db: Session, user: User, profession: Profession | None = None) -> dict:
    prof = profession or (db.get(Profession, user.profession_id) if user.profession_id else None)
    if not prof:
        return {"profession": None, "readiness": 0, "items": []}
    levels = skill_levels(db, user.id)
    items, got, total = [], 0, 0
    for ps in prof.skills:
        lv = levels.get(ps.skill_id, {"verified": 0, "claimed": 0, "evidence": 0})
        gap = max(0, ps.required_level - lv["verified"])
        if gap == 0:
            status = "ok"
        elif lv["claimed"] >= ps.required_level:
            status = "unverified"  # da'vo bor, lekin tasdiqlanmagan
        else:
            status = "gap"
        got += min(lv["verified"], ps.required_level) * ps.weight
        total += ps.required_level * ps.weight
        items.append(
            {
                "skill": {"id": ps.skill.id, "name": ps.skill.name, "category": ps.skill.category},
                "required": ps.required_level,
                "verified": lv["verified"],
                "claimed": lv["claimed"],
                "gap": gap,
                "weight": ps.weight,
                "priority": gap * ps.weight,
                "status": status,
            }
        )
    items.sort(key=lambda i: (-i["priority"], i["skill"]["name"]))
    return {
        "profession": {"id": prof.id, "title": prof.title},
        "readiness": round(100 * got / total) if total else 0,
        "items": items,
    }


def generate_roadmap(db: Session, user: User) -> list[RoadmapItem]:
    """Skill Gap asosida qoidaga tayanuvchi reja. Bajarilgan bandlar saqlanadi."""
    gap = skill_gap(db, user)
    old = db.scalars(select(RoadmapItem).where(RoadmapItem.user_id == user.id)).all()
    for r in old:
        if not r.done:
            db.delete(r)
    db.flush()
    pos = len([r for r in old if r.done])
    created = []
    for it in gap["items"]:
        if it["gap"] == 0:
            continue
        name = it["skill"]["name"]
        sid = it["skill"]["id"]
        steps = []
        if it["verified"] == 0 and it["claimed"] >= it["required"]:
            steps.append(("reassess", f"{name}: dalilni tasdiqlatish", "Amaliy topshiriq yoki loyiha himoyasi orqali ekspert tekshiruviga yuboring."))
        else:
            steps.append(("course", f"{name}: o'quv kursi", f"Hozirgi daraja {it['verified']}, kerakli daraja {it['required']}. Asosiy mavzularni o'rganing."))
            if it["gap"] >= 2:
                steps.append(("project", f"{name}: amaliy loyiha", "Mustaqil kichik loyiha bajarib, natijani dalil sifatida yuklang."))
            if it["gap"] >= 3:
                steps.append(("mentoring", f"{name}: mentorlik", "Soha mutaxassisi bilan 2-3 ta konsultatsiya belgilang."))
            steps.append(("reassess", f"{name}: qayta baholash", "Yangi dalilni yuklab, ekspert tekshiruvidan o'tkazing."))
        for kind, title, detail in steps:
            r = RoadmapItem(user_id=user.id, skill_id=sid, kind=kind, title=title, detail=detail, position=pos)
            pos += 1
            db.add(r)
            created.append(r)
    db.commit()
    return created


def passport(db: Session, user: User) -> list[dict]:
    rows = db.scalars(
        select(Evidence)
        .where(Evidence.user_id == user.id, Evidence.status == "verified")
        .order_by(Evidence.reviewed_at.desc())
    ).all()
    best: dict[int, dict] = {}
    for e in rows:
        b = best.setdefault(
            e.skill_id,
            {"skill": {"id": e.skill.id, "name": e.skill.name, "category": e.skill.category}, "level": 0, "evidence": []},
        )
        b["level"] = max(b["level"], e.verified_level or 0)
        b["evidence"].append(
            {"id": e.id, "type": e.type, "title": e.title, "url": e.url, "level": e.verified_level,
             "verified_at": e.reviewed_at.isoformat() if e.reviewed_at else None}
        )
    return sorted(best.values(), key=lambda x: (-x["level"], x["skill"]["name"]))
