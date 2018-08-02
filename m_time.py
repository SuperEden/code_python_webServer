import time

#定义一个方法返回当前时间
def say_time():
    return time.ctime()

#定义一个类返回当前时间
class Say_Time(object):
    def __call__(self):
        return time.ctime()

