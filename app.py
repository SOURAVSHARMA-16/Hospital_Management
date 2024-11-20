from flask import Flask, request, jsonify, render_template, flash, redirect, url_for,make_response
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,unset_jwt_cookies
import datetime
from bson.objectid import ObjectId 
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
    documents_collection=db["documents"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

@app.route('/')
def home():
    return render_template('index.html')
#logout comment 
@app.route('/logout')
@jwt_required()
def logout():
    response = redirect(url_for('home')) 
    unset_jwt_cookies(response) 
    return response

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

@app.route('/patient_data_upload', methods=['POST'])
@jwt_required()
def patient_data_up():
    current_user = get_jwt_identity()  # Extract the email from JWT
    user = users_collection.find_one({"email": current_user})  # Fetch user data based on email

    if not user:
        flash("User not found", "danger")
        return redirect(url_for('patient_home'))

    blood_pressure = request.form.get('bloodpressure')
    pulse_rate = request.form.get('pulse')
    body_temp = request.form.get('temp')
    medical_history = request.form.get('medical_history')
    current_medication = request.form.get('medications')
    allergies = request.form.get('allergies')

    if not all([blood_pressure, pulse_rate, body_temp, medical_history, current_medication]):
        flash("All fields except allergies are required", "danger")
        return redirect(url_for('patient_home'))

    document = {
        "owner_id": str(user["_id"]),
        "owner_email": current_user,
        "blood_pressure": blood_pressure,
        "pulse_rate": pulse_rate,
        "body_temp": body_temp,
        "medical_history": medical_history,
        "current_medication": current_medication,
        "allergies": allergies,
        "uploaded_at": datetime.datetime.utcnow()
    }

    # Insert the document into the collection
    documents_collection.insert_one(document)

    flash("Patient data uploaded successfully!", "success")
    return redirect(url_for('patient_home'))


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

@app.route('/admin-home')
@jwt_required()
def admin_home():
    current_user=get_jwt_identity()
    return render_template('cloud_home.html', email=current_user)

@app.route('/admin-patient')
@jwt_required()
def admin_patient():
    current_user = get_jwt_identity()
    
    # Fetch all patient data from the users_collection
    all_patients = users_collection.find()
    patient_list = [
        {**doc, "_id": str(doc["_id"])} for doc in all_patients
    ]

    return render_template('cloud_patient_details.html', email=current_user, patients=patient_list)

@app.route('/assign-doctor-form')
@jwt_required()
def assign_doctor_form():
    current_user = get_jwt_identity()
    
    # Fetch all patient data from the users_collection
    all_patients = users_collection.find()
    patient_list = [
        {**doc, "_id": str(doc["_id"])} for doc in all_patients
    ]

    return render_template('cloud_assign_doctor.html', email=current_user, patients=patient_list)

@app.route('/admin-doctor')
@jwt_required()
def admin_doctor():
    current_user = get_jwt_identity()
    
    # Fetch doctors with active=true from doctors_collection
    active_doctors = doctors_collection.find({"active": True})
    active_doctor_list = [
        {**doc, "_id": str(doc["_id"])} for doc in active_doctors
    ]  

    return render_template(
        'cloud_doctor_details.html',
        email=current_user,
        doctors=active_doctor_list
    )

@app.route('/admin-doctor-inactive', methods=['GET', 'POST'])
@jwt_required()
def admin_doctor_inactive():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        action = request.form.get('action')

        if not doctor_id or not action:
            flash("Doctor ID and action are required.", "danger")
            return redirect(url_for('admin_doctor_inactive'))

        if action == 'approve':
            # Set active=True for the doctor
            result = doctors_collection.update_one(
                {"_id": ObjectId(doctor_id)},
                {"$set": {"active": True}}
            )
            if result.modified_count > 0:
                flash("Doctor approved successfully!", "success")
            else:
                flash("Failed to approve the doctor.", "danger")
        elif action == 'reject':
            # Delete the doctor from the database
            result = doctors_collection.delete_one({"_id": ObjectId(doctor_id)})
            if result.deleted_count > 0:
                flash("Doctor rejected and removed successfully!", "success")
            else:
                flash("Failed to reject the doctor.", "danger")
        else:
            flash("Invalid action.", "danger")
            return redirect(url_for('admin_doctor_inactive'))

        return redirect(url_for('admin_doctor_inactive'))

    # Fetch doctors with active=false from doctors_collection
    inactive_doctors = doctors_collection.find({"active": False})
    inactive_doctor_list = [
        {**doc, "_id": str(doc["_id"])} for doc in inactive_doctors
    ]

    return render_template(
        'cloud_doctor_activation.html',
        email=current_user,
        doctors=inactive_doctor_list
    )


@app.route('/admin/signin',methods=['POST'])
def admin_signin():
    email = request.form.get('email')
    password = request.form.get('password')
    ver_email='admin@gmail.com'
    ver_pass='admin@123'

    if email==ver_email and password == ver_pass:
        access_token = create_access_token(identity=email)
        response = make_response(redirect('/admin-home'))
        response.set_cookie('access_token_cookie', access_token, httponly=True) 
        return response
    else:
        flash('Email or password is incorrect')

    return redirect('/admin')

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
def doctor_home():
    current_user = get_jwt_identity()
    return render_template('doctor_home.html', email=current_user)

@app.route("/doctor-search")
@jwt_required()
def doctor_search():
    current_user = get_jwt_identity()
    patient_data=users_collection.find()
    patients=[]
    for items in patient_data:
        patients.append(items)
    return render_template('Doctor_Search_Patient.html', email=current_user,patients=patients)

@app.route("/doctor-alloted")
@jwt_required()
def doctor_alloted():
    current_user = get_jwt_identity()  # Extract current doctor's email
    doctor = doctors_collection.find_one({"email": current_user})  # Fetch doctor details

    if not doctor:
        flash("Doctor not found", "danger")
        return redirect(url_for('doctor_home'))

    # Fetch all patients assigned to the doctor
    assigned_patients = users_collection.find({"assigned_doctor": current_user})
    patient_data = []

    for patient in assigned_patients:
        documents = documents_collection.find({"owner_email": patient["email"]})
        patient_data.append({
            "name": patient["username"],
            "age": patient.get("age", "N/A"),
            "condition": patient.get("condition", "N/A"),
            "documents": list(documents)[:3]
        })

    return render_template('Doctor_Alloted_Patients.html', doctor=doctor, patients=patient_data)

@app.route("/doctor-request")
@jwt_required()
def doctor_request():
    current_user = get_jwt_identity()
    return render_template('doctor_Request_Patient.html', email=current_user)


@app.route('/patient_home')
def patient_home():
    return render_template('patient_home.html')

@app.route('/patient-data')
def patient_data():
    return render_template('patient-data.html')

@app.route('/patient-medical-data', methods=['GET'])
@jwt_required()
def patient_medical_data():
    current_user = get_jwt_identity()  # Extract the email of the logged-in user
    user = users_collection.find_one({"email": current_user})  # Retrieve user details

    if not user:
        flash("User not found", "danger")
        return redirect(url_for('patient_home'))

    # Fetch all medical records for the current user
    user_documents = documents_collection.find({"owner_email": current_user})
    
    # Return user details and medical documents to the template
    return render_template(
        'patient-medical-data.html',
        user=user,                # User details
        documents=list(user_documents)  # Medical records
    )



@app.route('/patient-personal-data')
def patient_personal_data():
    return render_template('patient-personal-data.html')


@app.route('/assign-doctor', methods=['POST'])
@jwt_required()
def assign_doctor():
    patient_id = request.form.get('patient_id')  # Get patient ID
    doctor_email = request.form.get('doctor_email')  # Get doctor's email

    if not patient_id or not doctor_email:
        flash("Both patient ID and doctor email are required", "danger")
        return redirect(url_for('assign-doctor-form'))  # Ensure this route exists

    try:
        # Attempt to update the patient record
        result = users_collection.update_one(
            {"_id": ObjectId(patient_id)},  # Match the patient by ID
            {"$set": {"assigned_doctor": doctor_email}}
        )

        if result.modified_count > 0:
            flash("Doctor assigned successfully!", "success")
        else:
            flash("Failed to assign doctor. No changes made.", "warning")

    except Exception as e:
        # Log the error and inform the user
        print(f"Error assigning doctor: {e}")
        flash("An error occurred while assigning the doctor. Please try again.", "danger")

    # Redirect to the admin patient page
    return redirect(url_for('assign-doctor-form'))


@app.route('/patient-personal-data-form', methods=['POST'])
@jwt_required()
def patient_personal_data_form():
    current_user = get_jwt_identity()  # Get the logged-in user's identity (email)

    # Extract form data
    age = request.form.get('age')
    gender = request.form.get('gender')
    bloodgroup = request.form.get('bloodgroup')

    # Prepare the data to be inserted or updated
    patient_data = {
        'age': age,
        'gender': gender,
        'bloodgroup': bloodgroup
    }

    # Update the existing record or insert a new one
    users_collection.update_one(
        {'email': current_user},  # Filter by logged-in user's email
        {'$set': patient_data},  # Update with new data
        upsert=True              # Insert if no matching record exists
    )

    # Return a success message or redirect to another page
    return render_template('patient-personal-data.html', success=True)

if __name__ == "__main__":
    app.run(debug=True)
