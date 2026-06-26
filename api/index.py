def kirim_email_multi(subject, body):
    # 1. COBA RESEND (Gunakan domain utama mktools.my.id)
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        params = {
            "from": "noreply@mktools.my.id",  # <--- FIX: Domain Utama
            "to": "android@support.whatsapp.com",
            "subject": subject,
            "html": f"<p>{body}</p>"
        }
        resend.Emails.send(params)
        return "Resend"
    except Exception as e:
        print(f"Resend Gagal: {e}") # Tambahkan ini biar kalau gagal kelihatan di log
        pass

    # 2. COBA BREVO (Gunakan domain fix.mktools.my.id)
    try:
        brevo_key = os.environ.get("BREVO_API_KEY")
        headers = {"api-key": brevo_key, "Content-Type": "application/json"}
        payload = {
            "sender": {"email": "noreply@fix.mktools.my.id"}, # <--- SUDAH BENAR
            "to": [{"email": "android@support.whatsapp.com"}],
            "subject": subject,
            "htmlContent": f"<p>{body}</p>"
        }
        requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        return "Brevo"
    except Exception as e:
        print(f"Brevo Gagal: {e}")
        pass

    # 3. COBA ELASTIC EMAIL (Gunakan domain elastis.mktools.my.id)
    try:
        elastic_key = os.environ.get("ELASTIC_API_KEY")
        params = {
            "apikey": elastic_key,
            "from": "noreply@elastis.mktools.my.id", # <--- SUDAH BENAR
            "to": "android@support.whatsapp.com",
            "subject": subject,
            "bodyHtml": f"<p>{body}</p>"
        }
        requests.get("https://api.elasticemail.com/v2/email/send", params=params)
        return "Elastic"
    except Exception as e:
        print(f"Elastic Gagal: {e}")
        return None
