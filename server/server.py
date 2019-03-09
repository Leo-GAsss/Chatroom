# -*- coding: utf-8 -*-

import sys, time, re, html
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

HOST = QHostAddress.AnyIPv4
PORT = 10086    
msgMaxiLength = 200

class tcpServer(QObject):

    def __init__(self):
        super().__init__()

        self.tcpServer = QTcpServer(self)
        self.tcpServer.listen(HOST, PORT)
        self.tcpServer.newConnection.connect(self.addConnection)
        self.cxns = []

    def showCxnLog(self, peerCxn, log) -> str:
        print(
            QDateTime.currentDateTime().toString("hh:mm:ss yyyy-MM-dd\t"),
            f"{peerCxn.peerAddress().toString()}:{peerCxn.peerPort()}",
            log
        )

    def addConnection(self):
        clientCxn = self.tcpServer.nextPendingConnection()
        self.cxns.append(clientCxn)
        self.showCxnLog(clientCxn, "Joined")

        clientCxn.readyRead.connect(self.receiveMessage)
        clientCxn.disconnected.connect(self.removeConnection)

    def receiveMessage(self):  
        clientCxn = self.sender()
        self.showCxnLog(clientCxn, "Received Msg")

        try:
            recvMsg = bytes(clientCxn.readAll()).decode('utf-8')
        except:
            clientCxn.write(bytes('System|Invalid encoding!', encoding="utf-8"))
            self.showCxnLog(clientCxn, "Invalid encoding")
            return
        
        if len(recvMsg) > msgMaxiLength:
            clientCxn.write(bytes('System|Too long to send!', encoding="utf-8"))
            self.showCxnLog(clientCxn, "Too long to send")
            return
        elif not '|' in recvMsg:
            clientCxn.write(bytes('System|Invalid message format!', encoding="utf-8"))
            self.showCxnLog(clientCxn, "Invalid msg format")
            return

        recvMsg = html.escape(recvMsg, quote = True)
        recvMsg = re.sub(r'\n\s*\n', '\n\n', recvMsg)
        for cxn in self.cxns:
            cxn.write(bytes(recvMsg, encoding="utf-8"))

    def removeConnection(self):
        clientCxn = self.sender()
        self.showCxnLog(clientCxn, "Disconnected")
        self.cxns.remove(clientCxn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = tcpServer()
    app.exec_()