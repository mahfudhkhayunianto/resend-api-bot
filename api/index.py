from flask import Flask, request, jsonify
import resend
import requests
import os

app = Flask(__name__)

# Fungsi Pengirim Email dengan Failover (Cadangan Otomatis)
def kirim_email_multi(subject, body):
    # 1. COBA RESEND
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        params = {
            "from": "noreply@mktools.my.id",
            "to": "support@support.whatsapp.com",
            "subject": subject,
            "html": f"<p>{body}</p>"
        }
        resend.Emails.send(params)
        return "Resend"
    except Exception as e:
        print(f"Resend Error: {e}")

    # 2. COBA BREVO (Jika Resend Gagal)
    try:
        brevo_key = os.environ.get("BREVO_API_KEY")
        headers = {"api-key": brevo_key, "Content-Type": "application/json"}
        payload = {
            "sender": {"email": "noreply@fix.mktools.my.id"},
            "to": [{"email": "support@support.whatsapp.com"}],
            "subject": subject,
            "htmlContent": f"<p>{body}</p>"
        }
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        
        # Harus cek status code, karena requests tidak otomatis masuk 'except' kalau error 4xx/5xx
        if response.status_code == 201:
            return "Brevo"
        else:
            print(f"Brevo Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Brevo Exception: {e}")

    # 3. COBA ELASTIC EMAIL (Jika Resend & Brevo Gagal)
    try:
        elastic_key = os.environ.get("ELASTIC_API_KEY")
        params = {
            "apikey": elastic_key,
            "from": "noreply@elastis.mktools.my.id",
            "to": "support@support.whatsapp.com",
            "subject": subject,
            "bodyHtml": f"<p>{body}</p>"
        }
        response = requests.get("https://api.elasticemail.com/v2/email/send", params=params)
        
        if response.status_code == 200:
            return "Elastic"
        else:
            print(f"Elastic Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Elastic Exception: {e}")
        
    return None

@app.route('/api/send', methods=['POST'])
def send_email():
    data = request.json
    nomor = data.get('nomor')
    subject = data.get('subject', "Question about WhatsApp 'Login not available'")
    body = data.get('body', f"Banding untuk nomor: {nomor}")
    
    hasil = kirim_email_multi(subject, body)
    
    if hasil:
        print(f"Berhasil terkirim via: {hasil}")
        return jsonify({"status": "success", "provider": hasil}), 200
    else:
        return jsonify({"status": "error", "message": "Semua provider gagal"}), 500

if __name__ == '__main__':
    app.run()
