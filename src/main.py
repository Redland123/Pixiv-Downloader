import os
import sys
import requests
import pixivapi
import qdarkstyle

from pathlib import Path
from functools import partial
from pixivapi import Size, Visibility
from PySide2 import QtCore, QtWidgets, QtGui, QtUiTools, QtWidgets, QtUiTools


class mainWindowClass:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

        self.cDir = os.path.dirname(__file__)
        self.uiPath = os.path.join(self.cDir, 'mainWindow.ui')
        self.cDownloadPath = ''

        self.visibilityMode = pixivapi.Visibility.PUBLIC

        # Opens the uiFile in readOnly mode
        uiFile = QtCore.QFile(self.uiPath)
        uiFile.open(QtCore.QFile.ReadOnly)

        # Creates the mainWindow and loads the uiFile into it
        loader = QtUiTools.QUiLoader()
        self.mainWindow = loader.load(uiFile)

        self.currentSession = pixivapi.Client()

        #Closes uiFile
        uiFile.close()

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

    def on_privateCheck_clicked(self):
        if bool(self.mainWindow.privateCheck.checkState()):
            self.visibilityMode = pixivapi.Visibility.PRIVATE
        else:
            self.visibilityMode = pixivapi.Visibility.PUBLIC

    def on_openFileButton_clicked(self):
        self.cDownloadPath = QtWidgets.QFileDialog.getExistingDirectory(
            self.mainWindow, "Open Directory", self.cDir, QtWidgets.QFileDialog.ShowDirsOnly)
        self.mainWindow.lineEditCustomPath.setText(self.cDownloadPath)

    def on_checkPathButton_clicked(self, i):
        self.cDownloadPath = self.mainWindow.lineEditCustomPath.text()

        if self.cDownloadPath == '':
            self.mainWindow.listWidget.addItem('Error, no path entered.')
            self.mainWindow.listWidget.scrollToBottom()
            return 'Error'
        elif os.path.exists(self.cDownloadPath):
            if not i:
                self.mainWindow.listWidget.addItem('Path Exist')
                self.mainWindow.listWidget.scrollToBottom()
            return 'Exist'
        else:
            self.mainWindow.listWidget.addItem('Error, path does not exist.')
            self.mainWindow.listWidget.scrollToBottom()
            return 'Error'

    def on_logInButton_clicked(self):
        enteredUsername = self.mainWindow.lineEditUsername.text()
        enteredPassword = self.mainWindow.lineEditPassword.text()

        if not enteredUsername:
            self.mainWindow.listWidget.addItem('Error, no username.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        if not enteredPassword:
            self.mainWindow.listWidget.addItem('Error, no password.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        try:
            self.currentSession.login(enteredUsername, enteredPassword)
        except (pixivapi.LoginError):
            self.mainWindow.listWidget.addItem('Error, invalid login.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        currentID = self.currentSession.account

        self.mainWindow.listWidget_2.clear()
        self.mainWindow.listWidget_2.addItem('Logged in as: ')
        self.mainWindow.listWidget_2.addItem(currentID.name)
        self.mainWindow.listWidget_2.addItem(' ')
        self.mainWindow.listWidget_2.addItem('ID: ')
        self.mainWindow.listWidget_2.addItem(currentID.id)

        self.toggleUI(True)

    # Single image download
    def on_singleImageButton_clicked(self):
        enteredURL = self.mainWindow.lineEditImageUrl.text()

        if self.on_checkPathButton_clicked(1) == 'Error':
            return

        try:
            splitEnteredURL = enteredURL.split(
                ('https://www.pixiv.net/en/artworks/'))[1]
        except (ValueError, IndexError):
            self.mainWindow.listWidget.addItem('Error, getting image ID.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        try:
            newImg = self.currentSession.fetch_illustration(
                int(splitEnteredURL))
        except (pixivapi.errors.BadApiResponse, requests.RequestException):
            self.mainWindow.listWidget.addItem('Error getting image.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        try:
            newImg.download(directory=Path(self.cDownloadPath),
                            size=Size.ORIGINAL, filename=None)
            self.mainWindow.listWidget.addItem('Image downloaded.')
            self.mainWindow.listWidget.scrollToBottom()
        except (requests.RequestException, FileNotFoundError, PermissionError):
            self.mainWindow.listWidget.addItem('Error, downloading image.')
            self.mainWindow.listWidget.scrollToBottom()

        return

    # Image set download
    def on_setOfImagesButton_clicked(self):
        enteredID = self.mainWindow.lineEditUserID.text()
        enteredImageCount = self.mainWindow.lineEditImageCount.text()

        if self.on_checkPathButton_clicked(1) == 'Error':
            return

        try:
            int(enteredImageCount)
        except:
            self.mainWindow.listWidget.addItem(
                'Error, ' + str(enteredImageCount) + ' is not a valid number')
            self.mainWindow.listWidget.scrollToBottom()
            return

        try:
            retrievedImages = self.currentSession.fetch_user_bookmarks(
                user_id=enteredID, visibility=self.visibilityMode, max_bookmark_id=None, tag=None)
        except (requests.RequestException, pixivapi.errors.BadApiResponse):
            self.mainWindow.listWidget.addItem('Error, getting bookmarks.')
            self.mainWindow.listWidget.scrollToBottom()

        if not enteredID:
            self.mainWindow.listWidget.addItem('Error, no ID was entered.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        if int(enteredImageCount) > 30:
            self.mainWindow.listWidget.addItem(
                'Error, to many images. (Max 30, needs to be fixed)')
            self.mainWindow.listWidget.scrollToBottom()
            return

        for i in range(int(enteredImageCount)):
            try:
                # Index error not being caught if user does not have the given images
                retrievedImages['illustrations'][i].download(
                    directory=Path(self.cDownloadPath), size=Size.ORIGINAL)
                self.mainWindow.listWidget.addItem('Image downloaded.')
                self.mainWindow.listWidget.scrollToBottom()
            except (requests.RequestException, FileNotFoundError, PermissionError, IndexError):
                self.mainWindow.listWidget.addItem('Error, getting images.')
                self.mainWindow.listWidget.scrollToBottom()

    # All bookmarks button
    def on_allBookmarksButton_clicked(self):
        enteredID = self.mainWindow.lineEditUserID.text()

        if self.on_checkPathButton_clicked(1) == 'Error':
            return

        try:
            int(enteredID)
        except:
            self.mainWindow.listWidget.addItem(
                'Error, ' + str(enteredID) + ' is not a valid ID')
            self.mainWindow.listWidget.scrollToBottom()
            return

        try:
            retrievedImages = self.currentSession.fetch_user_bookmarks(
                user_id=enteredID, visibility=self.visibilityMode, max_bookmark_id=None, tag=None)
        except (requests.RequestException, pixivapi.BadApiResponse):
            self.mainWindow.listWidget.addItem('Error, getting bookmarks.')
            self.mainWindow.listWidget.scrollToBottom()
            return

        while True:
            for currentImg in retrievedImages['illustrations']:
                try:
                    currentImg.download(directory=Path(
                        self.cDownloadPath), size=Size.ORIGINAL)
                    self.mainWindow.listWidget.addItem('Image downloaded.')
                    self.mainWindow.listWidget.scrollToBottom()
                except (requests.RequestException, FileNotFoundError, PermissionError):
                    self.mainWindow.listWidget.addItem('Error, downloading.')
                    self.mainWindow.listWidget.scrollToBottom()
                    return

            # Breaks the loop if a next page does not exist
            if not retrievedImages['next']:
                break

            # Moves the list to the next page
            try:
                retrievedImages = self.currentSession.fetch_user_bookmarks(
                    enteredID, max_bookmark_id=retrievedImages['next'])
            except (requests.RequestException, pixivapi.BadApiResponse):
                self.mainWindow.listWidget.addItem('Error, getting next page.')
                self.mainWindow.listWidget.scrollToBottom()

    def setUpConnections(self):

        self.mainWindow.logInButton.clicked.connect(
            self.on_logInButton_clicked)
        self.mainWindow.singleImageButton.clicked.connect(
            self.on_singleImageButton_clicked)
        self.mainWindow.setOfImagesButton.clicked.connect(
            self.on_setOfImagesButton_clicked)
        self.mainWindow.allBookmarksButton.clicked.connect(
            self.on_allBookmarksButton_clicked)
        self.mainWindow.privateCheck.clicked.connect(
            self.on_privateCheck_clicked)
        self.mainWindow.openFileButton.clicked.connect(
            self.on_openFileButton_clicked)
        self.mainWindow.checkPathButton.clicked.connect(
            self.on_checkPathButton_clicked)
        self.mainWindow.lineEditCustomPath.returnPressed.connect(
            lambda i=1: self.on_checkPathButton_clicked(i))
        self.mainWindow.lineEditPassword.returnPressed.connect(
            self.on_logInButton_clicked)

def main():

    mainWindow = mainWindowClass()

    mainWindow.showMainWindow()
    mainWindow.setUpConnections()
    mainWindow.toggleUI(False)

    mainWindow.close()


if __name__ == '__main__':
    main()
