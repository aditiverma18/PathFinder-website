from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # your homepage

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validate user (in real app, check DB)
        return redirect(url_for('dashboard'))
    return render_template('login.html')  # form for login

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Save user (in real app, write to DB)
        return redirect(url_for('dashboard'))
    return render_template('signup.html')  # form for signup

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # dashboard after login/signup

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/help')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.run(debug=True)
