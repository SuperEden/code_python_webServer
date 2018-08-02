#web-server 服务器端 使用多进程来实现  使用类来抽象化程序
from socket import *
from multiprocessing import Process
import re
import sys

#定义常量
HTTP_ROOT_DIR = "./html"

#定义WSGI文件夹
WSDI_PYTHON_DIR = "./wsgi"

#定义类来抽象程序
class Http_Server(object):
    def __init__(self):
        # Socket创建套接字
        # bind绑定ip和port
        # listen监听
        # accept接收客户端连接
        # close关闭套接字
        self.webSocket = socket(AF_INET, SOCK_STREAM)

    def bind(self, port):
        self.webSocket.bind(("", port))

    def start(self):
        self.webSocket.listen(128)
        # 返回一个元组，新的Socket可以recv和send，还有客户端的ip和port信息
        #循环接收客户端连接
        while True:
            client_socket, client_addr = self.webSocket.accept()

            #创建多进程来处理客户端连接
            p = Process(target=self.fun, args=(client_socket,))
            p.start()
            client_socket.close()

        # 最后关闭服务器Socket
        self.webSocket.close()

    def start_response(self, staus, server_response):
        """
          staus = "200 OK"
          server_response = [
          ("Content-Type","text/html")
            ]
        """
        response_handers = "HTTP/1.1 " + staus + "\r\n"
        for hands in server_response:
            response_handers += "%s: %s\r\n"%hands
            print(response_handers)
        #将值保存在自身变量中
        self.response_handers = response_handers

    # 让web服务器创建每一个进程对应一个客户端连接，执行的方法
    def fun(self, client_socket):
        #每一个客户端连接创建一个进程，实现浏览器的数据请求
        #接收客户端的请求数据
        recv_data = client_socket.recv(1024)
        print("request:%s"%recv_data)

        #用空格分割用户提交的请求['GET / HTTP/1.1', 'Host: 127.0.0.1:8000', 'Connection: keep-alive']
        recv_lines = recv_data.splitlines()
        recv_var = recv_lines[0].decode("utf-8")
        print(recv_var)

        #判断浏览器请求是否为空  False
        if " " == bytes(recv_var, "utf-8"):
            print("request 传空！")
        else:
            #正则提取关键字'GET / HTTP/1.1'—> /index.html
            file_name = re.match(r"^\w+\s(.*)\s(.*)$", recv_lines[0].decode("utf-8")).group(1)
            print(file_name)

            #处理动态文件或者静态文件  判断依据就是用户请求末尾是否为.py
            if file_name.endswith(".py"):
                #将用户请求的动态模块导入，先用字符串切片"/time.py"
                #m = __import__("time") 类似import time , time等于m
                file_module = file_name[1:-3]
                m = __import__(file_module)
                env = {}
                response_body = m.application(env, self.start_response)
                response = self.response_handers + "\r\n" + response_body
            elif "/favicon.ico" == file_name:
                pass
            else:
                #判断用户输入的是/  默认为index.html
                if "/" == file_name:
                    file_name = "/index.html"
                #以下判断用户请求的不是以.py结尾，静态处理，打开指定文件
                try:
                    f = open(HTTP_ROOT_DIR + file_name, "rb")
                except IOError:
                    #构造服务器的回复数据response  当用户请求的资源不存在的时候
                    response_start_line = "HTTP/1.1 404 Not Found\r\n"
                    response_headers = "Server: My Server \r\n"
                    response_body = "Error! Not Found This Page!"
                else:
                    html_data = f.read()
                    #关闭文件操作
                    f.close()

                    #构造服务器的回复数据response
                    response_start_line = "HTTP/1.1 200 OK\r\n"
                    response_headers = "Server: My Server \r\n"
                    response_body = html_data.decode("utf-8")

                #构造服务器response回复客户端的数据
                response = response_start_line + response_headers + "\r\n" + response_body

                client_socket.send(bytes(response, "utf-8"))

            #关闭客户端Socket
            client_socket.close()

def main():
    #导入WSGI库的搜索路径
    sys.path.insert(1, WSDI_PYTHON_DIR)
    http_server = Http_Server()
    http_server.bind(8000)
    http_server.start()

#判断程序是否自己执行还是使用方法调用
if __name__ == "__main__":
    main()