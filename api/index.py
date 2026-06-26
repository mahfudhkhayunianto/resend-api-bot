from flask import Flask, request, jsonify
import resend
import os

app = Flask(__name__)

# Pastikan API Key sudah benar di Environment Variables
resend.api_key = os.environ.get("RESEND_API_KEY")

@app.route('/api/send', methods=['POST'])
def send_email():
    try:
        data = request.json
        nomor = data.get('nomor')
        subject = data.get('subject', "Question about WhatsApp 'Login not available'")
        body = data.get('body', f"Banding untuk nomor: {nomor}")
        
        params = {
            "from": "noreply@mktools.my.id", # Gunakan domain yang sudah verified
            "to": "android@support.whatsapp.com",
            "subject": subject,
            "html": f"<p>{body}</p>"
        }
        
        resend.Emails.send(params)
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
