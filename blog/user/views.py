from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
import json
from .models import  *
import hashlib
from tools.login_check import login_check

from btoken.views import make_token

@login_check('PUT')
def users(request,username = None):
    if request.method == 'GET':
        #获取用户数据
        if username:
            #拿指定用户
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                user = None
            if not user:
                result = {'code':208,'error':'no user'}
                return JsonResponse(result)
            #检查是否有查询字符串
            if request.GET.keys():
                #查询指定字段
                data = {}
                for k in request.GET.keys():
                    if hasattr(user,k):
                        v = getattr(user,k)
                        if k == 'avatar':
                            data[k] = str(v)
                        else:
                            data[k] = v
                result = {'code':200,'username':username,'data':data}
                return JsonResponse(result)

            else:
                #全量查询（ pwd emi不给）
                result = {'code':200,'username':username,'data':{'info':user.info,'sign':user.sign,'avatar':str(user.avatar),'nickname':user.nickname}}
                return JsonResponse(result)
            return JsonResponse({'code':200,'error':'wolaila GET %s'%(username)})
        else:
            return JsonResponse({'code':200,'error':'wolaila GET'})


    elif request.method == 'POST':
        #创建用户
        #前端注册页面 5000register
        #校验前端提交的基础数据
        json_str = request.body
        if not json_str:
            result = {'code':201,'error':'give me data'}
            return JsonResponse(result)
        #load回来是个字典，所以要 把字典中的字段取出来
        json_obj = json.loads(json_str)

        username = json_obj.get('username')
        if not username:
            result = {'code':200,'error':'give me username'}
            return JsonResponse(result)

        email = json_obj.get('email')
        if not email:
            result = {'code':203,'error':'give me email'}
            return JsonResponse(result)

        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not  password_1 or not password_2:
            result = {'code':204,'error':'give me pwd'}
            return JsonResponse(result)

        if password_1 != password_2:
            result = {'code':500,'error':'not same pwd'}
            return JsonResponse(result)

        #一定要优先查询当前用户名是否存在
        #用get查询一定要try一下
        old_user = UserProfile.objects.filter(username = username)
        if old_user:
            result = {'code':206,'error':'is existed'}
            return JsonResponse(result)

        #密码处理 md5 hash
        m = hashlib.md5()
        m.update(password_1.encode())

        #charfield 尽量避免使用null=true 都完成了之后再做数据的插入
        sign = info = ''
        try:
            UserProfile.objects.create(
                username = username,
                nickname = username,
                password = m.hexdigest(),
                sign = sign,
                info = info,
                email = email

            )
        except Exception as e:
            result = {'code':207,'error':'is busy'}
            return JsonResponse(result)

        #make token  用户注册成功 生成token 返给前端
        token = make_token(username)

        #正常返回前端
        result = {'code':200,'username':username,'data':{'token':token.decode()}}
        return JsonResponse(result)

    elif request.method == 'PUT':
        #更新数据
        #此头可获取前端传来的token
        #meta可拿去http协议原生头，meta也是类字典对象，可使用字典相关方法 ，有可能被django重命名
        request.META.get('HTTP_AUTHORIZATION')

        user = request.user
        print(111111111)
        print(user)
        json_str = request.body
        if not json_str:
            result = {'code': 209, 'error': 'p json'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)

        if 'sign' not in json_obj:
            result = {'code': 210, 'error': 'no sign'}
            return JsonResponse(result)
        if 'info' not in json_obj:
            result = {'code': 211, 'error': 'no info'}
            return JsonResponse(result)

        sign = json_obj.get('sign')
        info = json_obj.get('info')

        request.user.sign = sign
        request.user.info = info
        request.user.save()
        result = {'code':200,'username':request.user.username}
        return JsonResponse(result)
    else:
        raise
    return JsonResponse({'code':200})


@login_check('POST')
def user_avatar(request,username):
    """
    上传用户头像
    :param request:
    :param username:
    :return:
    """

    if request.method != 'POST':
        result = {'code': 212,'error': 'need post!'}
        return JsonResponse(result)
    avatar = request.FILES.get('avatar')

    if not avatar:
        result = {'code': 213, 'error': 'i need avatar'}
        return JsonResponse(result)
    #TODO 判断url中的username是否跟token中的username一致，若不一致，返回error
    request.user.avatar = avatar
    request.user.save()
    result = {'code': 200, 'username':request.user.username}
    return JsonResponse(result)


    return JsonResponse({'code': 200, 'error': 'avatar'})
