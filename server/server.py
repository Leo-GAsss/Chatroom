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

    def showPeerAddr(self, peerCxn: QTcpSocket) -> str:
        return f"{peerCxn.peerAddress().toString()}:{peerCxn.peerPort()}"

    def addConnection(self):
        clientCxn = self.tcpServer.nextPendingConnection()
        self.cxns.append(clientCxn)
        print(
            QDateTime.currentDateTime().toString("hh:mm:ss yyyy-MM-dd\t"),
            self.showPeerAddr(clientCxn), "Joined"
        )

        clientCxn.readyRead.connect(self.receiveMessage)
        clientCxn.disconnected.connect(self.removeConnection)

    def receiveMessage(self):  
        clientCxn = self.sender()
        print(
            QDateTime.currentDateTime().toString("hh:mm:ss yyyy-MM-dd\t"),
            self.showPeerAddr(clientCxn), "Received Msg"
        )

        recvMsg = bytes(clientCxn.readAll()).decode('utf-8')
        if len(recvMsg) > msgMaxiLength:
            clientCxn.write(bytes('System|Too long to send!', encoding="utf-8"))
            return

        recvMsg = html.escape(recvMsg, quote = True)
        recvMsg = re.sub(r'\n\s*\n', '\n\n', recvMsg)
        for cxn in self.cxns:
            cxn.write(bytes(recvMsg, encoding="utf-8"))

    def removeConnection(self):
        clientCxn = self.sender()
        print(
            QDateTime.currentDateTime().toString("hh:mm:ss yyyy-MM-dd\t"),
            self.showPeerAddr(clientCxn), "Disconnected"
        )
        self.cxns.remove(clientCxn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = tcpServer()
    app.exec_()