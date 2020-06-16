#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys
from flask import Flask, request, Response
import time
import subprocess
from shelljob import proc


app = Flask(__name__)

@app.route('/train/<company_name>')
def index(company_name):
    g = proc.Group()
    p = g.run( [ "python3", "/var/www/attendancekeeper/detector/trainer.py" , company_name ] )

    def read_process():
        while g.is_pending():
            lines = g.readlines()
            for proc, line in lines:
                yield line

    return Response( read_process(), mimetype= 'text/plain' )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)


			
