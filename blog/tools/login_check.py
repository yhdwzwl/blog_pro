from django.http import JsonResponse
import jwt
from user.models import UserProfile


KEY = '1234567'
def login_check(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            #通过request检查token
            #校验不通过，return J
            #user 查询出来
            token = request.META.get('HTTP_AUTHORIZATION')
            if request.method not in methods:
                return func(request, *args, **kwargs)
            if not token:
                result = {'code': 107, 'error': 'p login'}
                return JsonResponse(result)
            try:
                res = jwt.decode(token, KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                #token过期了
                result = {'code': 108, 'error': 'login'}
                return JsonResponse(result)
            except Exception as e:
                result = {'code': 109, 'error': 'please login'}
                return JsonResponse(result)

            username = res['username']
            try:
                user = UserProfile.objects.get(username=username)
            except:
                user = None
            if not user:
                result = {'code': 110, 'error': 'no user'}
                return JsonResponse(result)

            #将查询成功的user赋值给request
            request.user = user


            return func(request, *args, **kwargs)
        return wrapper
    return _login_check



def get_user_by_request(request):
    """
    通过request 尝试去获取user
    :param request:
    :return: userprofile or none
    """

    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None

    try:
        res = jwt.decode(token,KEY)
    except:
        return None

    #合法token 去拿用户名
    username = res['username']
    try:
        user = UserProfile.objects.get(username=username)
    except:
        return None

    return user


