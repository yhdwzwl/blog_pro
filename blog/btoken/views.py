from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
import json
from user.models import UserProfile
import hashlib
import time
import jwt

def tokens(request):
    """
    创建token == 登录
    :param request:
    :return:
    """

    if not request.method == 'POST':
        result = {'code':101,'error':'p use post'}
        return JsonResponse(result)
    #获取前端传来的数据、生成token
    #获取校验密码 生成token

    #获取前端提交的数据
    json_str = request.body
    if not json_str:
        result = {'code':102,'error':'give me json'}
        return JsonResponse(result)
    json_obj = json.loads(json_str)

    username = json_obj.get('username')
    password = json_obj.get('password')
    if not username:
        result = {'code':103,'error':'give me username'}
        return JsonResponse(result)
    if not password:
        result = {'code':104,'error':'give me username'}
        return JsonResponse(result)

    #与数据库校验数据
    user = UserProfile.objects.filter(username = username)
    if not user:
        result = {'code':105,'error':'username or password is w!'}
        return JsonResponse(result)

    user = user[0]
    m = hashlib.md5()
    m.update(password.encode())
    if m.hexdigest() != user.password:
        result = {'code':106,'error':'username or password is w!'}
        return  JsonResponse(result)


    #make token
    token = make_token(username)
    result = {'code':200,'username':username,'data':{'token':token.decode()}}
    return JsonResponse(result)

    # make token
def make_token(username, expire=3600 * 24):
    key = '1234567'
    now = time.time()
    payload = {'username': username, 'exp': int(now + expire)}
    return jwt.encode(payload, key, algorithm='HS256')
