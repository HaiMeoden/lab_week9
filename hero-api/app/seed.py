from sqlmodel import Session, select
from app.database import engine
from app.models import Team, Hero, Mission, SQLModel

def seed_db():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        existing_teams = session.exec(select(Team)).first()
        if existing_teams:
            print("Database already seeded!")
            return
            
        print("Seeding database...")
        
        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")
        
        mission1 = Mission(title="Battle of Sokovia")
        mission2 = Mission(title="Save the President")
        
        ironman = Hero(name="Tony", secret_name="Iron Man", age=45, team=avengers, missions=[mission1])
        blackwidow = Hero(name="Natasha", secret_name="Black Widow", age=35, team=avengers, missions=[mission1, mission2])
        wolverine = Hero(name="Logan", secret_name="Wolverine", age=150, team=xmen)
        spiderman = Hero(name="Peter", secret_name="Spider-Man", age=16)
        captain = Hero(name="Steve", secret_name="Captain America", team=avengers, missions=[mission1])
        
        session.add(avengers)
        session.add(xmen)
        session.add(ironman)
        session.add(blackwidow)
        session.add(wolverine)
        session.add(spiderman)
        session.add(captain)
        
        session.commit()
        print("Done!")

if __name__ == "__main__":
    seed_db()