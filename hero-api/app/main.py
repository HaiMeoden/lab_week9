from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.models import Hero, Team 
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import select
from app.database import SessionDep
from app.models import Hero, HeroCreate, HeroPublic, HeroUpdate
from sqlalchemy.exc import IntegrityError
from app.models import Team, TeamCreate, TeamPublic
from app.models import Mission, MissionCreate, MissionPublic

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello Hero API"}

@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero_in)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None
):
    statement = select(Hero)
    
    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)
    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)
    if name is not None:
        statement = statement.where(Hero.name.ilike(f"%{name}%"))
        
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    hero_data = hero_in.model_dump(exclude_unset=True)
    hero.sqlmodel_update(hero_data)
    
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    session.delete(hero)
    session.commit()
    return None

@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    db_team = Team.model_validate(team_in)
    session.add(db_team)
    try:
        session.commit()
        session.refresh(db_team)
        return db_team
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")

@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep, offset: int = 0, limit: int = 10):
    return session.exec(select(Team).offset(offset).limit(limit)).all()

@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def get_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes

@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    db_mission = Mission.model_validate(mission_in)
    session.add(db_mission)
    session.commit()
    session.refresh(db_mission)
    return db_mission

@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    
    if not hero or not mission:
        raise HTTPException(status_code=404, detail="Hero or Mission not found")
    
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return None

@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def get_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions