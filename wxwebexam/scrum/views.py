#!encoding=utf8
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import json
import hashlib, time, re, urllib2, urllib
from xml.etree import ElementTree as ET
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache


APP_ID = 'wx4a61d7aaa96ced25'
APP_SECRET = 'fc1956849a23315fec8b77d9beb28b8e'

def index(request):
    timestamp = int(time.time())
    noncestr = 'NONCE'
    jsapi_ticket = _get_jsapi_ticket()
    s = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (jsapi_ticket, noncestr, timestamp, request.build_absolute_uri())
    return render(request, 'scrum/index.html', {
                               'appId': APP_ID, 'timestamp': timestamp,
                               'nonceStr': noncestr, 'jsapi_ticket': jsapi_ticket,
                               'signature': hashlib.sha1(s).hexdigest(), 's': s})

def h5_mine(request):
    # # Fetch weixin oauth_access_token
    # code = request.GET.get('code', '')
    # nickname = _oauth_user_info(code)

    nickname = request.GET.get('nickname', '17Sports')
    headimgurl = request.GET.get('headimgurl', '')
    # Render html with weixin signature
    timestamp = int(time.time())
    noncestr = 'NONCE'

    if nickname == '17Sports':   # for anonymous user
        url = 'http://1.17sportsappserver.sinaapp.com/sports/h5_mine'
    else:
        url = 'http://1.17sportsappserver.sinaapp.com/sports/h5_mine?nickname=%s&headimgurl=%s' \
          % (urllib2.quote(smart_str(nickname), safe="%/:=&?~#+!$,;'@()*[]"), headimgurl)

    jsapi_ticket = _get_jsapi_ticket()
    s = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (jsapi_ticket, noncestr, timestamp, url)
    return render_to_response('sports/h5_mine.html',
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
    