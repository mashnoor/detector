
import pymysql
from sklearn import neighbors
import math
from face_recognition import FaceRecognition

import pandas as pd 
import sys


def getUrl(company_name):
    return "/var/www/attendancekeeper_" + company_name + "/public/assets/faces/"

def get_images_with_tag(company_name):
    url = getUrl(company_name)
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
            sql = "SELECT image_name, reference FROM tbl_employee_faces"
            cursor.execute(sql)
            results = cursor.fetchall()
            result_list = []
            for result in results:
                result_list.append((str(result['reference']), url + result['image_name']))


    finally:
        connection.close()

    return result_list


def train_dataframe(company_name):
    
    print("Loading Started...")
    known_faces = get_images_with_tag(company_name)
    all_ids = []
    all_locations = []
    fr = FaceRecognition()
    try:
        for name, known_file in known_faces:
           
            all_ids.append(name)
            all_locations.append(known_file)
            print("Loaded: " + name)
            
    except:
        print("Error for " + known_file + " tag: " + name)



    df = pd.DataFrame(list(zip(all_ids, all_locations)), columns =['person', 'path']) 
    print("Fitting started")
    fr.fit_from_dataframe(df)
    fr.save('/var/www/attendancekeeper_' + company_name + '/detector/knn.pkl')
    print("Fitting done")

if(len(sys.argv)>1):

    train_dataframe(sys.argv[1])