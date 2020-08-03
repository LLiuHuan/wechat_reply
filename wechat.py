# coding:utf-8

from flask import Flask, request, abort, make_response
import hashlib
import xmltodict
import time

WECHAT_TOKEN = "elephantnote"

app = Flask(__name__)


@app.route("/")
def test():
    return "/"


# 接口文档：https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Access_Overview.html
@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    """
  对接微信公众号服务器
  """
    # 1. 接收参数
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    # 2. 校验参数
    if not all([signature, timestamp, nonce]):
        abort(400)

    # 3. 按照微信流程进行计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    li.sort()
    tmp_str = "".join(li)
    # sha1加密
    sign = hashlib.sha1(tmp_str.encode("utf-8")).hexdigest()
    # 4. 将计算加密的值和微信的sign对比
    if signature != sign:
        abort(403)
    else:
        # 表示是微信请求
        # GET 请求为微信第一次请求链接请求
        if request.method == "GET":
            echostr = request.args.get("echostr")
            if not echostr:
                abort(400)
            return echostr
        # POST 请求为微信发送普通消息
        elif request.method == "POST":
            xml_str = request.data
            if not xml_str:
                abort(400)
            # 将返回过来的xml字符串转成字典
            xml_dict = xmltodict.parse(xml_str)
            xml_dict = xml_dict["xml"]
            # 获取请求消息类型
            msg_type = xml_dict.get("MsgType")
            # text bi傲视发送的是文本内容
            if msg_type == "text":
                # 构建返回值 由微信服务器返回给用户
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": "666"
                    }
                }
            else:
                # 构建返回值 由微信服务器返回给用户
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("ToUserName"),
                        "FromUserName": xml_dict.get("FromUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": xml_dict.get("Content"),
                        "MsgId": xml_dict.get("MsgId")
                    }
                }
            # 将字典转成xml
            resp_xml_str = xmltodict.unparse(resp_dict)

            # response = make_response(resp_xml_str)
            # response.headers['content-type'] = 'application/xml'
            # 将数据返回给微信服务器
            return resp_xml_str


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)