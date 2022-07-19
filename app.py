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

app = Flask(__name__)
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
        # get date range
        password = request_data['password']
        user_name_exist=db.table('user_login').where('user_name',user_name).first()
        if user_name_exist!=None:
            dict_pass=pd.DataFrame(list(db.table('user_login').select('user_name','password').where('user_name',user_name).get())).to_dict()
            dict_pass=dict_pass['password'][0]
            if dict_pass==password:
                exist_insight = db.table('test_details').where('patient_name',user_name).first()
                if exist_insight!=None:
                    return { "data": "Verified", "status_code": 200,"result":exist_insight}
                else:
                    return { "data": "Verified", "status_code": 200}
            else:
                return {"data":"Password is not correct","status_code": 400}
        else:
            return {"data":"User not found","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "success": False}

@app.route('/api/cornwell/user_registration',methods=['POST'])
def register():
    try:
        request_data = request.get_json()
        # Get Account Id
        serial_number=request_data['serial_number']
        user_name = request_data['user_name']
        # get date range
        password = request_data['password']
        exist_record = db.table('user_login').where('serial_number',serial_number).first()
        if exist_record!=None:
            return { "data": "user with this serial number already exist", "status_code": 200}
        else:
            insertion=db.table('user_login').insert({"user_name":user_name,"password":password,"time":d2,"serial_number":serial_number})
            if insertion==1:
                return { "data": "Updated", "status_code": 200}
            else:
                return {"data":"Not_Updated","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "success": False}

@app.route('/api/cornwell/generate_test_result',methods=['POST'])
def result():
    try:
        # request_data = request.get_json()
        request_data={
                        "card": {
                            "ri": "12A3",
                            "sig": "LTKJEY1T",
                            "sn": "C12043001F340",
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
                        "userName": "Test User"
                        }

        serial_number=request_data['card']['sn']
        user_name = request_data['userName']
        user_answers=request_data['userAnswers']
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
        insertion=db.table('test_details').insert({"patient_name":user_name,"serial_number":serial_number,"time_of_test":d2,"survey_answers":user_answers,"covid_results":covid_results})
        if insertion==1:
            return { "data": "Updated", "status_code": 200,"result":covid_results}
        else:
            return {"data":"Not_Updated","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "success": False}
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5100)