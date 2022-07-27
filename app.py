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
        response_email_id=request_data['email_id']
        response_pass = request_data['password']
        admin_detail=db.table('employee_detail').select("email_id","password","group_id").where('email_id',response_email_id).first()
        user_detail=db.table('employees_details').select("email_id","password","employee_id","name").where('email_id',response_email_id).first()
        if admin_detail!=None:
            try:
                admin_email_id=admin_detail['email_id']
                group_id=admin_detail['group_id']
                admin_password=admin_detail['password']
                if (response_pass==admin_password) and (response_email_id==admin_email_id):
                    group_id_exist=db.table('test_details').where("group_id",group_id).first()
                    print("here exist")
                    if group_id_exist!=None:
                        df=pd.DataFrame(list(db.table('test_details').where("group_id",group_id).get()))
                        results=df[['patient_name','time_of_test','covid_results']].to_dict(orient='index')
                        response={"data":"Covid results for admin for all employees","status_code":200,"group_id":group_id,"test_results":results}
                        return response
                    else:
                        return {"data":"Please ask your employees to take a corowell test","status_code":200,"group_id":group_id,"test_results":{}}
                else:
                    response={"data":"email_id or password does not match for admin","status_code":400}
                    return response
            except Exception as e:
                print("Error in admind= details login--------------------")
                response={"data":"Error for admin login","status_code":400}
                return response
        elif user_detail!=None:
            print("this is a user---------------------")
            try:
                user_email_id=user_detail['email_id']
                user_password=user_detail['password']
                user_id=user_detail['employee_id']
                user_name=user_detail['name']
                if (response_pass==user_password) and (response_email_id==user_email_id):
                    test_detail=db.table('test_details').where("email_id",user_email_id).first()
                    if test_detail!=None:
                        df=pd.DataFrame(list(db.table('test_details').where("email_id",user_email_id).get()))
                        results=df[['patient_name','time_of_test','covid_results']].tail(5).to_dict(orient='index')
                        response={"data":"Covid result for the patient","status_code":200,"user_name":user_name,"userid":user_id,"test_results":results}
                        return response
                    else:
                        return {"data":"Please take a corowell test","status_code":200,"user_name":user_name,"userid":user_id,"test_results":{}}
                else:
                    response={"data":"email_id or password does not match for user","status_code":400}
                    return response
            except Exception as e:
                print("Error in user details login--------------------")
                response={"data":"Error for user login","status_code":400}
                return response
        else:
            return {"data":"User not found","status_code": 400}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "status_code": 400}

@app.route('/api/cornwell/user_registration',methods=['POST'])
def register():
    try:
        request_data = request.get_json()
        email_id=request_data['email_id']
        password = request_data['password']
        exist_record=db.table('user_login').where('email_id',email_id).first()
        group_admin=request_data['group_admin']
        name=request_data['name']
        age=request_data['age']
        insurance_comp=request_data['insurance_comp']
        insurance_number=request_data['insurance_number']
        address=request_data['address']
        insurance_flag=request_data['insurance_flag']
        if group_admin=="yes": #if it is a group admin
            name_org=request_data['name_org']
            affilations=request_data['affiliations']
            group_id=generate_unique_id()
            print("here---------",group_id)
            exist_record=db.table('employee_detail').where('group_id',group_id).first()
            exist_email=db.table('employee_detail').where('email_id',email_id).first()
            if exist_email!=None:
                return {"data":"Admin id already exist please login with your email","status_code":200}
            if exist_record!=None:
                group_id=generate_unique_id()
                print("here ---------",group_id)
            db.table('employee_detail').insert(({"company_name":name_org,"address":address,"insurance_flag":insurance_flag,"email_id":email_id,"insurance_number":insurance_number,"insurance_company":insurance_comp,"group_id":group_id,"affilations":affilations,"password":password}))
            return { "data": "Updated for Admin", "status_code": 200,"group_id":group_id}
        else: #if it is a user login
            age=request_data['age']
            ethinicity=request_data['ethinicity']
            gender=request_data['gender']
            smoking_status=request_data['smoking_status']
            group_id=request_data['group_id']
            disease_details=request_data['disease_details']
            exist_record=db.table('employees_details').where('email_id',email_id).first()
            if exist_record!=None:
                print({"data":"user with email id already exist","status_code":400})
            else:
                db.table('employees_details').insert(({"age":age,"address":address,"insurance_flag":insurance_flag,"email_id":email_id,"insurance_number":insurance_number,"insurance_company":insurance_comp,"group_id":group_id,"gender":gender,"smoking_status":smoking_status,"name":name,"ethinicity":ethinicity,"disease_details":json.dumps(disease_details),"password":password}))        
                user_id=list(pd.DataFrame(list(db.table('employees_details').get())).tail(1)['employee_id'])[0]+1
                import requests
                url="https://backend.fadean.com/ticket/api/user-registration-niander"
                payload={"age":age,"gender":gender,"ethnicity":ethinicity,"smoking":smoking_status,"insuranceNr":insurance_number,"groupNr":group_id,"lung_disease":disease_details['lungs'],"heart_disease":disease_details['heart'],"liver_disease":disease_details['liver'],"diabetes":disease_details['diabetes'],"autoimmune_disorder":disease_details['autoimmune'],"cancer":disease_details['cancer'],"kidney_disease":disease_details['kidney'],"neurological_disease":disease_details['neurolo'],"address":address,"userid":user_id}
                res=requests.post(url, data = payload)
                return {"data":"Sent request to niander database","status_code":200,"user_name":name,"userid":user_id}
    except Exception as e:        
        print("error is---",str(e))
        return { "data": "Error", "status_code": 400}

@app.route('/api/cornwell/generate_test_result',methods=['POST'])
def result():
    try:
        request_data = request.get_json()
        serial_number=request_data['card']['sn']
        user_name = request_data['userName']
        # user_name=json.loads(user_name)
        user_answers=request_data['userAnswers']
        email_id=str(request_data['email_id'])
        # email_id=json.loads(email_id)
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
        try:
            insertion=db.table('test_details').insert({"patient_name":json.loads(user_name),"serial_number":serial_number,"time_of_test":d2,"survey_answers":user_answers,"covid_results":covid_results,"email_id":json.loads(email_id)})
            if insertion==1:
                response={ "data": "Inserted", "status_code": 200,"covid_results":covid_results,"email_id":json.loads(email_id),"patient_name":json.loads(user_name),"time_of_test":d2}
                return response
        except Exception as e:
            print("error is ",str(e))
            response={"data":"Not inserted","status_code": 400}
            print(type(response))
            return response
    except Exception as e:        
        print("error is---",str(e))
        response={ "data": "serial code is enter already used", "status_code": 400}
        return response

def generate_unique_id():
    import random
    n = random.random()
    n=n*100
    n=round(n) 
    import uuid
    unique_id=str(uuid.uuid4())
    unique_id=unique_id.split('-')[0][:4]+str(n)+unique_id.split('-')[2]
    return unique_id
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5100)