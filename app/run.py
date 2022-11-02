import os
import redis
import hashlib
from flask import Flask, request, render_template, redirect, url_for, session, escape

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# импортируем классы Book и Base из файла database_setup.py
from database_setup import News, Base, Users


app = Flask(__name__)
app.secret_key = "<Some secret key>"
app.config['SESSION_TYPE'] = 'filesystem'

salt = os.getenv("SECRET", "S0me_seCr3T-keY")

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379, db=0)

# Подключаемся и создаем сессию базы данных
engine = create_engine('sqlite:///news-collection.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/news')
def show_news():
    books = session.query(News).all()
    return render_template("news.html", books=books)


@app.route("/add", methods=["GET", "POST"])
def add_news():
    if request.method == "POST":
        title = request.values.get("title")
        author = request.values.get("author")
        genre = request.values.get("genre")
        text = request.values.get("text")
        news = News(title=title, author=author, genre=genre, text=text,)
        session.add(news)
        session.commit()
        return redirect(url_for('show_news'))
    else:
        return render_template('create_news.html')


def hash_password(password: str) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )


def check_password(password: str, hashed: bytes) -> bool:
    return hashed == hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )


@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        value = None
        if "key" in request.values:
            value = request.values.get("key")
            redis_client.set("key", value)
    else:
        value = redis_client.get("key")
    return render_template("index.html", value=value,)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.values.get("email")
        hashed = redis_client.get(email)
        if hashed and check_password(password=request.values.get("password"), hashed=hashed):
            return redirect('get_email')
    return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.values.get("email")
        hashed = hash_password(password=request.values.get("password"))
        redis_client.set(email, hashed)
        return redirect(url_for('get_email'))
    return render_template('register.html')


@app.route('/get_email')
def get_email():
    if 'email' and 'password' in session:
        return 'Logged in as %s' % escape(session['email'])

    return render_template('index.html')


@app.route('/logout')
def logout():
    if request.method == "POST":
        email = request.values.get("email")
        hashed = redis_client.get(email)
        if hashed and check_password(password=request.values.get("password"), hashed=hashed):
            redis_client.delete(email)
        return redirect('hello_world')
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
