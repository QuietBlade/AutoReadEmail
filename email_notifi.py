from ToastNotifier import ToastNotifier
import time
import poplib
from email.parser import Parser
from email.header import decode_header
import webbrowser
import os
import base64

_uidl = '' #留空就行
email = 'xxxxxxxxx@163.com'  #邮箱地址
password = ''   #密码
host = 'pop.163.com'        #邮箱服务器地址
sleep = 15 * 60   # 读取间隔 单位 s,官方要求最低15分钟请求一次

### 读取最新邮件
def ReadEmail(server):
    global _uidl
    print(server.getwelcome().decode('utf-8'))
    index = server.stat()[0]
    uidl = server.uidl(index)
    if _uidl == uidl.split()[2]:  #邮件相同，跳过
        return False
    else:
        _uidl = uidl.split()[2]
        resp, lines, octets = server.retr(index)
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        msg = Parser().parsestr(msg_content)
        From = decode_str(msg.get("From"))
        Subject = decode_str(msg.get("Subject"))
        CacheEmail(msg)
        ShowToast("新邮件提醒","来自%s\n%s"%(From,Subject),"temp.html")
        return True

### 新邮件缓存
def CacheEmail(msg):
    data = None
    charset = "utf-8"
    for message in msg.walk():
        if message.get_content_type() == "text/html":
            charset = message.get_content_charset()    
            data = message.get_payload(decode=True)
    f = open("temp.html", "w", encoding=charset)
    if charset == 'utf-8':
        f.write(str(data,charset).encode('utf-8').decode('unicode_escape'))
    else:
        f.write(str(data,charset))
    f.close()

# 解码头
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

# 连接邮箱
def ConnectEmail():
    global email
    global password
    global host
    server = poplib.POP3(host)
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(password)
    server.utf8()
    return server

### 提示
def ShowToast(title, content, url):
    toaster = ToastNotifier()
    toaster.show_toast(title, content, duration=2,
                       callback_on_click=lambda: open_ticket(url))

## 打开在浏览器
def open_ticket(url):
    webbrowser.open_new_tab("%s\\%s"%(os.getcwd(),url))

if __name__ == "__main__":    
    while True:
        server = ConnectEmail()
        ReadEmail(server)
        server.quit()
        time.sleep(sleep)