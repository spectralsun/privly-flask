import os
import simplejson

from flask import Flask, redirect
from flask.ext.login import LoginManager, current_user

from pyvly.controllers import post, user
from pyvly.forms import csrf
from pyvly.models import User


# Create the flask app
app = Flask('pyvly', static_folder='static/privly-applications', 
    static_url_path='/apps')

if os.environ.get('STREAM_HANDLER'):
    import logging
    from logging import StreamHandler
    file_handler = StreamHandler()
    app.logger.setLevel(logging.CRITICAL)  
    app.logger.addHandler(file_handler)

# Initialize CSRF protection of POST and DELETE requests
csrf.init_app(app)

# Load the configuration
app.config.from_object('config')

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(userid):
    """Load the user for the user manager"""
    return User.get(userid)

# Mount the controller Blueprints
app.register_blueprint(post.bp, url_prefix='/posts')
app.register_blueprint(user.bp, url_prefix='/users')

class ExtensibleJSONEncoder(simplejson.JSONEncoder):
    """A JSON encoder that will check for a .__json__ method on objects."""
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return super(ExtensibleJSONEncoder, self).default(obj)

# Override Flask's json encoder to check for __json__ method on objects
app.json_encoder = ExtensibleJSONEncoder

@app.route('/')
def index():
    if current_user.is_anonymous():
        return redirect(app.config['PRIVLY_LOGIN'])
    return redirect(app.config['PRIVLY_INDEX'])

@app.route('/pages/privacy')
def privacy():
    return 'Privacy Statement'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
