from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.uic import loadUi
import sys
import sqlite3
import time
import os
from datetime import date
import smtplib
import pandas as pd

class EditPackageDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(EditPackageDialog, self).__init__(*args, **kwargs)
        loadUi('GUIs/EditPackageInfo.ui',self) 
        self.btn_load.clicked.connect(self.LoadPackageInfo)
        self.btn_save.clicked.connect(self.EditPackage)
        
    def LoadPackageInfo(self):
        start_tracking = self.tracking_number.text()
        searchresult = '"'+start_tracking+'"'
        
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        result = self.c.execute("SELECT * from Packages WHERE tracking_number="+str(searchresult))
        row = result.fetchone()
        
        current_tracking = str(row[0])
        current_name = str(row[1])
        current_datein = str(row[2])
        current_dateout = str(row[3])
        empty = ''

        
        
        self.conn.commit()
        self.c.close()
        self.conn.close()
        
        self.update_tracking.setPlaceholderText(current_tracking)        
        self.update_name.setPlaceholderText(current_name)
        self.update_datein.setPlaceholderText(current_datein)
        if current_dateout is empty:
            self.update_dateout.setPlaceholderText("Outstanding")
        else:
            self.update_dateout.setPlaceholderText(current_dateout)




    def EditPackage(self):
        tracking_number = ""
        recipient = ""
        date_in = ""
        date_out = ""
        
        start_tracking = self.tracking_number.text()
        tracking_number = self.update_tracking.text()
        recipient = self.update_name.text()
        date_in = self.update_datein.text()
        date_out = self.update_dateout.text()
                
        
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()

            if self.box_name.isChecked():
                self.c.execute("UPDATE Packages SET recipient = ? WHERE tracking_number = ?",(recipient,start_tracking))
            if self.box_datein.isChecked():
                self.c.execute("UPDATE Packages SET date_in = ? WHERE tracking_number = ?",(date_in,start_tracking))
            if self.box_dateout.isChecked():
                self.c.execute("UPDATE Packages SET date_out = ? WHERE tracking_number = ?",(date_out,start_tracking))
            if self.box_tracking.isChecked():
                self.c.execute("UPDATE Packages SET tracking_number = ? WHERE tracking_number = ?",(tracking_number,start_tracking))


            print(self.c.execute)
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'Successful','Package info has been successfully updated to the Package Tracker.')
            self.close()

                                   
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not edit package info to the Package Tracker.')
            self.close()    
    

class CheckInPackageDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(CheckInPackageDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Save Package")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")

        self.setWindowTitle("Check In Package")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.QBtn.clicked.connect(self.InPackage)

        layout = QVBoxLayout()
        
        
        
        self.check_in_recipient = QLineEdit(self)
        self.check_in_recipient.setPlaceholderText("Soldier's Name")
        self.check_in_recipient.setAlignment(QtCore.Qt.AlignCenter)
        self.check_in_recipient.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        
        layout.addWidget(self.check_in_recipient)
        

        self.check_in_tracking_number = QLineEdit()
        self.check_in_tracking_number.setPlaceholderText("Tracking Number")
        self.check_in_tracking_number.setAlignment(QtCore.Qt.AlignCenter)
        self.check_in_tracking_number.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")

        layout.addWidget(self.check_in_tracking_number)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
        
    def InPackage(self):
        
        today = date.today().strftime('%d%b%Y')

        tracking_number = ""
        recipient = ""
        date_in = today.upper()
        date_out = ""
        
        tracking_number = self.check_in_tracking_number.text()
        recipient = self.check_in_recipient.text()

                
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            self.c.execute("INSERT INTO Packages(tracking_number,recipient,date_in,date_out) VALUES (?,?,?,?)",(tracking_number,recipient,date_in,date_out))
            print(self.c.execute)
            self.conn.commit()
            self.c.close()
            self.conn.close()
            
            recipient = ""
            recipient = self.check_in_recipient.text()

              
            try:
                
                searchresult = '"'+recipient+'"'

                conn = sqlite3.connect("database.db")
                c = conn.cursor()
                result = c.execute("SELECT email from Soldier WHERE Soldier="+str(searchresult))
                row = result.fetchone()
                conn.commit()
                c.close()
                conn.close()

                db = sqlite3.connect('database.db')
                df = pd.read_sql_query('SELECT * FROM Email', db)
                info = df.values.tolist()


                sender_email = info[0][0]
                rec_email = row
                password = str(info[0][1])
                subject = 'Package In The Maill Room'

                msg = recipient + ", \nYou have recieved a package with the tracking number " + tracking_number + ". Please come to the mailroom in the HHC Barracks mailroom in the hours of blah and blah. \nThank You \n\n-Mailroom"
                message = 'Subject: {}\n\n{}'.format(subject, msg)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                print("Login success")
                server.sendmail(sender_email, rec_email, message)
                print("Email has been sent to ", rec_email)

                QMessageBox.information(QMessageBox(),'Successful','Package has been successfully added to the Package Tracker and an email has been sent to ' + recipient + '.')
                self.close()
                
            except Exception:
                    
                QMessageBox.information(QMessageBox(),'Successful','Package has been successfully added to the Package Tracker but an email was not sent to ' + recipient + '.')
                self.close()
            
          
                                                          
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add Package to the Package Tracker.')
            self.close()

class CheckOutPackageDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(CheckOutPackageDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Check Out Package")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")


        self.setWindowTitle("Check Out Package")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.QBtn.clicked.connect(self.OutPackage)

        layout = QVBoxLayout()

        self.check_out_tracking_number = QLineEdit()
        self.check_out_tracking_number.setPlaceholderText("Tracking Number")
        self.check_out_tracking_number.setAlignment(QtCore.Qt.AlignCenter)
        self.check_out_tracking_number.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.check_out_tracking_number)
     

        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
    def OutPackage(self):
        
        today = date.today().strftime('%d%b%Y')

        
        tracking_number = self.check_out_tracking_number.text()
        date_out = today.upper()
     
        #try:
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        self.c.execute("UPDATE Packages SET date_out = ? WHERE tracking_number = ?",(date_out,tracking_number))
        print(self.c.execute)
        self.conn.commit()
        self.c.close()
        self.conn.close()            
            
              
            #try:
        tracking_number = self.check_out_tracking_number.text()

        tracking = '"'+tracking_number+'"'


        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        result = c.execute("SELECT * from Packages WHERE tracking_number="+str(tracking))
        recipt = result.fetchone()
        email = str(row[2])
        conn.commit()
        c.close()
        conn.close()
        print(recipt)
        searchresult = '"'+recipt+'"'

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        result = c.execute("SELECT email from Soldier WHERE soldier="+str(searchresult))
        resultmail = str(result.fetchone())
        conn.commit()
        c.close()
        conn.close()
        print(resultmail)

        db = sqlite3.connect('database.db')
        df = pd.read_sql_query('SELECT * FROM Email', db)
        info = df.values.tolist()

        sender_email = info[0][0]
        rec_email = resultmail
        password = str(info[0][1])
        subject = "Package Pickup Confirmation"

        msg = searchresult + ", \n This is a confirmation email stating you have received your package with the tracking number " + tracking_number + ". \n Thank You \n\n-Mailroom"
        message = 'Subject: {}\n\n{}'.format(subject, msg)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        print("Login success")
        server.sendmail(sender_email, rec_email, message)
        print("Email has been sent to ", rec_email)

        QMessageBox.information(QMessageBox(),'Successful','Package has been successfully added to the Package Tracker and an email has been sent.')
        self.close()

            #except Exception:
                    
                #QMessageBox.information(QMessageBox(),'Successful','Package is checked out of the database but the soldier does not have an email in the database')
                #self.close()
            
          
                                                                    
        #except Exception:
            #QMessageBox.warning(QMessageBox(), 'Error', 'Could not check out package.')
            #self.close()

class PackageLookupDialog(QDialog):
    def __init__(self, *args, **kwargs):

        super(PackageLookupDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")


        loadUi('GUIs/PackageLookupNameDailog.ui',self)

        self.btn_search.clicked.connect(self.loaddata)


        self.loaddata()


    def loaddata(self):

        searchrol = self.search_soldier.text()

        searchresult = '"'+searchrol+'"'
        
        lookup_name = 'Name'
        lookup_tracking = 'Tracking Number'
        
        outstanding = 'Outstanding Packages'
        todo = 'All Packages'
        
        lookup = self.lookupcombo.itemText(self.lookupcombo.currentIndex())
        
        package_ammount = self.packagecombo.itemText(self.packagecombo.currentIndex())

        
        if lookup in lookup_name:
            
            if package_ammount in outstanding:

                self.package_list.setAlternatingRowColors(True)
                self.package_list.setColumnCount(4)
                self.package_list.setColumnWidth(0,200)
                self.package_list.setColumnWidth(1,200)
                self.package_list.setColumnWidth(2,100)
                self.package_list.setColumnWidth(3,100)
                self.package_list.horizontalHeader().setCascadingSectionResizes(False)
                self.package_list.horizontalHeader().setSortIndicatorShown(False)
                self.package_list.horizontalHeader().setStretchLastSection(True)
                self.package_list.verticalHeader().setVisible(False)
                self.package_list.verticalHeader().setCascadingSectionResizes(False)
                self.package_list.verticalHeader().setStretchLastSection(False)
                self.package_list.setHorizontalHeaderLabels(("Tracking Number", "Soldier", "Date In", "Date Out"))
                self.package_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
        "alternate-background-color: rgb(124, 136, 126);\n"
        "border-color: rgb(160, 141, 131);\n"
        "gridline-color: rgb(145, 150, 127);")
                self.package_list.show()


                self.connection = sqlite3.connect("database.db")
                query = "SELECT * from Packages WHERE recipient IS "+str(searchresult)+ " and date_out IS ''"
                result = self.connection.execute(query)
                print(query)
                self.package_list.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.package_list.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.package_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
                self.connection.close()
                
            if package_ammount in todo:

                self.package_list.setAlternatingRowColors(True)
                self.package_list.setColumnCount(4)
                self.package_list.setColumnWidth(0,200)
                self.package_list.setColumnWidth(1,200)
                self.package_list.setColumnWidth(2,100)
                self.package_list.setColumnWidth(3,100)
                self.package_list.horizontalHeader().setCascadingSectionResizes(False)
                self.package_list.horizontalHeader().setSortIndicatorShown(False)
                self.package_list.horizontalHeader().setStretchLastSection(True)
                self.package_list.verticalHeader().setVisible(False)
                self.package_list.verticalHeader().setCascadingSectionResizes(False)
                self.package_list.verticalHeader().setStretchLastSection(False)
                self.package_list.setHorizontalHeaderLabels(("Tracking Number", "Soldier", "Date In", "Date Out"))
                self.package_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
        "alternate-background-color: rgb(124, 136, 126);\n"
        "border-color: rgb(160, 141, 131);\n"
        "gridline-color: rgb(145, 150, 127);")
                self.package_list.show()


                self.connection = sqlite3.connect("database.db")
                query = "SELECT * from Packages WHERE recipient IS "+str(searchresult)
                result = self.connection.execute(query)
                print(query)
                self.package_list.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.package_list.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.package_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
                self.connection.close()
                
        if lookup in lookup_tracking:
            self.package_list.setAlternatingRowColors(True)
            self.package_list.setColumnCount(4)
            self.package_list.setColumnWidth(0,200)
            self.package_list.setColumnWidth(1,200)
            self.package_list.setColumnWidth(2,100)
            self.package_list.setColumnWidth(3,100)
            self.package_list.horizontalHeader().setCascadingSectionResizes(False)
            self.package_list.horizontalHeader().setSortIndicatorShown(False)
            self.package_list.horizontalHeader().setStretchLastSection(True)
            self.package_list.verticalHeader().setVisible(False)
            self.package_list.verticalHeader().setCascadingSectionResizes(False)
            self.package_list.verticalHeader().setStretchLastSection(False)
            self.package_list.setHorizontalHeaderLabels(("Tracking Number", "Soldier", "Date In", "Date Out"))
            self.package_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
    "alternate-background-color: rgb(124, 136, 126);\n"
    "border-color: rgb(160, 141, 131);\n"
    "gridline-color: rgb(145, 150, 127);")
            self.package_list.show()


            self.connection = sqlite3.connect("database.db")
            query = "SELECT * from Packages WHERE tracking_number IS "+str(searchresult)
            result = self.connection.execute(query)
            print(query)
            self.package_list.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.package_list.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.package_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
            self.connection.close()


class DeletePackageDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeletePackageDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Delete")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")

        self.setWindowTitle("Delete Package")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.DeleteSoldier)
        layout = QVBoxLayout()

        self.deleteinput = QLineEdit()
        self.deleteinput.setPlaceholderText("Tracking Number")
        self.deleteinput.setAlignment(QtCore.Qt.AlignCenter)
        self.deleteinput.setStyleSheet("background-color: rgb(240, 170, 54);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.deleteinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)

    def DeleteSoldier(self):

        delrol = ""
        delrol = self.deleteinput.text()
        
        delresult = '"'+delrol+'"'
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            self.c.execute("DELETE from Packages WHERE tracking_number="+str(delresult))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'Successful','Package has been deleted from the Package Trackerr')
            self.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not delete package from the Package Tracker.')

class AddSoldierDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(AddSoldierDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Add Soldier")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")

        self.setWindowTitle("Add Soldier")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.QBtn.clicked.connect(self.InSoldier)

        layout = QVBoxLayout()

        self.soldier_add = QLineEdit()
        self.soldier_add.setPlaceholderText("Soldier's Name")
        self.soldier_add.setAlignment(QtCore.Qt.AlignCenter)
        self.soldier_add.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.soldier_add)
        
        
        self.barracks_add = QComboBox()
        self.barracks_add.addItem("HHC")
        self.barracks_add.addItem("GSB")
        self.barracks_add.addItem("17 Fires")
        self.barracks_add.addItem("Other")
        self.barracks_add.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"selection-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";\n"
"alternate-background-color: rgb(255, 255, 255);")
        layout.addWidget(self.barracks_add)
        
        self.email_add = QLineEdit()
        self.email_add.setPlaceholderText("Email")
        self.email_add.setAlignment(QtCore.Qt.AlignCenter)
        self.email_add.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.email_add)
     

        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
        
    def InSoldier(self):
        
        soldier = ""
        barracks = ""
        email = ""
        
        soldier = self.soldier_add.text()
        barracks = self.barracks_add.itemText(self.barracks_add.currentIndex())
        email = self.email_add.text()
                
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            self.c.execute("INSERT INTO Soldier(soldier,barracks,email) VALUES (?,?,?)",(soldier,barracks,email))
            print(self.c.execute)
            self.conn.commit()
            self.c.close()
            self.conn.close()
            
            try:

                soldier_name = soldier
                row = '"'+email+'"'

                db = sqlite3.connect('database.db')
                df = pd.read_sql_query('SELECT * FROM Email', db)
                info = df.values.tolist()

                sender_email = info[0][0]
                rec_email = row
                password = str(info[0][1])
                subject = "Email Confirmation"

                msg = soldier_name + ", \n\n \n\n This is a confirmation email from the mailroom. Thank you for signing up for email alerts. \n\n \n\n-Mail Room"
                message = 'Subject: {}\n\n{}'.format(subject, msg)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                print("Login success")
                server.sendmail(sender_email, rec_email, message)
                print("Email has been sent to ", rec_email)

                QMessageBox.information(QMessageBox(),'Successful',soldier_name+ ' has been added to the Package Tracker and a confirmation email has successfully been sent.')
                self.close()
                
            except Exception:

                QMessageBox.warning(QMessageBox(),'Warning', soldier_name+' has been added to the Package Tracker but a confirmation email was unsuccessfully sent.')
                self.close()

                                   
                                   
        except Exception:
            QMessageBox.critical(QMessageBox(), 'Error', 'Could not add Soldier to the Package Tracker.')
            self.close()

class EditSoldierDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(EditSoldierDialog, self).__init__(*args, **kwargs)
        loadUi('GUIs/EditSoldierInfo.ui',self)
        
        
        self.btn_load.clicked.connect(self.LoadSoldierInfo)
        self.btn_save.clicked.connect(self.EditSoldier)
        
    def LoadSoldierInfo(self):
        start_soldier = self.soldier_name.text()
        searchresult = '"'+start_soldier+'"'
        
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        result = self.c.execute("SELECT * from soldier WHERE soldier="+str(searchresult))
        row = result.fetchone()
        
        current_name = str(row[0])
        current_barracks = str(row[1])
        print(current_barracks)
        current_email = str(row[2])
        
        HHC = 'HHC'
        GSB = "GSB"
        Fires = '17 Fires'
        Other = 'Other'
        
        self.conn.commit()
        self.c.close()
        self.conn.close()
        
        self.update_name.setPlaceholderText(current_name)
        #self.update_barracks.
        if current_barracks in HHC:
            self.update_barracks.setCurrentIndex(0)
        if current_barracks in GSB:
            self.update_barracks.setCurrentIndex(1)
        if current_barracks in Fires:
            self.update_barracks.setCurrentIndex(2)
        if current_barracks in Other:
            self.update_barracks.setCurrentIndex(3)
        self.update_email.setPlaceholderText(current_email)
        

    def EditSoldier(self):
        soldier_name = ""
        soldier = ""
        barracks = ""
        email = ""
        
        soldier_name = self.soldier_name.text()
        soldier = self.update_name.text()
        barracks = self.update_barracks.itemText(self.update_barracks.currentIndex())
        email = self.update_email.text()
                
        
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()

            if self.box_barracks.isChecked():
                self.c.execute("UPDATE Soldier SET barracks = ? WHERE soldier = ?",(barracks,soldier_name))
            if self.box_email.isChecked():
                self.c.execute("UPDATE Soldier SET email = ? WHERE soldier = ?",(email,soldier_name))
            if self.box_name.isChecked():
                self.c.execute("UPDATE Soldier SET soldier = ? WHERE soldier = ?",(soldier,soldier_name))

            print(self.c.execute)
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'Successful','Soldier info has been successfully updated to the Package Tracker.')
            self.close()

                                   
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not edit soldier info to the Package Tracker.')
            self.close()

class DeleteSoldierDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeleteSoldierDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Delete")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")

        self.setWindowTitle("Delete Soldier")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.DeleteSoldier)
        layout = QVBoxLayout()

        self.deleteinput = QLineEdit()
        self.deleteinput.setPlaceholderText("Soldier")
        self.deleteinput.setAlignment(QtCore.Qt.AlignCenter)
        self.deleteinput.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.deleteinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)

    def DeleteSoldier(self):

        delrol = ""
        delrol = self.deleteinput.text()
        
        delresult = '"'+delrol+'"'
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            self.c.execute("DELETE from Soldier WHERE soldier="+str(delresult))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'Successful',delrol+' has been deleted from the Package Tracker')
            self.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not delete ' + delrol + ' from the Package Tracker.')

class SearchSoldierDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchSoldierDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Soldier Information Lookup")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")


        self.setWindowTitle("Soldier Infomation Lookup")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.SoldierLookup)
        

        layout = QVBoxLayout()
        
        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText("Soldier Name")
        self.searchinput.setAlignment(QtCore.Qt.AlignCenter)
        self.searchinput.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.searchinput)
        
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
    


    def SoldierLookup(self):

        searchrol = ""
        searchrol = self.searchinput.text()
        
        searchresult = '"'+searchrol+'"'
        
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            result = self.c.execute("SELECT * from Soldier WHERE Soldier="+str(searchresult))
            row = result.fetchone()
            serachresult = "Soldier Name : "+str(row[0])+'\n'+"Soldier's Barracks : "+str(row[1])+'\n'+"Soldier's Email : "+str(row[2])
            QMessageBox.information(QMessageBox(), 'Successful', serachresult)
            self.conn.commit()
            self.c.close()
            self.conn.close()
            
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find package from the Package Tracker.')


class SoldierEmailConfirmationDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(SoldierEmailConfirmationDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 10pt \"Courier New\";\n"
"")

        self.QBtn = QPushButton()
        self.QBtn.setText("Send Email Confirmation")
        self.QBtn.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"font: 13pt \"Courier\";")

        self.setWindowTitle("EmailConfirmation")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.QBtn.clicked.connect(self.SendEmailConfirmation)

        layout = QVBoxLayout()

        self.email_soldier = QLineEdit()
        self.email_soldier.setPlaceholderText("Soldier's Name")
        self.email_soldier.setAlignment(QtCore.Qt.AlignCenter)
        self.email_soldier.setStyleSheet("background-color: rgb(255, 184, 28);\n"
"border-color: rgb(0, 0, 0);\n"
"border-style:inset;\n"
"font: 13pt \"Courier\";")
        layout.addWidget(self.email_soldier)
        
       
    
     

        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
    def SendEmailConfirmation(self):

        soldier_name = ''

        soldier_name = self.email_soldier.text()

        try:

            searchresult = '"'+soldier_name+'"'

            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            result = c.execute("SELECT email from Soldier WHERE Soldier="+str(searchresult))
            row = result.fetchone()
            conn.commit()
            c.close()
            conn.close()

            db = sqlite3.connect('database.db')
            df = pd.read_sql_query('SELECT * FROM Email', db)
            info = df.values.tolist()

            sender_email = info[0][0]
            rec_email = row
            password = str(info[0][1])
            subject = "Email Confirmation"

            msg = soldier_name + ", \nThis is a confirmation email from the mailroom. Thank you for signing up for email alerts. \n\n-Mail Room"
            message = 'Subject: {}\n\n{}'.format(subject, msg)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            print("Login success")
            server.sendmail(sender_email, rec_email, message)
            print("Email has been sent to ", rec_email)

            QMessageBox.information(QMessageBox(),'Successful','Confirmation email successfully sent.')
            self.close()

        except Exception:

            QMessageBox.warning(QMessageBox(),'Error','Confirmation email unsuccessfully sent')
            self.close()

class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: rgb(28, 66, 32);\n"
"font: 14pt \"Courier New\";\n"
"")

        self.setFixedWidth(600)
        self.setFixedHeight(400)

        QBtn = QDialogButtonBox.Ok  
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        
        self.setWindowTitle("About")
        title = QLabel("Package Tracker")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        layout.addWidget(QLabel("v1.0"))

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

# HomeScreen
class Home(QMainWindow):
    def __init__(self):
        super(Home,self).__init__()
        self.setWindowTitle("Package Tracker")
        self.setWindowIcon(QIcon('GroupMail.png'))  #window icon

        loadUi('GUIs/HomeScreenNew.ui',self)

        
        self.btn_packages.clicked.connect(self.GoToPackageScreen)
        self.btn_soldiers.clicked.connect(self.GoToSoldiersScreen)
        self.btn_home.clicked.connect(self.GoToHomeScreen)
        self.btn_refresh.clicked.connect(self.GoToHomeScreen)
        
    # Menu Bar
        # Package Tracker
        self.homeHome_Page.triggered.connect(self.GoToHomeScreen)
        self.homeAbout.triggered.connect(self.About)
        
        # Packages
        self.homePackage_Page.triggered.connect(self.GoToPackageScreen)
        self.homeCheck_In.triggered.connect(self.CheckInPackage)
        self.homeCheck_Out.triggered.connect(self.CheckOutPackage)
        self.homePackage_Lookup.triggered.connect(self.PackageLookup)
        self.homeEdit_Package.triggered.connect(self.EditPackage)
        #self.homeResendEmail.triggered.connect(self.)
        self.homeDelete_Package.triggered.connect(self.DeletePackage)
        
        # Soldiers
        self.homeSoldiers_Page.triggered.connect(self.GoToSoldiersScreen)
        self.homeAdd.triggered.connect(self.AddSoldier)
        self.homeEdit.triggered.connect(self.EditSoldier)
        self.homeSearch.triggered.connect(self.SearchSoldier)
        self.homeDelete.triggered.connect(self.DeleteSoldier)
        self.homeSend_Email_Confirmation.triggered.connect(self.SoldierEmailConfirmation)


        
        self.loaddata()
        

    def loaddata(self):

        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS Packages(Tracking_Number TEXT PRIMARY KEY,Recipient TEXT,DateIn TEXT,DateOut TEXT)")
        self.c.close()
        
                
        #self.package_list = QtWidgets.QTableWidget()
        #self.package_list = QtWidgets.QTableWidget(self.centralwidget)
        #self.package_list.setGeometry(QtCore.QRect(20, 250, 1500, 510))
        self.package_list.setAlternatingRowColors(True)
        self.package_list.setColumnCount(4)
        self.package_list.setColumnWidth(0,610)
        self.package_list.setColumnWidth(1,610)
        self.package_list.setColumnWidth(2,125)
        self.package_list.setColumnWidth(3,125)
        self.package_list.horizontalHeader().setCascadingSectionResizes(False)
        self.package_list.horizontalHeader().setSortIndicatorShown(False)
        self.package_list.horizontalHeader().setStretchLastSection(True)
        self.package_list.verticalHeader().setVisible(False)
        self.package_list.verticalHeader().setCascadingSectionResizes(False)
        self.package_list.verticalHeader().setStretchLastSection(False)
        self.package_list.setHorizontalHeaderLabels(("Tracking Number", "Soldier", "Date In", "Date Out"))
        self.package_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
"alternate-background-color: rgb(124, 136, 126);\n"
"border-color: rgb(160, 141, 131);\n"
"gridline-color: rgb(145, 150, 127);")
        
        
        self.connection = sqlite3.connect("database.db")
        query = "SELECT * FROM Packages WHERE date_out IS ''"
        result = self.connection.execute(query)
        self.package_list.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.package_list.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.package_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
        self.connection.close()

        self.package_list.setSortingEnabled(True)
        self.package_list.sortByColumn(1, Qt.AscendingOrder)
        
        
    def GoToHomeScreen(self):
        movehome = Home()
        widget.addWidget(movehome)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def GoToPackageScreen(self):
        movepackages = PackageScreen()
        widget.addWidget(movepackages)
        widget.setCurrentIndex(widget.currentIndex()+1)   
        
    def GoToSoldiersScreen(self):
        movesoldiers = SoldiersScreen()
        widget.addWidget(movesoldiers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def EditPackage(self):
        dlg = EditPackageDialog()
        dlg.exec_()
        
    def CheckInPackage(self):
        dlg = CheckInPackageDialog()
        dlg.exec_()
        
    def CheckOutPackage(self):
        dlg = CheckOutPackageDialog()
        dlg.exec_()  
        
    def DeletePackage(self):
        dlg =  DeletePackageDialog()
        dlg.exec_()  
        
    def PackageLookup(self):
        dlg = PackageLookupDialog()
        dlg.exec_()
        
    def AddSoldier(self):
        dlg = AddSoldierDialog()
        dlg.exec_()
        
    def EditSoldier(self):
        dlg = EditSoldierDialog()
        dlg.exec_() 
        
    def SearchSoldier(self):
        dlg = SearchSoldierDialog()
        dlg.exec_()        
        
        
    def DeleteSoldier(self):
        dlg = DeleteSoldierDialog()
        dlg.exec_()   
        
    def SoldierEmailConfirmation(self):
        dlg = SoldierEmailConfirmation()
        dlg.exec_()
        
    def About(self):
        dlg = AboutDialog()
        dlg.exec_()

class PackageScreen(QMainWindow):
    def __init__(self):
        super(PackageScreen,self).__init__()
        self.setWindowIcon(QIcon('GroupMail.png'))  #window icon

        loadUi('GUIs/PackagesScreenNew.ui',self)
        self.btn_home.clicked.connect(self.GoToHomeScreen)
        self.btn_checkin.clicked.connect(self.CheckInPackage)
        self.btn_checkout.clicked.connect(self.CheckOutPackage)
        self.btn_lookup.clicked.connect(self.PackageLookup)
        self.btn_refresh.clicked.connect(self.loaddata)
        
        self.package_list.setSortingEnabled(True)
        self.package_list.sortByColumn(1, Qt.AscendingOrder)
        
    # Menu Bar
        # Package Tracker
        self.PackagesHome_Page.triggered.connect(self.GoToHomeScreen)
        self.PackagesAbout.triggered.connect(self.About)
        
        # Packages
        self.PackagesPackage_Page.triggered.connect(self.GoToPackageScreen)
        self.PackagesCheck_In.triggered.connect(self.CheckInPackage)
        self.PackagesCheck_Out.triggered.connect(self.CheckOutPackage)
        self.PackagesPackage_Lookup.triggered.connect(self.PackageLookup)
        self.PackagesEdit_Package.triggered.connect(self.EditPackage)
        #self.PackagesResend_Email_Package.triggered.connect(self.)
        self.PackagesDelete_Package.triggered.connect(self.DeletePackage)
        
        # Soldiers
        self.PackagesSoldiers_Page.triggered.connect(self.GoToSoldiersScreen)
        self.PackagesAdd.triggered.connect(self.AddSoldier)
        self.PackagesEdit.triggered.connect(self.EditSoldier)
        self.PackagesSearch.triggered.connect(self.SearchSoldier)
        self.PackagesDelete.triggered.connect(self.DeleteSoldier)
        self.PackagesResend_Email_Soldier.triggered.connect(self.SoldierEmailConfirmation)
        
    
        self.loaddata()

        
        
    def loaddata(self):
        
        if self.todopackages.isChecked():
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            self.c.execute("CREATE TABLE IF NOT EXISTS Packages(Tracking_Number TEXT PRIMARY KEY,Recipient TEXT,DateIn TEXT,DateOut TEXT)")
            self.c.close()


            self.package_list.setAlternatingRowColors(True)
            self.package_list.setColumnCount(4)
            self.package_list.setColumnWidth(0,610)
            self.package_list.setColumnWidth(1,610)
            self.package_list.setColumnWidth(2,125)
            self.package_list.setColumnWidth(3,125)
            self.package_list.horizontalHeader().setCascadingSectionResizes(False)
            self.package_list.horizontalHeader().setSortIndicatorShown(False)
            self.package_list.horizontalHeader().setStretchLastSection(True)
            self.package_list.verticalHeader().setVisible(False)
            self.package_list.verticalHeader().setCascadingSectionResizes(False)
            self.package_list.verticalHeader().setStretchLastSection(False)
            self.package_list.setHorizontalHeaderLabels(("Tracking Number", "Soldier", "Date In", "Date Out"))
            self.package_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
    "alternate-background-color: rgb(124, 136, 126);\n"
    "border-color: rgb(160, 141, 131);\n"
    "gridline-color: rgb(145, 150, 127);")


            self.connection = sqlite3.connect("database.db")
            query = "SELECT * FROM Packages"
            result = self.connection.execute(query)
            self.package_list.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.package_list.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.package_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
            self.connection.close()
            
            #self.package_list.setSortingEnabled(True)
            #self.package_list.sortByColumn(1, Qt.AscendingOrder)
            self.package_list.show()
            
            

        else:
        
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            self.c.execute("CREATE TABLE IF NOT EXISTS Packages(Tracking_Number TEXT PRIMARY KEY,Recipient TEXT,DateIn TEXT,DateOut TEXT)")
            self.c.close()

            
            self.package_list.setAlternatingRowColors(True)
            self.package_list.setColumnCount(4)
            self.package_list.setColumnWidth(0,610)
            self.package_list.setColumnWidth(1,610)
            self.package_list.setColumnWidth(2,125)
            self.package_list.setColumnWidth(3,125)
            self.package_list.horizontalHeader().setCascadingSectionResizes(False)
            self.package_list.horizontalHeader().setSortIndicatorShown(False)
            self.package_list.horizontalHeader().setStretchLastSection(True)
            self.package_list.verticalHeader().setVisible(False)
            self.package_list.verticalHeader().setCascadingSectionResizes(False)
            self.package_list.verticalHeader().setStretchLastSection(False)
            self.package_list.setHorizontalHeaderLabels(("Tracking Number", "Soldier", "Date In", "Date Out"))
            self.package_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
    "alternate-background-color: rgb(124, 136, 126);\n"
    "border-color: rgb(160, 141, 131);\n"
    "gridline-color: rgb(145, 150, 127);")


            self.connection = sqlite3.connect("database.db")
            query = "SELECT * FROM Packages WHERE date_out IS ''"
            result = self.connection.execute(query)
            self.package_list.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.package_list.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.package_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
            self.connection.close()

            #self.package_list.setSortingEnabled(True)
            #self.package_list.sortByColumn(1, Qt.AscendingOrder)
            self.package_list.show()
        

        
    def GoToHomeScreen(self):
        movehome = Home()
        widget.addWidget(movehome)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def GoToPackageScreen(self):
        movepackages = PackageScreen()
        widget.addWidget(movepackages)
        widget.setCurrentIndex(widget.currentIndex()+1)   
        
    def GoToSoldiersScreen(self):
        movesoldiers = SoldiersScreen()
        widget.addWidget(movesoldiers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def EditPackage(self):
        dlg = EditPackageDialog()
        dlg.exec_()
        
    def CheckInPackage(self):
        dlg = CheckInPackageDialog()
        dlg.exec_()
        
    def CheckOutPackage(self):
        dlg = CheckOutPackageDialog()
        dlg.exec_()  
        
    def DeletePackage(self):
        dlg =  DeletePackageDialog()
        dlg.exec_()  
        
    def PackageLookup(self):
        dlg = PackageLookupDialog()
        dlg.exec_()
        
    def AddSoldier(self):
        dlg = AddSoldierDialog()
        dlg.exec_()
        
    def EditSoldier(self):
        dlg = EditSoldierDialog()
        dlg.exec_() 
        
    def SearchSoldier(self):
        dlg = SearchSoldierDialog()
        dlg.exec_()        
        
        
    def DeleteSoldier(self):
        dlg = DeleteSoldierDialog()
        dlg.exec_()   
        
    def SoldierEmailConfirmation(self):
        dlg = SoldierEmailConfirmationDialog()
        dlg.exec_()
        
    def About(self):
        dlg = AboutDialog()
        dlg.exec_()


# SoldiersScreen
class SoldiersScreen(QMainWindow):
    def __init__(self):
        super(SoldiersScreen,self).__init__()
        self.setWindowIcon(QIcon('GroupMail.png'))  #window icon

        loadUi('GUIs/SoldiersScreenNew.ui',self)
        
        self.btn_home.clicked.connect(self.GoToHomeScreen)
        self.btn_add.clicked.connect(self.AddSoldier)
        self.btn_edit.clicked.connect(self.EditSoldier)
        #self.btn_lookup.clicked.connect()
        
        self.btn_refresh.clicked.connect(self.GoToSoldiersScreen)
        
        
    # Menu Bar
        # Package Tracker
        self.SoldiersHome_Page.triggered.connect(self.GoToHomeScreen)
        self.SoldiersAbout.triggered.connect(self.About)
        
        # Packages
        self.SoldiersPackage_Page.triggered.connect(self.GoToPackageScreen)
        self.SoldiersCheck_In.triggered.connect(self.CheckInPackage)
        self.SoldiersCheck_Out.triggered.connect(self.CheckOutPackage)
        self.SoldiersPackage_Lookup.triggered.connect(self.PackageLookup)
        self.SoldierEdit_Package.triggered.connect(self.EditPackage)
        #self.SoldiersResendEmail.triggered.connect(self.)
        self.SoldiersDelete_Package.triggered.connect(self.DeletePackage)
        
        # Soldiers
        self.SoldiersSoldiers_Page.triggered.connect(self.GoToSoldiersScreen)
        self.SoldiersAdd.triggered.connect(self.AddSoldier)
        self.SoldiersEdit.triggered.connect(self.EditSoldier)
        self.SoldiersSearch.triggered.connect(self.SearchSoldier)
        self.SoldiersDelete.triggered.connect(self.DeleteSoldier)
        self.SoldiersSend_Email_Confirmation.triggered.connect(self.SoldierEmailConfirmation)



        
        self.loaddata()



    def loaddata(self):
        
        
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS Soldier(Soldier TEXT PRIMARY KEY,Barracks TEXT,Email TEXT)")
        self.c.close()
        
                
        #self.soldier_list = QtWidgets.QTableWidget()
        #self.soldier_list = QtWidgets.QTableWidget(self.centralwidget)
        #self.soldier_list.setGeometry(QtCore.QRect(20, 250, 1500, 510))
        self.soldier_list.setAlternatingRowColors(True)
        self.soldier_list.setColumnCount(3)
        self.soldier_list.setColumnWidth(0,400)
        self.soldier_list.setColumnWidth(1,200)
        self.soldier_list.setColumnWidth(2,400)
        self.soldier_list.horizontalHeader().setCascadingSectionResizes(False)
        self.soldier_list.horizontalHeader().setSortIndicatorShown(False)
        self.soldier_list.horizontalHeader().setStretchLastSection(True)
        self.soldier_list.verticalHeader().setVisible(False)
        self.soldier_list.verticalHeader().setCascadingSectionResizes(False)
        self.soldier_list.verticalHeader().setStretchLastSection(False)
        self.soldier_list.setHorizontalHeaderLabels(("Soldier", "Barracks", "Email"))
        self.soldier_list.setStyleSheet("font: 14pt 'Courier New';background-color: rgb(114, 104, 112);\n"
"alternate-background-color: rgb(124, 136, 126);\n"
"border-color: rgb(160, 141, 131);\n"
"gridline-color: rgb(145, 150, 127);")
        
        self.connection = sqlite3.connect("database.db")
        query = "SELECT * FROM Soldier"
        result = self.connection.execute(query)
        self.soldier_list.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.soldier_list.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.soldier_list.setItem(row_number, column_number,QTableWidgetItem(str(data)))
        self.connection.close()
        
        self.soldier_list.setSortingEnabled(True)
        self.soldier_list.sortByColumn(0, Qt.AscendingOrder)
        
        
        
        
        
    def GoToHomeScreen(self):
        movehome = Home()
        widget.addWidget(movehome)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def GoToPackageScreen(self):
        movepackages = PackageScreen()
        widget.addWidget(movepackages)
        widget.setCurrentIndex(widget.currentIndex()+1)   
        
    def GoToSoldiersScreen(self):
        movesoldiers = SoldiersScreen()
        widget.addWidget(movesoldiers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def EditPackage(self):
        dlg = EditPackageDialog()
        dlg.exec_()
        
    def CheckInPackage(self):
        dlg = CheckInPackageDialog()
        dlg.exec_()
        
    def CheckOutPackage(self):
        dlg = CheckOutPackageDialog()
        dlg.exec_()  
        
    def DeletePackage(self):
        dlg =  DeletePackageDialog()
        dlg.exec_()  
        
    def PackageLookup(self):
        dlg = PackageLookupDialog()
        dlg.exec_()
        
    def AddSoldier(self):
        dlg = AddSoldierDialog()
        dlg.exec_()
        
    def EditSoldier(self):
        dlg = EditSoldierDialog()
        dlg.exec_() 
        
    def SearchSoldier(self):
        dlg = SearchSoldierDialog()
        dlg.exec_()        
        
    def DeleteSoldier(self):
        dlg = DeleteSoldierDialog()
        dlg.exec_()   
        
    def SoldierEmailConfirmation(self):
        dlg = SoldierEmailConfirmationDialog()
        dlg.exec_()
        
    def About(self):
        dlg = AboutDialog()
        dlg.exec_()

app=QApplication(sys.argv)
mainwindow=Home()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
#widget.showMaximized()
#widget.setFixedWidth(1540)
#widget.setFixedHeight(890)
widget.show()
app.exec_()





