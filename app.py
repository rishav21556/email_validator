import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash
from groq import Groq


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")  # Use a secure key

# SMTP Configuration (use environment variables)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "rishav21556@iiitd.ac.in")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "zmpg fdbn snvt fqmo")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "rishav21556@iiitd.ac.in")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ API Key! Set GROQ_API_KEY in environment variables.")

client = Groq(api_key=GROQ_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        recipient = request.form.get("recipient")
        subject = request.form.get("subject", "No Subject")
        prompt = request.form.get("prompt")

        if not recipient or not prompt:
            flash("Please provide both recipient email and prompt.", "error")
            return redirect(url_for("index"))

        # Generate email content using Groq API
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            generated_email = response.choices[0].message.content
        except Exception as e:
            flash(f"Error generating email: {e}", "error")
            return redirect(url_for("index"))

        return render_template("edit_email.html", recipient=recipient, subject=subject, email_content=generated_email)

    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send_email():
    recipient = request.form.get("recipient")
    subject = request.form.get("subject", "No Subject")
    email_content = request.form.get("email_content")

    if not recipient or not email_content:
        flash("Recipient and email content are required.", "error")
        return redirect(url_for("index"))

    # Create the MIME email message
    msg = MIMEText(email_content, "html")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = recipient

    # Send the email using SMTP
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, recipient, msg.as_string())
        flash("Email sent successfully!", "success")
    except Exception as e:
        flash(f"Failed to send email: {e}", "error")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
