from datetime import datetime, timezone
import enum

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, Enum as SAEnum

#TEAM
class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True)
    headquarters: str

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")

class TeamCreate(TeamBase):
    pass

class TeamPublic(TeamBase):
    id: int

def utc_now() -> datetime :
    return datetime.now( timezone.utc )
# HERO  
class HeroStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = None
    power: str | None = None
    team_id: int | None = Field(default=None, foreign_key="team.id")
    status: HeroStatus = Field(
        default=HeroStatus.active,
        sa_column=Column(SAEnum(HeroStatus, name="herostatus"), nullable=False)
    )
class HeroMissionLink(SQLModel, table=True):
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    mission_id: int | None = Field(default=None, foreign_key="mission.id", primary_key=True)

class MissionBase(SQLModel):
    title: str

class Mission(MissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="missions", link_model=HeroMissionLink)

class MissionCreate(MissionBase):
    pass

class MissionPublic(MissionBase):
    id: int

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str
    team: Team | None = Relationship(back_populates="heroes")
    created_at : datetime = Field ( default_factory=utc_now)
    missions: list[Mission] = Relationship(back_populates="heroes", link_model=HeroMissionLink)

class HeroCreate(HeroBase):
    secret_name: str

class HeroPublic(HeroBase):
    id: int
    created_at : datetime |None = None

class HeroUpdate(SQLModel):
    name: str | None = None
    age: int | None = None
    team_id: int | None = None
    secret_name: str | None = None