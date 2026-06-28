from flask import Flask, request, jsonify
import resend
import requests
import os

app = Flask(__name__)

# GANTI DENGAN EMAIL GMAIL ASLI BOSKU
EMAIL_PENERIMA_BALASAN = "mahfudhkhayunianto@gmail.com"

# Fungsi Pengirim Email dengan Failover & Rotasi Domain
def kirim_email_multi(subject, body):
    
    # 1. COBA RESEND (Rotasi 3 Domain)
    # Kita buat list konfigurasi. Jika key kosong (None), loop otomatis melewati itu.
    resend_configs = [
        {"key": os.environ.get("RESEND_API_KEY"), "sender": "noreply@mktools.my.id"},
        {"key": os.environ.get("RESEND_API_KEY_2"), "sender": "noreply@mkproject.mktools.my.id"},
        {"key": os.environ.get("RESEND_API_KEY_3"), "sender": "noreply@mktools.biz.id"}
        {"key": os.environ.get("RESEND_API_KEY_3"), "sender": "noreply@mkpro.biz.id"}
    ]

    for config in resend_configs:
        key = config.get("key")
        sender = config.get("sender")
        
        # Cek apakah key ada dan tidak None/Kosong agar tidak error
        if key:
            try:
                resend.api_key = key
                params = {
                    "from": sender, 
                    "to": "android@support.whatsapp.com",
                    "reply_to": EMAIL_PENERIMA_BALASAN,
                    "subject": subject,
                    "html": f"<p>{body}</p>"
                }
                resend.Emails.send(params)
                print(f"DEBUG: Sukses kirim via {sender}") # Log ini akan muncul di Vercel
                return f"Resend ({sender})"
            except Exception as e:
                print(f"Resend Error via {sender}: {e}")
                # Jika error (misal limit), loop lanjut ke config berikutnya
        else:
            print(f"DEBUG: Key untuk {sender} tidak ditemukan di Vercel, skip...")

    # 2. COBA BREVO
    brevo_key = os.environ.get("BREVO_API_KEY")
    if brevo_key:
        try:
            headers = {"api-key": brevo_key, "Content-Type": "application/json"}
            payload = {
                "sender": {"email": "noreply@fix.mktools.my.id"},
                "to": [{"email": "android@support.whatsapp.com"}],
                "replyTo": {"email": EMAIL_PENERIMA_BALASAN},
                "subject": subject,
                "htmlContent": f"<p>{body}</p>"
            }
            response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            if response.status_code == 201:
                return "Brevo"
        except Exception as e:
            print(f"Brevo Exception: {e}")

    # 3. COBA ELASTIC EMAIL
    elastic_key = os.environ.get("ELASTIC_API_KEY")
    if elastic_key:
        try:
            params = {
                "apikey": elastic_key,
                "from": "noreply@elastis.mktools.my.id",
                "to": "android@support.whatsapp.com",
                "replyTo": EMAIL_PENERIMA_BALASAN,
                "subject": subject,
                "bodyHtml": f"<p>{body}</p>"
            }
            response = requests.get("https://api.elasticemail.com/v2/email/send", params=params)
            if response.status_code == 200:
                return "Elastic"
        except Exception as e:
            print(f"Elastic Exception: {e}")
        
    return None

@app.route('/api/send', methods=['POST'])
def send_email():
    data = request.json
    nomor = data.get('nomor', 'UNKNOWN')
    subject = data.get('subject', "Question about WhatsApp 'Login not available'")
    body = data.get('body', f"Banding untuk nomor: {nomor}")
    
    hasil = kirim_email_multi(subject, body)
    
    if hasil:
        print(f"[{nomor}] Berhasil Terkirim -> {hasil}")
        return jsonify({"status": "success", "provider": hasil}), 200
    else:
        print(f"[{nomor}] GAGAL Terkirim -> Semua provider error/limit")
        return jsonify({"status": "error", "message": "Semua provider gagal"}), 500

# Vercel butuh app instance di top-level
if __name__ == '__main__':
    app.run()
