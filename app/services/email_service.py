import os
import smtplib
from email.message import EmailMessage

def send_resume_with_zoho(to_email, resume_path):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    # Debug print
    print("SMTP_SERVER:", smtp_server)
    print("SMTP_PORT:", smtp_port)
    print("SMTP_USER:", smtp_user)
    print("SMTP_PASS:", smtp_pass)
    print("EMAIL_FROM:", from_email)

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = "Stanley Owarieta's Resume"
    msg['From'] = from_email
    msg['To'] = to_email

    # Plain text fallback
    msg.set_content("""\
Hello,

Thank you for your interest in my resume.

I’ve attached a copy for your review. I’m currently open to new opportunities and would love to connect about any roles or collaborations you have in mind.

Looking forward to hearing from you!

Best regards,  
Stanley Owarieta
""")

    # HTML version (no heading, reduced margin/padding)
    msg.add_alternative(f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 480px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.2em 1.2em 1.5em 1.2em;'>
          <p style='font-size: 1.1em; margin-bottom: 1.5em;'>
            Thank you for your interest in my resume.<br><br>
            I’ve attached a copy for your review. I’m currently open to new opportunities and would love to connect about any roles or collaborations you have in mind.
          </p>
          <p style='margin-bottom: 2em;'>Looking forward to hearing from you!</p>
          <div style='font-weight: 500; color: #23272f;'>
            Best regards,<br>
            <span style='color: #667eea; font-weight: 700;'>Stanley Owarieta</span>
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    # Attach the resume PDF
    with open(resume_path, "rb") as f:
        file_data = f.read()
        file_name = "Stanley_Owarieta_Resume.pdf"
    msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    # Send the email via Zoho SMTP
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg) 