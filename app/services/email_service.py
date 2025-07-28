import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

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
    print(f"[EMAIL DEBUG] ===== STARTING SMTP CONNECTION =====")
    print(f"[EMAIL DEBUG] Connecting to {smtp_server}:{smtp_port}...")
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            print(f"[EMAIL DEBUG] ✅ SMTP SSL connection established")
            
            print(f"[EMAIL DEBUG] Attempting login with user: {smtp_user}")
            smtp.login(smtp_user, smtp_pass)
            print(f"[EMAIL DEBUG] ✅ Login successful")
            
            print(f"[EMAIL DEBUG] Sending message to: {to_email}")
            result = smtp.send_message(msg)
            print(f"[EMAIL DEBUG] ✅ Message sent successfully!")
            print(f"[EMAIL DEBUG] SMTP Response: {result}")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL DEBUG] ❌ SMTP Authentication Error: {e}")
        raise
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[EMAIL DEBUG] ❌ SMTP Recipients Refused: {e}")
        raise
    except smtplib.SMTPSenderRefused as e:
        print(f"[EMAIL DEBUG] ❌ SMTP Sender Refused: {e}")
        raise
    except smtplib.SMTPDataError as e:
        print(f"[EMAIL DEBUG] ❌ SMTP Data Error: {e}")
        raise
    except smtplib.SMTPConnectError as e:
        print(f"[EMAIL DEBUG] ❌ SMTP Connect Error: {e}")
        raise
    except smtplib.SMTPHeloError as e:
        print(f"[EMAIL DEBUG] ❌ SMTP Helo Error: {e}")
        raise
    except Exception as e:
        print(f"[EMAIL DEBUG] ❌ Unexpected SMTP Error: {e}")
        print(f"[EMAIL DEBUG] Error type: {type(e)}")
        raise
    
    print(f"[EMAIL DEBUG] ===== EMAIL SENDING COMPLETE =====") 


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


def send_booking_confirmation_with_zoho(client_name, client_email, call_datetime, provider, call_link, owner_email=None, client_message=None):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    if not owner_email:
        owner_email = from_email

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    # --- Client Email ---
    client_subject = "Your Call is Booked! [Google Meet Link Inside]"
    client_html = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>Your Call is Booked!</h2>
        <p style='font-size:1.1em;color:#222;'>Hi {client_name},<br/>
          Thank you for booking a call! Here are your meeting details:</p>
        <ul style='color:#222;font-size:1.05em;'>
          <li><b>Date & Time:</b> {call_datetime}</li>
          <li><b>Google Meet Link:</b> <a href='{call_link}' style='color:#2563eb;text-decoration:underline;'>{call_link}</a></li>
        </ul>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:24px 0;'>
          <b style='color:#2563eb;'>Please save this link to your notepad or calendar. You’ll use it to join the call.</b>
        </div>
        <p style='margin-top:2em;font-size:1em;color:#444;'>
          Looking forward to speaking with you!<br/>
          <span style='color:#2563eb;font-weight:bold;'>Stanley Owarieta</span>
        </p>
      </div>
    </body></html>
    """
    msg_client = EmailMessage()
    msg_client['Subject'] = client_subject
    msg_client['From'] = from_email
    msg_client['To'] = client_email
    msg_client.set_content(f"Your call is booked for {call_datetime}. Google Meet Link: {call_link}")
    msg_client.add_alternative(client_html, subtype='html')

    # --- Owner Email ---
    owner_subject = f"New Lead: Call Booked by {client_name}"
    owner_html = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>New Lead: Call Booked</h2>
        <ul style='color:#222;font-size:1.05em;'>
          <li><b>Name:</b> {client_name}</li>
          <li><b>Email:</b> {client_email}</li>
          <li><b>Date & Time:</b> {call_datetime}</li>
          <li><b>Google Meet Link:</b> <a href='{call_link}' style='color:#2563eb;text-decoration:underline;'>{call_link}</a></li>
          <li><b>Message:</b> {client_message or '(none)'}</li>
        </ul>
      </div>
    </body></html>
    """
    msg_owner = EmailMessage()
    msg_owner['Subject'] = owner_subject
    msg_owner['From'] = from_email
    msg_owner['To'] = owner_email
    msg_owner.set_content(
        f"New lead booked a call.\nName: {client_name}\nEmail: {client_email}\nDate & Time: {call_datetime}\nGoogle Meet Link: {call_link}\nMessage: {client_message or '(none)'}"
    )
    msg_owner.add_alternative(owner_html, subtype='html')

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg_client)
        smtp.send_message(msg_owner)


def send_password_reset_email_with_zoho(to_email, reset_token, reset_url):
    """
    Send password reset email to admin
    """
    print(f"[EMAIL DEBUG] ===== STARTING PASSWORD RESET EMAIL =====")
    print(f"[EMAIL DEBUG] To Email: {to_email}")
    print(f"[EMAIL DEBUG] Reset Token: {reset_token[:10]}...")
    print(f"[EMAIL DEBUG] Reset URL: {reset_url}")
    
    # Get environment variables
    print(f"[EMAIL DEBUG] Getting environment variables...")
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    print(f"[EMAIL DEBUG] Environment variables loaded:")
    print(f"[EMAIL DEBUG] - SMTP Server: {smtp_server}")
    print(f"[EMAIL DEBUG] - SMTP Port: {smtp_port}")
    print(f"[EMAIL DEBUG] - SMTP User: {smtp_user}")
    print(f"[EMAIL DEBUG] - From Email: {from_email}")
    print(f"[EMAIL DEBUG] - SMTP Pass: {'*' * len(smtp_pass) if smtp_pass else 'NOT SET'}")

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        print(f"[EMAIL DEBUG] ❌ Missing SMTP credentials!")
        print(f"[EMAIL DEBUG] - smtp_server: {bool(smtp_server)}")
        print(f"[EMAIL DEBUG] - smtp_port: {bool(smtp_port)}")
        print(f"[EMAIL DEBUG] - smtp_user: {bool(smtp_user)}")
        print(f"[EMAIL DEBUG] - smtp_pass: {bool(smtp_pass)}")
        print(f"[EMAIL DEBUG] - from_email: {bool(from_email)}")
        raise Exception("SMTP credentials are not fully set in environment variables.")
    
    print(f"[EMAIL DEBUG] ✅ All SMTP credentials present")

    print(f"[EMAIL DEBUG] Creating email message...")
    msg = EmailMessage()
    msg['Subject'] = "Password Reset Request - Stanley Owarieta Portfolio Admin"
    msg['From'] = from_email
    msg['To'] = to_email
    print(f"[EMAIL DEBUG] Email headers set:")
    print(f"[EMAIL DEBUG] - Subject: {msg['Subject']}")
    print(f"[EMAIL DEBUG] - From: {msg['From']}")
    print(f"[EMAIL DEBUG] - To: {msg['To']}")

    print(f"[EMAIL DEBUG] Setting email content...")
    # Plain text version
    plain_text_content = f"""\
Hello,

You requested a password reset for your admin account.

Click the following link to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email.

Best regards,
Stanley Owarieta Portfolio Admin
"""
    msg.set_content(plain_text_content)
    print(f"[EMAIL DEBUG] ✅ Plain text content set")

    # HTML version
    html_content = f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 480px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.2em 1.2em 1.5em 1.2em;'>
          <h2 style='color: #2563eb; margin-bottom: 1.5em; font-size: 1.5em;'>Password Reset Request</h2>
          
          <p style='font-size: 1.1em; margin-bottom: 1.5em; line-height: 1.6;'>
            Hello,<br><br>
            You requested a password reset for your admin account.
          </p>
          
          <div style='text-align: center; margin: 2em 0;'>
            <a href='{reset_url}' style='background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 0.8em 2em; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);'>
              Reset Password
            </a>
          </div>
          
          <p style='font-size: 0.95em; color: #666; margin-bottom: 1.5em;'>
            <strong>Important:</strong> This link will expire in 1 hour for security reasons.
          </p>
          
          <p style='font-size: 0.95em; color: #666; margin-bottom: 1.5em;'>
            If you didn't request this password reset, please ignore this email.
          </p>
          
          <div style='font-weight: 500; color: #23272f; margin-top: 2em; padding-top: 1.5em; border-top: 1px solid #e5e7eb;'>
            Best regards,<br>
            <span style='color: #2563eb; font-weight: 700;'>Stanley Owarieta Portfolio Admin</span>
          </div>
        </div>
      </body>
    </html>
    """
    msg.add_alternative(html_content, subtype='html')
    print(f"[EMAIL DEBUG] ✅ HTML content set")

    # Send the email via Zoho SMTP
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg) 

# Admin Notification Functions
def send_admin_contact_notification(admin_email, contact_data):
    """Send notification to admin when someone sends a contact message"""
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = f"🔔 New Contact Message from {contact_data['name']}"
    msg['From'] = from_email
    msg['To'] = admin_email

    # Plain text version
    msg.set_content(f"""\
New Contact Message Received

Name: {contact_data['name']}
Email: {contact_data['email']}
Subject: {contact_data.get('subject', 'No subject')}
Message: {contact_data['message']}

Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please respond to this inquiry promptly.
""")

    # HTML version
    msg.add_alternative(f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 600px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.5em;'>
          <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <h2 style='margin: 0; font-size: 1.3rem;'>🔔 New Contact Message</h2>
          </div>
          
          <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #667eea; margin-bottom: 1rem;'>Contact Details</h3>
            <p><strong>Name:</strong> {contact_data['name']}</p>
            <p><strong>Email:</strong> <a href='mailto:{contact_data['email']}' style='color: #667eea;'>{contact_data['email']}</a></p>
            <p><strong>Subject:</strong> {contact_data.get('subject', 'No subject')}</p>
            <p><strong>Received:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </div>
          
          <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;'>
            <h4 style='margin-top: 0; color: #667eea;'>Message:</h4>
            <p style='white-space: pre-wrap; margin: 0;'>{contact_data['message']}</p>
          </div>
          
          <div style='margin-top: 1.5rem; text-align: center;'>
            <a href='mailto:{contact_data['email']}' style='background: #667eea; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block;'>Reply to {contact_data['name']}</a>
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
            print(f"[ADMIN NOTIFICATION] Contact notification sent to admin")
    except Exception as e:
        print(f"[ADMIN NOTIFICATION] Error sending contact notification: {e}")
        raise

def send_admin_booking_notification(admin_email, booking_data):
    """Send notification to admin when someone books a call"""
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = f"📅 New Call Booking from {booking_data['name']}"
    msg['From'] = from_email
    msg['To'] = admin_email

    # Plain text version
    msg.set_content(f"""\
New Call Booking Request

Name: {booking_data['name']}
Email: {booking_data['email']}
Date & Time: {booking_data['datetime']}
Provider: {booking_data.get('provider', 'Not specified')}
Message: {booking_data.get('message', 'No additional message')}

Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please schedule this call and send confirmation to the client.
""")

    # HTML version
    msg.add_alternative(f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 600px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.5em;'>
          <div style='background: linear-gradient(135deg, #43e97b, #38f9d7); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <h2 style='margin: 0; font-size: 1.3rem;'>📅 New Call Booking</h2>
          </div>
          
          <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #667eea; margin-bottom: 1rem;'>Booking Details</h3>
            <p><strong>Name:</strong> {booking_data['name']}</p>
            <p><strong>Email:</strong> <a href='mailto:{booking_data['email']}' style='color: #667eea;'>{booking_data['email']}</a></p>
            <p><strong>Date & Time:</strong> {booking_data['datetime']}</p>
            <p><strong>Provider:</strong> {booking_data.get('provider', 'Not specified')}</p>
            <p><strong>Received:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </div>
          
          {f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #43e97b; margin-bottom: 1.5rem;'><h4 style='margin-top: 0; color: #43e97b;'>Client Message:</h4><p style='white-space: pre-wrap; margin: 0;'>{booking_data.get('message', 'No additional message')}</p></div>" if booking_data.get('message') else ""}
          
          <div style='margin-top: 1.5rem; text-align: center;'>
            <a href='mailto:{booking_data['email']}' style='background: #43e97b; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block; margin-right: 1rem;'>Reply to {booking_data['name']}</a>
            <a href='https://calendar.google.com' target='_blank' style='background: #667eea; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block;'>Open Calendar</a>
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
            print(f"[ADMIN NOTIFICATION] Booking notification sent to admin")
    except Exception as e:
        print(f"[ADMIN NOTIFICATION] Error sending booking notification: {e}")
        raise

def send_admin_review_notification(admin_email, review_data):
    """Send notification to admin when someone leaves a review"""
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = f"⭐ New Review from {review_data['client_name']} ({review_data['rating']} stars)"
    msg['From'] = from_email
    msg['To'] = admin_email

    # Create star rating display
    stars = "⭐" * review_data['rating'] + "☆" * (5 - review_data['rating'])

    # Plain text version
    msg.set_content(f"""\
New Review Received

Client: {review_data['client_name']}
Rating: {stars} ({review_data['rating']}/5)
Comment: {review_data.get('comment', 'No comment provided')}
Email: {review_data.get('client_email', 'No email provided')}

Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Review is currently pending approval.
""")

    # HTML version
    msg.add_alternative(f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 600px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.5em;'>
          <div style='background: linear-gradient(135deg, #ffd93d, #ff6b6b); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <h2 style='margin: 0; font-size: 1.3rem;'>⭐ New Review</h2>
          </div>
          
          <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #667eea; margin-bottom: 1rem;'>Review Details</h3>
            <p><strong>Client:</strong> {review_data['client_name']}</p>
            <p><strong>Rating:</strong> <span style='font-size: 1.2rem;'>{stars}</span> ({review_data['rating']}/5)</p>
            <p><strong>Email:</strong> {review_data.get('client_email', 'No email provided')}</p>
            <p><strong>Received:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </div>
          
          {f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffd93d; margin-bottom: 1.5rem;'><h4 style='margin-top: 0; color: #ffd93d;'>Comment:</h4><p style='white-space: pre-wrap; margin: 0; font-style: italic;'>{review_data.get('comment', 'No comment provided')}</p></div>" if review_data.get('comment') else ""}
          
          <div style='background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 8px; margin-top: 1.5rem;'>
            <p style='margin: 0; color: #856404;'><strong>Note:</strong> This review is currently pending approval in the admin dashboard.</p>
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
            print(f"[ADMIN NOTIFICATION] Review notification sent to admin")
    except Exception as e:
        print(f"[ADMIN NOTIFICATION] Error sending review notification: {e}")
        raise

def send_admin_lead_notification(admin_email, lead_data):
    """Send notification to admin when someone becomes a lead"""
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = f"🎯 New Lead: {lead_data['name']} from {lead_data.get('company', 'Unknown Company')}"
    msg['From'] = from_email
    msg['To'] = admin_email

    # Plain text version
    msg.set_content(f"""\
New Lead Generated

Name: {lead_data['name']}
Email: {lead_data['email']}
Company: {lead_data.get('company', 'Not specified')}
Phone: {lead_data.get('phone', 'Not provided')}
Source: {lead_data.get('source', 'Not specified')}
Message: {lead_data.get('message', 'No message provided')}

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a potential business opportunity - follow up promptly!
""")

    # HTML version
    msg.add_alternative(f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 600px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.5em;'>
          <div style='background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <h2 style='margin: 0; font-size: 1.3rem;'>🎯 New Lead</h2>
          </div>
          
          <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #667eea; margin-bottom: 1rem;'>Lead Details</h3>
            <p><strong>Name:</strong> {lead_data['name']}</p>
            <p><strong>Email:</strong> <a href='mailto:{lead_data['email']}' style='color: #667eea;'>{lead_data['email']}</a></p>
            <p><strong>Company:</strong> {lead_data.get('company', 'Not specified')}</p>
            <p><strong>Phone:</strong> {lead_data.get('phone', 'Not provided')}</p>
            <p><strong>Source:</strong> {lead_data.get('source', 'Not specified')}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </div>
          
          {f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #ff6b6b; margin-bottom: 1.5rem;'><h4 style='margin-top: 0; color: #ff6b6b;'>Message:</h4><p style='white-space: pre-wrap; margin: 0;'>{lead_data.get('message', 'No message provided')}</p></div>" if lead_data.get('message') else ""}
          
          <div style='margin-top: 1.5rem; text-align: center;'>
            <a href='mailto:{lead_data['email']}' style='background: #ff6b6b; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block;'>Contact {lead_data['name']}</a>
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
            print(f"[ADMIN NOTIFICATION] Lead notification sent to admin")
    except Exception as e:
        print(f"[ADMIN NOTIFICATION] Error sending lead notification: {e}")
        raise

def send_admin_newsletter_notification(admin_email, subscriber_data):
    """Send notification to admin when someone subscribes to newsletter"""
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        raise Exception("SMTP credentials are not fully set in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = f"📧 New Newsletter Subscriber: {subscriber_data['email']}"
    msg['From'] = from_email
    msg['To'] = admin_email

    # Plain text version
    msg.set_content(f"""\
New Newsletter Subscription

Email: {subscriber_data['email']}
Subscribed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total subscribers: {subscriber_data.get('total_subscribers', 'Unknown')}

This person is interested in your content and updates.
""")

    # HTML version
    msg.add_alternative(f"""
    <html>
      <body style='font-family: Inter, Roboto, Arial, sans-serif; background: #f9f9fb; color: #23272f; padding: 0.5em;'>
        <div style='max-width: 600px; margin: 1.5em auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(102,126,234,0.08); border: 1px solid #e5e7eb; padding: 1.5em;'>
          <div style='background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <h2 style='margin: 0; font-size: 1.3rem;'>📧 New Newsletter Subscriber</h2>
          </div>
          
          <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #667eea; margin-bottom: 1rem;'>Subscription Details</h3>
            <p><strong>Email:</strong> <a href='mailto:{subscriber_data['email']}' style='color: #667eea;'>{subscriber_data['email']}</a></p>
            <p><strong>Subscribed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total Subscribers:</strong> {subscriber_data.get('total_subscribers', 'Unknown')}</p>
          </div>
          
          <div style='background: #e3f2fd; border: 1px solid #bbdefb; padding: 1rem; border-radius: 8px; margin-top: 1.5rem;'>
            <p style='margin: 0; color: #1976d2;'>🎉 This person is interested in your content and updates!</p>
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
            print(f"[ADMIN NOTIFICATION] Newsletter notification sent to admin")
    except Exception as e:
        print(f"[ADMIN NOTIFICATION] Error sending newsletter notification: {e}")
        raise 