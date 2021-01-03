from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from tools.login_check import login_check,get_user_by_request
import json
from .models import Topic
from user.models import UserProfile

@login_check('POST')
def topics(request,author_id):


    if request.method == 'GET':
        #获取用户数据

        authors = UserProfile.objects.filter(username=author_id)
        if not authors:
            result = {'code': 308, 'error': 'no author'}
            return JsonResponse(result)
        #取出结果中的博主
        author = authors[0]

        #visitor
        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor.username

        #用户全量数据
        category = request.GET.get('category')
        if category in ['tec','no-tec']:
            if author_id == visitor_name:
                #博主访问自己的博客
                topics = Topic.objects.filter(author_id=author_id, category=category)
            else:
                #访客来了
                topics = Topic.objects.filter(author_id=author_id,category=category, limit='public')


        else:#用户全量数据
            if author_id == visitor_name:
                #博主访问自己的博客 获取全部数据
                topics = Topic.objects.filter(author_id=author_id)
            else:
                #访客来了，非博主本人 public
                topics = Topic.objects.filter(author_id=author_id, limit='public')
        #返回
        res = make_topics_res(author,topics)
        return JsonResponse(res)

    elif request.method == 'POST':
        #创建用户数据

        json_str = request.body
        if not json_str:
            result = {'code': 301, 'error': 'give json'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)

        title = json_obj.get('title')
        #xss注入脚本
        import html
        #进行转义
        title = html.escape(title)

        if not title:
            result = {'code': 302, 'error': 'g v title'}
            return JsonResponse(result)

        content = json_obj.get('content')
        if not content:
            result = {'code': 303, 'error': 'g v content'}
            return JsonResponse(result)

        #获取纯文本内容，用于切割文章简介
        content_text = json_obj.get('content_text')
        if not content_text:
            result = {'code': 304, 'error': 'p g v content_text'}
            return JsonResponse(result)

        #切割简介
        introduce = content_text[:30]
        limit = json_obj.get('limit')
        if limit not in ['public','private']:
            result = {'code': 305, 'error': 'limit is wrong'}
            return JsonResponse(result)

        category = json_obj.get('category')
        #TODO 检查 same to limit

        #创建数据
        Topic.objects.create(title=title,category=category,limit=limit,content=content,introduce=introduce,author=request.user)
        result = {'code': 200,'username': request.user.username}
        return JsonResponse(result)

    elif request.method == 'DELETE':
        #博主删除自己的文章
        #token存储的用户
        author = request.user
        token_author_id = author.username
        #url中传过来的author——id 必须与token中的用户名相等
        if author_id != token_author_id:
            result = {'code': 309, 'error': 'u can not do it'}
            return JsonResponse(result)
        topic_id = request.GET.get('topic_id')
        try:
            topic = Topic.objects.get(id=topic_id)
        except:
            result = {'code': 310, 'error': 'can not do it!'}
            return JsonResponse(result)

        #删除
        if topic.author.username != author_id:
            result = {'code': 311, 'error': 'u can not do it !!'}
            return JsonResponse(result)
        topic.delete()
        res = {'code': 200}
        return JsonResponse(res)


    return JsonResponse({'code': 200, 'error': 'test!'})


def make_topics_res(author, topics):
    res = {'code': 200, 'data': {}}
    data = {}
    data['nickname'] = author.nickname
    topics_list = []

    for topic in topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['introduce'] = topic.introduce
        d['author'] = author.nickname
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        topics_list.append(d)

    data['topics'] = topics_list
    res['data'] = data
    return res