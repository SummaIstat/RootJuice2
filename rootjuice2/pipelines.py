# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pysolr
import psycopg2
import rootjuice2.globalVars as gv


class SolrPipeline:
    # Inserting items into Solr
    def __init__(self):
        ipAddress = gv.solrIpAddress
        portNumber = gv.solrPortNumber
        coreName = gv.solrCoreName
        self.solr = pysolr.Solr("http://" + ipAddress + ":" + portNumber + "/solr/" + coreName + "/",
                           timeout=10,
                           always_commit=True)



    def process_item(self, item, spider):
        self.solr.add([item], commit=True, waitFlush=True)
        return item


class PostgresPipeline(object):

    def __init__(self):
        hostname = gv.pg_host
        portNumber = gv.pg_port
        username = gv.pg_user
        password = gv.pg_password
        database = gv.pg_database

    def open_spider(self, spider):
        hostname = gv.pg_host
        portNumber = gv.pg_port
        username = gv.pg_user
        password = gv.pg_password
        database = gv.pg_database
        self.connection = psycopg2.connect(host=hostname, port=portNumber, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        #self.cur.execute("insert into documenti(id,pa_id,fonte,isbinary,depth,lastmodified) values(%s,%s,%s,%s,%s,%s)", (item['id'], item['pa_id'], item['fonte'], item['isBinary'], item['depth'], item['lastModified']))
        try:
            self.cur.execute("insert into homepages2015(id,firmid,linkPosition,url,isbinary,depth,indexingDate,lastmodified) values(%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item['id'], item['firmId'], item['linkPosition'], item['url'], item['isBinary'], item['depth'], item['indexingDate'],
                          item['lastModified']))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
        return item
