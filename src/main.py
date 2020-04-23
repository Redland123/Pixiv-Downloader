#https://pixiv-api.readthedocs.io/en/latest/
#$ pip install pixiv-api 

from pathlib import Path
from pixivapi import Client
from pixivapi import Size
from pixivapi import Visibility
from os import system
import sys

#print("Hello world")

def downloadSingleImg(currentClient):
    if not currentClient:
        return -1

    url = input('Enter img URL: ')
    fName = input('Enter file name: ')
    imgLoc = 'images/'

    if not url or not imgLoc or not fName:
        return -1

    newImg = currentClient.fetch_illustration(
        url.split('https://www.pixiv.net/en/artworks/')[1])

    newImg.download(directory=Path(imgLoc), size=Size.ORIGINAL, filename=fName)
    print ('Image downloaded')

    return 1

def downloadBooksmarks(currentClient, userId, check, amount):
    bkMarks = currentClient.fetch_user_bookmarks(user_id=userId, visibility=Visibility.PUBLIC, max_bookmark_id=None, tag=None)

    imgLoc = 'images/'

    if check:
        while True:
            for currentImg in bkMarks['illustrations']:
                try:
                    currentImg.download(directory=Path(imgLoc), size=Size.ORIGINAL)
                    print ('Image downloaded')
                except:
                    print ('Error downloading?')

            # Breaks the loop if a next page does not exist
            if not bkMarks['next']:
                break

            # Moves the list to the next page
            bkMarks = currentClient.fetch_user_bookmarks(userId, max_bookmark_id=bkMarks['next'])

    if not check:
        for i in range(int(amount)):
            try:
                bkMarks['illustrations'][i].download(directory=Path(imgLoc), size=Size.ORIGINAL)
                print ('Image downloaded')
            except:
                print ('Error downloading?')


def main():
    #Creates new session
    currentSession = Client()

    userName = input ('Enter email: ') 
    passWord = input ('Enter password: ')

    #Authenticates the current session
    try:
        currentSession.login(userName, passWord)
    except:
        print('Error logging into account.')
        sys.exit([-1])

    system('cls')

    print ()
    print ('Select an option: ')
    print ('0: exit.')
    print ('1: Download a single image.')
    print ('2: Download a range of bookmarks. (Current max = 30, need to fix.)')
    print ('3: Download all booksmarks.')

    ans = input()

    system('cls')

    if ans == '0':
        sys.exit(1)
    elif ans == '1':
        downloadSingleImg(currentSession)
    elif ans == '2':
        userId = input('Enter userId: ')
        num = input('Enter the number of images to be downloaded: ')
        downloadBooksmarks(currentSession, userId, 0, num)
    elif ans == '3':
        userId = input('Enter userId: ')
        downloadBooksmarks(currentSession, userId, 1, 0)


if __name__ == '__main__':
    main()
