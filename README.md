# YandereImgScraper
 Download the images which are posted in 24 hours from yande.re.
 
 View Images in yande.re and download them within one-click.(With GUI)
## Environment&Dependencies:
  - Python3.6.1 64-bit
  - PyQT5
  - pyinstaller
## How to use
### 1. yandere.py
  - Config the path which you want all the images to be saved by setting *save_path*
  - Run the python script, it will automatically save all the images into a folder(name as year-month) under the set directory.
### 2. yanderescraper.py (with GUI)
  - Directly run in python environment or package it into executable by runnnig pyinstaller(install by *pip install pyinstaller*) command* pyinstaller yanderescraper.py * or * pyinstaller --noconsole yanderescraper.py * if you do not want console.(remember to install dependencies PyQt5)
  - *Save in* in setting menu to set the folder you want to save all the downloaded images.
  - *open in browser* to open the original images url in web browser.
  - "*save images posted today* to save all the images posted in 24 hours(as yandere.py does)
  - Prev/Next images buttons to go to previous/next image.
  - Start dowmloading to download the current image.
  - Use slider to zoom in/out.
  - Turn on/off R18 Mode by checking the checkbox.
# Yandere图片爬虫
 将最近24小时新发布的图片从yande.re上下载到本地

 在图形化界面下浏览yande.re的图片以及一键下载图片
## 环境: 
 - Python3.6.1 64位
 - PyQT5
 - pyinstaller
## 如何使用
### 1. yandere.py
  - 只需在脚本中配置*save_path*变量为你想要保存图片的文件夹路径即可
  - 运行python脚本，将自动下载保存所有图片到指定文件夹目录下面的自动新建的文件夹（名字格式： 年份-月份）。
### 2. yanderescraper.py (图形化界面)
  - 直接运行python脚本或者使用pyinstaller（pip install pyinstaller）运行pyinstaller命令(运行pip install pyinstaller安装)* pyinstaller yanderescraper.py * 或者如果你不想要控制台的话 * pyinstaller --noconsole yanderescraper.py *。（需要安装PyQt5）。
  - Setting 菜单中的*Save in*可设定保存图片的文件夹。
  - *Open in browser*可打开当前浏览图片的额原始链接。
  - "*save images posted today* 可以保存24小时内发布的所有新图。
  - Prev/Next images 按钮可以浏览前/后一张图片。
  - Start dowmloading 按钮可以下载当前图片。
  - 通过拉动滑条可以放大缩小图片。
  - 通过勾选框能够打开或关闭R18模式。
