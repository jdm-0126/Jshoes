from flask_mail import Message
from flask import current_app, render_template_string
from datetime import datetime

def send_payment_receipt(order):
    """Send payment receipt email to customer"""
    try:
        from flask import current_app
        mail = current_app.mail
        
        # Email template
        email_template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h1 style="color: #333;">JShoes - Payment Receipt</h1>
            </div>
            
            <div style="padding: 20px;">
                <h2>Thank you for your order!</h2>
                <p>Dear {{ customer_name }},</p>
                <p>We have received your payment for Order #{{ order_id }}. Here are your order details:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3>Order Information</h3>
                    <p><strong>Order Number:</strong> #{{ order_id }}</p>
                    <p><strong>Order Date:</strong> {{ order_date }}</p>
                    <p><strong>Payment Date:</strong> {{ payment_date }}</p>
                    <p><strong>Total Amount:</strong> ₱{{ total_amount }}</p>
                    {% if delivery_date %}
                    <p><strong>Expected Delivery:</strong> {{ delivery_date }}</p>
                    {% endif %}
                </div>
                
                <h3>Items Ordered</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #e9ecef;">
                            <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Item</th>
                            <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Qty</th>
                            <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Price</th>
                            <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;">{{ item.name }}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{{ item.quantity }}</td>
                            <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">₱{{ item.price }}</td>
                            <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">₱{{ item.total }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                {% if delivery_address %}
                <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3>Delivery Address</h3>
                    <p>{{ delivery_address }}</p>
                </div>
                {% endif %}
                
                <p>Your order is now being processed and will be delivered on the expected date above.</p>
                <p>Thank you for choosing JShoes!</p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
                    <p>JShoes - Premium Footwear</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Prepare email data
        items = []
        for item in order.items:
            items.append({
                'name': item.product.name,
                'quantity': item.quantity,
                'price': f"{item.price:,.2f}",
                'total': f"{item.price * item.quantity:,.2f}"
            })
        
        delivery_address = None
        if order.user.address:
            delivery_address = f"{order.user.address}, {order.user.city}"
            if order.user.postal_code:
                delivery_address += f", {order.user.postal_code}"
        
        # Render email content
        email_content = render_template_string(email_template,
            customer_name=order.user.username,
            order_id=order.id,
            order_date=order.created_at.strftime('%B %d, %Y'),
            payment_date=datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            total_amount=f"{order.total_amount:,.2f}",
            delivery_date=order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else None,
            items=items,
            delivery_address=delivery_address
        )
        
        # Create and send email
        msg = Message(
            subject=f'JShoes - Payment Receipt for Order #{order.id}',
            recipients=[order.user.email],
            html=email_content
        )
        
        if current_app.config.get('MAIL_SUPPRESS_SEND'):
            # Development mode - print to console
            print(f"\n=== EMAIL RECEIPT (DEV MODE) ===")
            print(f"To: {order.user.email}")
            print(f"Subject: {msg.subject}")
            print("Content: Payment receipt email would be sent")
            print("================================\n")
            return True
        else:
            # Production mode - send actual email
            mail.send(msg)
            return True
            
    except Exception as e:
        print(f"Failed to send receipt email: {str(e)}")
        return False