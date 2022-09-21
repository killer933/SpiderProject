from pip import main
import requests
import re
import lxml,time
from bs4 import BeautifulSoup
from selenium import webdriver
from browsermobproxy import Server

server = Server(r'D:\工程代码\python\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat')
server.start()
proxy = server.create_proxy()

# reObj = re.compile('第*章') 
# menu = ""
# with open('123.txt','r',encoding='gb18030') as f:
#     lines = f.readlines()
#     for line in lines:
#         str = reObj.findall(line)
#         if str:
#             menu = menu + line
# with open('menu.text','w',encoding='utf-8') as f:
#     f.write(menu)
def spider(url):
    hrefs=[]
    titles=[]
    headers = {
    'User-Agent':'Mozilla/5.0 (Linux; Android 11; M2101K7BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36'
    }
    doc = requests.get(url,headers=headers)
    doc.encoding='utf-8'
    #print(doc.text)
    bs4 = BeautifulSoup(doc.content, 'lxml') 
    out_str = bs4.prettify()
    with open('test_html.html','w',encoding='utf-8') as f:
        f.write(out_str)
    menu_div = bs4.find_all("li", class_='BCsectionTwo-top-chapter')
    for i,obj in enumerate(menu_div):
        kk = obj.find("a")
        href = kk['href']  
        menu = kk.string
        hrefs.append(href)
        titles.append(menu)
        # print('menu的链接是：\n',href)
        # print('menu的内容是：\n',menu)
        if i==99:
            break
    return hrefs,titles
def get_content(url):
    contents = []
    headers = {
    'User-Agent':'Mozilla/5.0 (Linux; Android 11; M2101K7BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36'
    }

    # doc = requests.get(url,headers=headers)
    # doc.encoding='utf-8'
    options = webdriver.ChromeOptions()
    ua = headers['User-Agent']
    print(proxy.proxy)
    options.add_argument("--user-data-dir="+r"C:/Users/39738/AppData/Local/Google/Chrome/User Data")
    options.add_argument('--proxy-server={0}'.format(proxy.proxy))
    options.add_argument('--ignore-certificate-errors')
  #  options.add_argument('user-agent=%s'%ua)
    options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors","enable-automation"])
    browser = webdriver.Chrome(chrome_options=options)
    proxy.new_har(options={'captureHeaders': True, 'captureContent': True})
    browser.get(url)
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    #print(doc.text)
    # time.sleep(5)
    # result = proxy.har
    # urls = []
    # content = []
    # for entry in result['log']['entries']:
    #     _url = entry['request']['url']
    #     request = entry['request']
    #     response = entry['response']
    #     if 'google' in _url:
    #         continue
    #     try:
    #         page_source = response['content']['text']
    #         urls.append(_url)
    #         content.append(page_source)
    #         if '环绕' in page_source:
    #             print(page_source)
    #         # print(_url)
    #         # print(page_source)

    #     except:
    #         continue
    #     if url in _url:
    #         code = response['status']
    #         if code == 200:
    #             print('链接：{0}\t响应码:{1}'.format(_url, code))
    #             #page_source = response['content']['text']
    #         else:
    #             # log.log_error('报错页面：{0}\n链接：{1}\n响应码:{2}\n响应内容:{3}'.format(url,_url, code, _response))
    #             print('报错链接：{0}\n状态码:{1}'.format(_url, code))
    #             return None

    bs4 = BeautifulSoup(browser.page_source, 'lxml') 
    content_div = bs4.find("div", class_='RBGsectionThree-content')
    for obj in content_div.find_all("p"):        
        content = obj.string
        contents.append(content)
    return contents


# for kk in menu_div.find_all("a"):
#     href = kk['href']
#     menu = kk.string
#     print('menu的链接是：\n',href)
#     print('menu的内容是：\n',menu)  
if __name__=="__main__":
    baseurl = "https://www.haitang123.co"
    url ="https://www.haitang123.co/book/120929/catalog/"
    # '/book/120929/4414892.html'
    # '/book/120929/4414893.html'
    for i in range(1,20):
        url = url + str(i) + ".html"
        hrefs,titles = spider(url)
        for j,href in enumerate(hrefs):
            content = get_content(baseurl+href)
