# coding=utf-8

import sys, time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

HOST = QHostAddress.AnyIPv4
PORT = 10086    

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
        recvMsg = clientCxn.readAll()
        for cxn in self.cxns:
            cxn.write(recvMsg)

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