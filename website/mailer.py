import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

def mail_to(email):
    sender_email = "prepairteam@gmail.com"
    receiver_email = email
    password = "ntgx mexg qitd noef"
    sender_name = "Pre-Pair Team"

    verification_code = f"{random.randint(0, 999999):06d}"

    # Create the HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pre-Pair Verification Code</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f8f8f8;
                text-align: center;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                padding: 20px;
            }}
            h1 {{
                color: #3498db;
            }}
            p {{
                font-size: 16px;
                color: #555;
            }}
            .verification-code {{
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c;
            }}
            .footer {{
                margin-top: 20px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Pre-Pair Verification Code</h1>
            <p>Dear user,</p>
            <p>Your verification code is:</p>
            <p class="verification-code">{verification_code}</p>
            <p>Please use this code to complete your verification process.</p>
            <div class="footer">
                <p>Best regards,<br>Pre-Pair Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    print(verification_code)
    # Create the MIME object
    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "Pre-Pair Verification Code"

    # Attach the HTML content to the email
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    # Establish a connection with the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        # Start the TLS connection
        server.starttls()

        # Login to the email account
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("Email sent successfully")
    return verification_code
