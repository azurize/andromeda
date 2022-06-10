from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, flash, render_template, request, redirect, url_for, session

import bcrypt
import logging
import os
import psycopg2

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='{asctime} {levelname:<8} {message}',
    style='{'
)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    class User:
        def __init__(self, email, password, name) -> None:
            self.email = email
            self.password = password
            self.name = name

    # Connection to Postgres DB
    def get_db_connection():
        connection = psycopg2.connect(
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            host=os.environ.get('DB_HOST'),  # localhost used during test phase
            database=os.environ.get('DB_NAME')
        )
        return connection

    @app.before_request
    def makeSessionPermanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if 'email' in session:
            return render_template('index.html')
        else:
            return redirect(url_for('login'))

    # User login page
    @app.route('/login/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = User(
                email=request.form['email'],
                password=request.form['password'],
                name=None
            )

            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                sql = 'SELECT password FROM users WHERE username = %s;'
                params = [user.email]
                cursor.execute(sql, params)
            except Exception as e:
                logging.critical('Failed with the following exception: ', e)

            login = cursor.fetchall()
            output = str([x[0] for x in login])
            password = output.strip("'[]")

            if login != []:
                if bcrypt.checkpw(user.password.encode('utf-8'), password.encode('utf-8')):
                    session['email'] = user.email
                    return redirect(url_for('index'))
                else:
                    flash('Email/password combination does not exist.')
            else:
                flash('Email/password combination does not exist.')

        return render_template('login.html')

    # User creation page
    @app.route('/create/', methods=['GET', 'POST'])
    def create():
        if request.method == 'POST':
            user = User(
                email=request.form['email'],
                password=request.form['password'],
                name=request.form['name']
            )

            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                sql = 'SELECT username FROM users WHERE username = (%s);'
                params = [user.email]
                cursor.execute(sql, params)
            except Exception as e:
                logging.critical('Failed with the following exception: ', e)

            output = cursor.fetchall()

            if output == []:
                email = user.email
                password = bcrypt.hashpw(
                    user.password.encode('utf-8'), bcrypt.gensalt())
                # Decoded for proper db storage - if not decoded, stored value causes issues with bcrypt checkpw for login
                password_decode = password.decode('utf-8')
                name = user.name

                sql = 'INSERT INTO users (username, password, name) VALUES (%s, %s, %s)'
                params = (email, password_decode, name)
                cursor.execute(sql, params)

                # Commit transaction to db
                connection.commit()

                # Close connection to db
                connection.close()

                session['email'] = email
                return redirect(url_for('index'))
            else:
                flash('That email is already registered.')

        return render_template('create.html')

    if __name__ == '__main__':
        app.secret_key
        app.run(debug=True)

    return app
