from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

AIRTABLE_URL = f'https://api.airtable.com/v0/{BASEID}/{TABLEID}'
AIRTABLE_LOGIN = f'https://api.airtable.com/v0/{BASEID}/{TABLELOGIN}'
AIRTABLE_URL_CREATOR = f'https://api.airtable.com/v0/{BASEID}/{TABLE_CREATOR_ID}'
STATUS = ''
CREATOR_URL = ''

@app.route('/authenticate', methods=['GET'])
def authenticateLogin():
    # Fetch data from airtable
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        'Content-type': "application/json"
    }
    response = requests.get(AIRTABLE_LOGIN, headers=headers)

    return response.json()

@app.route('/sendBrandData', methods=['OPTIONS', 'POST'])
def send_brand_data():
    if request.method == 'OPTIONS':
        # Handle the OPTIONS request
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    # Handle the POST request
    data = request.json
    # Do something with the data
    verify_BrandData(data)
    return jsonify({'received brand data': data})

@app.route('/sendCreatorData', methods=['OPTIONS', 'POST'])
def send_creator_data():
    if request.method == 'OPTIONS':
    # Handle the OPTIONS request
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    # Handle the POST request
    data = request.json
    # Do something with the data
    verify_CreatorData(data)
    return jsonify({'received creator data': data})

@app.route('/getCreatorVerification', methods=['GET'])
def getCreatorVerification():
    creatorlink = request.args.get('creatorURL')
    brand = request.args.get('brand')
    creator_request_exists = False
    
    # Fetch data from airtable
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        'Content-type': "application/json"
    }
    response = requests.get(AIRTABLE_URL_CREATOR, headers=headers)
    if response.status_code == 200:
        resp = response.json()
        
        # Determine if creator request exists in table
        for x in resp['records']:
            if(x['fields']['Creator URL'] == creatorlink and x['fields']['Brand'] == brand):
                creator_request_exists = True
    
    return {'creatorURL': creatorlink,"brand": brand,'status': creator_request_exists}
    
def createAirtableRecord(url,payload):
    print("Sending POST request with payload: ", payload)
    # Fetch data from airtable
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        'Content-type': "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response)
    if response.status_code == 200:
        return response.json()

def patchAirtableRecord(url, payload):
    print("Sending PATCH request with payload: ", payload)
    # Fetch data from airtable
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        'Content-type': "application/json"
    }
    response = requests.patch(url, headers=headers, json=payload)
    print(response)
    if response.status_code == 200:
        return response.json()

def verify_BrandData(data):
    brand_exists = False
    brand_update = False
    brand = data['fields']['Brand']
    ugcBudget = data['fields']['Max Budget for UGC']
    adBudget = data['fields']['Max Budget for Ad Access']
    igBudget = data['fields']['Max Budget for (1) IG Reel']
    url = data['fields']['Creator URL']
    recordID = ''
    
    # Fetch data from airtable
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        'Content-type': "application/json"
    }
    response = requests.get(AIRTABLE_URL_CREATOR, headers=headers)
    
    if response.status_code == 200:
        resp = response.json()
        
        # Determine if brand exists in table
        for x in resp['records']:
            if(x['fields']['Brand'] == brand and x['fields']['Creator URL'] == url):
                brand_exists = True
                recordID = x['id']
                
                if("Max Budget for UGC" in x['fields'] and "Max Budget for Ad Access" in x['fields'] and "Max Budget for (1) IG Reel" in x['fields']):
                    if(x['fields']["Max Budget for UGC"] != ugcBudget.replace("$","") or x['fields']["Max Budget for Ad Access"] != adBudget.replace("$","") or x['fields']["Max Budget for (1) IG Reel"] != igBudget.replace("$","")):
                        brand_update = True
                else:
                    brand_update = True

    # if data exists and needs updating, put record
    if(brand_exists and brand_update):
        print(brand_exists, brand_update, "1", recordID)
        patchAirtableRecord(f'{AIRTABLE_URL_CREATOR}/{recordID}', data);
        
    # # if data does not exist, post record in airtable
    # elif(brand_exists == False):
    #     print(brand_exists, brand_update, "2", recordID)
    #     createAirtableRecord(AIRTABLE_URL_CREATOR, data);

def verify_CreatorData(data):
    creator_request_exists = False
    recordID = ''
    status = False
    brand = data['fields']['Brand']
    creatorURL = data['fields']['Creator URL']
    global STATUS 
    global CREATOR_URL
    CREATOR_URL = creatorURL
    
    # Fetch data from airtable
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        'Content-type': "application/json"
    }
    response = requests.get(AIRTABLE_URL_CREATOR, headers=headers)
    
    if response.status_code == 200:
        resp = response.json()

        # Determine if creator request exists in table
        for x in resp['records']:
            if(x['fields']['Creator URL'] == creatorURL and x['fields']['Brand'] == brand):
                creator_request_exists = True
                recordID = x['id']

        # if data exists, update record
        if(creator_request_exists):
            STATUS = status
        # if data does not exist, create record in airtable
        else:
            status = True
            STATUS = status
            createAirtableRecord(AIRTABLE_URL_CREATOR, data)

if __name__ == '__main__':
    app.run()
    
