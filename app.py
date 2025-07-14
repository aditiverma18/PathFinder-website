#ZGzxoFRG8YEEpfz4
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import pickle
import json

# MongoDB Setup
client = MongoClient("mongodb+srv://10caditiverma:ZGzxoFRG8YEEpfz4@cluster0.jvmwija.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['pathFinder_db']
users_collection = db['users']

app = Flask(__name__)
app.secret_key = 'aditi_verma_secret_2025'

# Traits list (OCEAN)
traits = ["O_score", "C_score", "E_score", "A_score", "N_score"]

# Load ML Model + Label Encoder
with open('career_model.pkl', 'rb') as f:
    model, label_encoder = pickle.load(f)

# Load quiz questions
with open('questions.json', 'r') as f:
    questions_json = json.load(f)  # Load full JSON object
    questions_data = questions_json['content'] 


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
    try:
        # Return the pre-loaded questions data
        return jsonify(questions_data)  # questions_data is already the content array
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Submit and Predict Career
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # Initialize trait scores for OCEAN
    trait_scores = {"O": [], "C": [], "E": [], "A": [], "N": []}

    # Get weighted scores from each question
    for q in questions_data:
        qid = f"q{q['id']}"
        if qid not in request.form:
            return render_template('quiz.html', prediction_text="⚠️ Please complete all questions.")

        user_score = int(request.form[qid])
        user_answer_weights = q["weights"][str(user_score)]
        
        # Add weighted scores for each trait
        for trait, weight in user_answer_weights.items():
            trait_scores[trait].append(weight)

    # Calculate average scores for each trait
    input_features = []
    for trait in ["O", "C", "E", "A", "N"]:
        avg = sum(trait_scores[trait]) / len(trait_scores[trait]) if trait_scores[trait] else 0
        input_features.append(avg)

    # Predict and decode label
    prediction_index = model.predict([input_features])[0]
    prediction = label_encoder.inverse_transform([prediction_index])[0]

    return render_template('quiz.html', prediction_text=f"🎯 Recommended Career: {prediction}")

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
            session['user'] = user['email']
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
    app.run(host='0.0.0.0', port=5000, debug=True)
