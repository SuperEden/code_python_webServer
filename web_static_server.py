#web-server 服务器端 使用多进程来实现
from socket import *
from multiprocessing import Process
import re

#定义常量
HTTP_ROOT_DIR = "./html"

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

    #判断用户输入的是/  默认为index.html
    if "/" == file_name:
        file_name = "/index.html"

    #打开指定文件
    try:
        f = open(file_name, "r")
    except IOError:
        #构造服务器的回复数据response
        response_start_line = "HTTP/1.1 404 Not Found\r\n"
        response_headers = "Server: My Server \r\n"
        response_body = "Error"
    else:
        html_data = f.read()
        #关闭文件操作
        f.close()

        #构造服务器的回复数据response
        response_start_line = "HTTP/1.1 200 OK\r\n"
        response_headers = "Server: My Server \r\n"
        response_body = html_data

    response = response_start_line + response_headers + "\r\n" + response_body

    client_socket.send(bytes(response, "utf-8"))

    #关闭客户端Socket
    client_socket.close()

def main():
    # Socket创建套接字
    # bind绑定ip和port
    # listen监听
    # accept接收客户端连接
    # close关闭套接字
    webSocket = socket(AF_INET, SOCK_STREAM)
    webSocket.bind(("", 8000))
    webSocket.listen(128)
    #返回一个元组，新的Socket可以recv和send，还有客户端的ip和port信息

    #循环接收客户端连接
    while True:
        client_socket, client_addr = webSocket.accept()

        #创建多进程来处理客户端连接
        p = Process(target=fun, args=(client_socket,))
        p.start()
        client_socket.close()


    #最后关闭服务器Socket
    webSocket.close()


#判断程序是否自己执行还是使用方法调用
if __name__ == "__main__":
    main()