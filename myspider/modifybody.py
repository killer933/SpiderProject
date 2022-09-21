import mitmproxy.http
from mitmproxy import ctx, http
from bs4 import BeautifulSoup


class Joker:
    def request(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host != "www.baidu.com" or not flow.request.path.startswith("/s"):
            return

        if "wd" not in flow.request.query.keys():
            ctx.log.warn("can not get search word from %s" % flow.request.pretty_url)
            return

        ctx.log.info("catch search word: %s" % flow.request.query.get("wd"))
        flow.request.query.set_all("wd", ["360搜索"])

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host != "www.haitangsoshu.com":
            return
        #text = flow.response.get_text()
        ctx.log.info("!!!!!!!!!!!!!!!!!!!!!!!!!!catch haitangsoshu!!!!!!!!!!!!!!!!!!!!!!")
        content = flow.response.get_content()
        bs4 = BeautifulSoup(content, 'lxml') 
        #网站内容保持在网页
        out_str = bs4.prettify()
        with open('haitang.html','w',encoding='utf-8') as f:
            f.write(out_str)
        # text = flow.response.get_text()
        # text = text.replace("搜索", "请使用谷歌")
        # flow.response.set_text(text)

    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host == "www.google.com":
            #flow.response = http.HTTPResponse.make(404)
            ctx.log.info("catch google")

addons = [
    Joker()
]