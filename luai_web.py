from functools import wraps
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, session
import os

from sqlalchemy import asc, select
from db import db

from dotenv import load_dotenv

from models.chat import Chat

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///luai_web.db"

db.init_app(app)

with app.app_context():
    db.create_all()

API_KEY = os.getenv("API_KEY")

def api_key_required(func):
	@wraps(func)
	def check_authorization(*args, **kwargs):
		if request.headers.get('Authorization'):
			api_key = request.headers.get('Authorization').split(' ')[1]
			if api_key == API_KEY:
				return func(*args, **kwargs)
		else:
			return jsonify({"error": "Unauthorized"}), 401
	return check_authorization

def auth_required(func):
	@wraps(func)
	def check_session(*args, **kwargs):
		if session["username"] is not None:
			user = session["username"]
			if user == os.getenv("LUAI_USERNAME"):
				return func(*args, **kwargs)
			else:
				return redirect(url_for("login")), 302
		else:
			return redirect(url_for("login")), 302
	return check_session

@auth_required
@app.route("/")
def index():
	chats = db.session.query(Chat).all()
	#chats = db.session.query(Chat).order_by(asc(Chat.id)).all()
	return render_template("index.html", chats=chats)


@auth_required
@app.post('/send_message')
def send_message():
	message = request.form.get("message")
	message = message.strip()
	if message == None or message == "":
		return jsonify(), 500
	
	chat = Chat(message=message, sender="user")
	db.session.add(chat)
	db.session.commit()
	return jsonify(), 200


@api_key_required
@app.route("/get_message")
def get_message():
	chat = db.session.scalars(select(Chat).where(Chat.sender == "user")).first()
	if chat is None:
		return jsonify(), 404

	return jsonify({ "message": chat.message }), 200

@api_key_required
@app.post("/reply")
def reply():
	data = request.get_json()
	message = data["message"]
	print(f"Attempts: {data["attempts"]}")
	chat = Chat(message=message, sender="system")
	db.session.add(chat)
	db.session.commit()
	return jsonify(), 200


@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == 'POST':

		username_config = os.getenv("LUAI_USERNAME")
		password_config = os.getenv("LUAI_PASSWORD")
		username = request.form.get("username")
		password = request.form.get("password")

		if username_config == username and password_config == password:
			session["username"] = username
			return redirect(url_for("index"))

		flash("Username or password is incorrect")
		return render_template("login.html")

		

	return render_template("login.html")