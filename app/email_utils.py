import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import random

load_dotenv()

# Configuration
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT") or 587)
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS") == "True"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS") == "True"

# In a real app, you'd store this code more persistently (e.g., Redis or DB with expiry)
verification_codes = {}

def send_verification_email(email: str):
    code = str(random.randint(100000, 999999))
    verification_codes[email] = code
    
    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = email
    msg['Subject'] = "Your Setup Verification Code"
    
    body = f"Your verification code is: {code}"
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        if MAIL_STARTTLS:
            server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(MAIL_FROM, email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False