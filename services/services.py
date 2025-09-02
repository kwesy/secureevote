import requests
from decouple import config

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
    
def check_balance():
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
    
if __name__ == "__main__":
    # test the functions
    # check_balance()
    status = send_sms(["+233558297444"], "Hello, this is a test message.")
    print("SMS sent successfully!" if status else "Failed to send SMS.")
