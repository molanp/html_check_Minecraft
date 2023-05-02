from until import *
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import urlencode
import requests

app = Flask(__name__)

lim = ""
jip = str(input('输入网站端口，为空默认为2000 ：'))
pp = str(input('输入本网站的域名(不带端口，无域名请输入本机外网ip): '))
if jip == '':
  jip = 2000
limi = str(input("输入每分钟允许的最大请求次数："))
https = str(input("是否启用https(SSL)？(y/N)"))
if https == "y": 
  cer = str(input("输入SSL证书路径(.pem):\n"))
  cer_key = str(input("输入cer证书文件密钥路径(.key): \n"))
app.config['JSON_AS_ASCII']=False
CORS(app, resources=r'/*')

limiter = Limiter(get_remote_address,app=app)

@app.get('/check')
@limiter.limit(f"{limi}/minute")
def check():
  try:
    ip = request.args.get("ip")
    port = request.args.get("port")
    ms = MineStat(str(ip), int(port), resolve_srv=True)
    if ms.online:
      return {
          "status": 200,
          "msg": "OK",
          "favicon": ms.favicon_b64,
          "host": ms.address,
          "version": ms.version,
          "motd": ms.stripped_motd,
          "players_online": ms.current_players,
          "players_max": ms.max_players,
          "latency": ms.latency
        }
    else:
        return {
          "status": 400,
          "msg": "服务器离线"
        }
  except TypeError:
        return {
          "status": 400,
          "msg": "请求格式有误"
        }
  except ValueError:
        return {
        "status": 400,
        "msg": "端口必须是数字"
        }
        
@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == "127.0.0.1"
  
@app.errorhandler(429)
def ratelimit_handler(e):
    return {
      "status": 429,
      "msg": "请求次数过多，请稍后重试"
      }

@app.get('/')
@limiter.exempt
def api():
  return '''
  <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, shrink-to-fit=no" />
    <meta name="renderer" content="webkit" />
    <meta name="force-rendering" content="webkit" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mdui/1.0.2/css/mdui.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mdui/1.0.2/js/mdui.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/limonte-sweetalert2/11.4.17/sweetalert2.all.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap" rel="stylesheet">
    <title>服务器状态查询-蓝天云</title>
    <style>
        body {
            font-family: 'Noto Sans SC', sans-serif;
            background: url('http://stats.lantianclouds.com:48058/image/index.webp')
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            background-repeat: no-repeat;
            width: 100%;
            height: 100%;
        }

        #login-box {
            width: 50%;
            min-width: 300px;
            background-color: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: rgba(142, 142, 142, 0.19) 0px 6px 15px 0px;
            -webkit-box-shadow: rgba(142, 142, 142, 0.19) 0px 6px 15px 0px;
            border-radius: 12px;
            -webkit-border-radius: 12px;
            color: rgba(255, 255, 255, 0.75);
            text-align: center;
        }
        table {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
        }
        table td, table th {
            border: 1px solid #ddd;
            padding: 8px;
        }
        table tr:hover {background-color: #c4c4c4;}
        table th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
        }

        table th {
            color: #000000;
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
        }

        table tr {
            color: #000000;
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
        }

        .badge:hover {
          background-color:#777 !important;
        }
        .badge {
          display:inline-block;
          min-width:10px;
          padding:6px 10px;
          font-size:12px;
          font-weight:bold;
          color:#fff;
          line-height:1;
          vertical-align:middle;
          white-space:nowrap;
          text-align:center;
          background-color:#777;
          border-radius:10px;
          margin:5px;
        }

        .login-button {
            width: auto;
            height: 30px;
            font-size: 20px;
            font-weight: 600;
            color: #ffffff;
            background-image: linear-gradient(to right, #74ebd5 0%, #9face6 100%);
            border: 0;
            border-radius: 5px;
            line-height: 1.7rem;
        }

        p {
            color: #525252;
        }
    </style>
</head>

<body>
<center>
    <div id="login-box">
        <h1 id="title" style="color: #525252;">服务器状态查询</h1>
        <p>为了防止被人恶意使用 每个ip每分钟查询数量为'''+limi+'''次</p>
            <div class="form">
                <div class="mdui-textfield">
                    <input id="ip" class="mdui-textfield-input" type="text" placeholder="IP" required />
                    <div class="mdui-textfield-error">服务器IP不能为空</div>
                </div>
                <div class="mdui-textfield">
                    <input id="port" class="mdui-textfield-input" type="text" placeholder="端口" required />
                    <div class="mdui-textfield-error">端口不能为空</div>
                </div>
            </div>
        <div class="table-container">
        <center>
            <table id="ppm">
                <thead>
                    <tr>
                        <th>图标</th>
                        <th>服务器IP地址</th>
                        <th>服务器版本</th>
                        <th>MOTD</th>
                        <th>在线人数</th>
                        <th>延迟</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><img width="60px" src="data:image/png;base64,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"/></td>
                        <td>等待响应...</td>
                        <td>等待响应...</td>	
                        <td>等待响应...</td>
                        <td><span class="badge">等待响应...</span></td>
                        <td>等待响应...</td>
                    </tr>
                </tbody>
            </table>
            </center>
        </div>
        <button onclick="register()" class="login-button mdui-btn mdui-btn-raised mdui-ripple" id="login-btn">查询</button>
        <p id="copyright">&copy;Copyright 2023 蓝天云&trade;Power by <a href="https://github.com/molanp/html_check_Minecraft">molanp</a></p><br>
    </div>
    </center>
    <script>
    function register() {
    var username = document.getElementById("ip").value;
    var password = document.getElementById("port").value;
    link = "http://'''+pp+''':'''+str(jip)+'''/check?ip="+username+"&port="+password
  
    //console.log(link);
  
    if (username == "" || password == "") {
      regFail("IP或端口不能为空");
      return;
    }

    document.getElementById("login-btn").disabled = true;
    xhr = new XMLHttpRequest();
    xhr.open("GET", link);
    xhr.send();
    xhr.ontimeout = function (e) {
      regFail("超时");
      document.getElementById("login-btn").disabled = false;
    };
    xhr.onerror = function (e) {
      regFail("未知错误");
      document.getElementById("login-btn").disabled = false;
    };
    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4) {
          var result = JSON.parse(xhr.responseText);
          if (result.status == 200) {
            regSuccess(result);
          } else if (xhr.status == 200 && result.status != 200) {
            regFail(result.msg);
          } else if (xhr.status == 429) {
            regFail("请求次数过多，请稍后重试");
            }else {
          regFail(xhr.status);
        }
        document.getElementById("login-btn").disabled = false;
      }
  }
  }
  
  function regSuccess(context) {
    document.getElementById(
        "ppm"
      ).innerHTML = `
      <table id="ppm">
        <thead>
            <tr>
                <th>图标</th>
                <th>服务器IP地址</th>
                <th>服务器版本</th>
                <th>MOTD</th>
                <th>在线人数</th>
                <th>延迟</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><img width="60px" src="${context.favicon}"/></td>
                <td>${context.host}</td>
                <td>${context.version}</td>	
                <td>${context.motd}</td>
                <td><span class="badge">${context.players_online}/${context.players_max}</span></td>
                <td>${context.latency}ms</td>
            </tr>
        </tbody>
    </table>`
  }
  
  function regFail(reason) {
    swal.fire({
      icon: "error",
      title: "查询失败!",
      text: `错误原因: ${reason}.`,
      footer: "必要时可询问发给客服",
    });
  }
    </script>
</body>
</html>
'''

print("Power by 782552619")
if https == "y":
	app.run(host='0.0.0.0',port=jip,debug=False,threaded=True,ssl_context=(cer, cer_key))
else:
	app.run(host='0.0.0.0',port=jip,debug=False,threaded=True)
