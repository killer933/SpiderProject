from pip import main
import requests
import re,pickle
import lxml,time,random
from bs4 import BeautifulSoup
from selenium import webdriver
from browsermobproxy import Server
###可以用Mitmproxy替代browsermobproxy
import sys
sys.setrecursionlimit(1000000)
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  #基本设置，可以替代注释里的配置项
logger = logging.getLogger(__name__)   #创建logger对象
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt",encoding='utf-8')   #创建handler对象，保存文件
#handler.setLevel(logging.INFO)
#log_format = '[%(levelname)s TIME:%(asctime)s] %(message)s'
#formatter = logging.Formatter(log_format)
#handler.setFormatter(formatter)
logger.addHandler(handler)  #logger添加handler
class Myspider(object):
    def __init__(self,headers,headerless,picklefile,browsermobproxy=False,proxy_param=None) -> None:
        self.headerless =  headerless
        self.proxy_param = proxy_param
        self.browsermobproxy = browsermobproxy
        self.proxy_file = r'D:\工程代码\python\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat'
        self.selenium_userdata = r"C:/Users/39738/AppData/Local/Google/Chrome/User Data"
        self.dump_file = picklefile
        self.headers = headers
        self.proxy = None
        self.browser  =None 
        if self.browsermobproxy:
            self.init_proxy()
        self.init_selenium()
    def init_proxy(self):
        #使用browsermobproxy代理
        server = Server(self.proxy_file)
        server.start()
        self.proxy = server.create_proxy()
        self.proxy_param = format(self.proxy.proxy)
    def init_selenium(self):
        options = webdriver.ChromeOptions()
        ua = self.headers['User-Agent']
        options.add_argument("--user-data-dir=" + self.selenium_userdata )
        if self.proxy_param:
            options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
        options.add_argument('--ignore-certificate-errors')
    #  options.add_argument('user-agent=%s'%ua)
        if self.headerless:
            options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors","enable-automation"])
        self.browser = webdriver.Chrome(chrome_options=options)
    def run(self,baseurl,contenturl):
        index = 1
        self.browser.get("https://www.baidu.com")
        while True:
            results = []
            url = contenturl + str(index) + ".html"
            hrefs,titles = self.get_url(url)
            if  len(hrefs) == 0:
                break
            for j,href in enumerate(hrefs):
                menu_url = baseurl+href
                content=None
                result = dict()
                while True:
                    if content is not None:
                        break
                    try:
                        content = self.get_content(menu_url)
                        if key_content in "\n".join(content) or len(content) == 0:
                            content = None
                            logger.error("Error  下载不完全!! titles: %s,href: %s",titles[j],menu_url)
                            self.random_sleep(mu=3)
                    except:
                        logger.error("Error !! 下载出错 titles: %s,href: %s",titles[j],menu_url)
                        self.random_sleep(mu=3)
                # result["index"] = index
                # result["titles"] = titles[j]
                # result["menu_url"] = menu_url
                # result["content"] = "\n".join(content)
                # results.append(result)
                results.append((index,titles[j],menu_url,"\n".join(content)))
                logger.info("titles: %s,href: %s,content:%s",titles[j],menu_url,content[0])
                self.random_sleep(mu=1)
            self.dumps(index,results)
            logger.info("完成第 %d,href: %s",index,url)
            index = index + 1
    def dumps(self,index,results):
        with open(self.dump_file + '_' + str(index) + r'_pickle', 'wb') as fw:
            pickle.dump(results, fw,-1)
    def get_url(self,url):
        hrefs=[]
        titles=[]
        doc = requests.get(url,headers=self.headers,proxies =self.proxy_param)
        doc.encoding='utf-8'
        if doc.status_code != 200:
            return hrefs,titles
        #print(doc.text)
        bs4 = BeautifulSoup(doc.content, 'lxml') 
        #网站内容保持在网页
        # out_str = bs4.prettify()
        # with open('test_html.html','w',encoding='utf-8') as f:
        #     f.write(out_str)
        menu_div = bs4.find_all("li", class_='BCsectionTwo-top-chapter')
        for i,obj in enumerate(menu_div):
            kk = obj.find("a")
            href = kk['href']  
            menu = kk.string
            hrefs.append(href)
            titles.append(menu)
            # print('menu的链接是：\n',href)
            # print('menu的内容是：\n',menu)
        return hrefs,titles
    def get_content(self,url):
        contents = []
        if self.browsermobproxy:
            self.proxy.new_har(options={'captureHeaders': True, 'captureContent': True})
        self.browser.get(url)
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        page_source = self.browser.page_source
        #print(doc.text)
        if self.browsermobproxy:
            time.sleep(5)
            result = self.proxy.har
            urls = []
            content = []
            for entry in result['log']['entries']:
                _url = entry['request']['url']
                request = entry['request']
                response = entry['response']
                if url in _url:
                    code = response['status']
                    if code == 200:
                        print('链接：{0}\t响应码:{1}'.format(_url, code))
                        try:
                            page_source = response['content']['text']
                        except:
                            page_source =  None
                    else:
                        # log.log_error('报错页面：{0}\n链接：{1}\n响应码:{2}\n响应内容:{3}'.format(url,_url, code, _response))
                        print('报错链接：{0}\n状态码:{1}'.format(_url, code))
                        page_source =None
        if page_source == None or page_source == '':
            return contents
        bs4 = BeautifulSoup(page_source, 'lxml') 
        content_div = bs4.find("div", class_='RBGsectionThree-content')
        for obj in content_div.find_all("p"):        
            content = obj.string
            contents.append(content)
        return contents
    def random_sleep(self,mu=1, sigma=0.4):
        '''正态分布随机睡眠
        :param mu: 平均值
        :param sigma: 标准差，决定波动范围
        '''
        secs = random.normalvariate(mu, sigma)
        if secs <= 0:
            secs = mu  # 太小则重置为平均值
        time.sleep(secs)
if __name__=="__main__":
    #18763 30625  
    base_url = "https://www.haitang123.co"
    content_url ="https://www.haitang123.co/book/41142/catalog/"
    headers = {
    'User-Agent':'Mozilla/5.0 (Linux; Android 11; M2101K7BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36'
    }
    #用于表示是否下载完成
    key_content = r'内容未加载完成，请尝试【刷新网页】or【设置-关闭小说模式】or【设置-关闭广告屏蔽】~'
    # '/book/120929/4414892.html'
    # '/book/120929/4414893.html'
    myspider = Myspider(headers,headerless=False,picklefile=r'output/花间3',browsermobproxy=False,proxy_param=None)
    myspider.run(base_url,content_url)