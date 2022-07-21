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

@app.route('/api/cornwell/back_end',methods=['POST'])
def backend():
    request_data = request.get_json()
    serial_number=request_data['sn']
    request_data1=json.dumps(request_data)
    headers = {
            'Content-Type': 'application/json'
            }
    url="https://backend.fadean.com/ticket/api/list-request?sn="+serial_number+"&ln=en&av=0.1"        
    final_response=requests.post(url = url, headers=headers, data = request_data1)
    final_response=json.loads(final_response.text)
    print(final_response)
    return final_response

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
                print("here it is",exist_insight)
                if exist_insight!=None:
                    return { "data": "Verified", "status_code": 200,"result":exist_insight}
                else:
                    return { "data": "Verified", "status_code": 200,"result":exist_insight}
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
        request_data = request.get_json()
        serial_number=request_data['card']['sn']
        user_name = request_data['userName']
        user_answers=request_data['userAnswers']
        email_id=str(request_data['email_id'])
        user_answers=json.dumps(user_answers)
        print(type(user_answers),"here-----------------",user_answers)
        request_data=json.dumps(request_data)
        print(type(request_data),"here after request----------------",request_data)
        headers = {
            'Content-Type': 'application/json'
            }
        data=request_data
        url="https://backend.fadean.com/ticket/api/result-request?sn="+serial_number+"&ln=en&av=0.1"        
        try:
            final_response=requests.post(url = url, headers=headers, data = data)
            final_response=json.loads(final_response.text)
            print(final_response)
        except Exception as e:
            print("error after response",str(e))
            return { "data": "serial code is already used on server", "status_code": 400}
        covid_results=final_response['status']
        exist_record=db.table('user_login').where('email_id',email_id).first()
        print(exist_record)
        if exist_record!=None:
            updated=db.table('test_details').where("email_id",email_id).update({"serial_number":serial_number,"time_of_test":d2,"survey_answers":user_answers})
            if updated==1:
                response={ "data": "Updated", "status_code": 200,"covid_results":covid_results,"email_id":email_id,"patient_name":user_name,"time_of_test":d2}
                print(type(response))
                return response
        else:
            print("here")
            insertion=db.table('test_details').insert({"patient_name":user_name,"serial_number":serial_number,"time_of_test":d2,"survey_answers":user_answers,"covid_results":covid_results,"email_id":str(email_id)})
            if insertion==1:
                response={ "data": "Inserted", "status_code": 200,"covid_results":covid_results,"email_id":str(email_id),"patient_name":user_name,"time_of_test":d2}
                print(type(response))
                return response
            else:
                response={"data":"Not inserted","status_code": 400}
                print(type(response))
                return response
    except Exception as e:        
        print("error is---",str(e))
        response={ "data": "serial code is enter already used", "status_code": 400}
        return response
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5100)