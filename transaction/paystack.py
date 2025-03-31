import requests
import os
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Load Paystack Secret Key from environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"

if not PAYSTACK_SECRET_KEY:
    logger.error("PAYSTACK_SECRET_KEY is not set. Ensure it is properly configured in the environment.")

# General function to make API requests
def make_request(method, endpoint, payload=None):
    """Helper function to make requests to Paystack API."""
    url = f"{PAYSTACK_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=payload, headers=headers)
        else:
            logger.error(f"Unsupported request method: {method}")
            return {"status": False, "message": "Invalid request method"}

        response_data = response.json()

        if response.status_code in [200, 201] and response_data.get("status"):
            return response_data
        else:
            logger.warning(f"Paystack API error - Endpoint: {endpoint}, Response: {response_data}")
            return {"status": False, "message": response_data.get("message", "Request failed"), "details": response_data}

    except requests.RequestException as e:
        logger.error(f"Paystack API request failed: {e}")
        return {"status": False, "message": "Paystack API request failed", "error": str(e)}


def initialize_transaction(email, amount):
    """Initialize a transaction with Paystack."""
    endpoint = "/transaction/initialize"
    payload = {
        "email": email,
        "amount": int(amount) * 100,  # Convert to kobo (Paystack processes in the smallest currency unit)
        "currency": "NGN"
    }

    logger.info(f"Initializing transaction for {email} with amount {amount}")
    return make_request("POST", endpoint, payload)


def verify_transaction(reference):
    """Verify a Paystack transaction."""
    endpoint = f"/transaction/verify/{reference}"

    logger.info(f"Verifying transaction reference: {reference}")
    return make_request("GET", endpoint)
