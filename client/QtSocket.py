# coding=utf-8  

import sys, icon
import resources.resources
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.ui_main import Ui_MainWindow
from ui.ui_config import Ui_Dialog as Ui_ConfigWindow

class ConfigWindow(QDialog, Ui_ConfigWindow):                    #多重继承

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        font = QFont(":/consolas.ttf");
        font.setStyleHint(QFont.Monospace);
        self.setFont(font);
        self.setWindowIcon(QIcon(":/icon.ico"))
        self.yesButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
    def setData(self,ipString,nameString):
        
        self.ipEdit.setText(ipString)
        self.nameEdit.setText(nameString)
        
    def returnData(self):
        
        return {'Ip':self.ipEdit.text(),'Name':self.nameEdit.text()}
        

class MainWindow(QMainWindow, Ui_MainWindow):                    #多重继承

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.inits()

        self.setWindowIcon(QIcon(':/icon.ico'))

    def inits(self):

        self.ipAddress=''
        self.userName='Anonymous'
        self.configWin=ConfigWindow()
        self.chatBox.setCursorWidth(0)
        self.recvFlag=0
        
        self.cxn = QTcpSocket()
        
        self.cxn.readyRead.connect(self.readMsg)
        self.configButton.clicked.connect(self.configGo)
        self.sendButton.clicked.connect(self.sendMsg)
        self.sendBox.installEventFilter(self)

        
    def configGo(self):
        self.configWin.ipEdit.setFocus()
        if self.configWin.exec() == QDialog.Accepted :
            rtnData = self.configWin.returnData()
            # Verify IP Address
            rtnAddr = rtnData['Ip'].replace('：', ':')
            if not rtnAddr.split(':')[0]:
                QMessageBox.warning(self,"Error",'Please enter the IP Address',QMessageBox.Ok,QMessageBox.Ok)
                self.configWin.setData(self.ipAddress, self.userName)
                return            
            elif not ':' in rtnAddr or not rtnAddr.split(':')[1].isdigit():
                QMessageBox.warning(self,"Error",'Please enter the port number',QMessageBox.Ok,QMessageBox.Ok)
                self.configWin.setData(self.ipAddress, self.userName)
                return
            
            if '|' in rtnData['Name']:
                QMessageBox.warning(self,"Error",'The user name contain illegal character: "|"',QMessageBox.Ok,QMessageBox.Ok)
                self.configWin.setData(self.ipAddress, self.userName)
                return       
            elif self.ipAddress == rtnData['Ip']:
                self.userName = rtnData['Name']
                return
            
            self.ipAddress = rtnData['Ip'].replace('：', ':')
            self.userName = rtnData['Name']
            if not self.userName:
                self.userName = 'Anonymous'

            serverIP = self.ipAddress.split(':')[0]
            serverPort = self.ipAddress.split(':')[1]

            self.cxn.connectToHost(serverIP, int(serverPort))
            self.chatBox.clear()
            self.chatBox.insertHtml(welcomeMsg)
            self.sendBox.setFocus()

        else :
            self.configWin.setData(self.ipAddress,self.userName)
            


    def readMsg(self):
        dataReceived = self.cxn.readAll()
        
        self.chatBox.moveCursor(QTextCursor.End)
        recvString=bytes(dataReceived.data()).decode('utf8')
        recvString=recvString.replace('\n',"<br />")
        self.chatBox.insertHtml(
            htmlString.format(
                recvString.split('|')[0],
                QDateTime.currentDateTime().toString("hh:mm:ss MM/dd"),
                recvString[recvString.find('|')+1:]
            )
        )
        self.chatBox.verticalScrollBar().setValue(self.chatBox.verticalScrollBar().maximum())
    
    def sendMsg(self):
        if not self.ipAddress:
            QMessageBox.warning(self,"Error",'Please connect to the server first',QMessageBox.Ok,QMessageBox.Ok)
            return
        
        msg=bytes(self.userName+'|'+self.sendBox.toPlainText(),encoding='utf-8')
        self.cxn.write(msg)
        self.sendBox.clear()
        
    def eventFilter(self,obj,e):
        
        if obj != self.sendBox or not self.configWin.enterCheck.isChecked():
            return False
        if e.type() == QEvent.KeyPress:
            if e.key()==Qt.Key_Return or e.key()==Qt.Key_Enter:
                self.sendMsg()
                return True
        return False

htmlString=r"""
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style="color:#666666;font-size:10pt;">{0}&nbsp;&nbsp;</span><span style="color:#C0C0C0;font-size:9pt;">{1}</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style="font-size:14pt; color:#000000;">{2}</span></p>
<span style=" -qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt; font-size:7pt; color:#000000;"><br /></span>
"""

welcomeMsg='<p style="font-family:Consolas">You have entered the Chat Room</p><br />'
        
if __name__ == '__main__':

        app = QApplication(sys.argv)
        ex = MainWindow()
        ex.show()
        sys.exit(app.exec_())