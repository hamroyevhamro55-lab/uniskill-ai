from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # student | university | employer
    faculty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profession_id: Mapped[int | None] = mapped_column(ForeignKey("professions.id"), nullable=True)
    consent_employers: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(20))  # academic | practical | digital | personal


class Profession(Base):
    __tablename__ = "professions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", use_alter=True, name="fk_prof_creator"), nullable=True)
    skills: Mapped[list["ProfessionSkill"]] = relationship(
        back_populates="profession", cascade="all, delete-orphan", lazy="selectin"
    )


class ProfessionSkill(Base):
    __tablename__ = "profession_skills"
    __table_args__ = (UniqueConstraint("profession_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    profession_id: Mapped[int] = mapped_column(ForeignKey("professions.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    required_level: Mapped[int] = mapped_column(Integer, default=3)  # 1..5
    weight: Mapped[int] = mapped_column(Integer, default=1)  # 1..3
    profession: Mapped[Profession] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship(lazy="joined")


class Evidence(Base):
    """Talaba yuklagan dalil. Faqat 'verified' holati pasportga kiradi."""

    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    type: Mapped[str] = mapped_column(String(20))  # grade|assignment|project|certificate|self
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    claimed_level: Mapped[int] = mapped_column(Integer)  # talaba da'vosi 1..5
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|verified|rejected|self
    verified_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    skill: Mapped[Skill] = relationship(lazy="joined")
    user: Mapped[User] = relationship(foreign_keys=[user_id], lazy="joined")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    kind: Mapped[str] = mapped_column(String(20))  # course|project|mentoring|internship|reassess
    title: Mapped[str] = mapped_column(String(255))
    detail: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    skill: Mapped[Skill] = relationship(lazy="joined")
