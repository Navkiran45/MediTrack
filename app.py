"""
Web Application Development with Flask
SAS Model
"""

from flask import *
import datetime
import hashlib
from database import MongoDBHelper
from bson.objectid import ObjectId
from functools import wraps

web_app = Flask("MediTrack")
db_helper = MongoDBHelper()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if "email" not in session or not session["email"]:
            # Redirect to login page if not logged in
            return render_template("index.html")
        return f(*args, **kwargs)
    return decorated_function

@web_app.route("/") 
def index():

    message = """
    <html>
    <head>
        <title> Doctor's App </title>
        <body>
        <center>
            <h3> Welcome to Doctor's App </h3>
        </center>
        </body>
    </head>
    </html>
    """
    #return message

    # render_template is used to return web pages (html pages)
    return render_template("index.html")

@web_app.route("/register")
def register():
    return render_template("register.html")

@web_app.route("/home")
def home():
    if session["email"] != "":
        return render_template("home.html", name = session['name'], email= session['email'])
    else:
        return redirect("/")

@web_app.route("/success")
def success():
    return render_template("success.html", name = session['name'], email= session['email'])

@web_app.route("/error")
def error():
    return render_template("error.html", name = session['name'], email= session['email'])

@web_app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@web_app.route("/add-user", methods= ["POST"])
def add_user_in_db():

    user_data = {
        "name": request.form["name"],
        "email": request.form["email"],
        "password": hashlib.sha256(request.form["password"].encode('utf-8')).hexdigest(),
        "created_on": datetime.datetime.now()
    }
    db_helper.collection = db_helper.db["users"]
    
    result = db_helper.insert(user_data)

    session['user_id'] = str(result.inserted_id)
    session['name'] = user_data["name"]
    session['email'] = user_data["email"]

    return render_template("home.html", email= session['email'])

@web_app.route("/fetch-user", methods= ["POST"])
def fetch_user_from_db():
   
    user_data = {
        "email": request.form["email"],
        "password": hashlib.sha256(request.form["password"].encode('utf-8')).hexdigest()
    }
    db_helper.collection = db_helper.db["users"]

    result = db_helper.fetch(query = user_data)

    print("Result is: ",result)

    if len(result)>0:
        user_data = result[0]
        session['name'] = user_data["name"]
        session['email'] = user_data["email"]

        return render_template("home.html", name= session['name'], email=session['email'])
    else:
        return render_template("error.html", message ="User Not Found. Please Try Again", name= session['name'], email=session['email'])
   
@web_app.route("/add-patient", methods= ["POST"])
@login_required
def add_patient_in_db():
    
    patient_data = {
        "name": request.form["name"],
        "email": request.form["email"],
        "phone": request.form["phone"],
        "gender": request.form["gender"],
        "age": int(request.form["age"]),
        "address": request.form["address"],
        "doctor_email": session["email"],
        "doctor_name": session["name"],
        "created_on": datetime.datetime.now()
    }
    
    db_helper.collection = db_helper.db["patients"]
   
    result = db_helper.insert(patient_data)
   
    return render_template("success.html", message = "Patient added Successfully." , name= session['name'], email=session['email'] )

@web_app.route("/update-patient/<id>")
@login_required
def update_patient(id):
    print("Patient to be updated: ", id)

    session["id"] = id
    
    query = {"_id": ObjectId(id)}
    db_helper.collection = db_helper.db["patients"]


    result = db_helper.fetch(query=query)

    patient_doc = result[0]
    return render_template("update.html", name= session['name'], email=session['email'], patient = patient_doc )

@web_app.route("/update-patient-in-db", methods= ["POST"])
@login_required
def update_patient_in_db():
   
    patient_data = {
        "name": request.form["name"],
        "email": request.form["email"],
        "phone": request.form["phone"],
        "gender": request.form["gender"],
        "age": int(request.form["age"]),
        "address": request.form["address"],
        "doctor_email": session["email"],
        "doctor_name": session["name"],
        "created_on": datetime.datetime.now()
    }
    
    db_helper.collection = db_helper.db["patients"]
    query = {"_id": ObjectId(session["id"])}

    result = db_helper.update(patient_data, query)
   
    return render_template("success.html", message = "Patient Updated Successfully." , name= session['name'], email=session['email'] )

@web_app.route("/delete-patient/<id>")
@login_required
def delete_patient(id):
    print("Patient to be deleted: ", id)
    query = {"_id": ObjectId(id)}
    db_helper.collection = db_helper.db["patients"]
    db_helper.delete(query)
    return render_template("success.html", message = "Patient Deleted Successfully." , name= session['name'], email=session['email'] )

@web_app.route("/fetch-patients")
@login_required
def fetch_patients_from_db():
      
    if len(session["email"]) == 0:
        return redirect("/")
    
    user_data = {
        "doctor_email": session["email"]
    }
    db_helper.collection = db_helper.db["patients"]
    
    result = db_helper.fetch(query = user_data)

    if len(result)>0:
        print(result)
        return render_template("patients.html", patients= result, name=session["name"], email=["email"])
    else:
        return render_template("error.html", message ="Patients Not Found" , name= session['name'], email=session['email'])

@web_app.route("/add-consultation/<id>")
@login_required
def add_consultation(id):
    session["patient_id"] = id
    query = {"_id": ObjectId(id)}
    db_helper.collection = db_helper.db["patients"]
    
    result = db_helper.fetch(query=query)
    patient_doc = result[0]
    session["patient_name"] = patient_doc["name"]
    
    return render_template("add-consultation.html", name= session['name'], email = session['email'], patient_name=session["patient_name"])

@web_app.route("/add-consultation-in-db", methods= ["POST"])
@login_required
def add_consultation_in_db():
    consultation_data = {
        "complaints": request.form["complaints"],
        "bp": request.form["bp"],
        "temperature": request.form["temperature"],
        "sugar": request.form["sugar"],
        "medicines": request.form["medicines"],
        "remarks": request.form["remarks"],
        "follow_up": request.form['follow_up'],
        "doctor_email": session['email'],
        "doctor_name": session['name'],
        "patient_id" : session["patient_id"],
        "patient_name" : session["patient_name"],
        "created_on": datetime.datetime.now()
    }

    db_helper.collection = db_helper.db["consultations"]
    result = db_helper.insert(consultation_data)
   
    return render_template("success.html", message = "Consultation added Successfully." , name= session['name'], email=session['email']  )

@web_app.route("/fetch-consultations")
@login_required
def fetch_consultations_from_db():
      
    if len(session["email"]) == 0:
        return redirect("/")
    
    user_data = {
        "doctor_email": session["email"]
    }
    db_helper.collection = db_helper.db["consultations"]
    
    result = db_helper.fetch(query = user_data)

    if len(result)>0:
        print(result)
        return render_template("consultations.html", consultations= result, name=session["name"], email=session["email"])
    else:
        return render_template("error.html", message ="Consultations Not Found" , name= session['name'], email=session['email'])

@web_app.route("/fetch-consultations-of-patient/<id>")
@login_required
def fetch_consultations_of_patient_from_db(id):
      
    if len(session["email"]) == 0:
        return redirect("/")
    user_data = {
        "doctor_email": session["email"],
        "patient_id": id
    }
    db_helper.collection = db_helper.db["consultations"]
    
    result = db_helper.fetch(query = user_data)

    if len(result)>0:
        print(result)
        return render_template("consultations.html", consultations= result, name=session["name"], email=session["email"])
    else:
        return render_template("error.html", message ="Consultations Not Found" , name= session['name'], email=session['email'])

@web_app.route("/delete-consultation/<id>")
@login_required
def delete_consultation(id):
    print("Consultation to be deleted: ", id)
    query = {"patient_id": id}
    db_helper.collection = db_helper.db["consultations"]
    db_helper.delete(query)
    return render_template("success.html", message = "Consultation Deleted Successfully." , name= session['name'], email=session['email'] )

@web_app.route("/update-consultation/<id>")
@login_required
def update_consultation(id):
    print("Consultation to be updated: ", id)

    query = {"_id": ObjectId(id)}
    db_helper.collection = db_helper.db["consultations"]

    result = db_helper.fetch(query=query)

    consultation_doc = result[0]
    return render_template("update-cons.html", name= session['name'], email=session['email'], consultation = consultation_doc )

@web_app.route("/update-consultation-in-db", methods= ["POST"])
@login_required
def update_consultation_in_db():
    consultation_data = {
        "complaints": request.form["complaints"],
        "bp": request.form["bp"],
        "temperature": request.form["temperature"],
        "sugar": request.form["sugar"],
        "medicines": request.form["medicines"],
        "remarks": request.form["remarks"],
        "follow_up": request.form['follow_up'],
        "doctor_email": session['email'],
        "doctor_name": session['name'],
        "created_on": datetime.datetime.now()
    }
    
    db_helper.collection = db_helper.db["consultations"]
    query = {"_id": ObjectId(id)}
    result = db_helper.update(consultation_data, query)
   
    return render_template("success.html", message = "Consultation Updated Successfully." , name= session['name'], email=session['email'] )

@web_app.route("/search-patient")
@login_required
def search_patient():
    return render_template("search.html", name=session["name"], email= session["email"])

@web_app.route("/search-patient-from-db", methods= ["POST"])
def search_patient_from_db():
    patient_data = {
        "email" : request.form["email"],
        "doctor_email" : session["email"]
    }

    db_helper.collection = db_helper.db["patients"]
    
    result = db_helper.fetch(query = patient_data)
    if len(result)>0:
        return render_template("patient-card.html", patient= result[0], name=session["name"], email=["email"])
    else:
        return render_template("error.html", message ="Patients Not Found" , name= session['name'], email=session['email'])

def main():
    web_app.secret_key = "doctors-key-v1"
    web_app.run(debug = True)

if __name__ == "__main__":
    main()