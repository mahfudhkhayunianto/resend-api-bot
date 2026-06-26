from flask import Flask, request, jsonify
import resend
import os

app = Flask(__name__)

# Mengambil API Key dari Environment Variables
resend.api_key = os.environ.get("RESEND_API_KEY")

@app.route('/api/send', methods=['POST'])
def send_email():
    try:
        data = request.json
        nomor = data.get('nomor')
        
        # Ubah bagian 'from' menjadi email yang menggunakan domain Anda
params = {
    "from": "noreply@mktools.my.id", # Sesuaikan dengan domain yang sudah verified
    "to": "support@support.whatsapp.com",
    "subject": "Question about WhatsApp 'Login not available'",
    "html": f"<p>Banding untuk nomor: {nomor}</p>"
}
        resend.Emails.send(params)
        
        return jsonify({"status": "success"}), 200
    xcept Exception as e:
        # Kita kembalikan error aslinya agar Anda tahu kenapa gagal
        return jsonify({"error": str(e)}), 500

# Wajib ada agar Vercel bisa menjalankan Flask
if __name__ == '__main__':
    app.run()
