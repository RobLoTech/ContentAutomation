import csv
import os
from datetime import datetime, timedelta
import json

class MetricsLogger:
    def __init__(self):
        self.metrics_file = '../data/metrics.csv'
        self.ensure_metrics_file_exists()
    
    def ensure_metrics_file_exists(self):
        """Create metrics CSV if it doesn't exist"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'date', 'week', 'posts_published', 'total_impressions', 
                    'total_clicks', 'ctr_percent', 'newsletter_subs', 
                    'top_post_title', 'top_post_views', 'revenue_estimate'
                ])
    
    def log_weekly_metrics(self, posts_count, impressions, clicks, newsletter_subs, 
                          top_post_title='', top_post_views=0, revenue=0.0):
        """Log weekly metrics"""
        
        week_number = datetime.now().isocalendar()[1]
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        
        with open(self.metrics_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                date_str,
                week_number,
                posts_count,
                impressions,
                clicks,
                f"{ctr:.2f}",
                newsletter_subs,
                top_post_title,
                top_post_views,
                f"{revenue:.2f}"
            ])
        
        print(f"✅ Logged metrics for week {week_number}")
        return {
            'date': date_str,
            'posts': posts_count,
            'ctr': ctr,
            'subs': newsletter_subs
        }
    
    def get_recent_metrics(self, weeks=4):
        """Get metrics for recent weeks"""
        if not os.path.exists(self.metrics_file):
            return []
        
        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_metrics = list(reader)
        
        return all_metrics[-weeks:] if len(all_metrics) > weeks else all_metrics
    
    def calculate_performance(self):
        """Calculate performance against targets"""
        from config import Config
        
        recent_metrics = self.get_recent_metrics(weeks=4)
        
        if not recent_metrics:
            return {
                'avg_posts_per_week': 0,
                'avg_ctr': 0,
                'avg_newsletter_subs': 0,
                'targets_met': False
            }
        
        avg_posts = sum(int(m['posts_published']) for m in recent_metrics) / len(recent_metrics)
        avg_ctr = sum(float(m['ctr_percent']) for m in recent_metrics) / len(recent_metrics)
        avg_subs = sum(int(m['newsletter_subs']) for m in recent_metrics) / len(recent_metrics)
        
        targets_met = (
            avg_posts >= Config.POSTS_PER_WEEK_TARGET and
            avg_ctr >= Config.CTR_TARGET and
            avg_subs >= Config.NEWSLETTER_SUBS_TARGET
        )
        
        return {
            'avg_posts_per_week': avg_posts,
            'avg_ctr': avg_ctr,
            'avg_newsletter_subs': avg_subs,
            'targets_met': targets_met,
            'targets': {
                'posts': Config.POSTS_PER_WEEK_TARGET,
                'ctr': Config.CTR_TARGET,
                'subs': Config.NEWSLETTER_SUBS_TARGET
            }
        }


def example_usage():
    """Example usage of metrics logger"""
    logger = MetricsLogger()
    
    logger.log_weekly_metrics(
        posts_count=3,
        impressions=5000,
        clicks=175,
        newsletter_subs=25,
        top_post_title='ChatGPT for Cybersecurity: 10 Practical Use Cases',
        top_post_views=1250,
        revenue=45.50
    )
    
    print("\n📊 Recent Metrics:")
    recent = logger.get_recent_metrics(weeks=4)
    for metric in recent:
        print(f"  Week {metric['week']}: {metric['posts_published']} posts, CTR: {metric['ctr_percent']}%, Subs: {metric['newsletter_subs']}")
    
    print("\n🎯 Performance vs Targets:")
    performance = logger.calculate_performance()
    print(f"  Avg Posts/Week: {performance['avg_posts_per_week']:.1f} (Target: {performance['targets']['posts']})")
    print(f"  Avg CTR: {performance['avg_ctr']:.2f}% (Target: {performance['targets']['ctr']}%)")
    print(f"  Avg Newsletter Subs: {performance['avg_newsletter_subs']:.1f} (Target: {performance['targets']['subs']})")
    print(f"  Targets Met: {'✅ Yes' if performance['targets_met'] else '❌ No'}")


if __name__ == '__main__':
    print("Metrics Logger - Example Usage")
    print("=" * 50)
    example_usage()
