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


def send_contact_message_with_zoho(name, email, message, subject=None):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    owner_email = from_email  # Send to yourself

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    email_subject = f"Contact: {subject}" if subject else f"New Contact Message from {name}"
    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = from_email
    msg['To'] = owner_email
    # Plain text
    msg.set_content(f"""
Subject: {subject or '(No Subject)'}

Name: {name}
Email: {email}

Message:
{message}

Best regards,
Stanley Owarieta Portfolio
""")
    # HTML version
    msg.add_alternative(f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>New Contact Message</h2>
        <p style='margin:0 0 16px 0;color:#222;font-size:1.1em;'>
          <b>Subject:</b> {subject or '(No Subject)'}<br/>
          <b>Name:</b> {name}<br/>
          <b>Email:</b> {email}
        </p>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin-bottom:24px;'>
          <b style='color:#2563eb;'>Message:</b><br/>
          <span style='color:#222;'>{message}</span>
        </div>
        <p style='margin-top:2em;font-size:1em;color:#444;'>
          Best regards,<br/>
          <span style='color:#2563eb;font-weight:bold;'>Stanley Owarieta Portfolio</span>
        </p>
      </div>
    </body></html>
    """, subtype='html')
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)


def send_booking_confirmation_with_zoho(client_name, client_email, call_datetime, provider, call_link, owner_email=None):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    if not owner_email:
        owner_email = from_email

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    subject = f"Call Booking Confirmation for {client_name}"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>Your Call is Booked!</h2>
        <p style='font-size:1.1em;color:#222;'>Hi {client_name},<br/>
          Thank you for booking a call. Here are your details:</p>
        <ul style='color:#222;font-size:1.05em;'>
          <li><b>Date & Time:</b> {call_datetime}</li>
          <li><b>Provider:</b> {provider}</li>
          <li><b>Google Meet Link:</b> <a href='{call_link}' style='color:#2563eb;text-decoration:underline;'>{call_link}</a></li>
        </ul>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:24px 0;'>
          <b style='color:#2563eb;'>What to expect:</b><br/>
          <span style='color:#222;'>You will receive a reminder before the call. Please join the meeting a few minutes early. If you have any questions, feel free to reply to this email.</span>
        </div>
        <p style='margin-top:2em;font-size:1em;color:#444;'>
          Looking forward to speaking with you!<br/>
          <span style='color:#2563eb;font-weight:bold;'>Stanley Owarieta Portfolio</span>
        </p>
      </div>
    </body></html>
    """
    # Send to client
    msg_client = EmailMessage()
    msg_client['Subject'] = subject
    msg_client['From'] = from_email
    msg_client['To'] = client_email
    msg_client.set_content(f"Your call is booked for {call_datetime} via {provider}. Call Link: {call_link}")
    msg_client.add_alternative(html_content, subtype='html')
    # Send to owner
    msg_owner = EmailMessage()
    msg_owner['Subject'] = subject
    msg_owner['From'] = from_email
    msg_owner['To'] = owner_email
    msg_owner.set_content(f"Call with {client_name} booked for {call_datetime} via {provider}. Call Link: {call_link}")
    msg_owner.add_alternative(html_content, subtype='html')
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg_client)
        smtp.send_message(msg_owner) 