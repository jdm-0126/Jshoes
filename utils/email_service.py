from flask import current_app
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    mail.init_app(app)
    return mail

def send_inquiry_notification(inquiry):
    try:
        msg = Message(
            subject=f'New Inquiry: {inquiry.subject}',
            recipients=[current_app.config['MAIL_USERNAME']],
            body=f'''
New inquiry received:

Name: {inquiry.name}
Email: {inquiry.email}
Subject: {inquiry.subject}

Message:
{inquiry.message}

Submitted at: {inquiry.created_at}
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        return False

def send_order_confirmation(order):
    try:
        msg = Message(
            subject=f'Order Confirmation #{order.id}',
            recipients=[order.user.email],
            body=f'''
Thank you for your order!

Order #: {order.id}
Total: ${order.total_amount:.2f}
Status: {order.status}

We'll process your order shortly.
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        return False