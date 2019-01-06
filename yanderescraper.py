import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QMainWindow, QPushButton, QAction, QFileDialog, QSlider, QCheckBox, QApplication, QMessageBox)
from PyQt5.QtGui import (QPixmap, QIcon)
from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication
import math
import urllib.request
import webbrowser

import urllib.parse
import re, os, zlib
import time, datetime

class MangaDown:
    def __init__(self, url, save_path = None):
        self.base_url = "https://yande.re"
        self.url = url
        if save_path == None:
            save_path = ''
        self.save_path = save_path
        self.current_month = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month).zfill(2)
        content = self.get_content(self.url)
        if not content:
            print ("Manga init failed.")
            return
    
        self.need_check_pic = False

    def get_content(self, url):
        #open page
        try:
            response = urllib.request.urlopen(url,timeout = 20)
            html = response.read().decode("utf-8")
            return html
        except Exception as e:
            print (e)
            print ("Failed to open："+ url + "!")
            return None
        
    def get_pic_urls(self, pageurl):
        content = self.get_content(pageurl)
        if not content:
            return None

        pattern = re.compile('<ul id="post-list-posts"(.*?)>(.*?)</ul>',re.S)
        pic_ul = re.search(pattern, content)
        ul_list = pic_ul.groups(1)[1]

        pattern = re.compile('<li.*?>(.*?)</li>',re.S)
        lists = re.findall(pattern, ul_list)
        img_arr = []
        for a_list in lists:
            img_arr.append(a_list)

        return img_arr

    def parse_img_path(self, img_arr):
        img_infos = []
        for img_html in img_arr:
            pattern = re.compile('<a class="directlink (large|small)img" href="(.*?)">', re.S)
            url_result = re.search(pattern, img_html)
            img_url = url_result.groups(0)[1]

            pattern = re.compile('<a class="thumb" href="(.*?)"(.*?)>', re.S);
            detail_result = re.search(pattern, img_html)
            detail_url = detail_result.groups(0)[0]

            pattern = re.compile('alt="Rating:(.*?)Score', re.S)
            rating_result =re.search(pattern, img_html)
            rating = rating_result.groups(0)[0].replace(' ', '')

            image_info = dict()
            image_info["url"] = img_url
            image_info["detail"] = detail_url
            image_info['rating'] = rating
            img_infos.append(image_info)
        return img_infos

    def get_img_info(self, detail_url):
        detail_info = self.get_content(self.base_url + detail_url)
        if not detail_info:
            return None
        
        pattern = re.compile('<title>(.*?)</title>',re.S)
        title_result = re.search(pattern, detail_info)
        title = title_result.groups(0)[0]

        # posted time
        pattern = re.compile('<a title="(.*?)"(.*?)href=(.*?)>', re.S)
        time_result = re.search(pattern, detail_info)
        post_time_str = time_result.groups(0)[0]

        post_time_struct = time.strptime(post_time_str, "%a %b %d %H:%M:%S %Y")
        post_time = datetime.datetime.fromtimestamp(time.mktime(post_time_struct))
        current_time = datetime.datetime.now()

        if (current_time - post_time).total_seconds() <=  24 * 60 * 60:
            return True, post_time_str, title
        else:
            return False, post_time_str, title

    def create_dir_path(self, path):
        #以漫画名创建文件夹 Create folder based on time(Year-Month)
        
        exists = os.path.exists(path)
        if not exists:
            print("Create folder : " + self.current_month)    
            os.makedirs(path)
        else:
            print("Folder : " + self.current_month +" already exists!") 
    
    def save_pics(self, img_infos):
        self.create_dir_path(self.save_path + self.current_month)
        # boolean value to determine whether this page is the end of latest images(posted today)
        b_all_posts_today = True        
        
        for img_info in img_infos:
            detail_info = self.get_img_info(img_info["detail"])

            # only download image posted today
            if detail_info[0] == True:
                picurl = img_info["url"]
                if picurl == None:
                    continue
                
                title = detail_info[2].split('|')[0] + detail_info[1]
                title = title.replace(' ', '_').replace(':', '-')
                if title == None:
                    continue
                if self.save_path == '':
                    pic_path = self.current_month + '/' + title + '.jpg'
                else:
                    pic_path = self.save_path + '/' + self.current_month + '/' + title + '.jpg'
                exists = os.path.exists(pic_path)
                if exists:
                    print ("Image has already been downloaded!")
                    continue
            

                connection_tries = 1
                for connection_tries in range(1, 3):
                    try:
                        urllib.request.urlretrieve(picurl,pic_path)
                        break
                    except Exception as e:
                        if connection_tries <= 4:
                            connection_tries += 1
                            print('Try to download [' + title + '] times: ' + str(connection_tries), e)
                            continue
                        else:
                            print('Unable to connect to the server, download [ ' + title + ' ]failed!')
                if  connection_tries < 5:
                    print (title + "successfully downloaded！")
        return self.get_img_info(img_infos[len(img_infos)-1]["detail"])[0]
    
    def save_pic(self, img_info):
        self.create_dir_path(self.save_path + '/' + self.current_month)
        img_url = img_info['url']
        detail_info = self.get_img_info(img_info["detail"])
        
        if img_url is not None:        
            title = detail_info[2].split('|')[0] + detail_info[1]
            title = title.replace(' ', '_').replace(':', '-')
            if title == None:
                return
            if self.save_path == '':
                pic_path = self.current_month + '/' + title + '.jpg'
            else:
                pic_path = self.save_path + '/' + self.current_month + '/' + title + '.jpg'
            exists = os.path.exists(pic_path)
            if exists:
                print ("Image has already been downloaded!")
                return
        
            connection_tries = 1
            for connection_tries in range(1, 3):
                try:
                    urllib.request.urlretrieve(img_url,pic_path)
                    break
                except Exception as e:
                    if connection_tries <= 4:
                        connection_tries += 1
                        print('Try to download [' + title + '] times: ' + str(connection_tries), e)
                        continue
                    else:
                        print('Unable to connect to the server, download [ ' + title + ' ]failed!')
            if  connection_tries < 5:
                print (title + "successfully downloaded！")
      

class YandereGUI(QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.r18_mode = False
        self.initImageLoading()
        self.initUI()
        self.resized.connect(self.onWindowResized)

    
    def initImageLoading(self):
        self.url = 'https://yande.re/post'
        self.imgs = MangaDown(self.url, None)
        self.current_page = 1 # one-index
        self.current_index = 0 # 0-index
        self.loadImages(self.current_page)
    
    def loadImages(self, currentPage):
        arr = self.imgs.get_pic_urls(self.url + '?page=' + str(currentPage))
        self.img_infos = self.imgs.parse_img_path(arr)
        if self.r18_mode == False:
            self.filterR18()
        self.current_index = 0
        self.scaling_factor = 1

    def initUI(self):
        # File menu bar
        self.setWindowIcon(QIcon('Icons/Icon.jpg'))

        setSavePath = QAction(QIcon('Icons/SaveIn.jpg'), 'Save in', self)
        setSavePath.setShortcut('Ctrl+F')
        setSavePath.setStatusTip('Save in the folder')
        setSavePath.triggered.connect(self.showDialog)

        openBrowser = QAction(QIcon('Icons/openBrowser.jpg'), 'Open in browser', self)
        openBrowser.setShortcut('Ctrl+B')
        openBrowser.setStatusTip('Open this image in browser')
        openBrowser.triggered.connect(self.openInBrowser)

        savePostsToday = QAction(QIcon('Icons/24Hrs.jpg'), 'Save images posted today', self)
        savePostsToday.setShortcut('Ctrl+S')
        savePostsToday.setStatusTip('Save images posted in 24 hours')
        savePostsToday.triggered.connect(self.go_through_all_new_posted_pages)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Setting')
        fileMenu.addAction(setSavePath)
        fileMenu.addAction(openBrowser)
        fileMenu.addAction(savePostsToday)
        # buttons
        butList = QHBoxLayout(self)
        
        self.startBut = QPushButton(self)
        self.startBut.setGeometry(375, 560, 150, 30)
        self.startBut.setText('Start Downloading')
        butList.addWidget(self.startBut)
        self.startBut.clicked.connect(self.downloadPic)

        self.leftBut = QPushButton(self)
        self.leftBut.setGeometry(175, 560, 150, 30)
        self.leftBut.setText('Prev Image')
        butList.addWidget(self.leftBut)
        self.leftBut.clicked.connect(self.prevImage)

        self.rightBut = QPushButton(self)
        self.rightBut.setGeometry(575, 560, 150, 30)
        self.rightBut.setText('Next Image')
        butList.addWidget(self.rightBut)
        self.rightBut.clicked.connect(self.nextImage)
        
        self.slider = QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setValue(50)
        self.slider.setGeometry(300, 20, 300, 30)
        self.slider.valueChanged[int].connect(self.changeScale)

        self.r18mode = QCheckBox('R18 Mode', self)
        self.r18mode.setGeometry(700, 20, 100, 30)
        # self.r18mode.toggle()
        self.r18mode.stateChanged.connect(self.checkR18Mode)
        # image viewer
        hBox = QHBoxLayout(self)
        
        if self.img_infos and len(self.img_infos) > 0:
            img_url = self.img_infos[self.current_index]['url']
        else:
            img_url = 'https://files.yande.re/image/41dd5cedf9494fc4e0c9a9c48f7e0881/yande.re%20505979%20animal_ears%20japanese_clothes%20mugenkidou%20no_bra%20open_shirt%20possible_duplicate%20thighhighs%20tomose_shunsaku.jpg'

        self.readImageFromUrl(img_url)
        img = self.img.scaled(890, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        self.container = QLabel(self)
        self.container.setAlignment(QtCore.Qt.AlignCenter)
        self.container.setPixmap(img)
        self.container.setGeometry(5, 50, 890, 500)
        # self.container.setScaledContents(True)

        hBox.addWidget(self.container)
        # self.setLayout(hBox)
        
        vBox = QVBoxLayout(self)
        vBox.addChildLayout(hBox)
        vBox.addStretch()
        vBox.addChildLayout(butList)
        self.setLayout(vBox)
        self.setGeometry(300, 300, 900, 600)
        self.setWindowTitle('YandereViewer')
        self.show()

        
    def go_through_all_new_posted_pages(self):
        current_page = 1
        b_all_posts_today = True

        while b_all_posts_today:
            arr = self.imgs.get_pic_urls(self.url + '?page=' + str(current_page))
            img_infos = self.imgs.parse_img_path(arr)
            b_all_posts_today = self.imgs.save_pics(img_infos)
            current_page = current_page + 1
        downloadedHints = QMessageBox.question(self, 'Successfully downloaded!',
            "Successfully downloaded all images posted in 24 hours!", QMessageBox.Ok)
   
    def showDialog(self):
        folderBrowser = QFileDialog() 
        folderBrowser.setFileMode(QFileDialog.DirectoryOnly) # Directory
        
        fname = QFileDialog.getExistingDirectory(self)
        if fname:
            print('Select folder: ' + fname)
            self.imgs.save_path = fname

    def openInBrowser(self):
        img_url = ''
        if self.img_infos:
            img_url = self.url.replace('/post', '') + self.img_infos[self.current_index]['detail']
        webbrowser.open(img_url)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(YandereGUI, self).resizeEvent(event)

    def readImageFromUrl(self, url):
        data = urllib.request.urlopen(url).read()
        self.img = QPixmap('')
        self.img.loadFromData(data)

    def scaleImage(self):
        widthRatio = self.geometry().width() / 900 * self.scaling_factor
        heightRatio = self.geometry().height() / 600 * self.scaling_factor
        img = self.img.scaled(math.ceil(890 * widthRatio), math.ceil(500 * heightRatio), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.container.setPixmap(img)

    def downloadPic(self):
        self.imgs.save_pic(self.img_infos[self.current_index])
        downloadedHints = QMessageBox.question(self, 'Successfully downloaded!',
            "Successfully downloaded this image!", QMessageBox.Ok)

    def prevImage(self):
        self.current_index = self.current_index - 1
        if self.img_infos:
            if self.current_index < 0:
                if self.current_page - 1 >= 0:
                    self.current_page = self.current_page - 1
                    self.loadImages(self.current_page)
            if self.current_index < len(self.img_infos):
                img_url = self.img_infos[self.current_index]['url']
            else:
                img_url = 'https://files.yande.re/image/41dd5cedf9494fc4e0c9a9c48f7e0881/yande.re%20505979%20animal_ears%20japanese_clothes%20mugenkidou%20no_bra%20open_shirt%20possible_duplicate%20thighhighs%20tomose_shunsaku.jpg'
        else:
            img_url = 'https://files.yande.re/image/41dd5cedf9494fc4e0c9a9c48f7e0881/yande.re%20505979%20animal_ears%20japanese_clothes%20mugenkidou%20no_bra%20open_shirt%20possible_duplicate%20thighhighs%20tomose_shunsaku.jpg'
        
        self.readImageFromUrl(img_url)
        self.scaleImage()
    

    def nextImage(self):
        self.current_index = self.current_index + 1
        if self.img_infos:
            if self.current_index >= len(self.img_infos):
                self.current_page + 1
                self.loadImages(self.current_page)
            if self.current_index < len(self.img_infos):
                img_url = self.img_infos[self.current_index]['url']
            else:
                img_url = 'https://files.yande.re/image/41dd5cedf9494fc4e0c9a9c48f7e0881/yande.re%20505979%20animal_ears%20japanese_clothes%20mugenkidou%20no_bra%20open_shirt%20possible_duplicate%20thighhighs%20tomose_shunsaku.jpg'
        else:
            img_url = 'https://files.yande.re/image/41dd5cedf9494fc4e0c9a9c48f7e0881/yande.re%20505979%20animal_ears%20japanese_clothes%20mugenkidou%20no_bra%20open_shirt%20possible_duplicate%20thighhighs%20tomose_shunsaku.jpg'
        
        
        self.readImageFromUrl(img_url)
        self.scaleImage()

    def onWindowResized(self):
        widthRatio = self.geometry().width() / 900
        heightRatio = self.geometry().height() / 600
        self.slider.setGeometry(math.ceil(300 * widthRatio), math.ceil(20 * heightRatio),  math.ceil(300 * widthRatio),  math.ceil(30 * heightRatio))
        self.r18mode.setGeometry(math.ceil(700 * widthRatio), math.ceil(20 * heightRatio),  math.ceil(100 * widthRatio),  math.ceil(30 * heightRatio))
        self.container.setGeometry(math.ceil(5 * widthRatio), math.ceil(50 * heightRatio),  math.ceil(890 * widthRatio),  math.ceil(500 * heightRatio))
        self.startBut.setGeometry(math.ceil(375 * widthRatio), math.ceil(560 * heightRatio),  math.ceil(150 * widthRatio),  math.ceil(30 * heightRatio))
        self.leftBut.setGeometry(math.ceil(175 * widthRatio), math.ceil(560 * heightRatio),  math.ceil(150 * widthRatio),  math.ceil(30 * heightRatio))
        self.rightBut.setGeometry(math.ceil(575 * widthRatio), math.ceil(560 * heightRatio),  math.ceil(150 * widthRatio),  math.ceil(30 * heightRatio))
        self.scaleImage()

    def closeEvent(self, event):
        super().closeEvent(event)
        sys.exit(0)
    
    def changeScale(self, value):
        self.scaling_factor = value / 50.0
        if self.scaling_factor < 0.5:
            self.scaling_factor = 0.5
        self.scaleImage()
    
    def checkR18Mode(self, state):
        self.current_page = 1 # one-index
        self.current_index = 0 # 0-index
        arr = self.imgs.get_pic_urls(self.url)
        self.img_infos = self.imgs.parse_img_path(arr)
        if state == QtCore.Qt.Checked:
            self.r18_mode = True
        else:
            self.filterR18()
            self.r18_mode = False
        self.readImageFromUrl(self.img_infos[self.current_index]['url'])

    def filterR18(self):
        img_infos = self.img_infos
        self.img_infos = []
        for img_info in img_infos:
            if img_info['rating'] == 'Safe':
                self.img_infos.append(img_info)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    yandereGui =  YandereGUI()

    if sys and app:
        sys.exit(app.exec_())
