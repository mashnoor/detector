import requests
import sys

attendance_url = "https://attendancekeeper.net/westacebd/api/webcam_attendance"

def add(typ, ref):
    data = {"type":typ, "reference":ref}
    requests.post(attendance_url, data=data)

if(len(sys.argv)>1):

    add(sys.argv[1], sys.argv[2])
