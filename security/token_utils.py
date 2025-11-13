import time, os
from dotenv import load_dotenv

load_dotenv(override=True)  # Force reload environment variables
TOKEN = os.getenv("CORE_AUTH_TOKEN")
print(f"[DEBUG] Token_utils.py loaded token: {TOKEN}")

def is_token_valid(token):
    # Reload token from environment to ensure it's current
    current_token = os.getenv("CORE_AUTH_TOKEN")
    print(f"[DEBUG] Token validation:")
    print(f"  - Stored token: {TOKEN}")
    print(f"  - Current env token: {current_token}")
    print(f"  - Received token: {token}")
    
    # Simulate expiry check (valid for 1 hour)
    expiry_time = int(time.time()) + 3600
    
    if token == current_token and time.time() < expiry_time:
        print("[DEBUG] Token validation successful")
        return True
    print("[DEBUG] Token validation failed")
    return False
