# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3


class EttodayPipeline:
    def __init__(self):
        self.cursor = None
        self.conn = None

    def open_spider(self, spider):
        self.conn = sqlite3.connect('ettoday.sqlite')
        self.cursor = self.conn.cursor()
        self.cursor.execute("create table if not exists ettoday("
                            "url text, "
                            "id text PRIMARY KEY, "
                            "title text, "
                            "author text, "
                            "content text, "
                            "author_time text, "
                            "created_date text, "
                            "modified_date text"
                            ");")

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        pass

    def process_item(self, item, spider):
        col = ",".join(item.keys())
        placeholders = ",".join(len(item) * "?")

        # 當爬到已經存在的新聞時更新資料，但不改動第一次建檔時間 created_date
        update_list = list()
        for i in item:
            if i != "created_date":
                update_list.append(i + "='" + item[i] + "'")
        updates = ",".join(update_list)

        sql = "insert into ettoday({}) values({}) ON CONFLICT(id) DO UPDATE SET {}"

        self.cursor.execute(sql.format(col, placeholders, updates), list(item.values()))

        return item
