from flask import Flask, request, jsonify
import resend
import os

app = Flask(__name__)

# Konfigurasi API Key Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

@app.route('/api/send', methods=['POST'])
def send_email():
    try:
        data = request.json
        if not data or 'nomor' not in data:
            return jsonify({"error": "No nomor provided"}), 400
        
        nomor = data['nomor']
        
        params = {
            "from": "noreply@mktools.my.id",
            "to": "support@support.whatsapp.com",
            "subject": "Question about WhatsApp 'Login not available'",
            "html": f"<p>Banding untuk nomor: {nomor}</p>"
        }
        
        resend.Emails.send(params)
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
