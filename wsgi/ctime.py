import time

def application(env, start_response):
    staus = "200 OK"
    server_response = [
        ("Content-Type","text/html")
    ]
    start_response(staus, server_response)
    return time.ctime()
