import os
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    """Handle all notifications - SMS, Email, Push"""
    
    @staticmethod
    def send_sms(phone, message):
        """Send SMS notification via Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                print("⚠️  Twilio credentials not configured")
                return False
            
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            
            print(f"✓ SMS sent to {phone}: {message.sid}")
            return True
        except Exception as e:
            print(f"✗ SMS Error: {e}")
            return False
    
    @staticmethod
    def send_email(recipient, subject, body):
        """Send email notification"""
        try:
            # Try to use flask-mail if available; fall back to smtplib otherwise.
            try:
                from flask_mail import Mail, Message  # type: ignore
                has_flask_mail = True
            except Exception:
                has_flask_mail = False

            from flask import current_app

            if has_flask_mail:
                mail = Mail(current_app)
                msg = Message(
                    subject=subject,
                    recipients=[recipient],
                    body=body,
                    html=body
                )
                mail.send(msg)
            else:
                # Fallback using smtplib and email.message.EmailMessage
                import smtplib
                from email.message import EmailMessage

                smtp_server = os.getenv('SMTP_SERVER')
                smtp_port = int(os.getenv('SMTP_PORT', '587'))
                smtp_user = os.getenv('SMTP_USERNAME')
                smtp_pass = os.getenv('SMTP_PASSWORD')
                sender = os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('SMTP_FROM') or 'no-reply@example.com'

                if not all([smtp_server, smtp_user, smtp_pass]):
                    print("⚠️  SMTP credentials not configured and flask_mail not available")
                    return False

                em = EmailMessage()
                em['Subject'] = subject
                em['From'] = sender
                em['To'] = recipient
                em.set_content(body)
                em.add_alternative(body, subtype='html')

                with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(smtp_user, smtp_pass)
                    smtp.send_message(em)

            print(f"✓ Email sent to {recipient}")
            return True
        except Exception as e:
            print(f"✗ Email Error: {e}")
            return False
    
    @staticmethod
    def notify_ngo_new_donation(ngo, donation):
        """Notify NGO about new nearby donation"""
        message = f"""
        🍽️  New Food Available!
        
        Donor: {donation.get('donor_name')}
        Type: {donation.get('food_type')}
        Quantity: {donation.get('quantity')}
        Pickup Time: {donation.get('pickup_time')}
        Location: {donation.get('location', {}).get('address')}
        
        Click to accept and arrange pickup!
        """
        
        phone = ngo.get('phone')
        if phone:
            NotificationService.send_sms(phone, message)
    
    @staticmethod
    def notify_donor_accepted(donor, ngo):
        """Notify donor that NGO accepted their donation"""
        message = f"""
        ✅ Your Food Donation Accepted!
        
        NGO: {ngo.get('name')}
        Contact: {ngo.get('phone')}
        Email: {ngo.get('email')}
        
        They will arrive at the scheduled time.
        """
        
        phone = donor.get('phone')
        if phone:
            NotificationService.send_sms(phone, message)
