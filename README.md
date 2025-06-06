# luai_web

## Setup
Copy `.env.example` to `.env` and update the values.
```
SECRET_KEY="" // for Flask app
LUAI_USERNAME="admin"
LUAI_PASSWORD="changeme" // change it
API_KEY="" // Create an api key that Luai will use to authenticate. Must be the same as Luai's LUAI_API_KEY
```

## Create environment and install dependencies
```
python -m venv .luai_web
.\.luai_web\Scripts\activate
pip install -r requirements.txt
```

## Start app
```
flask --app luai_web run --debug
```
