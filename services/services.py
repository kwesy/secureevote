import requests
from decouple import config
from rest_framework.exceptions import (
    ValidationError,
    APIException
)
import logging
from uuid import UUID

logger = logging.getLogger("paystack")

def send_sms(recipients: list, message: str) -> bool:
    """
    Send an SMS to the specified phone number with the given message.
    
    Args:
        phone_number (str): The recipient's phone number.
        message (str): The message content to be sent.
        
    Returns:
        bool: True if the SMS was sent successfully, False otherwise.
    """
    url = "https://sms.arkesel.com/api/v2/sms/send"
    api_key = config("SMS_API_KEY")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "sender": "Hello world",
        "message":message,
        "recipients": recipients,
        "sandbox": True
    }
    
    try:
        response = requests.post(url=url,headers=headers, json=body)
        response.raise_for_status()
        print(response.json())
        return response.json().get("status", False)
    except requests.RequestException as e:
        print(f"Error sending SMS: {e}")
        return False
    
def check_sms_balance():
    """
    Check the SMS balance of the account.
    
    Returns:
        dict: A dictionary containing balance details if successful, None otherwise.
    """
    api_url = "https://sms.arkesel.com/api/v2/clients/balance-details"
    api_key = config("SMS_API_KEY")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers) 
        response.raise_for_status()
        print(response.json())
        return response.json().get("status", None)
    except requests.RequestException as e:
        print(f"Error sending SMS: {e}")
        return False
    
def charge_mobile_money(id:UUID, amount:float, phone_number:str, provider:str, email:str=None):
    """
    Debit the account by the specified amount via mobile money.
    
    Args:
        amount (float): The amount to debit.
        
    Returns:
        bool: True if the transaction was successful, False otherwise.
    """
    url = "https://api.paystack.co/charge"
    api_key = config("PAYSTACK_SECRET_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email or phone_number,
        "amount": float(amount),
        "currency": "GHS",
        "mobile_money": {
            "phone": phone_number,
            "provider": provider
        },
        "reference": str(id)
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 401:
            logger.error("Paystack API key Invalid: %s", response.json())
        elif response.status_code == 400:
            logger.error("Paystack Validation error: %s", response.json())
        
        raise APIException("internal error") # Paystack error
    except requests.exceptions.Timeout:
        logger.error("Paystack request timed out.")
        raise APIException("internal error")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Paystack.")
        raise APIException("internal error")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        raise APIException("An unexpected error occured.")

    data = response.json()

    # If status is False in Paystack response, treat as ValidationError
    if not data.get("status", False):
        logger.error("Paystack returned an error: %s", data)
        raise ValidationError(data.get("message", "Unknown error"))

    return ({
        "status": data["data"]["status"],
        "reference": data["data"]["reference"],
        "display_text": data["data"].get("display_text", "")
    })
    
# if __name__ == "__main__":
    # test the functions
    # check_balance()
    # status = send_sms(["+233558297444"], "Hello, this is a test message.")
    # print("SMS sent successfully!" if status else "Failed to send SMS.")
    # charge_mobile_money(0.1, "0548297444", "mtn")
