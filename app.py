from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime


# TMShmJ0HXVB5Rpf
app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = '8139de647a5cb6614508ace5752d18d7'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
client = MongoClient("mongodb+srv://riddhisomani2003:TMShmJ0HXVB5RpfD@authentication.nptnb.mongodb.net")
db = client["healthdatabase"]
users_collection = db["users"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/patientregistration', methods=["POST"])
def registration():
    new_user = request.get_json()
    new_username = users_collection.find_one({"username":new_user["username"]}) 

    if not new_username:
        users_collection.insert_one(new_user)
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'message': 'Username already exists'}), 400
        

if __name__ == "__main__":
    app.run(debug=True)