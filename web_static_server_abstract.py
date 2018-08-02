#web-server 服务器端 使用多进程来实现  使用类来抽象化程序
from socket import *
from multiprocessing import Process
import re

#定义常量
HTTP_ROOT_DIR = "./html"

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
            p = Process(target=fun, args=(client_socket,))
            p.start()
            client_socket.close()

        # 最后关闭服务器Socket
        self.webSocket.close()

# 让web服务器创建每一个进程对应一个客户端连接，执行的方法
def fun(client_socket):
    #每一个客户端连接创建一个进程，实现浏览器的数据请求
    #接收客户端的请求数据
    recv_data = client_socket.recv(1024)
    print("request:%s"%recv_data)
    #用空格分割用户提交的请求['GET / HTTP/1.1', 'Host: 127.0.0.1:8000', 'Connection: keep-alive']
    recv_lines = recv_data.splitlines()
    recv_var = recv_lines[0].decode("utf-8")
    print(recv_var)
    #正则提取关键字'GET / HTTP/1.1'—> /index.html
    file_name_temp = re.match(r"^\w+\s(.*)\s(.*)$", recv_lines[0].decode("utf-8")).group(1)
    print(HTTP_ROOT_DIR + file_name_temp)
    file_name = HTTP_ROOT_DIR + file_name_temp

    #处理动态文件或者静态文件  判断依据就是用户请求末尾是否为.py
    if ".py" == file_name.endswith(".py"):
        pass
    else:
        #判断用户输入的是/  默认为index.html
        if "/" == file_name:
            file_name = "/index.html"

        #以下判断用户请求的不是以.py结尾，静态处理，打开指定文件
        try:
            f = open(file_name, "rb")
        except IOError:
            #构造服务器的回复数据response  当用户请求的资源不存在的时候
            response_start_line = "HTTP/1.1 404 Not Found\r\n"
            response_headers = "Server: My Server \r\n"
            response_body = "Error".decode("utf-8")
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

    #过滤服务器发送空数据给客户端
    if response != " ":
        client_socket.send(bytes(response, "utf-8"))

    #关闭客户端Socket
    client_socket.close()

def main():
    http_server = Http_Server()
    http_server.bind(8000)
    http_server.start()

#判断程序是否自己执行还是使用方法调用
if __name__ == "__main__":
    main()