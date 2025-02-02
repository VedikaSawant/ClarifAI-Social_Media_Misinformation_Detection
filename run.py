from flask import Flask
from app.routes import api
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/misinformation_db"
mongo = MongoClient(app.config["MONGO_URI"])
db = mongo.get_database()

# Register Routes
app.register_blueprint(api)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
