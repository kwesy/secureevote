import uuid
import requests
from decouple import config

HUBTEL_BASE_URL = config("HUBTEL_BASE_URL", default="https://api.hubtel.com")
MERCHANT_ACCOUNT_NUMBER = config("HUBTEL_ACCOUNT_NUMBER", default="your_account_number")
MERCHANT_CLIENT_ID = config("HUBTEL_CLIENT_ID", default="your_client_id")
MERCHANT_CLIENT_SECRET = config("HUBTEL_CLIENT_SECRET", default="your_client_secret")
CALLBACK_URL = config("HUBTEL_CALLBACK_URL", default="/api/xxxxx")  # e.g. /api/v1/payments/webhook/

def initiate_payment(reference, amount, description, customer_number):
    url = f"{HUBTEL_BASE_URL}/payment/v1/merchantaccount/onlinecheckout/initiate"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {config('HUBTEL_AUTH_BASE64', default='your_base64_encoded_credentials')}",
    }

    payload = {
        "amount": str(amount),
        "customerName": "Secure Voter",
        "customerMsisdn": customer_number,
        "customerEmail": "anonymous@secureevote.com",
        "channel": "momo",
        "primaryCallbackUrl": CALLBACK_URL,
        "description": description,
        "clientReference": reference
    }

    # response = requests.post(url, json=payload, headers=headers)
    # return response.json()
    return payload # For testing purposes, we return the payload directly
