from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os
import random

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT")),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# In a real app, you'd store this code more persistently (e.g., Redis or DB with expiry)
verification_codes = {}

async def send_verification_email(email: str):
    code = str(random.randint(100000, 999999))
    verification_codes[email] = code
    
    message = MessageSchema(
        subject="Your Setup Verification Code",
        recipients=[email],
        body=f"Your verification code is: {code}",
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    return True