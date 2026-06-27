from flask import Flask, request, jsonify
import resend
import requests
import os

app = Flask(__name__)

# GANTI DENGAN EMAIL GMAIL ASLI BOSKU UNTUK MENERIMA BALASAN WHATSAPP
EMAIL_PENERIMA_BALASAN = "mahfudhkhayunianto@gmail.com" 

# ==========================================
# FUNGSI 1: Mengambil daftar akun Brevo dari Vercel
# ==========================================
def get_brevo_accounts():
    raw_config = os.environ.get("BREVO_ACCOUNTS", "")
    accounts = []
    if raw_config:
        for item in raw_config.split(','):
            if '|' in item:
                key, sender = item.split('|')
                accounts.append({"key": key.strip(), "sender": sender.strip()})
    return accounts

# ==========================================
# FUNGSI 2: Pengirim Email dengan Super Failover 
# ==========================================
def kirim_email_multi(subject, body):
    # ------------------------------------------
    # 1. COBA RESEND (Multi-Key dengan Domain Mapping)
    # ------------------------------------------
    # Menghubungkan kunci dengan email pengirim yang benar agar tidak ditolak Resend
    resend_configs = [
        {"key": os.environ.get("RESEND_API_KEY"), "sender": "noreply@mktools.my.id"},
        {"key": os.environ.get("RESEND_API_KEY_2"), "sender": "noreply@mkproject.mktools.my.id"}
        {"key": os.environ.get("RESEND_API_KEY_3"), "sender": "noreply@mktools.biz.id"}
    ]

    for config in resend_configs:
        key = config["key"]
        sender = config["sender"]
        
        # Hanya jalankan jika kunci API ada
        if key:
            try:
                resend.api_key = key
                params = {
                    "from": sender, 
                    "to": "support@support.whatsapp.com",
                    "reply_to": EMAIL_PENERIMA_BALASAN,
                    "subject": subject,
                    "html": f"<p>{body}</p>"
                }
                resend.Emails.send(params)
                return "Resend" # Jika berhasil, kirim sukses dan berhenti di sini
            except Exception as e:
                print(f"Resend Error (Domain {sender}): {e}")
                continue # Jika gagal, coba kunci berikutnya

    # ------------------------------------------
    # 2. COBA BREVO (Rotasi Multi-Akun)
    # ------------------------------------------
    brevo_accounts = get_brevo_accounts()
    for acc in brevo_accounts:
        try:
            headers = {"api-key": acc['key'], "Content-Type": "application/json"}
            payload = {
                "sender": {"email": acc['sender']},
                "to": [{"email": "support@support.whatsapp.com"}],
                "replyTo": {"email": EMAIL_PENERIMA_BALASAN},
                "subject": subject,
                "htmlContent": f"<p>{body}</p>"
            }
            response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            
            if response.status_code == 201:
                return f"Brevo ({acc['sender'].split('@')[0]})" 
            else:
                print(f"Brevo Failed via {acc['sender']}: {response.status_code} - {response.text}")
                continue 
        except Exception as e:
            print(f"Brevo Exception via {acc['sender']}: {e}")
            continue 

    # ------------------------------------------
    # 3. COBA ELASTIC EMAIL 
    # ------------------------------------------
    try:
        elastic_key = os.environ.get("ELASTIC_API_KEY")
        if elastic_key:
            params = {
                "apikey": elastic_key,
                "from": "noreply@elastis.mktools.my.id",
                "to": "support@support.whatsapp.com",
                "replyTo": EMAIL_PENERIMA_BALASAN,
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

# ==========================================
# ROUTE: Endpoint API
# ==========================================
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

if __name__ == '__main__':
    app.run()
