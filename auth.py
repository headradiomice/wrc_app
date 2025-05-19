import dash_auth

VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin'
}

def auth(app):
    dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
