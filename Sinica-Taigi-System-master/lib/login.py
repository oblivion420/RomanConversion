from functools import wraps
from flask import request, Response
from importlib import import_module
from flask_login import UserMixin, LoginManager, login_required, login_user

cfg = import_module("config.{}".format("prd"))
users = cfg.users

# ====================================================
# HTTP Basic Authentication
# ====================================================
def check_auth(username, password):
  return password == users[username]["password"]

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ====================================================
# Flask Login
# ====================================================
