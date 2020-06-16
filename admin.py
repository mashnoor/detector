
from flask import Flask, request
import os
import json
from face_recognition import FaceRecognition
import base64
from gevent.pywsgi import WSGIServer # Imports the WSGIServer
from gevent import monkey; monkey.patch_all() 
import uuid
import socket
from flask_cors import CORS, cross_origin
import logging
import requests
import pymysql
from datetime import datetime
import subprocess


app = Flask(__name__)
logging.basicConfig(filename='face_rec.log', level=logging.DEBUG, format='%(asctime)s : %(message)s')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
fr = FaceRecognition()


def getModelUrl(company_name):
    return "/var/www/attendancekeeper_" + company_name + "/detector/knn.pkl"

def getUrl(company_name):

    return "/var/www/attendancekeeper_" + company_name + "/public/assets/login_faces/"

def get_employee_id(company_name, reference):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='Mashnoor11',
                                 db='timesheet_' + company_name,
                                 charset='utf8mb4',
                                 #unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            #sql = "SELECT image_name, users.idno FROM tbl_employee_faces INNER JOIN users ON tbl_employee_faces.reference=users.reference"
            sql = "SELECT idno FROM tbl_company_data WHERE reference=" + reference
            cursor.execute(sql)
            result = cursor.fetchone()



    finally:
        connection.close()

    return result['idno']


def update_last_seen(company_name, reference):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='Mashnoor11',
                                 db='timesheet_' + company_name,
                                 charset='utf8mb4',
                                 #unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            #sql = "SELECT image_name, users.idno FROM tbl_employee_faces INNER JOIN users ON tbl_employee_faces.reference=users.reference"
            sql = "SELECT id FROM webcam_data WHERE reference=" + reference
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                add_webcam_data = ("INSERT INTO webcam_data (reference, last_seen) VALUES ('" + reference + "','" + dt_string + "')")
                
                cursor.execute(add_webcam_data)
                connection.commit()
            else:
                sql_update_query = "UPDATE webcam_data SET last_seen = '" + dt_string + "' WHERE reference = '" + reference + "'"
                cursor.execute(sql_update_query)
                connection.commit()




    finally:
        connection.close()

   


def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.


@app.route('/face_rec/<company_name>', methods=['POST'])
def face_recognition(company_name):
    fr.load(getModelUrl(company_name))
    
    image_data = str(request.form.get('image_data')).replace("data:image/jpeg;base64,", "")
    # image_data = request.form.get('image_data')
    image_name = my_random_string() + ".jpg"
    imgdata = base64.b64decode(image_data)
    with open(getUrl(company_name) + image_name, 'wb') as f:
        f.write(imgdata)

    result = fr.predict(getUrl(company_name) + image_name)
    app.logger.info("Company Name: " + company_name)
    app.logger.info("ID: " + str(result['predictions'][0]['person']))
    app.logger.info("Confidence: " + str(result['predictions'][0]['confidence']))
    print("ID: " + str(result['predictions'][0]['person']))
    print("Confidence: " + str(result['predictions'][0]['confidence']) + "\n")
    return str(get_employee_id(company_name, result['predictions'][0]['person']))


attendance_url = "https://attendancekeeper.net/westacebd/api/webcam_attendance"
@app.route('/face_rec_multiple/<company_name>', methods=['POST'])
def face_recognition_multiple(company_name):
    fr.load(getModelUrl(company_name))
    
    image_data = str(request.form.get('image_data')).replace("data:image/jpeg;base64,", "")
    typ = str(request.form.get('type'))
    # image_data = request.form.get('image_data')
    image_name = my_random_string() + ".jpg"
    imgdata = base64.b64decode(image_data)
    with open(getUrl(company_name) + image_name, 'wb') as f:
        f.write(imgdata)

    result = fr.predict(getUrl(company_name) + image_name)
    res = []
    for i in range(len(result['predictions'])):
        ref = str(result['predictions'][i]['person'])
        subprocess.call("python3 add_attendance.py " + typ + " " + ref, shell=True)
        #requests.post(attendance_url, data=data)

        update_last_seen(company_name, result['predictions'][i]['person'])
        res.append(get_employee_id(company_name, result['predictions'][i]['person']))

    return str(res)

   
@app.route('/')
def hello():
    return "blas"
    return requests.get("http://localhost:5004/get_id").text

# print(get_images_with_tag())
if __name__ == '__main__':
    LISTEN = ('0.0.0.0',5009)

    http_server = WSGIServer( LISTEN, app,keyfile='/etc/letsencrypt/live/attendancekeeper.net/privkey.pem', certfile='/etc/letsencrypt/live/attendancekeeper.net/fullchain.pem' )
    http_server.serve_forever()

    