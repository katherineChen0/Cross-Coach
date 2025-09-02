import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ..analytics.correlation_service import run_weekly_correlation_analysis

logger = logging.getLogger(__name__)

class BackgroundScheduler:
    """Background task scheduler for periodic analytics jobs."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs."""
        # Run correlation analysis every Sunday at 2 AM
        self.scheduler.add_job(
            func=self._run_correlation_analysis,
            trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
            id='weekly_correlation_analysis',
            name='Weekly Correlation Analysis',
            replace_existing=True
        )
        
        logger.info("Background jobs scheduled")
    
    async def _run_correlation_analysis(self):
        """Run correlation analysis asynchronously."""
        try:
            logger.info("Starting scheduled correlation analysis")
            # Run in thread pool since the analysis is CPU-intensive
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, run_weekly_correlation_analysis)
            logger.info("Scheduled correlation analysis completed")
        except Exception as e:
            logger.error(f"Error in scheduled correlation analysis: {e}")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Background scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Background scheduler shutdown")

# Global scheduler instance
scheduler = BackgroundScheduler() 