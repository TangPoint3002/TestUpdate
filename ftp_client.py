from socket import *
import os,sys
import time
#具体功能封装为类
class FtpClient():
    def __init__(self,sockfd):
        self.sockfd=sockfd
    def get_list(self):
        self.sockfd.send(b"L") #发送请求
        #等待回复
        data=self.sockfd.recv(128).decode()                #连续发送 这边连续接收  <--->  粘包
        if data=="OK": #ok表示请求成功
            data=self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)
    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("O(∩_∩)O谢谢使用")
    def download_file(self,filename):
        self.sockfd.send(("D "+filename).encode())
        data=self.sockfd.recv(128).decode()
        if data=="OK":
            fd=open(filename,"wb")
            #接收文件写入文件
            while True:
                data=self.sockfd.recv(1024)
                if data==b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)
    def upload_file(self,filename):
        try:
            f=open(filename,"rb")
        except Exception:
            print("没有该文件")
            return

        filename=filename.split('/')[-1]
        self.sockfd.send(("U "+filename).encode())
        #等待回复
        data=self.sockfd.recv(128).decode()
        if data=="OK":
            while True:
                data=f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print(data)
def request(sockfd):
    ftp=FtpClient(sockfd)
    while True:
        print("\n================命令选项==================")
        print("****************1.list*******************")
        print("****************2.download file**********")
        print("****************3.upload file************")
        print("****************4.quit*******************")
        print("=========================================")
        cmd=input("输入命令(1/2/3/4)：")
        if cmd.strip()=="1":
            ftp.get_list()
        elif cmd.strip()=="2":
            filename=input("请输入要下载的文件名：")
            ftp.download_file(filename)
        elif cmd.strip()=="3":
            filename = input("请输入要上传的文件名：")
            ftp.upload_file(filename)
        elif cmd.strip()=="4":
            ftp.do_quit()

def main():
    sockfd=socket()
    ADDR=("127.0.0.1",8888)
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("链接服务器失败",e)
        return
    else:
        print("""
            *********************************
                Data        File       Image
            *********************************
        """)
        cls = input("请输入文件类型:")
        if cls not in ["Data","File","Image"]:
            print("Sorry  for  input  Error")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)   #发送具体请求


    sockfd.close()
if __name__=="__main__":
    main()
