from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/billing/health')
def health():
    return jsonify({
        "status": "online",
        "node_id": "BILLING-BRIDGE-01",
        "region": "GLOBAL",
        "uptime": "14d 2h"
    })

@app.route('/api/billing/config')
def config():
    return jsonify({
        "internal_token": "BILL-TOKEN-881-XJ",
        "payout_schedule": "weekly",
        "flag": "FLAG{INTERNAL_SERVICE_ENUM_SUCCESS}"
    })

@app.route('/')
def index():
    return "Nexus Internal Billing Bridge v1.0"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
