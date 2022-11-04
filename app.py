from flask import Flask, render_template, request, g
from flask_cors import CORS
from sqlalchemy import create_engine
from ldap import *
from employee import *
from masking import *
from apis import *

 

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_pyfile('config.py')

import pymysql
pymysql.install_as_MySQLdb()


# elsastic APM agent 셋팅
#from elasticapm.contrib.flask import ElasticAPM


# [url 설정]

if getConfig() in ['prd', 'dev']:

    app.config['ELASTIC_APM'] = {
        "SERVICE_NAME": os.environ.get('POD_NAMESPACE', 'local') + "__" + os.environ.get('PROJECT_NAME', 'project'),
#        "SECRET_TOKEN": "e77061bb3aaedae5ae8dd0ca193eb662513aedde",
#        "SERVER_URL": "http://apm-server-apm-server.appdu-monitoring:8200",
        "ENVIRONMENT": "production",
        "TRANSACTIONS_IGNORE_PATTERNS": ['/health_check']
    }
#    apm = ElasticAPM(app)


database = create_engine(app.config['DB_URL'], encoding = 'utf-8')
app.database = database


@app.route("/")
def template_test():
    return render_template(
                'index.html',                      #렌더링 html 파일명
                title="Flask Template Test",       #title 텍스트 바인딩1
                my_str="Hello Flask!",             #my_str 텍스트 바인딩2
                my_list=[x + 1 for x in range(10)] #30개 리스트 선언(1~30)
            )


# 로그인 시도
@app.route('/signin', methods = ['POST'])
def signin():
    if request.method == 'POST':
        # json.dumps(dict): dict('') -> json("")
        # json.loads(json): json("") -> dict('')
        # request.get_json(): dict object
        response = signinwithotp(request.get_json())
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)



# OTP 확인 및 토큰 발행
@app.route('/verify', methods = ['POST'])
def verify():
    if request.method == 'POST':
        response = verifywithotp(request.get_json())
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405) 

# 로그아웃
@app.route('/signout', methods = ['POST'])
def signout():
    if request.method == 'POST':
        response = dosignout(request.headers, app)
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)

# CRUD - Read
@app.route('/employee/getEmployees', methods = ['GET', 'POST'])
def getEmployees():
    if request.method in ['GET', 'POST']:
        response = userlist(request.headers, app)
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)

# CRUD - Create
@app.route('/employee/addNewEmployee', methods = ['POST'])
def addNewEmployee():
    if request.method == 'POST':
        response = add_user(request.headers, request.get_json(), app)
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)

# CRUD - Update
@app.route('/employee/updateEmployeeInfo', methods = ['POST'])
def updateEmployeeInfo():
    if request.method == 'POST':
        response = update_user(request.headers, request.get_json(), app)
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)

# CRUD - Delete
@app.route('/employee/deleteEmployee', methods = ['POST'])
def deleteEmployee():
    if request.method == 'POST':
        response = delete_user(request.headers, request.get_json(), app)
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)
      
# health_check
@app.route('/health_check', methods = ['GET'])
def health_check():
    if request.method == 'GET':
        return json.dumps({'returnCode': 'OK'})
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


if __name__ == '__main__':

    app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0',port=8000,debug=True)
