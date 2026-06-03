#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z.ai Chat Client - Lightweight proxy + HTML page for old browsers
=================================================================

HOW IT WORKS:
1. This script starts a local web server on port 8080
2. You open http://localhost:8080 in your browser
3. The page lets you log in and chat with Z.ai
4. All API calls go through the local proxy (bypasses CORS)

HOW TO GET YOUR TOKEN (3 ways):
--------------------------------

WAY 1 - From any working browser (phone, friend's computer, etc):
  1. Open chat.z.ai and log in
  2. Click in address bar and type:  javascript:alert(localStorage.token)
  3. Copy the token (starts with "eyJ...")
  4. Paste it in our client

WAY 2 - From your old browser directly:
  1. Open chat.z.ai/auth in your old browser
  2. Log in with Google/GitHub (these work in old browsers!)
  3. After login, type in address bar: javascript:alert(localStorage.token)
  4. Copy the token and paste it in our client (http://localhost:8080)

WAY 3 - Create account with email:
  1. Use our client's signup form (but may require captcha)

USAGE:
  python zai_local_chat.py
  Then open http://localhost:8080 in any browser

Requirements: Python 3.4+ (no extra packages needed)
"""

import http.server
import json
import ssl
import urllib.request
import urllib.error
import os
import sys
import webbrowser

# ============================================================
# CONFIG
# ============================================================
PORT = 8080
REMOTE_BASE = "https://chat.z.ai"

# Disable SSL verification for old Python
ssl_ctx = ssl.create_default_context()
try:
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
except:
    pass


# ============================================================
# HTML PAGE
# ============================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Z.ai Chat</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,Helvetica,sans-serif;background:#1a1a2e;color:#e0e0e0}
#app{max-width:900px;margin:0 auto;padding:10px;height:100vh;display:flex;flex-direction:column}

#token-screen{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%}
#token-screen h1{color:#4fc3f7;margin-bottom:10px;font-size:28px}
#token-screen .subtitle{color:#81d4fa;margin-bottom:20px;font-size:14px}
.token-box{background:#16213e;padding:25px;border-radius:10px;width:420px;max-width:95%}
.token-box h3{color:#4fc3f7;margin-bottom:10px;font-size:15px}
.token-box p{color:#aaa;font-size:12px;line-height:1.6;margin-bottom:10px}
.token-box .step{background:#0f3460;padding:8px 12px;margin:5px 0;border-radius:5px;font-size:12px;line-height:1.5;word-break:break-all}
.token-box .step b{color:#4fc3f7}
.token-box textarea{width:100%;height:70px;padding:8px;margin:8px 0;border:1px solid #333;border-radius:5px;background:#0f3460;color:#fff;font-size:12px;font-family:monospace;resize:vertical}
.token-box textarea:focus{border-color:#4fc3f7;outline:none}
.token-box button{width:100%;padding:12px;margin:5px 0;border:none;border-radius:5px;cursor:pointer;font-size:14px;font-weight:bold}
.btn-go{background:#4fc3f7;color:#000}
.btn-go:hover{background:#81d4fa}
.btn-alt{background:#0f3460;color:#4fc3f7;border:1px solid #4fc3f7}
.btn-alt:hover{background:#1a5276}
.error-msg{color:#f44336;margin:5px 0;font-size:12px;min-height:18px}
.token-link{color:#4fc3f7;cursor:pointer;text-decoration:underline;font-size:12px;margin-top:8px;display:inline-block}

#chat-screen{display:none;flex-direction:column;height:100%}
#chat-header{padding:8px 12px;background:#16213e;border-radius:8px 8px 0 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap}
#chat-header span{color:#4fc3f7;font-weight:bold}
#user-info{font-size:11px;color:#888;margin-left:8px}
.toolbar{display:flex;gap:4px;flex-wrap:wrap}
.toolbar button{background:#0f3460;color:#aaa;border:1px solid #333;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:11px}
.toolbar button:hover{background:#1a5276;color:#fff}

#chat-messages{flex:1;overflow-y:auto;padding:10px;background:#0f0f23;border-left:1px solid #222;border-right:1px solid #222}
.msg{margin:8px 0;padding:8px 12px;border-radius:8px;max-width:88%;word-wrap:break-word;white-space:pre-wrap;font-size:14px;line-height:1.5}
.msg-user{background:#1a5276;margin-left:auto;text-align:right}
.msg-assistant{background:#1e3a2f;margin-right:auto}
.msg-system{background:#2c2c3e;margin:5px auto;text-align:center;font-size:12px;color:#888;max-width:95%}
.msg-error{background:#4a1a1a;color:#f44336;margin:5px auto;text-align:center;font-size:13px}

#chat-input-area{padding:10px;background:#16213e;border-radius:0 0 8px 8px;display:flex;gap:8px}
#msg-input{flex:1;padding:10px;border:1px solid #333;border-radius:5px;background:#0f3460;color:#fff;font-size:14px;font-family:inherit}
#msg-input:focus{border-color:#4fc3f7;outline:none}
#send-btn{padding:10px 20px;background:#4fc3f7;color:#000;border:none;border-radius:5px;cursor:pointer;font-weight:bold;font-size:14px}
#send-btn:hover{background:#81d4fa}
#send-btn:disabled{background:#555;color:#888;cursor:not-allowed}
#status-bar{padding:4px 10px;font-size:11px;color:#666;text-align:center}

#chat-list{display:none;position:fixed;top:0;left:0;width:280px;height:100%;background:#16213e;z-index:100;padding:10px;overflow-y:auto;border-right:2px solid #4fc3f7}
#chat-list h3{color:#4fc3f7;margin-bottom:10px}
#chat-list .chat-item{padding:8px;margin:3px 0;background:#0f3460;border-radius:5px;cursor:pointer;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#chat-list .chat-item:hover{background:#1a5276}
#chat-list .close-btn{position:absolute;top:8px;right:8px;background:#e74c3c;color:#fff;border:none;padding:3px 10px;border-radius:3px;cursor:pointer}

#login-expand{display:none;background:#16213e;padding:20px;border-radius:10px;width:360px;max-width:95%;margin-top:15px}
#login-expand h3{color:#4fc3f7;margin-bottom:10px}
#login-expand input{width:100%;padding:8px;margin:4px 0;border:1px solid #333;border-radius:5px;background:#0f3460;color:#fff;font-size:13px}
#login-expand input:focus{border-color:#4fc3f7;outline:none}
</style>
</head>
<body>
<div id="app">

<!-- TOKEN ENTRY SCREEN -->
<div id="token-screen">
  <h1>Z.ai Chat</h1>
  <div class="subtitle">Lightweight client - works in any browser</div>
  <div class="token-box">
    <h3>Enter your token</h3>
    <p>You need to get your token once from chat.z.ai. Here's how:</p>
    
    <div class="step"><b>Step 1:</b> Open <b>chat.z.ai</b> in ANY browser that works (your phone, another computer, etc.)</div>
    <div class="step"><b>Step 2:</b> Log in with Google or GitHub</div>
    <div class="step"><b>Step 3:</b> After login, click the address bar and type:<br><b>javascript:document.title=localStorage.token</b><br>The token will appear in the browser title bar - copy it</div>
    <div class="step"><b>Alternative:</b> Press F12, go to Console, type:<br><b>copy(localStorage.token)</b><br>This copies the token to clipboard</div>
    
    <textarea id="token-input" placeholder="Paste your token here (starts with eyJ...)"></textarea>
    <button class="btn-go" onclick="connectWithToken()">Connect</button>
    <div class="error-msg" id="token-error"></div>
    
    <span class="token-link" onclick="toggleLoginForm()">Or sign in with email/password</span>
  </div>
  
  <div id="login-expand">
    <h3>Email Login</h3>
    <input type="email" id="login-email" placeholder="Email">
    <input type="password" id="login-password" placeholder="Password">
    <button class="btn-go" onclick="doEmailLogin()">Sign In</button>
    <div class="error-msg" id="login-error"></div>
  </div>
</div>

<!-- CHAT SCREEN -->
<div id="chat-screen">
  <div id="chat-header">
    <div>
      <span>Z.ai Chat</span>
      <span id="user-info"></span>
    </div>
    <div class="toolbar">
      <button onclick="showChatList()">History</button>
      <button onclick="newChat()">New</button>
      <button onclick="doLogout()">Logout</button>
    </div>
  </div>
  <div id="chat-messages"></div>
  <div id="chat-input-area">
    <input type="text" id="msg-input" placeholder="Type message... (Enter to send)" onkeydown="handleKey(event)">
    <button id="send-btn" onclick="sendMessage()">Send</button>
  </div>
  <div id="status-bar">Ready</div>
</div>

<!-- CHAT LIST -->
<div id="chat-list">
  <button class="close-btn" onclick="hideChatList()">X</button>
  <h3>Chat History</h3>
  <div id="chat-list-items"></div>
</div>

</div>

<script>
var token = '';
var chatId = '';
var chatHistory = [];
var isStreaming = false;
var currentXhr = null;

function apiCall(method, path, body, callback) {
  var xhr = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
  xhr.open(method, '/proxy' + path, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  if (token) xhr.setRequestHeader('Authorization', 'Bearer ' + token);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      var data;
      try { data = JSON.parse(xhr.responseText); } catch(e) { data = xhr.responseText; }
      if (callback) callback(xhr.status, data);
    }
  };
  xhr.send(body ? JSON.stringify(body) : null);
}

function connectWithToken() {
  var t = document.getElementById('token-input').value.trim();
  var err = document.getElementById('token-error');
  if (!t) { err.textContent = 'Please paste your token'; return; }
  
  token = t;
  err.textContent = 'Connecting...';
  
  apiCall('GET', '/api/v1/auths/', null, function(status, data) {
    if (status === 200 && data.token) {
      token = data.token; // Use the refreshed token
      enterChat(data);
    } else {
      err.textContent = 'Invalid token. Please check and try again.';
      token = '';
    }
  });
}

function toggleLoginForm() {
  var el = document.getElementById('login-expand');
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function doEmailLogin() {
  var email = document.getElementById('login-email').value.trim();
  var password = document.getElementById('login-password').value;
  var err = document.getElementById('login-error');
  if (!email || !password) { err.textContent = 'Enter email and password'; return; }
  
  err.textContent = 'Signing in...';
  apiCall('POST', '/api/v1/auths/signin', {email: email, password: password}, function(status, data) {
    if (status === 200 && data.token) {
      token = data.token;
      enterChat(data);
    } else {
      err.textContent = (data.detail || 'Login failed') + ' (Note: captcha may be required for email login. Try the token method instead.)';
    }
  });
}

function enterChat(user) {
  document.getElementById('token-screen').style.display = 'none';
  document.getElementById('chat-screen').style.display = 'flex';
  document.getElementById('user-info').textContent = (user.name || user.email || '');
  newChat();
}

function doLogout() {
  token = ''; chatId = ''; chatHistory = [];
  document.getElementById('token-screen').style.display = 'flex';
  document.getElementById('chat-screen').style.display = 'none';
  document.getElementById('chat-messages').innerHTML = '';
  document.getElementById('token-input').value = '';
}

function newChat() {
  setStatus('Creating chat...');
  apiCall('POST', '/api/v1/chats/new', {chat: {title: 'New Chat'}}, function(status, data) {
    if (status === 200 && data.id) {
      chatId = data.id;
      chatHistory = [];
      document.getElementById('chat-messages').innerHTML = '';
      addSystemMsg('New chat started');
      setStatus('Ready');
    } else {
      addErrorMsg('Failed to create chat: ' + (data.detail || ''));
      setStatus('Error');
    }
  });
}

function sendMessage() {
  if (isStreaming) return;
  var input = document.getElementById('msg-input');
  var message = input.value.trim();
  if (!message || !chatId) return;
  
  input.value = '';
  addUserMsg(message);
  chatHistory.push({role: 'user', content: message});
  
  isStreaming = true;
  document.getElementById('send-btn').disabled = true;
  setStatus('Thinking...');
  
  var assistantDiv = addAssistantMsg('');
  var fullContent = '';
  
  var body = {
    chat: {id: chatId},
    model: 'GLM-5.1',
    messages: chatHistory.slice(-20),
    stream: true,
    params: {},
    features: {web_search: false, auto_web_search: false, image_generation: false}
  };
  
  currentXhr = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
  currentXhr.open('POST', '/proxy/api/v1/chats/message', true);
  currentXhr.setRequestHeader('Content-Type', 'application/json');
  currentXhr.setRequestHeader('Accept', 'text/event-stream');
  if (token) currentXhr.setRequestHeader('Authorization', 'Bearer ' + token);
  
  var lastIndex = 0;
  currentXhr.onreadystatechange = function() {
    if (currentXhr.readyState >= 3) {
      var newData = currentXhr.responseText.substring(lastIndex);
      lastIndex = currentXhr.responseText.length;
      
      var lines = newData.split('\n');
      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].replace(/^\s+/, '');
        if (line.indexOf('data:') === 0) {
          var dataStr = line.substring(5).replace(/^\s+/, '');
          if (dataStr === '[DONE]') { finishStream(); return; }
          try {
            var parsed = JSON.parse(dataStr);
            var c = extractContent(parsed);
            if (c) { fullContent += c; assistantDiv.textContent = fullContent; scrollDown(); }
          } catch(e) {}
        }
      }
    }
    if (currentXhr.readyState === 4) {
      if (currentXhr.status === 401) {
        addErrorMsg('Authentication failed. Please re-enter your token.');
        finishStream();
        doLogout();
      } else if (currentXhr.status !== 200 && !fullContent) {
        try {
          var err = JSON.parse(currentXhr.responseText);
          addErrorMsg('Error: ' + (err.detail || currentXhr.status));
        } catch(e) {
          addErrorMsg('HTTP Error: ' + currentXhr.status);
        }
        finishStream();
      } else if (fullContent) {
        finishStream();
      }
    }
  };
  currentXhr.send(JSON.stringify(body));
  
  function finishStream() {
    if (fullContent) chatHistory.push({role: 'assistant', content: fullContent});
    isStreaming = false;
    document.getElementById('send-btn').disabled = false;
    input.focus();
    setStatus('Ready');
  }
}

function extractContent(d) {
  if (d.choices) { for(var i=0;i<d.choices.length;i++) { var dt=d.choices[i].delta; if(dt&&dt.content) return dt.content; } }
  if (typeof d.content === 'string') return d.content;
  if (d.type && (d.type==='message'||d.type.indexOf('delta')>=0) && d.content) return d.content;
  return '';
}

function handleKey(e) { if(e.keyCode===13){e.preventDefault();sendMessage();} }

function addUserMsg(t) { var d=document.createElement('div'); d.className='msg msg-user'; d.textContent=t; document.getElementById('chat-messages').appendChild(d); scrollDown(); }
function addAssistantMsg(t) { var d=document.createElement('div'); d.className='msg msg-assistant'; d.textContent=t; document.getElementById('chat-messages').appendChild(d); scrollDown(); return d; }
function addSystemMsg(t) { var d=document.createElement('div'); d.className='msg msg-system'; d.textContent=t; document.getElementById('chat-messages').appendChild(d); scrollDown(); }
function addErrorMsg(t) { var d=document.createElement('div'); d.className='msg msg-error'; d.textContent=t; document.getElementById('chat-messages').appendChild(d); scrollDown(); }
function scrollDown() { var el=document.getElementById('chat-messages'); el.scrollTop=el.scrollHeight; }
function setStatus(t) { document.getElementById('status-bar').textContent=t; }

function showChatList() {
  document.getElementById('chat-list').style.display='block';
  apiCall('GET', '/api/v1/chats/?page=1', null, function(status, data) {
    var c = document.getElementById('chat-list-items');
    c.innerHTML = '';
    if (status === 200 && data && data.length) {
      for(var i=0;i<data.length;i++) {
        var d=document.createElement('div'); d.className='chat-item';
        d.textContent=data[i].title||'Untitled';
        d.setAttribute('data-id',data[i].id);
        d.onclick=function(){chatId=this.getAttribute('data-id');loadChat(chatId);hideChatList();};
        c.appendChild(d);
      }
    } else { c.innerHTML='<div style="color:#888;padding:10px">No chats</div>'; }
  });
}
function hideChatList() { document.getElementById('chat-list').style.display='none'; }

function loadChat(id) {
  setStatus('Loading...');
  apiCall('GET', '/api/v1/chats/'+id, null, function(status, data) {
    if (status===200) {
      chatId=id; chatHistory=[];
      document.getElementById('chat-messages').innerHTML='';
      var msgs=(data.chat||data).messages||{};
      if(typeof msgs==='object') { for(var mid in msgs) { var m=msgs[mid]; if(m.role==='user'){addUserMsg(m.content);chatHistory.push({role:'user',content:m.content});} else if(m.role==='assistant'){addAssistantMsg(m.content);chatHistory.push({role:'assistant',content:m.content});} } }
      setStatus('Ready');
    } else { addErrorMsg('Load failed'); setStatus('Error'); }
  });
}
</script>
</body>
</html>"""


# ============================================================
# PROXY SERVER
# ============================================================
class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """Serves HTML page and proxies API requests to chat.z.ai"""

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self._serve_html()
        elif self.path.startswith('/proxy/'):
            self._proxy('GET')
        else:
            self._serve_html()

    def do_POST(self):
        if self.path.startswith('/proxy/'):
            self._proxy('POST')
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _serve_html(self):
        data = HTML_PAGE.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def _proxy(self, method):
        path = self.path[7:]  # Strip '/proxy'
        url = REMOTE_BASE + path

        body = None
        if method == 'POST':
            cl = int(self.headers.get('Content-Length', 0))
            if cl > 0:
                body = self.rfile.read(cl)

        headers = {}
        for key in ['Content-Type', 'Authorization', 'Accept', 'Accept-Language', 'X-FE-Version', 'X-Signature']:
            val = self.headers.get(key)
            if val:
                headers[key] = val

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=120)
            ct = resp.headers.get('Content-Type', 'application/json')

            if 'event-stream' in ct:
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self._cors_headers()
                self.end_headers()
                try:
                    while True:
                        chunk = resp.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                except:
                    pass
                finally:
                    resp.close()
            else:
                resp_body = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', str(len(resp_body)))
                self._cors_headers()
                self.end_headers()
                self.wfile.write(resp_body)

        except urllib.error.HTTPError as e:
            err = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self._cors_headers()
            self.end_headers()
            self.wfile.write(err)

        except Exception as e:
            err = json.dumps({"detail": str(e)}).encode('utf-8')
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self._cors_headers()
            self.end_headers()
            self.wfile.write(err)

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept, Accept-Language, X-FE-Version, X-Signature')

    def log_message(self, fmt, *args):
        msg = fmt % args
        if 'proxy' not in msg.lower():
            sys.stderr.write("[%s] %s\n" % (time.strftime('%H:%M:%S'), msg))


# ============================================================
# MAIN
# ============================================================
def main():
    import time
    print()
    print("=" * 55)
    print("   Z.ai Chat Client - for old browsers")
    print("=" * 55)
    print()
    print("  1. Open this URL in your browser:")
    print(f"     http://localhost:{PORT}")
    print()
    print("  2. Get your token from chat.z.ai:")
    print("     - Open chat.z.ai in any working browser")
    print("     - Log in with Google or GitHub")
    print("     - Press F12 -> Console -> type:")
    print("       copy(localStorage.token)")
    print("     - Token is now in your clipboard!")
    print()
    print("  3. Paste the token in the client")
    print()
    print("  Press Ctrl+C to stop the server")
    print("=" * 55)
    print()

    server = http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler)

    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
