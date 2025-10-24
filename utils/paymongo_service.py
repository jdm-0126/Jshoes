import requests
import base64
from flask import current_app

class PayMongoService:
    BASE_URL = "https://api.paymongo.com/v1"
    
    @staticmethod
    def get_auth_header():
        secret_key = current_app.config['PAYMONGO_SECRET_KEY']
        if not secret_key:
            raise ValueError("PayMongo secret key not configured")
        
        encoded_key = base64.b64encode(f"{secret_key}:".encode()).decode()
        return {"Authorization": f"Basic {encoded_key}"}
    
    @staticmethod
    def create_payment_intent(amount, currency="PHP", description="JShoes Order"):
        """Create a payment intent for the given amount"""
        url = f"{PayMongoService.BASE_URL}/payment_intents"
        
        data = {
            "data": {
                "attributes": {
                    "amount": int(amount * 100),  # Convert to centavos
                    "currency": currency,
                    "description": description,
                    "payment_method_allowed": ["gcash", "paymaya", "grab_pay"]
                }
            }
        }
        
        headers = {
            **PayMongoService.get_auth_header(),
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    @staticmethod
    def create_source(amount, type="gcash", currency="PHP"):
        """Create a payment source"""
        url = f"{PayMongoService.BASE_URL}/sources"
        
        data = {
            "data": {
                "attributes": {
                    "amount": int(amount * 100),  # Convert to centavos
                    "currency": currency,
                    "type": type,
                    "redirect": {
                        "success": "http://127.0.0.1:5000/payment/success",
                        "failed": "http://127.0.0.1:5000/payment/failed"
                    }
                }
            }
        }
        
        headers = {
            **PayMongoService.get_auth_header(),
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"PayMongo Status: {response.status_code}")
        print(f"PayMongo Response Text: {response.text[:500]}")
        
        if response.status_code != 200:
            return {'error': f'API Error {response.status_code}: {response.text[:200]}'}
        
        try:
            result = response.json()
            return result
        except ValueError:
            return {'error': 'Invalid JSON response from PayMongo'}