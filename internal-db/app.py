from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "active", "node": "SECURE-VAULT-B"})

@app.route('/api/vault/credentials')
def credentials():
    return jsonify({
        "admin_db": "admin:NexusPass!2025",
        "api_secret": "kjsdhf-shdf-9923-skdjf",
        "recovery_codes": ["NX-123", "NX-456"],
        "flag": "FLAG{VAULT_REACHED_VIA_SSRF_PIVOT}"
    })

@app.route('/')
def index():
    return "Nexus Secure Data Vault (Restricted Access)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
