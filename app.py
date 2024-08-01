from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_pymongo import PyMongo
import subprocess
import os
import threading
import time

app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/user-registration"
mongo = PyMongo(app)

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
        mongo.db.users.insert_one(new_user)
        return jsonify({"message": "User registered successfully", "redirect": "/game"}), 201
    except Exception as e:
        return jsonify({"error": "There was an error registering the user"}), 500

# @app.route('/game')
# def game():
#     # Run the breaker_game.py script with the current directory as an argument
#     subprocess.Popen(["python", "breaker_game.py", os.getcwd()])
#     return "Game launched. Check your desktop for the game window."\
# @app.route('/game')
# def game():
#     latest_user = mongo.db.users.find_one(sort=[('_id', -1)])
#     player_name = latest_user['name'] if latest_user else "Player"
    
#     # Use pythonw.exe to run the game without a console window
#     game_process = subprocess.Popen(["pythonw", "breaker_game.py", os.getcwd(), player_name])
    
#     # Start a thread to wait for the game to finish
#     threading.Thread(target=wait_for_game, args=(game_process,)).start()
    
#     return "Game launched. Check your desktop for the game window."

@app.route('/game')
def game():
    latest_user = mongo.db.users.find_one(sort=[('_id', -1)])
    player_name = latest_user['name'] if latest_user else "Player"
    
    # Remove the result file if it exists
    if os.path.exists('game_result.txt'):
        os.remove('game_result.txt')
    
    # Use pythonw.exe to run the game without a console window
    subprocess.Popen(["pythonw", "breaker_game.py", os.getcwd(), player_name])
    
    return jsonify({"message": "Game launched. Check your desktop for the game window."})

@app.route('/check_game_status')
def check_game_status():
    if os.path.exists('game_result.txt'):
        with open('game_result.txt', 'r') as f:
            result = f.read().strip()
        os.remove('game_result.txt')
        return jsonify({"status": "completed", "result": result})
    return jsonify({"status": "running"})

if __name__ == '__main__':
    app.run(debug=True)