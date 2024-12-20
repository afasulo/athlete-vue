import pymssql
import pandas as pd
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.config import Config

class HittraxSync:
    """Enhanced HitTrax sync implementation with full and incremental sync capabilities"""
    
    # Conversion constants
    MPS_TO_MPH = 2.23694
    METERS_TO_FEET = 3.28084
    
    def __init__(self):
        """Initialize logger and database connections"""
        # Set up logging
        self.logger = logging.getLogger('HittraxSync')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Create SQLAlchemy engine for PostgreSQL
        self.pg_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    def reset_database(self):
        """Drop and recreate tables in proper order"""
        self.logger.info("Resetting database - dropping all tables...")
        
        try:
            with self.pg_engine.connect() as conn:
                # Drop in reverse order of dependencies
                conn.execute(text("DROP TABLE IF EXISTS plays CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS session CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error resetting database: {str(e)}")
            raise

    def get_mssql_connection(self):
        """Create connection to HitTrax MS SQL database using FreeTDS"""
        return pymssql.connect(
            server=Config.HITTRAX_DB['server'],
            port=Config.HITTRAX_DB['port'],
            database=Config.HITTRAX_DB['database'],
            user=Config.HITTRAX_DB['user'],
            password=Config.HITTRAX_DB['password'],
            tds_version='7.0'
        )

    def sync_users(self, full_sync=False):
        """Sync Users table from HitTrax to PostgreSQL"""
        self.logger.info(f"Starting {'full' if full_sync else 'incremental'} users sync")
        
        try:
            with self.get_mssql_connection() as conn:
                query = """
                SELECT 
                    Id, UnitId, FirstName, LastName, UserName, Password,
                    Created, Email, Stadium, SkillLevel, GameType, Height,
                    Role, Active, Weight, Position, Bats, Throws,
                    School, HomeTown, GraduationYear, Gender, BirthDate
                FROM Users
                WHERE Active = 1
                """
                
                if not full_sync:
                    query += " AND DATEADD(day, -2, GETDATE()) <= Created"
                
                # Create a SQLAlchemy engine that wraps the pymssql connection
                source_engine = create_engine('mssql+pymssql://', creator=lambda: conn)
                df = pd.read_sql(query, source_engine)
                
                self.logger.info(f"Retrieved {len(df)} users from source")
                
                if not df.empty:
                    # Convert column names to lowercase
                    df.columns = df.columns.str.lower()
                    df.to_sql('users', self.pg_engine, if_exists='append', index=False,
                             method='multi', chunksize=1000)
                    self.logger.info(f"Successfully synced {len(df)} users")
                return len(df)
                
        except Exception as e:
            self.logger.error(f"Error syncing users: {str(e)}")
            raise

    def sync_sessions(self, full_sync=False):
        """Sync Sessions table from HitTrax to PostgreSQL"""
        self.logger.info(f"Starting {'full' if full_sync else 'incremental'} sessions sync")
        
        try:
            with self.get_mssql_connection() as conn:
                # Create a SQLAlchemy engine that wraps the pymssql connection
                source_engine = create_engine('mssql+pymssql://', creator=lambda: conn)
                
                query = """
                SELECT 
                    Id, UnitId, UserId, TimeStamp, Stadium, Type,
                    SkillLevel, GameType, MaxPitchVel, MaxExitVel, 
                    AvgPitchVel, AvgExitVel, AvgElevation, AvgDistance,
                    MaxDistance, PitchCount, HitCount, Singles, Doubles,
                    Triples, HomeRuns, FoulBalls, Strikes, Balls, AVG,
                    SLG, Active, StrikeZoneWidth
                FROM Session
                WHERE Active = 1
                """
                
                if not full_sync:
                    query += " AND DATEADD(day, -2, GETDATE()) <= TimeStamp"
                    
                df = pd.read_sql(query, source_engine)
                
                self.logger.info(f"Retrieved {len(df)} sessions from source")
                
                if not df.empty:
                    # Convert column names to lowercase
                    df.columns = df.columns.str.lower()
                    df.to_sql('session', self.pg_engine, if_exists='append', index=False,
                             method='multi', chunksize=1000)
                    self.logger.info(f"Successfully synced {len(df)} sessions")
                return len(df)
                
        except Exception as e:
            self.logger.error(f"Error syncing sessions: {str(e)}")
            raise

    def sync_plays(self, full_sync=False):
        """Sync Plays table from HitTrax to PostgreSQL"""
        self.logger.info(f"Starting {'full' if full_sync else 'incremental'} plays sync")
        
        try:
            with self.get_mssql_connection() as conn:
                # Create a SQLAlchemy engine that wraps the pymssql connection
                source_engine = create_engine('mssql+pymssql://', creator=lambda: conn)
                
                query = """
                SELECT 
                    p.Id, p.SessionId, p.TimeStamp, 
                    p.ExitBallVel1, p.ExitBallVel2, p.ExitBallVel3,
                    p.Distance, p.PitchVel, p.Result, p.Type, 
                    p.Fielder, p.Quadrant, p.PitchType, p.Elevation,
                    p.GroundDist, p.Active, p.ExitVelo, p.Points
                FROM Plays p
                JOIN Session s ON p.SessionId = s.Id
                WHERE p.Active = 1 AND s.Active = 1
                """
                
                if not full_sync:
                    query += " AND DATEADD(day, -2, GETDATE()) <= p.TimeStamp"
                    
                df = pd.read_sql(query, source_engine)
                
                self.logger.info(f"Retrieved {len(df)} plays from source")
                
                if not df.empty:
                    # Convert column names to lowercase
                    df.columns = df.columns.str.lower()
                    df.to_sql('plays', self.pg_engine, if_exists='append', index=False,
                             method='multi', chunksize=1000)
                    self.logger.info(f"Successfully synced {len(df)} plays")
                return len(df)
                
        except Exception as e:
            self.logger.error(f"Error syncing plays: {str(e)}")
            raise

    def run_full_sync(self):
        """Run a complete sync of all historical data"""
        self.logger.info("Starting full HitTrax sync")
        try:
            # Reset database
            self.reset_database()
            
            # Sync data in correct order
            users_count = self.sync_users(full_sync=True)
            sessions_count = self.sync_sessions(full_sync=True)
            plays_count = self.sync_plays(full_sync=True)
            
            return {
                'status': 'success',
                'users_synced': users_count,
                'sessions_synced': sessions_count,
                'plays_synced': plays_count
            }
            
        except Exception as e:
            self.logger.error(f"Error during full sync: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def run_incremental_sync(self):
        """Run an incremental sync of recent data"""
        self.logger.info("Starting incremental HitTrax sync")
        try:
            users_count = self.sync_users(full_sync=False)
            sessions_count = self.sync_sessions(full_sync=False)
            plays_count = self.sync_plays(full_sync=False)
            
            return {
                'status': 'success',
                'users_synced': users_count,
                'sessions_synced': sessions_count,
                'plays_synced': plays_count
            }
            
        except Exception as e:
            self.logger.error(f"Error during incremental sync: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }