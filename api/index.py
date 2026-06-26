from flask import Flask, request, jsonify
import resend
import os

app = Flask(__name__)
resend.api_key = os.environ.get("RESEND_API_KEY")

@app.route('/api/send', methods=['POST'])
def send_email():
    if request.headers.get('x-api-key') != os.environ.get('MY_API_KEY'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.json
    try:
        params = {
            "from": "admin@mktools.my.id",
            "to": ["support@support.whatsapp.com"],
            "subject": f"Question about WhatsApp 'Login not available' : +{data['nomor']}",
            "text": f"Hello WhatsApp, I want to appeal about registering my WhatsApp number, 'Login not available'. Please review this problem, my number is +{data['nomor']}"
        }
        resend.Emails.send(params)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
