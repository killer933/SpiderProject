import re,pickle,os
from ebooklib import epub
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  #基本设置，可以替代注释里的配置项
logger = logging.getLogger(__name__)   #创建logger对象
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log_epub.txt",encoding='utf-8')   #创建handler对象，保存文件
#handler.setLevel(logging.INFO)
#log_format = '[%(levelname)s TIME:%(asctime)s] %(message)s'
#formatter = logging.Formatter(log_format)
#handler.setFormatter(formatter)
logger.addHandler(handler)  #logger添加handler
def read_content(title,path):
    c = len(os.listdir(path))
    results = []
    for index in range(1,c+1):
        with open(os.path.join(path, title) + '_' + str(index) + r'_pickle', 'rb') as fw:
            result = pickle.load(fw)
            results.append(result)
            logger.info("读取%s第%d个文件",title,index)
    return results
def write_epub(title,results):
    book = epub.EpubBook()
    # add metadata
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('cn')
    book.add_author('killer')

    # intro chapter
    c1 = epub.EpubHtml(title='图书介绍', file_name='intro.xhtml', lang='en')
    c1.content=u'<html><head></head><body><h1>Introduction</h1><p>由killer自动爬虫打造</p></body></html>'
    book.add_item(c1)
    c_all = []
    title_key = dict() 
    for result in  results:
        for result_single in result:
            (index,titles,menu_url,content) = result_single
            if titles in title_key:
                continue
            title_key[titles] = menu_url
            content = content.replace("\n",r'<br/>&emsp;')
            c = epub.EpubHtml(title=titles, file_name=titles + '.xhtml')
            c.content = '<h1>{}</h1><p>&emsp;{}</p>'.format(titles,content)
            c_all.append(c)
            book.add_item(c)
    # about chapter
    #c2 = epub.EpubHtml(title='About this book', file_name='about.xhtml')
    #c2.content='<h1>About this book</h1><p>Helou, this is my book! There are many books, but this one is mine.</p>'

    # add chapters to the book    
    # create table of contents
    # - add section
    # - add auto created links to chapters

    book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
                (epub.Section('目录'),
                tuple(c_all))
                )

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define css style
    style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h1 {
  color: blue;
  text-align: center;
  border: medium double rgb(255,0,0);
  font-size: 20px;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}
p {
  color: blue;
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
'''
    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spine
    book.spine = ['nav', c1]    
    book.spine.extend(c_all)
    # create epub file
    epub.write_epub(title+'.epub', book, {})
def test_epub(title):
    book = epub.EpubBook()
    # set metadata
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('cn')
    book.add_author('killer')
    #book.add_author('Danko Bananko', file_as='Gospodin Danko Bananko', role='ill', uid='coauthor')

    # create html chapter
    c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='hr')
    #c1.content=u'<h1>Intro heading</h1><p>Zaba je skocila u baru.</p><p><img alt="[ebook logo]" src="istatic/ebooklib.gif"/><br/></p>'

    # create image from the local image
    #image_content = open('ebooklib.gif', 'rb').read()
    #img = epub.EpubImage(uid='image_1', file_name='static/ebooklib.gif', media_type='image/gif', content=image_content)
    #c1 = epub.
    # add chapter
    book.add_item(c1)
    # add image
    #book.add_item(img)

    # define Table Of Contents
    book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
                (epub.Section('Simple book'),
                (c1, ))
                )

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = ['nav', c1]

    # write to the file
    epub.write_epub(title+'.epub', book, {})
if __name__=="__main__":
    #test_epub()
    title = "花间1"
    results = read_content(title,"output")
    write_epub(title,results=results)
    
