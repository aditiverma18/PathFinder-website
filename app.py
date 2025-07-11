#ZGzxoFRG8YEEpfz4
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import pickle
import numpy as np
import json
import os

# MongoDB Setup
client = MongoClient("mongodb+srv://10caditiverma:ZGzxoFRG8YEEpfz4@cluster0.jvmwija.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['pathFinder_db']
users_collection = db['users']

app = Flask(__name__)
app.secret_key = 'aditi_verma_secret_2025' 

# Load ML Model
with open('career_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load quiz questions
with open('questions.json', 'r') as f:
    questions_data = json.load(f)

# Home (Redirects to Dashboard)
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Quiz Page
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# Serve Quiz Questions
@app.route('/get_questions')
def get_questions():
    return jsonify(questions_data)

# Predict Career Based on Quiz Responses
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_features = [
            float(data['O_score']),
            float(data['C_score']),
            float(data['E_score']),
            float(data['A_score']),
            float(data['N_score']),
            float(data['Numerical']),
            float(data['Spatial']),
            float(data['Perceptual']),
            float(data['Abstract']),
            float(data['Verbal']),
        ]
        prediction = model.predict([input_features])[0]
        return jsonify({'career': prediction})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        with open('questions.json', 'r') as f:
            questions = json.load(f)

        scores = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0,
                  'Numerical': 0, 'Spatial': 0, 'Perceptual': 0,
                  'Abstract': 0, 'Verbal': 0}
        count = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0,
                 'Numerical': 0, 'Spatial': 0, 'Perceptual': 0,
                 'Abstract': 0, 'Verbal': 0}

        # Aggregate trait scores
        for q in questions:
            trait = q['trait']
            response = int(request.form.get(f"q{q['id']}"))
            scores[trait] += response
            count[trait] += 1

        # Average the scores
        traits = [round(scores[k] / count[k], 2) if count[k] != 0 else 0 for k in [
            'O', 'C', 'E', 'A', 'N',
            'Numerical', 'Spatial', 'Perceptual',
            'Abstract', 'Verbal'
        ]]

        # Predict using the ML model
        prediction = model.predict([traits])[0]
        return render_template('quiz.html', prediction_text=f'Recommended Career: {prediction}')

    except Exception as e:
        return f"Prediction error: {e}"


# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if users_collection.find_one({'email': email}):
            return "⚠️ User already exists!"

        users_collection.insert_one({
            'name': full_name,
            'email': email,
            'password': password
        })
        return redirect(url_for('dashboard'))

    return render_template('signup.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            return redirect(url_for('dashboard'))
        else:
            return "❌ Invalid credentials"

    return render_template('login.html')

# Other Routes
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run App
if __name__ == '__main__':
    app.run(debug=True)
