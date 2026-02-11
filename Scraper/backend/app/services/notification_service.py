"""
Notification Service
Handles multi-channel alerts (WhatsApp via Meta Cloud API, Email via SMTP).
"""

import os
import requests
import json
from typing import Dict, Any, Optional

class NotificationService:
    """
    Service to send alerts to sales officers.
    """
    
    # Meta Cloud API Config
    META_API_URL = "https://graph.facebook.com/v19.0"
    
    def __init__(self):
        # WhatsApp Config
        self.wa_phone_id = os.getenv("META_PHONE_NUMBER_ID")
        self.wa_token = os.getenv("META_ACCESS_TOKEN")
        
        # Email Config (Placeholder)
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")

    def send_whatsapp_alert(self, lead: Dict[str, Any], user_phone: str) -> bool:
        """
        Send WhatsApp template message using Meta Cloud API.
        """
        if not self.wa_phone_id or not self.wa_token:
            print("⚠️  WhatsApp credentials missing. Skipping alert.")
            return False
            
        if not user_phone:
            print("⚠️  User phone number missing. Skipping alert.")
            return False
            
        url = f"{self.META_API_URL}/{self.wa_phone_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.wa_token}",
            "Content-Type": "application/json"
        }
        
        # Construct message payload (using a template)
        # Note: You must create a template named 'new_lead_alert' in Meta Business Manager
        payload = {
            "messaging_product": "whatsapp",
            "to": user_phone,
            "type": "template",
            "template": {
                "name": "new_lead_alert",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": lead.get('company_name', 'Unknown Company')
                            },
                            {
                                "type": "text",
                                "text": str(lead.get('confidence', 0.0))
                            },
                            {
                                "type": "text",
                                "text": lead.get('signal_type', 'General')
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"✅ WhatsApp alert sent to {user_phone}")
            return True
        except Exception as e:
            print(f"❌ Failed to send WhatsApp alert: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return False

    def send_email_alert(self, lead: Dict[str, Any], user_email: str) -> bool:
        """
        Send email alert (Placeholder).
        """
        if not user_email:
            return False
            
        # TODO: Implement SMTP sending logic
        print(f"📧 [Mock] Email sent to {user_email}: New Lead - {lead.get('company_name')}")
        return True

    def notify_officer(self, lead: Dict[str, Any], user_context: Dict[str, Any]):
        """
        Route notification based on user preferences.
        """
        if user_context.get('push_enabled', False) and user_context.get('phone'):
            self.send_whatsapp_alert(lead, user_context['phone'])
            
        if user_context.get('email_enabled', True) and user_context.get('email'):
            self.send_email_alert(lead, user_context['email'])
