from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>RobLoTech Automation Suite</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2563eb; }
            .card { border: 1px solid #e5e7eb; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .card:hover { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            a { color: #2563eb; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .status { color: #10b981; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🚀 RobLoTech Content Automation Suite</h1>
        <p class="status">✅ System Online</p>
        
        <div class="card">
            <h2>📊 Deliverables</h2>
            <ul>
                <li><a href="/audit/summary.md" target="_blank">Site Audit Summary (Markdown)</a></li>
                <li><a href="/audit/site_audit.json" target="_blank">Site Audit (JSON)</a></li>
                <li><a href="/backlog/content_backlog.csv" target="_blank">Content Backlog (25 Articles)</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🎨 Embeddable Widgets</h2>
            <ul>
                <li><a href="/widgets/tools/" target="_blank">AI Tools Directory (30 Tools)</a></li>
                <li><a href="/widgets/playbooks/" target="_blank">Automation Playbooks (10 Recipes)</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>📈 Analytics Dashboard</h2>
            <ul>
                <li><a href="/dashboard/" target="_blank">Metrics Dashboard</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🔧 Workers & Documentation</h2>
            <p>Python automation workers are in <code>/workers/</code>:</p>
            <ul>
                <li><strong>site_auditor.py</strong> - Content audit & SEO gap analysis</li>
                <li><strong>news_summarizer.py</strong> - RSS feed ingestion & AI summarization</li>
                <li><strong>affiliate_enricher.py</strong> - Auto-affiliate link wrapping</li>
                <li><strong>wp_publish.py</strong> - WordPress REST API publisher</li>
                <li><strong>metrics_logger.py</strong> - Performance tracking</li>
            </ul>
            <p><a href="/docs/IMPLEMENTATION.md" target="_blank">View Implementation Guide</a></p>
        </div>
        
        <div class="card">
            <h2>📝 Next Steps</h2>
            <ol>
                <li>Set WordPress credentials in <code>.env</code> (WP_USER, WP_APP_PASSWORD)</li>
                <li>Configure affiliate partner IDs in <code>.env</code></li>
                <li>Review and customize the 25 article ideas in content backlog</li>
                <li>Test WordPress publishing with <code>python workers/wp_publish.py</code></li>
                <li>Embed widgets in WordPress using provided HTML snippets</li>
            </ol>
        </div>
    </body>
    </html>
    """

@app.route('/audit/<path:filename>')
def serve_audit(filename):
    return send_from_directory('audit', filename)

@app.route('/backlog/<path:filename>')
def serve_backlog(filename):
    return send_from_directory('backlog', filename)

@app.route('/widgets/tools/')
def serve_tools_widget():
    return send_from_directory('widgets/tools', 'index.html')

@app.route('/widgets/playbooks/')
def serve_playbooks_widget():
    return send_from_directory('widgets/playbooks', 'index.html')

@app.route('/widgets/<path:path>')
def serve_widgets(path):
    return send_from_directory('widgets', path)

@app.route('/dashboard/')
def serve_dashboard():
    return send_from_directory('dashboard', 'index.html')

@app.route('/docs/<path:filename>')
def serve_docs(filename):
    return send_from_directory('docs', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
