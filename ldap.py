import requests, json ,io

from urllib.parse import urlparse
from jwtTokenUtil import *
#from RSACipher import *
from flask import g
from commonUtil import *
import os

 

def getConfig():
    flag = ""
    try:
        f = open('/etc/config/env.properties', 'r')
        devprdflag = f.read()
        flag = devprdflag.split('=')[1]
    except FileNotFoundError:
        print("File does not exist")
    finally:
        if flag != "":
            f.close()
        return flag
 

# LDAP 로그인 시도

def signinwithotp(req):
    '''
    {
        "username": "string",
        "password": "string"
    }
    '''

    url = mediatorUrl + "/apis/signin"
    headers = {'Content-Type': 'application/json', 'pod_namespace' : os.environ.get('POD_NAMESPACE', 'local') }
  
    username = req['username'] # LDAP 사용자 이름
    if len(username) <= 1:
        ret = {"returnCode": "NG"}
        ret.update({"message": "username is not valid."})
        ret.update({"data": ""})
        return ret 
       
    str_json_data = json.dumps(req) # json(str)

   
    try:
        # LDAP API 호출
        res = requests.post(urlparse(url).geturl(), headers=headers, data=str_json_data)
        json_data = json.loads(res.text) # dict

        if res.status_code in [200, 201]:
            ret = {"returnCode": "OK"}
            ret.update({"message": "OTP 발송 (3분 안에 OTP 인증을 시도하세요)"})
            # otp 발송

        elif res.status_code == 404:
            ret = {"returnCode": "NG"}
            ret.update({"message": "Page Not Found"})
        else:
            ret = {"returnCode": "NG"}
            ret.update({"message": json_data})
        return ret
    except Exception as e:
        ret = {'returnCode': 'NG', 'message': str(e)}
        return ret
    return ""



# OTP 확인 후 토큰 발행
def verifywithotp(req):
    '''
    {
        "authorization": Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI4ODg4ODg4OCIsImlzcyI6Ijg4ODg4ODg4IiwiaWF0IjoxNjE4ODIxNzU0LCJhdXRob3JpdGllcyI6WyJVU0VSIl0sImV4cCI6MTYxODkwODE1NH0.wVuAEIG9y13246b2N4mEgpxxrwFKD92052sbIdhPZSI
    }
    '''

    url = mediatorUrl + "/apis/verify"
    headers = {'Content-Type': 'application/json', 'pod_namespace' : os.environ.get('POD_NAMESPACE', 'local') }
    username = req['username'] # LDAP 사용자 이름
    if len(username) <= 1:
        ret = {"returnCode": "NG"}
        ret.update({"message": "username is not valid."})
        ret.update({"data": ""})
        return ret

    str_json_data = json.dumps(req) # json(str)
    try:
        # LDAP API 호출
        res = requests.post(urlparse(url).geturl(), headers=headers, data=str_json_data)
        json_data = json.loads(res.text)

        if res.status_code in [200, 201]:          
            # token 발행
            '''
            authorities = json_data['data']['authorities']
            auth_list = []
            for auth in authorities:
                auth_list.append(auth["authority"])
            '''
            token = generateToken(json_data['data'])
            print("token:", token)
            ret = {"returnCode": "OK"}
            ret.update({"message": "OTP 확인완료"})            
            ret.update({"data": token})
        elif res.status_code == 404:
            ret = {"returnCode": "NG"}
            ret.update({"message": "Page Not Found"})
        else:
            ret = {"returnCode": "NG"}
            ret.update({"message": json_data})
        return ret
    except Exception as e:
        ret = {'returnCode': 'NG', 'message': str(e)}
        return ret
    return ""

# 로그아웃할 때 Logout에 토큰 추가
def dosignout(hdr, app):
    try:
        # 토큰 -> logout 테이블에 추가
        token = hdr['Authorization'].split(" ")[1]
        username = getUsernameFromToken(token)
        if (username == "expired"):
            response = app.response_class(
                response = json.dumps({'returnCode': 'OK', 'message': 'logout is success.', 'data': ''}),
                status = 200,
                mimetype = 'application/json'
            )
            return response
        sql = '''
            INSERT INTO logout
            (id, token)
            VALUES
            (%s, %s)
            ON DUPLICATE KEY
            UPDATE token = %s;
            '''
        app.database.execute(sql, (username, token, token))
        response = app.response_class(
            response = json.dumps({'returnCode': 'OK', 'message': 'logout is success.', 'data': ''}),
            status = 200,
            mimetype = 'application/json'
        )
        return response
    except Exception as e:
        response = app.response_class(
            response = json.dumps({'returnCode': 'NG', 'message': str(e)}),
            status = 200,
            mimetype = 'application/json'
        )
        return response
    return ""
