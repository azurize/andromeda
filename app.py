from flask import Flask, flash, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    client = MongoClient(os.environ.get('MONGODB_URI'))
    app.db = client.andromeda

    @app.route('/')
    def index():
        if 'email' in session:
            return render_template('index.html')
        else: return redirect(url_for('login'))

    @app.route('/login/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            users = app.db.users
            login_user = users.find_one({'email' : request.form['email']})
            password = request.form['password'].encode('utf-8')

            if login_user:
                if bcrypt.checkpw(password, login_user['password']):
                    session['email'] = request.form['email']
                    return redirect(url_for('index'))
            else: flash('Incorrect email/password combination!')
                
        return render_template('login.html')

    @app.route('/create/', methods=['GET', 'POST'])
    def create():
        if request.method == 'POST':
            users = app.db.users
            existing_user = users.find_one({'email' : request.form['email']})

            if existing_user is None:
                hashed_pword = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name' : request.form['name'], 'email' : request.form['email'], 'password' : hashed_pword})
                session['email'] = request.form['email']
                return redirect(url_for('index'))
            else: flash('That email is already registered.')

        return render_template('create.html')

    if __name__ == '__main__':
        app.secret_key
        app.run(debug=True)

    return app
