import os, json, time
from dotenv import load_dotenv
from security.signature_utils import generate_keys, sign_payload
from security.crypto_utils import generate_fingerprint
from db.db_utils import store_data, fetch_all
from security.token_utils import is_token_valid
import requests

load_dotenv(override=True)  # Force reload environment variables
generate_keys()  # Ensure RSA keys exist

CORE_AUTH_TOKEN = os.getenv("CORE_AUTH_TOKEN")
print(f"[DEBUG] Main.py loaded token: {CORE_AUTH_TOKEN}")
RECEIVER_URL = "http://127.0.0.1:5000/receive"

def send_payload(data):
    if not is_token_valid(CORE_AUTH_TOKEN):
        print("[!] Token invalid → running in restricted mode.")
        store_data(data)
        return

    # Add security fields
    signature = sign_payload(data)
    data["signature"] = signature
    data["timestamp"] = time.time()
    data["build_id"] = "BRG-v0.3"
    data["fingerprint"] = generate_fingerprint(data)

    # Log fingerprint
    with open("logs/fingerprint_log.json", "a") as f:
        json.dump({"fingerprint": data["fingerprint"], "time": time.ctime()}, f)
        f.write("\n")

    # Send to receiver
    headers = {"Authorization": f"Bearer {CORE_AUTH_TOKEN}"}
    print(f"Sending request to {RECEIVER_URL}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    try:
        response = requests.post(RECEIVER_URL, json=data, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

# Example usage
if __name__ == "__main__":
    sample_event = {"event": "sensor_update", "value": 42}
    send_payload(sample_event)
