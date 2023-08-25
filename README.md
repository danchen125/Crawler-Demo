# CrawlerDemo

本Demo專案以Scrapy框架建置，演示爬取Ettoday新聞內容，並將爬取結果解析後存放於SQLite當中，僅擷取部分雲首頁新聞。

爬蟲位置：/MyCrawler/spiders/ettoday.py

資料解析：/MyCrawler/pipelines.py 

SQLite：/ettoday.sqlite (table name:ettoday)
