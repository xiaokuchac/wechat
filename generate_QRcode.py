# -*- coding:utf-8 -*-

"""
1.需要获取access_token
2.使用access_token向指定的URL获取ticket
3.使用ticket向指定的URL获取二维码图片
"""
import time
import urllib2
import json


appID = 'wxb00c80a313447952'
appsecret = '38e2eab6c811cd113b22a83ba5ef9dc5'

"""
access_token的了解：全局使用，会过期，需要一个统一的入口，保证唯一
https请求方式: GET
https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
{"access_token":"ACCESS_TOKEN","expires_in":7200}
{"errcode":40013,"errmsg":"invalid appid"}


获取access_token分析
1.access_token多个地方都要使用，所以需要使用变量记录
2.记录access_token包括：access_token的值，生成时间，过期时间（7200秒）
3.获取access_token：先判断是否存在或者是否过期，如果不存在或者过期就获取新的，反之，读取之前的
"""


class AccessToken(object):
    """中控服务器，统一获取access_token"""

    # 使用私有变量,就是为了不让外界轻易更改我的关键数据
    _access_token = {
        'access_token':'',
        'create_time':time.time(),
        'expires_in':7200
    }

    # 定义专用的接口，专门来访问_access_token
    @classmethod
    def get_access_token(cls):

        acs = cls._access_token

        # 判断access_token是否有值，或者过期。如果为空或者过期需要向指定URL获取access_token
        if not acs.get('access_token') or (time.time() - acs.get('create_time') > acs.get('expires_in')):

            # 向指定URL获取access_token
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appID,appsecret)
            resposne_json_str = urllib2.urlopen(url).read()

            # 将相应的json字符串转成字典，易于操作
            response_json_dict = json.loads(resposne_json_str)

            # 校验错误
            if 'errcode' in response_json_dict:
                raise Exception(response_json_dict.get('errmsg'))

            # 需要记录access_token
            cls._access_token['access_token'] = response_json_dict.get('access_token')
            cls._access_token['expires_in'] = response_json_dict.get('expires_in')
            cls._access_token['create_time'] = time.time()

        return acs.get('access_token')


# -*- coding:utf-8 -*-

from flask import Flask


app = Flask(__name__)


"""
http请求方式: POST
URL: https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=TOKEN
POST数据格式：json
POST数据例子：{"expire_seconds": 604800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": 123}}}

{"ticket":"gQH47joAAAAAAAAAASxodHRwOi8vd2VpeGluLnFxLmNvbS9xL2taZ2Z3TVRtNzJXV1Brb3ZhYmJJAAIEZ23sUwMEmm
3sUw==","expire_seconds":60,"url":"http://weixin.qq.com/q/kZgfwMTm72WWPkovabbI"}
"""

@app.route('/<int:scene_id>')
def index(scene_id):

    url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=' + AccessToken.get_access_token()
    params = {
        "expire_seconds": 604800,
        "action_name": "QR_SCENE",
        "action_info": {"scene": {"scene_id": scene_id}}
    }
    response_json_str = urllib2.urlopen(url, data=json.dumps(params)).read()
    resposne_json_dict = json.loads(response_json_str)

    # 获取ticket
    ticket = resposne_json_dict.get('ticket')

    # 使用ticket向指定URL获取二维码图片
    # HTTP GET请求（请使用https协议）https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=TICKET

    return '<img src="https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s">' % ticket


if __name__ == '__main__':
    app.run(debug=True)


# if __name__ == '__main__':
#     print AccessToken.get_access_token()
#     print AccessToken.get_access_token()

