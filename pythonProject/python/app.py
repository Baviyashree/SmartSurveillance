# from flask import Flask
# from flask_cors import CORS
# from routes import routes
# import camera 

# app = Flask(__name__)
# CORS(app)

# app.register_blueprint(routes)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=9000)
#     app.run(debug=True)


from flask import Flask
from flask_cors import CORS
from routes import routes
from alerts import alerts_bp  
from utils import init_db 
import requests# ✅ import alerts blueprint

app = Flask(__name__)
CORS(app)


# Initialize DB when app starts
init_db()

# Register blueprints
app.register_blueprint(routes)
app.register_blueprint(alerts_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)

