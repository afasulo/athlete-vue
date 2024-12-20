# create_views.py

from app import create_app, db
from sqlalchemy import text

def create_views():
    app = create_app()
    with app.app_context():
        try:
            # Drop existing views if they exist
            db.session.execute(text("DROP VIEW IF EXISTS PlaysConverted CASCADE;"))
            db.session.execute(text("DROP VIEW IF EXISTS SessionConverted CASCADE;"))
            db.session.execute(text("DROP VIEW IF EXISTS UsersConverted CASCADE;"))
            
            # Create UsersConverted view
            db.session.execute(text("""
                CREATE OR REPLACE VIEW UsersConverted AS
                SELECT 
                    Id,
                    UnitId,
                    FirstName,
                    LastName,
                    UserName,
                    Password,
                    Created,
                    Email,
                    Stadium,
                    SkillLevel,
                    GameType,
                    ROUND((Height * 3.28084)::numeric, 1) as HeightFeet,
                    ROUND((Weight * 2.20462)::numeric, 1) as WeightLbs,
                    Role,
                    Active,
                    Position,
                    Bats,
                    Throws,
                    School,
                    HomeTown,
                    GraduationYear,
                    Gender,
                    BirthDate
                FROM Users;
            """))
            
            # Create SessionConverted view
            db.session.execute(text("""
                CREATE OR REPLACE VIEW SessionConverted AS
                SELECT 
                    Id,
                    UnitId,
                    UserId,
                    TimeStamp,
                    Stadium,
                    Type,
                    SkillLevel,
                    GameType,
                    ROUND((MaxPitchVel * 2.23694)::numeric, 1) as MaxPitchVelMph,
                    ROUND((MaxExitVel * 2.23694)::numeric, 1) as MaxExitVelMph,
                    ROUND((AvgPitchVel * 2.23694)::numeric, 1) as AvgPitchVelMph,
                    ROUND((AvgExitVel * 2.23694)::numeric, 1) as AvgExitVelMph,
                    ROUND((AvgDistance * 3.28084)::numeric) as AvgDistanceFeet,
                    ROUND((MaxDistance * 3.28084)::numeric) as MaxDistanceFeet,
                    PitchCount,
                    HitCount,
                    Singles,
                    Doubles,
                    Triples,
                    HomeRuns,
                    FoulBalls,
                    Strikes,
                    Balls,
                    AVG,
                    SLG,
                    Active,
                    StrikeZoneWidth
                FROM Session;
            """))
            
            # Create PlaysConverted view
            db.session.execute(text("""
                CREATE OR REPLACE VIEW PlaysConverted AS
                SELECT 
                    Id,
                    SessionId,
                    TimeStamp,
                    ROUND((ExitVelo * 2.23694)::numeric, 1) as ExitVelMph,
                    ROUND((Distance * 3.28084)::numeric) as DistanceFeet,
                    ROUND((PitchVel * 2.23694)::numeric, 1) as PitchVelMph,
                    Result,
                    Type,
                    Fielder,
                    Quadrant,
                    PitchType,
                    Elevation,
                    ROUND((GroundDist * 3.28084)::numeric) as GroundDistFeet,
                    Active,
                    Points
                FROM Plays;
            """))
            
            db.session.commit()
            print("Successfully created views!")
            
        except Exception as e:
            print(f"Error creating views: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_views()