from flask import Flask, render_template, request, jsonify, redirect, url_for
import psycopg2
import subprocess
import os
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# PostgreSQL connection parameters
DB_NAME = "pygamebreaker"
DB_USER = "postgres"
DB_PASSWORD = "pygamebreaker"
DB_HOST = "database-1.c3imkoqug979.us-east-1.rds.amazonaws.com"
DB_PORT = "5432"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Create the users table if it doesn't exist
def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            score INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Call this function when the app starts
create_users_table()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = {
        "name": data['name'],
        "email": data['email'],
        "password": data['password']  # Note: In a real application, you should hash this password
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if the email already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (new_user['email'],))
        if cur.fetchone():
            return jsonify({"error": "Email already registered."}), 400
        
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (new_user['name'], new_user['email'], new_user['password'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User registered successfully", "redirect": "/game"}), 201
    except Exception as e:
        return jsonify({"error": f"There was an error registering the user: {str(e)}"}), 500

@app.route('/game')
def game():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users ORDER BY id DESC LIMIT 1")
    latest_user = cur.fetchone()
    cur.close()
    conn.close()

    player_id = latest_user[0] if latest_user else None
    player_name = latest_user[1] if latest_user else "Player"
    
    # Remove the result file if it exists
    if os.path.exists('game_result.txt'):
        with open('game_result.txt', 'r') as f:
            result = f.read().strip()
        
        # Assuming the result is either 'win' or 'lose'
        score = 1 if result == 'win' else 0
        
        # Update the score in the database
        if player_id is not None:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET score = score + %s WHERE id = %s", (score, player_id))
            conn.commit()
            cur.close()
            conn.close()
    # Remove the result file after updating the score
        os.remove('game_result.txt')
        
    # Use pythonw.exe to run the game without a console window on Windows
    if os.name == 'nt':  # Windows
        subprocess.Popen(["pythonw", "breaker_game.py", os.getcwd(), player_name])
    # else:  # Unix/Linux
    #     game_script = os.path.join(os.getcwd(), "breaker_game.py")
    #     process = subprocess.Popen(["python3", game_script, player_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     stdout, stderr = process.communicate()
    #     if stderr:
    #         print(f"Error launching game: {stderr.decode()}")
    #     else:
    #         print(f"Game launched successfully: {stdout.decode()}")
    
    else:  # Unix/Linux
      game_script = os.path.join(os.getcwd(), "breaker_game.py")
      # Start Xvfb and then run the game script
      subprocess.Popen(["xvfb-run", "python3", game_script, player_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      

    return jsonify({"message": "Game launched. Check your desktop for the game window."})

@app.route('/check_game_status', methods=['GET'])
def check_game_status():
    if os.path.exists('game_result.txt'):
        with open('game_result.txt', 'r') as f:
            result = f.read().strip()
        return jsonify({"status": "completed", "result": result}), 200
    return jsonify({"status": "in_progress"}), 200

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)