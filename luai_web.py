from functools import wraps
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, session
import os
import time

from sqlalchemy import asc, desc, select
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
		if session.get("username") is not None:
			user = session.get("username")
			if user == os.getenv("LUAI_USERNAME"):
				return func(*args, **kwargs)
			else:
				return redirect(url_for("login")), 302
		else:
			return redirect(url_for("login")), 302
	return check_session

@app.route("/")
@auth_required
def index():
	chats = db.session.query(Chat).all()
	#chats = db.session.query(Chat).order_by(asc(Chat.id)).all()
	return render_template("index.html", chats=chats)


@app.post('/send_message')
@auth_required
def send_message():
	message = request.form.get("message")
	message = message.strip()
	if message == None or message == "":
		return jsonify(), 500
	
	chat = Chat(message=message, sender="user")
	db.session.add(chat)
	db.session.commit()

	while True:
		time.sleep(15)
		last_message = get_last_message()
		if last_message.sender == "system":
			return jsonify({"message": last_message.message}), 200


def get_last_message():
	last_message = db.session.scalars(select(Chat).order_by(desc(Chat.id))).first()
	return last_message


@app.post("/delete_chats")
@auth_required
def delete_chats():
	db.session.query(Chat).delete()
	db.session.commit()
	return jsonify(), 200


@app.route("/get_message")
@api_key_required
def get_message():
	chat = db.session.scalars(select(Chat).where(Chat.sender == "user").order_by(desc(Chat.id))).first()
	if chat is None:
		return jsonify(), 404

	return jsonify({ "message": chat.message }), 200

@app.post("/reply")
@api_key_required
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