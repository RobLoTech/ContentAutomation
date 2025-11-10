import schedule
import time
import os
from datetime import datetime

def run_news_summarizer():
    """Run news summarizer worker"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running News Summarizer...")
    print(f"{'='*60}\n")
    os.system("cd workers && python news_summarizer.py")

def run_metrics_logger():
    """Run metrics logger worker"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running Metrics Logger...")
    print(f"{'='*60}\n")
    os.system("cd workers && python metrics_logger.py")

def run_content_audit():
    """Run monthly content audit"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running Content Audit...")
    print(f"{'='*60}\n")
    os.system("cd workers && python site_auditor.py")

def check_and_run_monthly_audit():
    """Check if today is the 1st of the month and run content audit"""
    today = datetime.now()
    if today.day == 1:
        run_content_audit()

def setup_schedules():
    """Set up all scheduled tasks"""
    
    schedule.every().day.at("07:00").do(run_news_summarizer)
    
    schedule.every().sunday.at("20:00").do(run_metrics_logger)
    
    schedule.every().day.at("00:01").do(check_and_run_monthly_audit)
    
    print("✅ Scheduler configured:")
    print("   - News Summarizer: Daily at 7:00 AM EST")
    print("   - Metrics Logger: Every Sunday at 8:00 PM EST")
    print("   - Content Audit: 1st of each month at 12:01 AM EST")
    print("\n⏳ Waiting for scheduled tasks...")

def run_scheduler():
    """Main scheduler loop"""
    setup_schedules()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    print("RobLoTech Automation Scheduler")
    print("=" * 60)
    print("\nStarting scheduler daemon...\n")
    
    run_scheduler()
