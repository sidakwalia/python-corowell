import sys
from flask import Flask, request,jsonify
import json
from database import db
import pandas as pd
import time
from datetime import date
from datetime import datetime
import pytz
import requests
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_SORT_KEYS'] = False

tz_NY = pytz.timezone('America/New_York') 
datetime_NY = datetime.now(tz_NY)

today = date.today()
d2 = today.strftime("%B %d, %Y")+" " +str(datetime_NY.strftime("%H:%M:%S"))

@app.route('/api/cornwell/user_login',methods=['POST'])
def login():
    try:
        request_data = request.get_json()
        # Get Account Id
        user_name = request_data['user_name']
        email_id = request_data['email_id']

        # get date range
        password = request_data['password']
        email_id_exist=db.table('user_login').where('email_id',email_id).first()
        if email_id_exist!=None:
            dict_pass=pd.DataFrame(list(db.table('user_login').select('user_name','password',"email_id").where('email_id',email_id).get())).to_dict()
            print(dict_pass)
            password_resonse=dict_pass['password'][0]
            email_response=dict_pass['email_id'][0]
            if (password_resonse==password) and (email_id==email_response):
                print("here")
                exist_insight = db.table('test_details').where('email_id',email_id).first()
                if exist_insight!=None:
                    return { "data": "Verified", "status_code": 200,"result":exist_insight}
                else:
                    return { "data": "Verified", "status_code": 200}
            else:
                return {"data":"Password or email id entered is not correct","status_code": 400}
        else:
            return {"data":"User not found","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "status_code": 400}

@app.route('/api/cornwell/user_registration',methods=['POST'])
def register():
    try:
        request_data = request.get_json()
        # serial_number=request_data['serial_number']
        email_id=request_data['email_id']
        user_name = request_data['user_name']
        password = request_data['password']
        exist_record=db.table('user_login').where('email_id',email_id).first()
        # exist_sn=db.table('user_login').where('serial_number',serial_number).first()
        if exist_record!=None:
            return { "data": "user with this email id already exist", "status_code": 200}
        else:
            insertion=db.table('user_login').insert({"user_name":user_name,"password":password,"time":d2,"email_id":email_id})
            if insertion==1:
                return { "data": "Updated", "status_code": 200}
            else:
                return {"data":"Not_Updated","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "status_code": 400}

@app.route('/api/cornwell/generate_test_result',methods=['POST'])
def result():
    try:
        # request_data = request.get_json()
        request_data={
                        "card": {
                            "ri": "12A3",
                            "sig": "LTKJEY1T",
                            "sn": "C120430201F3130112",
                            "v": 1
                        },
                        "userAnswers": {
                            "scentFeedback": "dill",
                            "survey": {
                            "q1": "no",
                            "q2": "yes",
                            "q3": "no",
                            "q4": "no",
                            "q5": "yes",
                            "q6": 10,
                            "q7": "no"
                            }
                        },
                        "userName": "Test User",
                        "email_id":"rahul@gmail.com"
                        }

        serial_number=request_data['card']['sn']
        user_name = request_data['userName']
        user_answers=request_data['userAnswers']
        email_id=request_data['email_id']
        user_answers=json.dumps(user_answers)
        data=request_data
        # url="https://backend.fadean.com/ticket/api/result-request?sn="+serial_number+"&ln=en&av=0.1"
        # final_response=requests.post(url = url, data = data).json()
        final_response={
            "awpManifest": None,
            "awpPassJson": None,
            "awpSignature": None,
            "codeMessage": None,
            "correctScent": "lavender",
            "status": "fail"
        }
        covid_results=final_response['status']
        exist_record=db.table('user_login').where('email_id',email_id).first()
        if exist_record!=None:
            updated=db.table('test_details').update({"serial_number",serial_number}).update({"covid_results":covid_results}).update({"survey_answers":user_answers}).where("email_id",email_id)
            if updated==1:
                return { "data": "Updated", "status_code": 200,"covid_result":covid_results}
        else:
            insertion=db.table('test_details').insert({"patient_name":user_name,"serial_number":serial_number,"time_of_test":d2,"survey_answers":user_answers,"covid_results":covid_results,"email_id":email_id})
            if insertion==1:
                return { "data": "Inserted", "status_code": 200,"covid_result":covid_results}
            else:
                return {"data":"Not inserted","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "serial code is enter already used", "status_code": 400}
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5100)