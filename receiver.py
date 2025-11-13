from flask import Flask, request, jsonify
from dotenv import load_dotenv
import sqlite3
import os
from flask_docs import ApiDoc # Assuming you want to keep ApiDoc

# --- Configuration & Setup ---

# Load environment variables (for EXPECTED_TOKEN)
load_dotenv(override=True)
EXPECTED_TOKEN = os.getenv('CORE_AUTH_TOKEN', 'my-super-secret-token')
DB_NAME = 'bridge_buffer.db'
print(f"[DEBUG] App loaded expected token: {EXPECTED_TOKEN}")


# --- STUB SECURITY FUNCTIONS (Essential for Security Logic) ---

def is_token_valid(token: str) -> bool:
    """Checks if the received token matches the expected token."""
    if not token:
        return False
    is_valid = token == EXPECTED_TOKEN
    print(f"[DEBUG] Token Valid Check: '{token}' == '{EXPECTED_TOKEN}' -> {is_valid}")
    return is_valid

def verify_signature(data: dict, signature: str) -> bool:
    """Stub: Always returns True for this demonstration."""
    # NOTE: In a real app, this MUST perform HMAC or similar verification.
    return True 

# --------------------------------------------------------

# --- Database Setup ---

def init_db():
    """Initializes the SQLite database and creates the 'items' table."""
    if os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized with 'items' table.")


# --- Flask App Initialization ---

app = Flask(__name__)
ApiDoc(app) # Initialize documentation

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Server is running", "endpoints": ["/data"]}), 200


# --- Secured Central API Interface ---

@app.route("/data", methods=["GET", "POST"])
def handle_data():
    """Handles secured GET (retrieve) and POST (create) requests for data."""
    
    # 1. TOKEN EXTRACTION (Combines Header and Query Param check)
    auth_header = request.headers.get("Authorization")
    token = ""
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
    
    if not token:
        token = request.args.get("api_key", "")

    # 2. TOKEN VALIDATION CHECK
    if not is_token_valid(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    # 3. DATABASE CONNECTION (Only established after authorization)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        if request.method == "POST":
            # --- Handle POST Request (Insert Data + Signature Check) ---
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 415
            
            data = request.json
            
            # Signature Check (Applied to the payload before processing)
            signature = data.pop("signature", "")
            if not verify_signature(data, signature):
                return jsonify({"error": "Signature invalid"}), 400
                
            name = data.get("name")
            value = data.get("value")

            if not name or value is None:
                return jsonify({"error": "Missing 'name' or 'value' in payload"}), 400

            cursor.execute("INSERT INTO items (name, value) VALUES (?, ?)", (name, value))
            conn.commit()
            new_id = cursor.lastrowid
            
            return jsonify({
                "status": "Success", 
                "message": "Item created securely", 
                "id": new_id,
                "name": name,
                "value": value
            }), 201

        elif request.method == "GET":
            # --- Handle GET Request (Retrieve Data) ---
            cursor.execute("SELECT id, name, value FROM items")
            records = cursor.fetchall()
            
            items = []
            for record in records:
                items.append({
                    "id": record[0],
                    "name": record[1],
                    "value": record[2]
                })
            
            return jsonify({"status": "Success", "count": len(items), "items": items}), 200
        
    except Exception as e:
        # Catch any database or JSON parsing errors
        return jsonify({"error": f"An internal processing error occurred: {str(e)}"}), 500
    
    finally:
        # 4. Close connection regardless of success or failure
        conn.close()


# --- Run Application ---

if __name__ == "__main__":
    init_db() # Ensure the database is ready
    app.run(debug=True, port=5000)