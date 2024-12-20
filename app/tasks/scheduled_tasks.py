# app/tasks/scheduled_tasks.py
from app import celery
from app.services.hittrax_sync import HittraxSync

@celery.task
def sync_hittrax_data():
    """Daily sync of HitTrax data"""
    try:
        # Sync last 2 days of data to catch any updates
        HittraxSync.sync_athletes()
        HittraxSync.sync_sessions(days_back=2)
        HittraxSync.sync_plays(days_back=2)
        return "HitTrax sync completed successfully"
    except Exception as e:
        return f"Error during HitTrax sync: {str(e)}"

# Schedule the task to run daily at 2 AM
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=2, minute=0),  # 2 AM
        sync_hittrax_data.s(),
        name='daily-hittrax-sync'
    )