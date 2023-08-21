import bs4
import scrapy
from MyCrawler.items import EttodayItem
import re
import requests as rq
import datetime
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor


class EttodaySpider(scrapy.Spider):
    name = "ettoday"
    allowed_domains = ["www.ettoday.net",
                       "house.ettoday.net",
                       "sports.ettoday.net",
                       "star.ettoday.net",
                       "finance.ettoday.net"]
    start_urls = ["https://www.ettoday.net",
                  "https://house.ettoday.net",
                  "https://sports.ettoday.net",
                  "https://star.ettoday.net",
                  "https://finance.ettoday.net"]

    # rules 是 for CrawlSpider 使用，Demo先改回 scrapy.Spider，func parse_list 先改名回parse
    """ 
    rules = [
        Rule(LinkExtractor(allow="/news/"), callback='parse_list', follow=True)
    ]
    """

    def parse(self, response, **kwargs):
        domain = "https://www.ettoday.net"
        soup = bs4.BeautifulSoup(response.body, "html.parser")
        for news in soup.select("h3 > a"):

            # 僅擷取含有"/news/"的新聞網址
            if "/news/" in news.get("href"):

                # 判斷網址是否為絕對路徑，如果不是則加上domain
                if "http://" in news.get("href") or "https://" in news.get("href"):
                    url = news.get("href")
                else:
                    url = domain + news.get("href")

                # 因需紀錄網址，透過meta將url傳入給parse_detail處理
                yield scrapy.Request(url, self.parse_detail, meta={'url': url})

    @staticmethod
    def parse_detail(response):
        ettoday_item = EttodayItem()  # 於items.py中定義的類別
        soup = bs4.BeautifulSoup(response.body, "html.parser")

        url = rq.get(response.meta["url"]).url  # 網站機制有跨網域轉導，改抓轉導後的url
        url = url.split("?")[0]  # 排除參數

        news_id = url.split("/")[-1].replace(".htm", "")  # 從網址中擷取新聞編號

        authors = list()
        contents = list()
        for tag in soup.select(".story > p:not(.no_margin)"):

            # strong tag 用於圖片說明，不列入正文
            if tag.text != "" and tag.get('class') != "no_margin" and not tag.select('strong'):
                txt = tag.text

                # 將作者區隔出來
                if re.search("／.*報導", txt) or re.search("文／", txt) or re.search("／.*編譯", txt):

                    # 有發現作者與正文並在同一個<p>內，因此特別處理
                    if len(txt) < 20:
                        authors.append(txt)
                    else:
                        authors.append(txt.split("\n")[0])

                        txt = ''.join(txt.split("\n")[1:])
                        txt = txt.replace("\n", "")

                        contents.append(txt)

                else:
                    txt = txt.replace("\n", "")
                    contents.append(txt)

        # 網站上日期格式不一，統一調整成 yyyy-mm-dd HH:MM:00
        time = soup.select("time.date")[0].text.strip()
        trans_table = time.maketrans({"年": "-", "月": "-", "日": ""})
        time = time.translate(trans_table) + ":00"

        ettoday_item['id'] = news_id
        ettoday_item['url'] = url
        ettoday_item['title'] = soup.select("h1.title")[0].text
        ettoday_item['author'] = "".join(authors)
        ettoday_item['content'] = "\n".join(contents)
        ettoday_item['author_time'] = time

        ettoday_item['created_date'] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        ettoday_item['modified_date'] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        return ettoday_item
