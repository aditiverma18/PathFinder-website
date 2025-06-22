#ZGzxoFRG8YEEpfz4
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

client = MongoClient("mongodb+srv://10caditiverma:ZGzxoFRG8YEEpfz4@cluster0.jvmwija.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['pathFinder_db']
users_collection = db['users']


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

#@app.route('/login', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
