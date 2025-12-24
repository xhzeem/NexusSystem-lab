from flask import Flask, session, request, redirect, url_for, jsonify, render_template_string

app = Flask(__name__)
app.secret_key = 'backup-control-emergency-key'

# Weak emergency password
BACKUP_CODE = "password"

@app.route('/')
def index():
    if not session.get('authorized'):
        return '''
            <div style="font-family: sans-serif; background: #000; color: #0f0; padding: 2rem; height: 100vh;">
                <h1>[!] Nexus Backup Control Node</h1>
                <p>EMERGENCY OVERRIDE ONLY. Credentials Required.</p>
                <form action="/auth" method="post">
                    Override Code: <input type="password" name="code" style="background: #000; color: #0f0; border: 1px solid #0f0;">
                    <input type="submit" value="Authorize" style="background: #0f0; color: #000; border: none; cursor: pointer;">
                </form>
            </div>
        '''
    return '''
        <div style="font-family: sans-serif; background: #000; color: #0f0; padding: 2rem; height: 100vh;">
            <h1>[✓] AUTHORIZED ACCESS: Backup Control</h1>
            <p>Node Status: Standby</p>
            <p>Emergency Flag: <code>FLAG{INTERNAL_ADMIN_TAKEOVER}</code></p>
            <hr>
            <h3>Backup Operations</h3>
            <form action="/backup" method="get">
                <p>System Status Report:</p>
                <input type="text" name="node" placeholder="Enter node name" style="background: #000; color: #0f0; border: 1px solid #0f0;">
                <input type="submit" value="Generate Report" style="background: #0f0; color: #000; border: none; cursor: pointer;">
            </form>
            <hr>
            <a href="/logout" style="color: #f00;">Terminate Session</a>
        </div>
    '''

@app.route('/auth', methods=['POST'])
def auth():
    code = request.form.get('code')
    if code == BACKUP_CODE:
        session['authorized'] = True
        return redirect(url_for('index'))
    return "ACCESS DENIED. EVENT LOGGED.", 403

@app.route('/backup')
def backup():
    if not session.get('authorized'):
        return redirect(url_for('index'))
    
    node = request.args.get('node', 'default')
    
    # SSTI Vulnerability: Direct template rendering of user input
    template = f'''
        <div style="font-family: sans-serif; background: #000; color: #0f0; padding: 2rem;">
            <h1>Backup Report: {node}</h1>
            <p>Node Status: {{% if node == "admin" %}}CRITICAL{{% else %}}NORMAL{{% endif %}}</p>
            <p>Last Backup: {{% if "backup" in node.lower() %}}COMPLETED{{% else %}}PENDING{{% endif %}}</p>
            <p>System Health: {{node|upper}}_STATUS</p>
            <hr>
            <a href="/" style="color: #0f0;">← Back to Control Panel</a>
        </div>
    '''
    
    return render_template_string(template, node=node)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
