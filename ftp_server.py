"""
ftp 文件服务器
并发网络功能训练
"""
from socket import *
from threading import Thread
import os,sys
from time import sleep
#全局变量
HOST="0.0.0.0"
PORT=8888
ADDR = (HOST, PORT)
FTP="/home/tarena/FTP/" #文件库路径
#将客户端请求功能封装为类
class FtpServer():
    def __init__(self,connfd,FTP_PATH):
        self.connfd=connfd
        self.path=FTP_PATH
    def get_list(self):#给客户端发送列表
        #获取文件列表
        files=os.listdir(self.path)
        if not files:
            self.connfd.send("该文件类别为空".encode())
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
        fs=""
        for file in files:
            if file[0]!="." and os.path.isfile(self.path+file): #不是隐藏文件和是普通文件
                fs+=file+'\n'
        self.connfd.send(fs.encode())
    def download_file(self,filename):
        try:
            fd=open(self.path+filename,"rb")
        except Exception:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
        #发送文件
        while True:
            data=fd.read(1024)
            if not data: #读到结尾
                sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)  #正常发送
    def upload_file(self,filename):
        if os.path.exists(self.path+filename):
            self.connfd.send("该文件已存在".encode())
            return
        self.connfd.send(b"OK")
        fd=open(self.path+filename,"wb")
        #接收文件
        while True:
            data=self.connfd.recv(1024)
            if data==b"##":
                break
            fd.write(data)
        fd.close()

def handle(connfd):
   cls=connfd.recv(1024).decode()
   FTP_PATH=FTP+cls+"/"
   ftp=FtpServer(connfd,FTP_PATH)  #创建服务器处理类的对象
   while True:
       data=connfd.recv(1024).decode()
       #如果客户端断开返回data为空
       if not data or data[0]=="Q" :
           return
       elif data[0]=="D":
           filename=data.split(" ")[-1]
           ftp.download_file(filename)
       elif data[0]=="U":
           filename=data.split(" ")[-1]
           ftp.upload_file(filename)
       elif data[0]=="L":
           ftp.get_list()
#并发网络搭建
def main():
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("Listen the port 8888...")
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:
            sys.exit("客户端退出")
        except Exception as e:
            print(e)
            continue
        print("链接的客户端：",addr)
        #创建线程处理请求
        client=Thread(target=handle,args=(connfd,))
        client.setDaemon(True)
        client.start()
if __name__=="__main__":
        main()