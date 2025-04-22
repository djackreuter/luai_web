from functools import wraps
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, session
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

API_KEY = os.getenv("API_KEY")

def api_key_required(func):
	@wraps(func)
	def check_authorization(*args, **kwargs):
		if request.headers.get('Authorization'):
			api_key = request.headers.get('Authorization').split(' ')[1]
			if api_key == API_KEY:
				return func(*args, **kwargs)
			else:
				return jsonify({"error": "API key is not valid"}), 401
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
	return render_template("index.html")

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