# run_sync.py
import logging
from app import create_app
from app.services.hittrax_sync import HittraxSync

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('run_sync')

def main():
    logger = setup_logging()
    logger.info("Starting HitTrax sync process")
    
    # Create app context
    app = create_app()
    with app.app_context():
        try:
            # Initialize sync
            sync = HittraxSync()
            
            # Run full sync
            logger.info("Running full sync")
            result = sync.run_full_sync()
            
            if result['status'] == 'success':
                logger.info("Sync completed successfully!")
                logger.info(f"Users synced: {result['users_synced']}")
                logger.info(f"Sessions synced: {result['sessions_synced']}")
                logger.info(f"Plays synced: {result['plays_synced']}")
            else:
                logger.error(f"Sync failed: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error during sync process: {str(e)}")
            raise

if __name__ == "__main__":
    main()