# coding=utf-8

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

PORT = 10086    

class tcpClient(QObject):
    def __init__(self):
        super().__init__()
        HOST = '127.0.0.1'
        PORT = 10086
        self.tcpSocket = QTcpSocket()
        self.tcpSocket.connectToHost(HOST, PORT)
        self.tcpSocket.write(bytes("Hello, world", encoding='utf-8'))
        self.tcpSocket.readyRead.connect(self.dealCommunication)
        self.tcpSocket.error.connect(self.displayError)

    def dealCommunication(self):
        print("connected !\n")
        # i want here to send and receive messages

    def displayError(self):
        print(self, "The following error occurred: %s." % self.tcpSocket.errorString())

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    client = tcpClient()
    sys.exit(app.exec_())
