#ZGzxoFRG8YEEpfz4
from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient
import pickle
import numpy as np

client = MongoClient("mongodb+srv://10caditiverma:ZGzxoFRG8YEEpfz4@cluster0.jvmwija.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['pathFinder_db']
users_collection = db['users']



app = Flask(__name__)
app.secret_key = 'aditi_verma_secret_2025' 
with open('career_model.pkl', 'rb') as f:
  model = pickle.load(f)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_features = [
            float(request.form['O_score']),
            float(request.form['C_score']),
            float(request.form['E_score']),
            float(request.form['A_score']),
            float(request.form['N_score']),
            float(request.form['Numerical']),
            float(request.form['Spatial']),
            float(request.form['Perceptual']),
            float(request.form['Abstract']),
            float(request.form['Verbal']),
        ]

        prediction = model.predict([input_features])[0]

        return render_template('quiz.html', prediction_text=f'Recommended Career: {prediction}')
    except Exception as e:
        return f"Error: {e}"
@app.route('/')
def index():
    return render_template('index.html') 

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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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



if __name__ == '__main__':
    app.run(debug=True)
