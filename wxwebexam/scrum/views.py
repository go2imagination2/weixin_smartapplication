#!encoding=utf8
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import json
import hashlib, re, urllib2, urllib
from xml.etree import ElementTree as ET
from django.utils.datetime_safe import time, datetime
from django.utils import timezone
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from models import *

APP_ID = 'wx4a61d7aaa96ced25'
APP_SECRET = 'fc1956849a23315fec8b77d9beb28b8e'


# TODO a timebox 20min for 20 entry, but not strict
# TODO bi-lingual exam

def index(request):
    question = '中国最早推广Scrum认证的机构是哪家?'
    options = [('A', 'Agile Alliance敏捷联盟'), ('B', 'UPerform敏捷学院'), ('C', 'Scrum Alliance'), ]
    answer = 'B'
    explanation = 'UPerform－优普丰敏捷学院是中国地区首家国际Scrum Alliance联盟REP(注册教育提供商)及Agile Alliance联盟企业会员，中国敏捷运动的核心推动团队。创立于2007年，通过将Scrum创始人Ken Schwaber的扛鼎之作《Scrum敏捷项目管理》一书翻译引进中国，并于2008年在上海参与召集了首次敏捷社区聚会，带头吹响了中国敏捷推广的集结号。十年来，得到国际多位敏捷大师的支持和眷顾，包括Ken Schwaber、Mike Cohn、Lyssa Adkins、Michael Spayd、Ken Rubin、Jurgen Appelo、Pete Deemer、Peter Borsella 、Vernon Stinebaker,、Chris Sims等，目前是华语地区拥有导师级Scrum认证者最多的机构，也是目前亚洲地区唯一获得2017新版CSP认证成长路径教练资格的机构。发展出大量原创敏捷内容，包括理论哲学、现场实践、工具方法等。'
    return render(request, 'scrum/index.html',
                  {'question': question, 'options': options, 'answer': answer, 'explanation': explanation})


def enroll_page(request):
    return render(request, 'scrum/enroll_page.html', {})


def enroll(request):
    paper = Paper.objects.get(pk=1)
    exam = Exam.objects.get(pk=1)
    exam_record = ExamRecord.objects.create(exam=exam)
    exam_record.name = request.POST.get('name', 'Unnamed')
    exam_record.name = request.POST.get('company', 'Nowhere')
    exam_record.answers = ','.join(['-'] * paper.count())
    exam_record.start_time = timezone.now()
    exam_record.save()
    request.session['current_exam_record_id'] = exam_record.id
    request.session['current_entry_id'] = 1
    request.session['entry_count'] = paper.count()

    return redirect('/single/')


def single(request):
    entry_id = request.session.get('current_entry_id', None)
    entry_id = request.GET.get('entry_id', entry_id)

    if entry_id is None:
        return redirect('/')

    entry_id = int(entry_id)
    request.session['current_entry_id'] = entry_id
    exam_record_id = request.session['current_exam_record_id']
    print 'current_exam_record_id=%s' % request.session['current_exam_record_id']
    print 'entry_id=%s' % entry_id
    print 'entry_count=%s' % request.session['entry_count']
    entry = Entry.objects.get(pk=entry_id)

    # TODO check if it's answered then display desc and notify frontend disable submit
    exam_record = ExamRecord.objects.get(pk=exam_record_id)
    updated_answers = exam_record.answers.split(',')
    answered = updated_answers[entry_id - 1] != '-'
    is_answered_correct = entry.answer == updated_answers[request.session['current_entry_id'] - 1]

    enumerated_options = map(lambda (idx, option): (chr(idx + 65), option.desc), enumerate(entry.entryoption_set.all()))

    return render(request, 'scrum/single.html',
                  {'entry': entry, 'enumerated_options': enumerated_options,
                   'entry_count': request.session['entry_count'], 'answered': answered,
                   'is_answered_correct': is_answered_correct,
                   'elapsed_seconds': timezone.now() - exam_record.start_time,
                   'start_time': exam_record.start_time.strftime('%b %d, %Y %H:%M:%S')})


def answerit(request):
    if request.method != 'POST':
        return redirect('/single/')

    entry_id = request.session['current_entry_id']

    if entry_id is None:
        return redirect('/')

    entry = Entry.objects.get(pk=entry_id)

    if entry.category == 'S':
        actual_answers = request.POST.get('radio_single', '')
    elif entry.category == 'M':
        actual_answers = ''.join(request.POST.getlist('checkbox_multi', ['']))
    else:
        print 'unknown category %s' % entry.category
    print 'actual_answers=%s' % actual_answers

    # TODO record the answer in exam record and not able to answer again
    exam_record = ExamRecord.objects.get(pk=(request.session['current_exam_record_id']))
    updated_answers = exam_record.answers.split(',')
    updated_answers[entry_id - 1] = actual_answers
    exam_record.answers = ','.join(updated_answers)
    exam_record.save()

    return redirect('/single/')


def scoring(request):
    exam_record = ExamRecord.objects.get(pk=(request.session['current_exam_record_id']))
    actual_answers = exam_record.answers.split(',')

    final_score = 0
    for i in xrange(request.session['entry_count']):
        expected = Entry.objects.get(pk=i + 1).answer
        actual = actual_answers[i]
        final_score += round(100.0 / request.session['entry_count']) if expected == actual else 0
    final_score = int(final_score)
    exam_record.score = min(final_score, 100)
    exam_record.save()

    if request.session.has_key('current_entry_id'):
        del request.session['current_entry_id']

    return render(request, 'scrum/scoring.html', {'final_score': final_score})


def finishing(request):
    print request.POST.get('email', '')
    exam_record = ExamRecord.objects.get(pk=(request.session['current_exam_record_id']))
    exam_record.email = request.POST.get('email', '')
    exam_record.save()
    # TODO send email with final score
    # service@scrumchina.com

    return redirect('http://www.uperform.cn')


#############################

def h5_main(request):
    timestamp = int(time.time())
    noncestr = 'NONCE'
    jsapi_ticket = _get_jsapi_ticket()
    s = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (
        jsapi_ticket, noncestr, timestamp, request.build_absolute_uri())  # 需要将服务器的IP添加到微信公众号白名单中
    return render(request, 'scrum/index.html', {
        'appId': APP_ID, 'timestamp': timestamp,
        'nonceStr': noncestr, 'jsapi_ticket': jsapi_ticket,
        'signature': hashlib.sha1(s).hexdigest(), 's': s})


# @DeprecationWarning
def h5_main_ex(request):
    # # Fetch weixin oauth_access_token
    # code = request.GET.get('code', '')
    # nickname = _oauth_user_info(code)

    nickname = request.GET.get('nickname', '17Sports')
    headimgurl = request.GET.get('headimgurl', '')
    # Render html with weixin signature
    timestamp = int(time.time())
    noncestr = 'NONCE'

    if nickname == '17Sports':  # for anonymous user
        url = 'http://1.17sportsappserver.sinaapp.com/sports/h5_mine'
    else:
        url = 'http://1.17sportsappserver.sinaapp.com/sports/h5_mine?nickname=%s&headimgurl=%s' \
              % (urllib2.quote(smart_str(nickname), safe="%/:=&?~#+!$,;'@()*[]"), headimgurl)

    jsapi_ticket = _get_jsapi_ticket()
    s = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (jsapi_ticket, noncestr, timestamp, url)
    return render_to_response('scrum/h5_main.html',
                              {'nickname': nickname, 'headimgurl': headimgurl, 'appId': APP_ID, 'timestamp': timestamp,
                               'nonceStr': noncestr, 'jsapi_ticket': jsapi_ticket,
                               'signature': hashlib.sha1(s).hexdigest(), 's': s})


def _oauth_user_info(code):
    """ 微信只对服务号开放了网页授权接口！！！
    :param code:
    :return:
    """

    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' \
          % (APP_ID, APP_SECRET, code)
    json_str = _url_request(url)
    result = json.loads(json_str)

    if result['errcode'] == 0:
        oauth_access_token = result.get('access_token')
        refresh_token = result.get('refresh_token')
        openid = result.get('openid')

        json_str = _url_request('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' % (
            oauth_access_token, openid))
        result = json.loads(json_str)
        return result.get('nickname', '17运动网')
    else:
        return '17运动网'


def _get_access_token():
    """
    7200s有效，需要全局缓存下来
    """
    cached_access_token = cache.get('cached_access_token')
    if cached_access_token is None:
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
            APP_ID, APP_SECRET)
        json_str = _url_request(url)
        cached_access_token = json.loads(json_str).get('access_token')
        cache.set('cached_access_token', cached_access_token, 7000)

    return cached_access_token


def _get_jsapi_ticket():
    """
    7200s有效，需要全局缓存下来
    """
    cached_jsapi_ticket = cache.get('cached_jsapi_ticket')
    if cached_jsapi_ticket is None:
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % (_get_access_token())
        json_str = _url_request(url)
        cached_jsapi_ticket = json.loads(json_str).get('ticket')
        cache.set('cached_jsapi_ticket', cached_jsapi_ticket, 7000)

    return cached_jsapi_ticket


def _url_request(url, body=''):
    req = urllib2.urlopen(urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]"), body)
    json_str = req.read()
    return json_str


def _get_user_info(open_id):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN' % (
        _get_access_token(), open_id)
    json_str = _url_request(url)
    return json.loads(json_str)
