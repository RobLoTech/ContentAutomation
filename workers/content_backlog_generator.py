import csv
import os
from datetime import datetime

class ContentBacklogGenerator:
    def __init__(self):
        self.pillars = {
            'AI Tools & Automations': 10,
            'Security Awareness': 9,
            'How-To Workflows': 6
        }
        self.articles = []
    
    def generate_backlog(self):
        """Generate 25 article ideas across 3 pillars"""
        
        ai_automation_articles = [
            {
                'title': 'ChatGPT for Cybersecurity: 10 Practical Use Cases',
                'target_keyword': 'chatgpt cybersecurity',
                'intent': 'informational',
                'h2_outline': 'Introduction|What is ChatGPT|Threat Intelligence Analysis|Incident Response Automation|Security Policy Generation|Phishing Email Detection|Code Security Review|Security Documentation|Best Practices|Limitations|Conclusion',
                'cta': 'Download ChatGPT Security Prompts Cheat Sheet',
                'affiliate_angles': 'OpenAI Plus subscription, Jasper AI, Grammarly'
            },
            {
                'title': 'Make.com Security Automation: Build a Threat Alert System in 15 Minutes',
                'target_keyword': 'make.com security automation',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Why Automate Security Alerts|Prerequisites|Step 1: RSS Feed Setup|Step 2: Filter Configuration|Step 3: Notification Setup|Step 4: Testing|Advanced Customization|Conclusion',
                'cta': 'Get Make.com automation template',
                'affiliate_angles': 'Make.com Pro plan, StackSocial automation bundles'
            },
            {
                'title': 'AI-Powered Vulnerability Scanning Tools: Complete 2025 Guide',
                'target_keyword': 'ai vulnerability scanning',
                'intent': 'commercial',
                'h2_outline': 'Introduction|Traditional vs AI Scanning|Top 10 AI Scanners|Feature Comparison|Pricing Guide|Integration Options|Getting Started|Best Practices|Conclusion',
                'cta': 'Compare AI scanning tools',
                'affiliate_angles': 'Security tool subscriptions, Amazon security books'
            },
            {
                'title': 'Automated Security Reporting with Python: A Beginner\'s Guide',
                'target_keyword': 'python security reporting',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Why Automate Reports|Setup Environment|Data Collection Scripts|Report Generation|Email Automation|Scheduling with Cron|Real-World Examples|Conclusion',
                'cta': 'Download Python security scripts',
                'affiliate_angles': 'Python courses, hosting for scripts'
            },
            {
                'title': 'No-Code Security Dashboards: Visualize Threats Without Programming',
                'target_keyword': 'no-code security dashboard',
                'intent': 'commercial',
                'h2_outline': 'Introduction|Best No-Code Tools|Google Sheets Dashboard|Power BI Security Metrics|Tableau Integration|Live Demo Setup|Customization Tips|Conclusion',
                'cta': 'Access free dashboard templates',
                'affiliate_angles': 'StackSocial no-code tools, AppSumo deals'
            },
            {
                'title': 'Zapier vs Make.com for Security Workflows: Which Should You Choose?',
                'target_keyword': 'zapier vs make.com security',
                'intent': 'commercial comparison',
                'h2_outline': 'Introduction|Feature Comparison|Pricing Analysis|Security Capabilities|Integration Options|Ease of Use|Real Use Cases|Verdict|Conclusion',
                'cta': 'Get automation starter pack',
                'affiliate_angles': 'Make.com, Zapier plans, automation courses'
            },
            {
                'title': 'AI Writing Tools for Security Documentation: Save 10 Hours Per Week',
                'target_keyword': 'ai security documentation',
                'intent': 'commercial',
                'h2_outline': 'Introduction|Documentation Challenges|Best AI Writing Tools|Grammarly for Security|Jasper Templates|ChatGPT Prompts|Workflow Integration|ROI Calculation|Conclusion',
                'cta': 'Try AI writing tools free',
                'affiliate_angles': 'Grammarly Business, Jasper AI, Copy.ai'
            },
            {
                'title': 'Automated Threat Intelligence Feeds: Setup Guide for SOC Teams',
                'target_keyword': 'threat intelligence automation',
                'intent': 'how-to',
                'h2_outline': 'Introduction|What Are Threat Feeds|Popular Feed Sources|Integration Methods|Python Scripts|SIEM Integration|False Positive Filtering|Monitoring Setup|Conclusion',
                'cta': 'Download threat feed scripts',
                'affiliate_angles': 'Security platforms, threat intel subscriptions'
            },
            {
                'title': 'Build a Personal Security Lab with Free AI Tools',
                'target_keyword': 'security lab ai tools',
                'intent': 'informational',
                'h2_outline': 'Introduction|Lab Architecture|Virtual Machine Setup|Free AI Security Tools|Network Simulation|Attack Scenarios|Learning Path|Resources|Conclusion',
                'cta': 'Get security lab checklist',
                'affiliate_angles': 'VPS hosting, online courses, security certifications'
            },
            {
                'title': 'Email Security Automation: Filter Phishing with AI and Make.com',
                'target_keyword': 'email security automation',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Phishing Threats|Make.com Email Module|AI Detection Logic|Rule Configuration|Alert System|Testing Examples|Maintenance Tips|Conclusion',
                'cta': 'Get Make.com phishing filter template',
                'affiliate_angles': 'Make.com, email security tools'
            }
        ]
        
        security_awareness_articles = [
            {
                'title': 'Social Engineering Red Flags: 15 Warning Signs Everyone Misses',
                'target_keyword': 'social engineering warning signs',
                'intent': 'informational',
                'h2_outline': 'Introduction|What is Social Engineering|Psychological Tactics|15 Red Flags|Real-World Examples|How to Respond|Training Your Team|Conclusion',
                'cta': 'Download social engineering checklist',
                'affiliate_angles': 'Security awareness training, anti-phishing tools'
            },
            {
                'title': 'Password Manager Comparison 2025: Which One Protects You Best?',
                'target_keyword': 'best password manager 2025',
                'intent': 'commercial comparison',
                'h2_outline': 'Introduction|Why You Need One|Top 10 Password Managers|Security Features|Pricing Breakdown|Family Plans|Business Options|Migration Guide|Conclusion',
                'cta': 'Compare password managers',
                'affiliate_angles': '1Password, LastPass, Bitwarden, Dashlane'
            },
            {
                'title': 'Zero Trust Security Explained for Non-Technical Users',
                'target_keyword': 'zero trust security explained',
                'intent': 'informational',
                'h2_outline': 'Introduction|Traditional Security Model|What is Zero Trust|Core Principles|Real-World Benefits|Implementation Basics|Small Business Guide|Conclusion',
                'cta': 'Get zero trust implementation guide',
                'affiliate_angles': 'Security platforms, VPN services'
            },
            {
                'title': 'Ransomware Prevention Checklist: 20 Steps to Protect Your Data',
                'target_keyword': 'ransomware prevention checklist',
                'intent': 'informational',
                'h2_outline': 'Introduction|Ransomware Landscape|Backup Strategy|Access Controls|Email Security|Software Updates|Network Segmentation|Incident Response Plan|Conclusion',
                'cta': 'Download ransomware defense kit',
                'affiliate_angles': 'Backup software, security tools, cyber insurance'
            },
            {
                'title': 'Home Network Security: Secure Your WiFi in 30 Minutes',
                'target_keyword': 'home network security',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Common Vulnerabilities|Router Configuration|Strong WiFi Passwords|Guest Network Setup|IoT Device Security|Network Monitoring|Regular Maintenance|Conclusion',
                'cta': 'Get home security setup guide',
                'affiliate_angles': 'Routers, security cameras, network tools'
            },
            {
                'title': 'Cloud Storage Security: Google Drive vs OneDrive vs Dropbox',
                'target_keyword': 'cloud storage security comparison',
                'intent': 'commercial comparison',
                'h2_outline': 'Introduction|Security Comparison|Encryption Methods|Privacy Policies|Compliance Certifications|Sharing Controls|Pricing vs Security|Best Choice By Use Case|Conclusion',
                'cta': 'Compare cloud storage plans',
                'affiliate_angles': 'Cloud storage subscriptions'
            },
            {
                'title': 'Mobile Device Security: Protect Your Phone from Hackers',
                'target_keyword': 'mobile device security',
                'intent': 'informational',
                'h2_outline': 'Introduction|Mobile Threat Landscape|OS Updates|App Permissions|Public WiFi Risks|VPN Usage|Biometric Security|Lost Device Procedures|Conclusion',
                'cta': 'Download mobile security checklist',
                'affiliate_angles': 'VPN services, mobile security apps'
            },
            {
                'title': 'Data Breach Response: What to Do When Your Info Is Compromised',
                'target_keyword': 'data breach response guide',
                'intent': 'informational',
                'h2_outline': 'Introduction|Detecting a Breach|Immediate Actions|Password Changes|Credit Monitoring|Identity Theft Protection|Legal Rights|Prevention for Future|Conclusion',
                'cta': 'Get breach response checklist',
                'affiliate_angles': 'Identity theft protection, credit monitoring services'
            },
            {
                'title': 'Business Email Compromise: How to Protect Your Company',
                'target_keyword': 'business email compromise prevention',
                'intent': 'informational',
                'h2_outline': 'Introduction|What is BEC|Attack Methods|Warning Signs|Email Authentication|Employee Training|Technical Controls|Incident Response|Conclusion',
                'cta': 'Download BEC prevention guide',
                'affiliate_angles': 'Email security gateways, training platforms'
            }
        ]
        
        howto_workflows_articles = [
            {
                'title': 'Build a Security News Aggregator with Python and RSS Feeds',
                'target_keyword': 'python rss security aggregator',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Project Overview|Required Libraries|RSS Feed Parser|Content Filtering|Summary Generation|Email Notifications|Scheduling with Cron|Conclusion',
                'cta': 'Download complete Python script',
                'affiliate_angles': 'Python courses, hosting services'
            },
            {
                'title': 'Automate Your Security Patching with These 5 Scripts',
                'target_keyword': 'automate security patching',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Patching Challenges|Script 1: Windows Updates|Script 2: Linux Updates|Script 3: Application Updates|Script 4: Verification|Script 5: Reporting|Conclusion',
                'cta': 'Download all patching scripts',
                'affiliate_angles': 'Patch management tools, hosting'
            },
            {
                'title': 'Set Up Automated Security Alerts with Google Sheets and Make.com',
                'target_keyword': 'google sheets security alerts',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Use Case Overview|Google Sheets Setup|Make.com Configuration|Trigger Logic|Alert Formatting|Testing Workflow|Advanced Tips|Conclusion',
                'cta': 'Get Make.com template',
                'affiliate_angles': 'Make.com Pro, Google Workspace'
            },
            {
                'title': 'Log Analysis Automation: Parse Security Logs with Python',
                'target_keyword': 'python log analysis automation',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Log Analysis Basics|Python Setup|Parsing Common Formats|Pattern Detection|Alert Generation|Visualization|Full Script Walkthrough|Conclusion',
                'cta': 'Download log analysis script',
                'affiliate_angles': 'Python books, SIEM platforms'
            },
            {
                'title': 'Create a Custom Phishing Simulation for Your Team (No-Code)',
                'target_keyword': 'no-code phishing simulation',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Why Phishing Simulations|Tool Selection|Campaign Design|Email Templates|Tracking Setup|Results Analysis|Employee Training|Conclusion',
                'cta': 'Access phishing templates',
                'affiliate_angles': 'Security awareness platforms, email tools'
            },
            {
                'title': 'WordPress Security Hardening: Step-by-Step Automation Guide',
                'target_keyword': 'wordpress security automation',
                'intent': 'how-to',
                'h2_outline': 'Introduction|Common WP Vulnerabilities|Automated Scanning|Plugin Security|Update Automation|Backup Scripts|Monitoring Setup|Incident Response|Conclusion',
                'cta': 'Download WordPress security scripts',
                'affiliate_angles': 'WordPress hosting, security plugins, Namecheap'
            }
        ]
        
        pillar_1 = [{'pillar': 'AI Tools & Automations', **article} for article in ai_automation_articles]
        pillar_2 = [{'pillar': 'Security Awareness', **article} for article in security_awareness_articles]
        pillar_3 = [{'pillar': 'How-To Workflows', **article} for article in howto_workflows_articles]
        
        self.articles = pillar_1 + pillar_2 + pillar_3
        return self.articles
    
    def export_to_csv(self, filepath='../backlog/content_backlog.csv'):
        """Export backlog to CSV file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        fieldnames = ['pillar', 'title', 'target_keyword', 'intent', 'h2_outline', 'cta', 'affiliate_angles']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.articles)
        
        print(f"✅ Exported {len(self.articles)} articles to {filepath}")


if __name__ == '__main__':
    generator = ContentBacklogGenerator()
    generator.generate_backlog()
    generator.export_to_csv()
    print(f"\n📊 Content Backlog Summary:")
    print(f"  - AI Tools & Automations: 10 articles")
    print(f"  - Security Awareness: 9 articles")
    print(f"  - How-To Workflows: 6 articles")
    print(f"  - Total: 25 articles")
