from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(pattern="^(student|employer)$")
    faculty: str | None = Field(default=None, max_length=255)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class MeUpdate(BaseModel):
    faculty: str | None = Field(default=None, max_length=255)
    profession_id: int | None = None
    consent_employers: bool | None = None


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    faculty: str | None
    profession_id: int | None
    consent_employers: bool

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    token: str
    user: UserOut


class SkillOut(BaseModel):
    id: int
    name: str
    category: str

    model_config = {"from_attributes": True}


class ReqIn(BaseModel):
    skill_id: int
    required_level: int = Field(ge=1, le=5)
    weight: int = Field(default=1, ge=1, le=3)


class ProfessionIn(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str = ""
    requirements: list[ReqIn] = Field(min_length=1)


class ReqOut(BaseModel):
    skill: SkillOut
    required_level: int
    weight: int

    model_config = {"from_attributes": True}


class ProfessionOut(BaseModel):
    id: int
    title: str
    description: str
    skills: list[ReqOut]

    model_config = {"from_attributes": True}


class EvidenceIn(BaseModel):
    skill_id: int
    type: str = Field(pattern="^(grade|assignment|project|certificate|self)$")
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(default="", max_length=4000)
    url: str | None = Field(default=None, max_length=500)
    claimed_level: int = Field(ge=1, le=5)


class EvidenceOut(BaseModel):
    id: int
    skill: SkillOut
    type: str
    title: str
    description: str
    url: str | None
    claimed_level: int
    status: str
    verified_level: int | None
    reviewer_note: str | None
    ai_level: int | None
    ai_feedback: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewIn(BaseModel):
    approve: bool
    verified_level: int | None = Field(default=None, ge=1, le=5)
    note: str = Field(default="", max_length=2000)


class ReviewItem(EvidenceOut):
    student_name: str
    student_faculty: str | None


class RoadmapOut(BaseModel):
    id: int
    skill: SkillOut
    kind: str
    title: str
    detail: str
    position: int
    done: bool

    model_config = {"from_attributes": True}


class RoadmapPatch(BaseModel):
    done: bool
