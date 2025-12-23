import sqlite3
import requests
import os
import json
from flask import Flask, request, render_template_string, redirect, url_for, session, render_template, jsonify

app = Flask(__name__)
app.secret_key = 'nexus-portal-secure-2025-v3'

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('DROP TABLE IF EXISTS posts')
    c.execute('DROP TABLE IF EXISTS diagnostic_nodes')
    
    # User Table
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, signature TEXT)')
    c.execute("INSERT INTO users (username, password, role, signature) VALUES ('admin', 'admin123', 'Executive', 'Corporate Communications Team')")
    c.execute("INSERT INTO users (username, password, role, signature) VALUES ('staff', 'staff123', 'Employee', 'Regional Support Office')")
    
    # Posts/News Table
    c.execute('CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, content TEXT, author TEXT, image_url TEXT, date TEXT)')
    posts = [
        ('Expansion Plans Q1 2026', 'Nexus Systems is proud to announce a 20% growth in internal service infrastructure...', 'admin', '/static/images/growth.jpg', '2025-12-23'),
        ('New Marketing Suite Online', 'The Marketing team has successfully migrated to the new internal PHP-based suite at 172.20.0.50.', 'admin', '/static/images/tech.jpg', '2025-12-22'),
    ]
    c.executemany('INSERT INTO posts (title, content, author, image_url, date) VALUES (?, ?, ?, ?, ?)', posts)

    # Diagnostic Nodes Table (For Command Injection)
    c.execute('CREATE TABLE diagnostic_nodes (id INTEGER PRIMARY KEY, node_name TEXT, ip_address TEXT, status TEXT)')
    nodes = [
        ('Edge-Gateway-01', '127.0.0.1', 'Operational'),
        ('Finance-Bridge', '172.20.0.20', 'Stable'),
        ('Asset-Vault', '172.20.0.30', 'Encrypted'),
        ('Creative-Hub', '172.20.0.50', 'Operational'),
    ]
    c.executemany('INSERT INTO diagnostic_nodes (node_name, ip_address, status) VALUES (?, ?, ?)', nodes)
    
    conn.commit()
    conn.close()

if not os.path.exists('portal.db'):
    init_db()

# --- ROUTES ---

@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        conn = sqlite3.connect('portal.db')
        c = conn.cursor()
        # Vulnerable SQLi (still present but less obvious)
        user = c.execute(f"SELECT * FROM users WHERE username = '{u}' AND password = '{p}'").fetchone()
        conn.close()
        if user:
            session['user'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('dashboard'))
        error = "Login failed. Invalid credentials."
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('user'): return redirect(url_for('login'))
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    news = c.execute("SELECT * FROM posts ORDER BY date DESC").fetchall()
    # Fetch user signature
    user_data = c.execute("SELECT signature FROM users WHERE username = ?", (session['user'],)).fetchone()
    conn.close()
    
    # VULN: SSTI in the signature rendering within the dashboard
    signature = user_data[0] if user_data else ""
    try:
        # We render the signature dynamically as if it supports placeholders like {{ user }}
        rendered_sig = render_template_string(signature, user=session['user'])
    except Exception:
        rendered_sig = signature

    return render_template('dashboard.html', posts=news, signature=rendered_sig, user=session['user'])

# --- VULN: INDIRECT OS COMMAND INJECTION ---
@app.route('/diagnostics', methods=['GET', 'POST'])
def diagnostics():
    if not session.get('user'): return redirect(url_for('login'))
    
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    nodes = c.execute("SELECT * FROM diagnostic_nodes").fetchall()
    conn.close()
    
    result = None
    if request.method == 'POST':
        action = request.form.get('action')
        node_id = request.form.get('node_id')
        
        if action == 'ping' and node_id:
            conn = sqlite3.connect('portal.db')
            c = conn.cursor()
            node = c.execute("SELECT ip_address FROM diagnostic_nodes WHERE id = ?", (node_id,)).fetchone()
            conn.close()
            
            if node:
                target_ip = node[0]
                # VULNERABLE: We allow an 'ip_override' which is hidden from the UI but can be added by a savvy user
                ip_override = request.form.get('ip_override')
                final_target = ip_override if ip_override else target_ip
                
                cmd = f"ping -c 1 {final_target}"
                import subprocess
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                except Exception as e:
                    result = str(e)

    return render_template('diagnostics.html', nodes=nodes, result=result, user=session['user'])

# --- VULN: SSRF (Internal Image/Resource Proxy) ---
@app.route('/proxy')
def proxy():
    if not session.get('user'): return redirect(url_for('login'))
    url = request.args.get('url')
    if not url: return "URL Required", 400
    try:
        # VULNERABLE: Fetches ANY internal URL based on user input
        resp = requests.get(url, timeout=3)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return f"Fetch Error: {str(e)}", 500

# --- VULN: LFI (Document Download) ---
@app.route('/download')
def download():
    if not session.get('user'): return redirect(url_for('login'))
    doc = request.args.get('doc')
    if not doc: return redirect(url_for('dashboard'))
    try:
        # VULNERABLE: Path traversal via 'doc' parameter
        base_path = os.path.join(app.root_path, 'static', 'docs')
        file_path = os.path.join(base_path, doc)
        with open(file_path, 'r') as f:
            content = f.read()
        return (content, 200, {'Content-Type': 'application/octet-stream', 'Content-Disposition': f'attachment; filename={doc}'})
    except Exception as e:
        return f"Access Denied: Resource locked or missing. {str(e)}", 403

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if not session.get('user'): return redirect(url_for('login'))
    
    # Mock inventory data
    assets = [
        (1, 'Edge-Gateway-01', 'Router', '127.0.0.1', 'Online', '2025-12-23 06:30:00'),
        (2, 'Finance-Bridge', 'Database Server', '172.20.0.20', 'Online', '2025-12-23 06:35:00'),
        (3, 'Asset-Vault', 'Storage Array', '172.20.0.30', 'Online', '2025-12-23 06:40:00'),
        (4, 'Creative-Hub', 'Web Server', '172.20.0.50', 'Maintenance', '2025-12-23 06:25:00'),
    ]
    
    ping_result = None
    if request.method == 'POST' and 'ping_target' in request.form:
        target = request.form.get('ping_target')
        if target:
            # VULNERABLE: Direct command injection in ping
            import subprocess
            try:
                cmd = f"ping -c 3 {target}"
                ping_result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            except Exception as e:
                ping_result = str(e)
    
    search = request.args.get('q', '')
    if search:
        assets = [asset for asset in assets if search.lower() in asset[1].lower() or search in asset[3]]
    
    return render_template('inventory.html', assets=assets, search=search, ping_result=ping_result, user=session['user'])

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    if not session.get('user'): return redirect(url_for('login'))
    
    signature = 'Corporate Communications Team'
    preview = '<div style="padding: 1rem; border: 1px solid var(--border-color); border-radius: 6px;"><p style="font-size: 0.8rem; color: var(--text-secondary);">Report generated by Nexus Systems</p></div>'
    
    if request.method == 'POST':
        signature = request.form.get('signature', signature)
        try:
            preview = render_template_string(signature, user=session['user'])
        except Exception:
            preview = signature
    
    return render_template('reports.html', signature=signature, preview=preview, user=session['user'])

@app.route('/network', methods=['GET', 'POST'])
def network():
    if not session.get('user'): return redirect(url_for('login'))
    
    status = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                resp = requests.get(url, timeout=3)
                status = f"Status: {resp.status_code}\nResponse: {resp.text[:200]}..."
            except Exception as e:
                status = f"Connection failed: {str(e)}"
    
    return render_template('network.html', status=status, user=session['user'])

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    if not session.get('user'): return redirect(url_for('login'))
    
    logs = ['access.log', 'error.log', 'system.log', 'security.log']
    current_log = request.args.get('log', '')
    content = None
    error = None
    
    if current_log:
        try:
            # VULNERABLE: Allow path traversal via log parameter
            with open(current_log, 'r') as f:
                content = f.read()
        except Exception as e:
            error = f"Unable to read log file: {str(e)}"
    
    return render_template('maintenance.html', logs=logs, current_log=current_log, content=content, error=error, user=session['user'])

if __name__ == '__main__':
    # Setup directories
    for d in ['static/images', 'static/docs']:
        if not os.path.exists(d): os.makedirs(d)
    
    # Create fake assets
    with open('static/docs/policy_v1.txt', 'w') as f: f.write("Corporate Policy: All internal access is logged.")
    
    # Create mock log files for LFI demonstration
    log_files = {
        'access.log': '2025-12-23 06:30:00 INFO: User admin logged in from 192.168.1.100\n2025-12-23 06:35:00 INFO: User staff accessed dashboard\n2025-12-23 06:40:00 WARNING: Failed login attempt from unknown IP\n2025-12-23 06:45:00 INFO: System backup completed',
        'error.log': '2025-12-23 06:30:15 ERROR: Database connection timeout\n2025-12-23 06:35:22 ERROR: Invalid API key detected\n2025-12-23 06:40:11 ERROR: File not found: /etc/shadow\n2025-12-23 06:45:03 ERROR: Permission denied on /root directory',
        'system.log': '2025-12-23 06:30:00 INFO: System startup completed\n2025-12-23 06:35:00 INFO: All services online\n2025-12-23 06:40:00 WARNING: High CPU usage detected\n2025-12-23 06:45:00 INFO: Maintenance cycle completed',
        'security.log': '2025-12-23 06:30:00 SECURITY: Authentication successful\n2025-12-23 06:35:00 SECURITY: Access granted to admin panel\n2025-12-23 06:40:00 SECURITY: Suspicious activity detected from 10.0.0.1\n2025-12-23 06:45:00 SECURITY: Firewall rule updated'
    }
    
    for filename, content in log_files.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    app.run(host='0.0.0.0', port=5000)
