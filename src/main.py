#https://pixiv-api.readthedocs.io/en/latest/
#$ pip install pixiv-api 

import PySide2
import os
import sys
from PySide2 import QtCore, QtWidgets, QtGui, QtUiTools
import PySide2.QtWidgets
import PySide2.QtUiTools
import pixivapi
import qdarkstyle
import requests
from pathlib import Path
from pixivapi import Client
from pixivapi import Size
from pixivapi import Visibility
from os import system

#print("Hello world")

class mainWindowClass:
    def __init__ (self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

        self.directoryPath = os.path.dirname(__file__) 
        windowPath = os.path.join(self.directoryPath, 'mainWindow.ui')
        ui_file = QtCore.QFile(windowPath)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.mainWindow = loader.load(ui_file)
        ui_file.close()

        self.currentSession = Client()
        self.dlFldPth = 'images/'

    # Checks for the download folder and creates it if its not found.
    def checkForImageFile(self):
        if not os.path.exists(self.dlFldPth):
            os.mkdir(self.dlFldPth)

    # Shows main window inside this object
    def showMainWindow(self):
        self.mainWindow.show() 

    # Kills the application
    def close(self):
        sys.exit(self.app.exec_())

    # Toggles the UI elements of the main window.
    def toggleUI(self, i):
        self.mainWindow.singleImageButton.setEnabled(i)
        self.mainWindow.lineEditImageUrl.setEnabled(i)
        self.mainWindow.setOfImagesButton.setEnabled(i)
        self.mainWindow.lineEditUserID.setEnabled(i)
        self.mainWindow.lineEditImageCount.setEnabled(i)
        self.mainWindow.allBookmarksButton.setEnabled(i)
        self.mainWindow.lineEditUserID_2.setEnabled(i)

    def on_logInButton_clicked(self):
        enteredUsername = self.mainWindow.lineEditUsername.text()
        enteredPassword = self.mainWindow.lineEditPassword.text()

        if not enteredUsername:
            self.mainWindow.listWidget.addItem('Error, no username.')
            return

        if not enteredPassword:
            self.mainWindow.listWidget.addItem('Error, no password.')
            return

        try:
            self.currentSession.login(enteredUsername, enteredPassword)
        except (pixivapi.LoginError) as err:
            self.mainWindow.listWidget.addItem('Error, invalid login.\n' + str(err))
            return 

        self.mainWindow.lineEditUsername.clear()
        self.mainWindow.lineEditPassword.clear()

        tmpPswStr, tmpUsrStr = "", ""

        for _ in enteredUsername:
            tmpUsrStr += '*'

        for _ in enteredPassword:
            tmpPswStr += '*'
            
        self.mainWindow.lineEditUsername.setText(tmpUsrStr)
        self.mainWindow.lineEditPassword.setText(tmpPswStr)

        currentID = self.currentSession.account

        self.mainWindow.listWidget_2.clear()
        self.mainWindow.listWidget_2.addItem('Logged in as: ')
        self.mainWindow.listWidget_2.addItem(currentID.name)
        self.mainWindow.listWidget_2.addItem(' ')
        self.mainWindow.listWidget_2.addItem('ID: ')
        self.mainWindow.listWidget_2.addItem(currentID.id)

        self.toggleUI(True)
    
    def on_singleImageButton_clicked(self):
        enteredURL = self.mainWindow.lineEditImageUrl.text()

        try:
            splitEnteredURL = enteredURL.split(('https://www.pixiv.net/en/artworks/'))[1]
        except (ValueError, IndexError) as err:
            self.mainWindow.listWidget.addItem('Error getting image ID.\n' + str(err))
            return

        try:
            newImg = self.currentSession.fetch_illustration(int(splitEnteredURL))
        except (pixivapi.errors.BadApiResponse, requests.RequestException) as err:
            self.mainWindow.listWidget.addItem('Error getting image.\n' + str(err))
            return

        try: 
            newImg.download(directory=Path(self.dlFldPth), size=Size.ORIGINAL, filename=None)
            self.mainWindow.listWidget.addItem('Image downloaded.')
        except (requests.RequestException, FileNotFoundError, PermissionError) as err:
            self.mainWindow.listWidget.addItem('Error downloading image.\n' + str(err))

        return

    def on_setOfImagesButton_clicked(self):
        enteredID = self.mainWindow.lineEditUserID.text()
        enteredImageCount = self.mainWindow.lineEditImageCount.text()

        try:
            int(enteredImageCount)
        except:
            self.mainWindow.listWidget.addItem('Error, ' + str(enteredImageCount) + ' is not a valid number')
            return

        try:
            retrievedImages = self.currentSession.fetch_user_bookmarks(user_id=enteredID, visibility=Visibility.PUBLIC, max_bookmark_id=None, tag=None)
        except (requests.RequestException, pixivapi.errors.BadApiResponse) as err:
            self.mainWindow.listWidget.addItem('Error getting bookmarks.')

        if not enteredID:
            self.mainWindow.listWidget.addItem('No ID was entered.')
            return

        if  int(enteredImageCount) > 30:
            self.mainWindow.listWidget.addItem('Error, to many images. (Max 30, needs to be fixed)')
            return

        for i in range(int(enteredImageCount)):
            try:
                # Index error not being caught if user does not have the given images
                retrievedImages['illustrations'][i].download(directory=Path(self.dlFldPth), size=Size.ORIGINAL)
                self.mainWindow.listWidget.addItem('Image downloaded.') 
            except (requests.RequestException, FileNotFoundError, PermissionError, IndexError) as err:
                self.mainWindow.listWidget.addItem('Error getting images.\n' + str(err))

    def on_allBookmarksButton_clicked(self):
        enteredID = self.mainWindow.lineEditUserID.text()

        try:
            int(enteredID)
        except:
            self.mainWindow.listWidget.addItem('Error, ' + str(enteredID) + ' is not a valid ID')
            return

        try:
            retrievedImages = self.currentSession.fetch_user_bookmarks(user_id=enteredID, visibility=Visibility.PUBLIC, max_bookmark_id=None, tag=None)
        except (requests.RequestException, pixivapi.BadApiResponse) as err:
            self.mainWindow.listWidget.addItem('Error getting bookmarks.\n' + str(err))
            return 

        while True:
            for currentImg in retrievedImages['illustrations']:
                try:
                    currentImg.download(directory=Path(self.dlFldPth), size=Size.ORIGINAL)
                    self.mainWindow.listWidget.addItem('Image downloaded.')
                except (requests.RequestException, FileNotFoundError, PermissionError) as err:
                    self.mainWindow.listWidget.addItem('Error downloading.\n' + str(err))
                    return

            # Breaks the loop if a next page does not exist
            if not retrievedImages['next']:
                break

            # Moves the list to the next page
            try:
                retrievedImages = self.currentSession.fetch_user_bookmarks(enteredID, max_bookmark_id=retrievedImages['next'])
            except (requests.RequestException, pixivapi.BadApiResponse) as err:
                self.mainWindow.listWidget.addItem('Error getting next page.\n' + str(err))

    def setUpConnections(self):
        self.mainWindow.logInButton.clicked.connect(self.on_logInButton_clicked)
        self.mainWindow.singleImageButton.clicked.connect(self.on_singleImageButton_clicked)
        self.mainWindow.setOfImagesButton.clicked.connect(self.on_setOfImagesButton_clicked)
        self.mainWindow.allBookmarksButton.clicked.connect(self.on_allBookmarksButton_clicked)
        
def main():

    mainWindow = mainWindowClass()

    mainWindow.showMainWindow()
    mainWindow.setUpConnections()
    mainWindow.toggleUI(False)
    mainWindow.checkForImageFile()

    mainWindow.close()

if __name__ == '__main__':
    main()
