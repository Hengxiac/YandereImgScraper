#coding UTF-8
import urllib.request
import urllib.parse
import re, os, zlib
import time, datetime

class MangaDown:
    def __init__(self, url, save_path):
        self.base_url = "https://yande.re"
        self.url = url
        self.save_path = save_path
        self.current_month = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month).zfill(2)
        content = self.get_content(self.url)
        if not content:
            print ("Manga init failed.")
            return
    
        # 标记每次下载图片时,是否先检查本地已存在对应图片
        self.need_check_pic = False

    def get_content(self, url):
        #打开网页
        try:
            response = urllib.request.urlopen(url,timeout = 20)
            # response = urllib.request.urlopen(req, timeout = 20)
            html = response.read().decode("utf-8")
            return html
        except Exception as e:
            print (e)
            print ("打开网页："+ url + "失败。")
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

            image_info = dict()
            image_info["url"] = img_url
            image_info["detail"] = detail_url
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
                
                pic_path = self.save_path + self.current_month + '/' + title + '.jpg'
                exists = os.path.exists(pic_path)
                if exists:
                    print ("Image has already been downloaded!")
                    continue
            
                #opener = urllib.request.build_opener()
                
                #headers = [
                #    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36')
                #]
                #opener.addheaders = headers
                #urllib.request.install_opener(opener)

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

def go_through_all_new_posted_pages(url, save_path):
    mangadown = MangaDown(url, save_path)
    
    current_page = 1
    b_all_posts_today = True

    while b_all_posts_today:
        arr = mangadown.get_pic_urls(url + '?page=' + str(current_page))
        img_infos = mangadown.parse_img_path(arr)
        b_all_posts_today = mangadown.save_pics(img_infos)
        current_page = current_page + 1
    print('Download ends!')

save_path = "E://YandereImages/"
url = "https://yande.re/post"

go_through_all_new_posted_pages(url, save_path)
              
