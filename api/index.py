from flask import Flask, request, jsonify
import resend
import requests
import os

app = Flask(__name__)

# GANTI DENGAN EMAIL GMAIL ASLI BOSKU UNTUK TERIMA BALASAN
EMAIL_PENERIMA_BALASAN = "mahfudhkhayunianto@gmail.com"
# Email Default jika Bosku tidak menuliskan sender di Vercel
EMAIL_DEFAULT = "noreply@mktools.my.id"

# FUNGSI AUTO-DETECT KONFIGURASI DARI VERCEL
def get_resend_configs():
    configs = []
    # Loop semua variabel yang diawali RESEND_CONFIG_
    for env_key, env_val in os.environ.items():
        if env_key.startswith("RESEND_CONFIG_"):
            # Jika ada tanda |, formatnya: API_KEY|sender
            if '|' in env_val:
                parts = env_val.split('|')
                configs.append({"key": parts[0].strip(), "sender": parts[1].strip()})
            else:
                # Jika hanya API_KEY, pakai sender default
                configs.append({"key": env_val.strip(), "sender": EMAIL_DEFAULT})
    return configs

def kirim_email_multi(subject, body):
    # 1. COBA RESEND (Otomatis dari Vercel Config)
    resend_configs = get_resend_configs()
    
    for config in resend_configs:
        key = config.get("key")
        sender = config.get("sender")
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
                return f"Resend ({sender})"
            except Exception as e:
                print(f"Resend Error via {sender}: {e}")
                continue
    
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
        # Tampilan bersih tanpa detail dalam kurung
        tampilan = hasil.split(' (')[0]
        print(f"[{nomor}] Berhasil Terkirim -> {tampilan}")
        return jsonify({"status": "success", "provider": tampilan}), 200
    else:
        print(f"[{nomor}] GAGAL Terkirim -> Semua provider error/limit")
        return jsonify({"status": "error", "message": "Semua provider gagal"}), 500

if __name__ == '__main__':
    app.run()
