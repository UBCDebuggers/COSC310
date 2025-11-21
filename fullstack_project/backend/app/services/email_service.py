# Email service for sending notifications via SMTP.
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Email Configuration
class EmailConfig:
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = ""  # test?
    SENDER_PASSWORD: str = ""  # 123?
    SENDER_NAME: str = "TheDebuggers Library Notifications"
    APP_NAME: str = "TheDebuggers Library"

# Send a formatted notification email via SMTP (True -> Successful, False -> Otherwise)
def send_notification_email(to_email: str, notification_type: str, category: str, message: str) -> bool:
    try:
        # Format subject
        subject = f"[{category.title()}] {notification_type.title()} - {EmailConfig.APP_NAME}"

        # Format HTML body with styling
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .footer {{ background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; }}
                .message {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{EmailConfig.APP_NAME}</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <div class="message">
                        <p>{message}</p>
                    </div>
                    <p>Best regards,<br><strong>{EmailConfig.SENDER_NAME}</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {EmailConfig.APP_NAME}. All rights reserved.</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create MIME message
        message_obj = MIMEMultipart("alternative")
        message_obj["From"] = f"{EmailConfig.SENDER_NAME} <{EmailConfig.SENDER_EMAIL}>"
        message_obj["To"] = to_email
        message_obj["Subject"] = subject

        # Attach HTML body
        message_obj.attach(MIMEText(html_body, "html"))

        # Send via SMTP
        with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT, timeout=10) as server:
            server.starttls()  # Upgrade to secure TLS connection
            server.login(EmailConfig.SENDER_EMAIL, EmailConfig.SENDER_PASSWORD)
            server.send_message(message_obj)

        print(f"✓ Email sent to {to_email} (type: {notification_type})")
        return True

    except smtplib.SMTPAuthenticationError:
        print(f"✗ SMTP authentication failed. Check SENDER_EMAIL and SENDER_PASSWORD.")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error sending email to {to_email}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error sending email to {to_email}: {e}")
        return False

# Send a simple email (plain text or HTML)
def send_simple_email(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = f"{EmailConfig.SENDER_NAME} <{EmailConfig.SENDER_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "html" if is_html else "plain"))

        with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EmailConfig.SENDER_EMAIL, EmailConfig.SENDER_PASSWORD)
            server.send_message(message)

        print(f"✓ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"✗ Failed to send email to {to_email}: {e}")
        return False
