# coding=utf-8

from lxml import etree
import sqlite3
import re
import requests
import random
import time
import logging

user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 "
    "Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 "
    "Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR "
    "3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 "
    "Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET "
    "CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) "
    "Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) "
    "Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) "
    "Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) "
    "Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) "
    "AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) "
    "Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 "
    "Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) "
    "wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) "
    "AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    # iPhone 6：
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 "
    "Mobile/10A5376e Safari/8536.25",
]


def get_user_agent():
    headers = {"User-Agent": random.choice(user_agent)}
    return headers


class Scraper:
    database: str
    tag: str
    page: int

    def __init__(self):
        self.database = "book.db"
        self.tag = ""
        self.page = 0
        self.pattern_number = re.compile(r"\d+\.?\d*")
        logging.basicConfig(filename="scraper.log", level=logging.ERROR)

    def get_current_progress(self) -> ():
        conn = sqlite3.connect(self.database)
        results = conn.execute("SELECT tag, page from progress where id = '0'")
        for row in results:
            return row[0], row[1]
        return "", 0

    def save_current_progress(self, current_tag, current_page):
        conn = sqlite3.connect(self.database)
        conn.execute(
            "UPDATE progress set tag = '{}', page = {} where id = '0'".format(
                current_tag, current_page
            )
        )
        conn.commit()
        conn.close()

    def start_grab(self) -> bool:
        self.create_tables()
        scraper.grab_tag()
        current_tag, current_page = self.get_current_progress()
        tags = self.get_tag_list()
        for i in range(0, len(tags)):
            no = 0
            if i == 0 and current_tag == tags[i]:
                no = current_page
            while self.grab_book_list(tags[i], no):
                no = no + 20
        return True

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        try:
            conn.execute("CREATE TABLE tags (tag TEXT PRIMARY KEY)")
            conn.commit()
        except sqlite3.Error as e:
            logging.error(str(e))
            conn.rollback()

        try:
            conn.execute(
                "CREATE TABLE book ("
                "id TEXT PRIMARY KEY, title TEXT, author TEXT, "
                "publisher TEXT, original_title TEXT, "
                "translator TEXT, pub_year TEXT, pages INTEGER, "
                "price INTEGER, currency_unit TEXT, binding TEXT, "
                "isbn TEXT, author_intro TEXT, book_intro text, "
                "content TEXT, tags TEXT, picture BLOB)"
            )
            conn.commit()
        except sqlite3.Error as e:
            logging.error(str(e))
            conn.rollback()

        try:
            conn.execute(
                "CREATE TABLE progress (id TEXT PRIMARY KEY, tag TEXT, page integer )"
            )
            conn.execute("INSERT INTO progress values('0', '', 0)")
            conn.commit()
        except sqlite3.Error as e:
            logging.error(str(e))
            conn.rollback()

    def grab_tag(self):
        url = "https://book.douban.com/tag/?view=cloud"
        r = requests.get(url, headers=get_user_agent())
        r.encoding = "utf-8"
        h: etree.ElementBase = etree.HTML(r.text)
        tags: [] = h.xpath(
            '/html/body/div[@id="wrapper"]/div[@id="content"]'
            '/div[@class="grid-16-8 clearfix"]/div[@class="article"]'
            '/div[@class=""]/div[@class="indent tag_cloud"]'
            "/table/tbody/tr/td/a/@href"
        )
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        try:
            for tag in tags:
                t: str = tag.strip("/tag")
                c.execute("INSERT INTO tags VALUES ('{}')".format(t))
            c.close()
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logging.error(str(e))
            conn.rollback()
            return False
        return True

    def grab_book_list(self, tag="小说", pageno=1) -> bool:
        logging.info("start to grab tag {} page {}...".format(tag, pageno))
        self.save_current_progress(tag, pageno)
        url = "https://book.douban.com/tag/{}?start={}&type=T".format(tag, pageno)
        r = requests.get(url, headers=get_user_agent())
        r.encoding = "utf-8"
        h: etree.Element = etree.HTML(r.text)

        li_list: [] = h.xpath(
            '/html/body/div[@id="wrapper"]/div[@id="content"]'
            '/div[@class="grid-16-8 clearfix"]'
            '/div[@class="article"]/div[@id="subject_list"]'
            '/ul/li/div[@class="info"]/h2/a/@href'
        )
        next_page = h.xpath(
            '/html/body/div[@id="wrapper"]/div[@id="content"]'
            '/div[@class="grid-16-8 clearfix"]'
            '/div[@class="article"]/div[@id="subject_list"]'
            '/div[@class="paginator"]/span[@class="next"]/a[@href]'
        )
        has_next = True
        if len(next_page) == 0:
            has_next = False
        if len(li_list) == 0:
            return False

        for li in li_list:
            li.strip("")
            book_id = li.strip("/").split("/")[-1]
            try:
                delay = float(random.randint(0, 200)) / 100.0
                time.sleep(delay)
                self.crow_book_info(book_id)
            except BaseException as e:
                logging.error(
                    logging.error("error when scrape {}, {}".format(book_id, str(e)))
                )
        return has_next

    def get_tag_list(self) -> [str]:
        ret = []
        conn = sqlite3.connect(self.database)
        results = conn.execute(
            "SELECT tags.tag from tags join progress where tags.tag >= progress.tag"
        )
        for row in results:
            ret.append(row[0])
        return ret

    def crow_book_info(self, book_id) -> bool:
        conn = sqlite3.connect(self.database)
        for _ in conn.execute("SELECT id from book where id = ('{}')".format(book_id)):
            return

        url = "https://book.douban.com/subject/{}/".format(book_id)
        r = requests.get(url, headers=get_user_agent())
        r.encoding = "utf-8"
        h: etree.Element = etree.HTML(r.text)
        e_text = h.xpath('/html/body/div[@id="wrapper"]/h1/span/text()')
        if len(e_text) == 0:
            return False

        title = e_text[0]

        elements = h.xpath(
            '/html/body/div[@id="wrapper"]'
            '/div[@id="content"]/div[@class="grid-16-8 clearfix"]'
            '/div[@class="article"]'
        )
        if len(elements) == 0:
            return False

        e_article = elements[0]

        book_intro = ""
        author_intro = ""
        content = ""
        tags = ""

        e_book_intro = e_article.xpath(
            'div[@class="related_info"]'
            '/div[@class="indent"][@id="link-report"]/*'
            '/div[@class="intro"]/*/text()'
        )
        for line in e_book_intro:
            line = line.strip()
            if line != "":
                book_intro = book_intro + line + "\n"

        e_author_intro = e_article.xpath(
            'div[@class="related_info"]'
            '/div[@class="indent "]/*'
            '/div[@class="intro"]/*/text()'
        )
        for line in e_author_intro:
            line = line.strip()
            if line != "":
                author_intro = author_intro + line + "\n"

        e_content = e_article.xpath(
            'div[@class="related_info"]'
            '/div[@class="indent"][@id="dir_' + book_id + '_full"]/text()'
        )
        for line in e_content:
            line = line.strip()
            if line != "":
                content = content + line + "\n"

        e_tags = e_article.xpath(
            'div[@class="related_info"]/'
            'div[@id="db-tags-section"]/'
            'div[@class="indent"]/span/a/text()'
        )
        for line in e_tags:
            line = line.strip()
            if line != "":
                tags = tags + line + "\n"

        e_subject = e_article.xpath(
            'div[@class="indent"]'
            '/div[@class="subjectwrap clearfix"]'
            '/div[@class="subject clearfix"]'
        )
        pic_href = e_subject[0].xpath('div[@id="mainpic"]/a/@href')
        picture = None
        if len(pic_href) > 0:
            res = requests.get(pic_href[0], headers=get_user_agent())
            picture = res.content

        info_children = e_subject[0].xpath('div[@id="info"]/child::node()')

        e_array = []
        e_dict = dict()

        for e in info_children:
            if isinstance(e, etree._ElementUnicodeResult):
                e_dict["text"] = e
            elif isinstance(e, etree._Element):
                if e.tag == "br":
                    e_array.append(e_dict)
                    e_dict = dict()
                else:
                    e_dict[e.tag] = e

        book_info = dict()
        for d in e_array:
            label = ""
            span = d.get("span")
            a_label = span.xpath("span/text()")
            if len(a_label) > 0 and label == "":
                label = a_label[0].strip()
            a_label = span.xpath("text()")
            if len(a_label) > 0 and label == "":
                label = a_label[0].strip()
            label = label.strip(":")
            text = d.get("text").strip()
            e_a = d.get("a")
            text.strip()
            text.strip(":")
            if label == "作者" or label == "译者":
                a = span.xpath("a/text()")
                if text == "" and len(a) == 1:
                    text = a[0].strip()
                if text == "" and e_a is not None:
                    text_a = e_a.xpath("text()")
                    if len(text_a) > 0:
                        text = text_a[0].strip()
                        text = re.sub(r"\s+", " ", text)
            if text != "":
                book_info[label] = text

        sql = (
            "INSERT INTO book("
            "id, title, author, "
            "publisher, original_title, translator, "
            "pub_year, pages, price, "
            "currency_unit, binding, isbn, "
            "author_intro, book_intro, content, "
            "tags, picture)"
            "VALUES("
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?, ?, "
            "?, ?)"
        )

        unit = None
        price = None
        pages = None
        conn = sqlite3.connect(self.database)
        try:
            s_price = book_info.get("定价")
            if s_price is None:
                # price cannot be NULL
                logging.error(
                    "error when scrape book_id {}, cannot retrieve price...", book_id
                )
                return None
            else:
                e = re.findall(self.pattern_number, s_price)
                if len(e) != 0:
                    number = e[0]
                    unit = s_price.replace(number, "").strip()
                    price = int(float(number) * 100)

            s_pages = book_info.get("页数")
            if s_pages is not None:
                # pages can be NULL
                e = re.findall(self.pattern_number, s_pages)
                if len(e) != 0:
                    pages = int(e[0])

            conn.execute(
                sql,
                (
                    book_id,
                    title,
                    book_info.get("作者"),
                    book_info.get("出版社"),
                    book_info.get("原作名"),
                    book_info.get("译者"),
                    book_info.get("出版年"),
                    pages,
                    price,
                    unit,
                    book_info.get("装帧"),
                    book_info.get("ISBN"),
                    author_intro,
                    book_intro,
                    content,
                    tags,
                    picture,
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            logging(str(e))
            conn.rollback()
        except TypeError as e:
            logging.error("error when scrape {}, {}".format(book_id, str(e)))
            conn.rollback()
            return False
        conn.close()
        return True


if __name__ == "__main__":
    scraper = Scraper()
    scraper.start_grab()
