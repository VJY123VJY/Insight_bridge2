import hashlib
import json

def generate_fingerprint(data_dict):
    payload_str = json.dumps(data_dict, sort_keys=True)
    return hashlib.sha256(payload_str.encode()).hexdigest()
