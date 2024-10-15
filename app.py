from flask import Flask, request, jsonify, render_template, flash, redirect, url_for,make_response
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import os


# TMShmJ0HXVB5Rpf
app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'  # Cookies sent to all paths
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for simplicity

app.config['JWT_SECRET_KEY'] = '8139de647a5cb6614508ace5752d18d7'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.secret_key = "b'\xa5~\xcd\xfa\xb4\x1c\xce\x95x\xdb/\xd4'"

# print(f"App secret key: {app.secret_key}")


try:
    client = MongoClient(
        "mongodb+srv://riddhisomani2003:TMShmJ0HXVB5RpfD@authentication.nptnb.mongodb.net", 
        tls=True,
        tlsAllowInvalidCertificates=True 
    )
    db = client["healthdatabase"]
    users_collection = db["users"]
    doctors_collection = db["doctors"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/patient-home')
def patient():
    return render_template('patient.html')

@app.route('/doctor-home')
def doctor():
    return render_template('doctor.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/patient_register')
def patient_register():
    return render_template('patient-registration.html')

@app.route('/patient_login')
def patient_login():
    return render_template('patient.html')

@app.route('/doctor_login')
def doctor_login():
    return render_template('doctor.html')

@app.route('/doctor_register')
def doctor_register():
    return render_template('doctor-registration.html')

@app.route('/register/patient', methods=["POST"])
def patient_registration():
    if request.method == "POST" : 
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('pass')
        confirmpass = request.form.get('confirmpass')

        if confirmpass != password:
            flash("Confirm Password does not match to the above password")
            return redirect(url_for('patient_register'))
            
        if users_collection.find_one({'email':email}):
            flash("Email already in registered")
            return redirect(url_for('patient_register'))
            
        new_user = {
            'username':username,
            'email':email,
            'phone' : phone,
            'password' : password
        }

        users_collection.insert_one(new_user)
        flash("Registration Successful")
        return redirect(url_for('patient_login'))
        
@app.route('/register/doctor', methods=["POST"])
def doctor_registration():
    if request.method == "POST" : 
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('pass')
        confirmpass = request.form.get('confirmpass')

        if confirmpass != password:
            flash("Confirm Password does not match to the above password")
            return redirect(url_for('doctor_register'))
            
        if doctors_collection.find_one({'email' : email}):
            flash("Email already in registered")
            return redirect(url_for('doctor_register'))

        new_user = {
            'username':username,
            'email':email,
            'phone' : phone,
            'password' : password
        }

        doctors_collection.insert_one(new_user)
        flash("Registration Successful")
        return redirect(url_for('doctor_login'))


    
@app.route('/patientsignin', methods=["POST"])
def patientsignin():
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        flash('Email and password are required')
    user_from_db = users_collection.find_one({"email":email})

    if not user_from_db:
        flash('User does not exist')

    if user_from_db and password == user_from_db.get("password"):
        access_token = create_access_token(identity=user_from_db["email"])
        response = make_response(redirect('/home-patient'))
        response.set_cookie('access_token_cookie', access_token, httponly=True) 
        return response
    else:
        flash('Email or password is incorrect')

    return redirect('/patient_login')

@app.route('/home-patient')
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return render_template('patient_home.html', email=current_user)

@app.route('/doctorsignin', methods=["POST"])
def doctorsignin():
    email = request.form.get('email')
    password = request.form.get('password')

    # print(f"Email : {email}, Password : {password}")
    if not email or not password:
        flash("Email and password are required", 'danger')
    doctor_details = doctors_collection.find_one({"email":email})

    if not doctor_details:
        flash('User does not exist')

    if doctor_details and password == doctor_details.get("password"):
        access_token = create_access_token(identity=doctor_details["email"])
        response = make_response(redirect('/home-doctor'))
        response.set_cookie('access_token_cookie', access_token, httponly=True) 
        return response
    else:
        flash("Password or email incorrect", "danger")
        
    return render_template('doctor.html')

@app.route('/home-doctor')
@jwt_required()
def token_protected():
    current_user = get_jwt_identity()
    return render_template('doctor_home.html', email=current_user)


if __name__ == "__main__":
    app.run(debug=True)