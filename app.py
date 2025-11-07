# app.py
from flask import Flask, render_template, request, redirect, url_for
import os, requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

print("🚀 Flask app initialized successfully")


# ---------- App Config ----------
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp-relay.brevo.com")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

# ---------- Brevo API Setup ----------
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER = app.config['MAIL_DEFAULT_SENDER']
BREVO_RECEIVER = os.getenv("MAIL_RECEIVER", BREVO_SENDER)

BREVO_SEND_ENDPOINT = "https://api.brevo.com/v3/smtp/email"
REQUEST_TIMEOUT = 5  # seconds

# ---------- Helper: Send Brevo Email ----------
def send_brevo_email(subject, html_content, text_content, to_emails):
    if not BREVO_API_KEY:
        app.logger.error("❌ Missing BREVO_API_KEY in environment.")
        return False, "Missing API key"

    to_list = [{"email": email} for email in to_emails]
    payload = {
        "sender": {"name": "Glowhite Orders", "email": BREVO_SENDER},
        "to": to_list,
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        resp = requests.post(BREVO_SEND_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code in (200, 201, 202):
            app.logger.info(f"✅ Email sent successfully: {subject}")
            return True, resp.text
        else:
            app.logger.error(f"❌ Brevo API error {resp.status_code}: {resp.text}")
            return False, resp.text
    except requests.exceptions.RequestException as e:
        app.logger.error(f"❌ Request failed: {e}")
        return False, str(e)


# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    address = request.form.get('address')

    app.logger.info(f"📦 New Order:\nName: {name}\nPhone: {phone}\nEmail: {email}\nAddress: {address}")

    # --- Admin Email ---
    admin_subject = f"🛍️ New Order from {name}"
    admin_text = f"New order from {name}\nPhone: {phone}\nEmail: {email}\nAddress: {address}"
    admin_html = f"""
    <h2>New Order Received</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Phone:</strong> {phone}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Address:</strong> {address}</p>
    <p>Check WhatsApp for quick response.</p>
    """
    send_brevo_email(admin_subject, admin_html, admin_text, [BREVO_RECEIVER])

    # --- Customer Email ---
    if email:
        customer_subject = "🎉 Your Glowhite Order Has Been Received!"
        customer_text = f"Hi {name}, thank you for your order! We'll contact you shortly."
        customer_html = f"""
        <div style="font-family:Arial;background:#f4f6f8;padding:20px;">
          <div style="background:#fff;padding:25px;border-radius:10px;max-width:600px;margin:auto;">
            <h2 style="color:#f4b400;">🎉 Order Received!</h2>
            <p>Hi <b>{name}</b>,</p>
            <p>Thank you for shopping with <b>Glowhite</b>! We’ll contact you soon.</p>
            <p><b>Address:</b> {address}<br><b>Phone:</b> {phone}</p>
            <a href="https://wa.me/2349160824849"
               style="background:#1daa52;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;">
               💬 Chat on WhatsApp
            </a>
            <p style="margin-top:20px;">Best regards,<br>Glowhite Team</p>
          </div>
        </div>
        """
        send_brevo_email(customer_subject, customer_html, customer_text, [email])
    else:
        app.logger.warning("No customer email provided; skipping customer email.")

    return redirect(url_for('thankyou', name=name))


@app.route('/thank-you')
def thankyou():
    name = request.args.get('name', 'Customer')
    return render_template('thankyou.html', name=name)


@app.route('/test-email')
def test_email():
    """Quick test to verify Brevo email configuration."""
    test_subject = "✅ Test Email from Over"
    test_html = "<h2>It works!</h2><p>Your Brevo API setup is working correctly.</p>"
    test_text = "Your Brevo API setup is working correctly."
    ok, info = send_brevo_email(test_subject, test_html, test_text, [BREVO_RECEIVER])
    return f"✅ Success: {info}" if ok else f"❌ Failed: {info}", (200 if ok else 500)


# ---------- Run ----------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"✅ Flask app running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ != '__main__':
    print("✅ Gunicorn worker successfully started for Glowhite!")
