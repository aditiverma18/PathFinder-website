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

# Load ML Model + Label Encoder + Scaler + Career Mapping
try:
    with open('career_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
        if isinstance(model_data, tuple) and len(model_data) == 4:
            model, label_encoder, scaler, career_mapping = model_data
        else:
            print("⚠️ Model file format incorrect. Retraining model...")
            # If model format is wrong, retrain it
            import subprocess
            subprocess.run(['python', 'career_model.py'])
            with open('career_model.pkl', 'rb') as f:
                model, label_encoder, scaler, career_mapping = pickle.load(f)
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("🔄 Retraining model...")
    import subprocess
    subprocess.run(['python', 'career_model.py'])
    with open('career_model.pkl', 'rb') as f:
        model, label_encoder, scaler, career_mapping = pickle.load(f)

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
    # Initialize trait scores for all 10 features
    trait_scores = {
        "O": [], "C": [], "E": [], "A": [], "N": [],
        "Numerical": [], "Spatial": [], "Perceptual": [], "Abstract": [], "Verbal": []
    }

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

    # Calculate average scores for each trait in the correct order
    input_features = []
    feature_order = ["O", "C", "E", "A", "N", "Numerical", "Spatial", "Perceptual", "Abstract", "Verbal"]
    
    for trait in feature_order:
        if trait_scores[trait]:
            avg = sum(trait_scores[trait]) / len(trait_scores[trait])
        else:
            avg = 0
        input_features.append(avg)

    # Debug output
    print("🔍 Raw trait scores:", {trait: sum(trait_scores[trait])/len(trait_scores[trait]) if trait_scores[trait] else 0 for trait in feature_order})
    
    # Scale the features using the same scaler from training
    input_features_scaled = scaler.transform([input_features])
    
    # Predict and decode label
    prediction_index = model.predict(input_features_scaled)[0]
    predicted_category = label_encoder.inverse_transform([prediction_index])[0]
    
    # Get prediction probabilities for debugging
    probabilities = model.predict_proba(input_features_scaled)[0]
    top_predictions = [(label_encoder.inverse_transform([i])[0], prob) for i, prob in enumerate(probabilities)]
    top_predictions.sort(key=lambda x: x[1], reverse=True)
    
    # Get specific career suggestions from the predicted category
    specific_careers = [career for career, category in career_mapping.items() if category == predicted_category]
    
    print("🎯 Top 3 predictions:", top_predictions[:3])
    print("🎯 Predicted category:", predicted_category)
    print("🎯 Specific careers:", specific_careers[:3])

    # Create a more detailed prediction message
    if specific_careers:
        career_suggestions = ", ".join(specific_careers[:3])
        prediction_text = f"🎯 Recommended Career Field: {predicted_category}<br>💼 Specific careers to consider: {career_suggestions}"
    else:
        prediction_text = f"🎯 Recommended Career Field: {predicted_category}"

    return render_template('quiz.html', prediction_text=prediction_text)

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
