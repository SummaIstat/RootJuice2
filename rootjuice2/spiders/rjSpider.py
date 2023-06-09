from itertools import chain
import re
import time

from tikapp import TikaApp
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from rootjuice2.customLinkExtractor import CustomLinkExtractor
from rootjuice2.items import Rootjuice2Item
from urllib.parse import urlparse
import rootjuice2.globalVars as gv
import os
import sys
import shutil
import logging
from datetime import datetime
from scrapy import signals
from pydispatch import dispatcher

import warnings
warnings.filterwarnings("ignore") # suppress all warnings

logger = logging.getLogger('rootJuice2Logger')
control_chars = ''.join(map(chr, chain(range(0, 9), range(11, 32), range(127, 160))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(control_chars))
# TEXTRACT_EXTENSIONS = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
TEXTRACT_EXTENSIONS = [".pdf"]


def checkSeedFile(argv):

    if len(argv) < 8:
        return False # the first 4 arguments are part of the default program call

    if not argv[3].startswith('seedFilePath'):
        return False

    return True


def checkConfigFile(argv):
    '''
    if len(argv) < 8:
        return False

    if not argv[5].startswith('confFilePath'):
        return False
    '''
    return True

def getLastModifiedAsSolrDate(scrapedTime):
    if scrapedTime != "":
        tmpTime = time.strptime(scrapedTime, "%a, %d %b %Y %H:%M:%S %Z")
        lastModified = str(tmpTime.tm_year) + "-" + \
                       str(tmpTime.tm_mon).zfill(2) + "-" + \
                       str(tmpTime.tm_mday).zfill(2) + \
                       "T" + \
                       str(tmpTime.tm_hour).zfill(2) +\
                       ":" + \
                       str(tmpTime.tm_min).zfill(2) + \
                       ":" + \
                       str(tmpTime.tm_sec).zfill(2) + \
                       "Z"
        return lastModified

def getConfigFilePath(argv):
    for i, arg in enumerate(argv):
        if argv[i].startswith('confFilePath'):
            return argv[i].split("=")[1]


class RjSpider(CrawlSpider):

    name = "rjSpider"
    external_settings = dict()
    tika_client = ""
    jobdir = ""

    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    # if not checkSeedFile(sys.argv):
    #    sys.exit("No seed file provided ! \n USAGE: scrapy crawl rjSpider -a seedFilePath=my_path/seed.tsv -a confFilePath=my_path/config.cfg")

    if checkConfigFile(sys.argv):

        # load external configuration
        # configFilePath = str(sys.argv.__getitem__(5)).split("=")[1]
        configFilePath = getConfigFilePath(sys.argv)
        with open(configFilePath, "rt") as f:
            for line in f.readlines():
                if not line.startswith("#"):
                    tokens = line.split("=")
                    if len(tokens) == 2:
                        external_settings[tokens[0]] = tokens[1]

        # apply external configuration
        gv.init()
        try:
            MAX_NUM_PAGES_PER_SITE = int(external_settings['MAX_NUM_PAGES_PER_SITE'])
            DEPTH_LIMIT = int(external_settings['DEPTH_LIMIT'])
            LOG_FILE_FOLDER = str(external_settings['LOG_FILE_FOLDER']).rstrip()
            LOG_LEVEL = str(external_settings['LOG_LEVEL']).rstrip()
            BIN_FOLDER = str(external_settings['BIN_FOLDER']).rstrip()
            TIKA_APP_JAR = str(external_settings['TIKA_APP_JAR']).rstrip()
            SOLR_IP_ADDRESS = str(external_settings['SOLR_IP_ADDRESS']).rstrip()
            SOLR_PORT_NUMBER = str(external_settings['SOLR_PORT_NUMBER']).rstrip()
            SOLR_CORE_NAME = str(external_settings['SOLR_CORE_NAME']).rstrip()
            POSTGRES_DATABASE = str(external_settings['POSTGRES_DATABASE']).rstrip()
            POSTGRES_USER = str(external_settings['POSTGRES_USER']).rstrip()
            POSTGRES_PASSWORD = str(external_settings['POSTGRES_PASSWORD']).rstrip()
            POSTGRES_HOST = str(external_settings['POSTGRES_HOST']).rstrip()
            POSTGRES_PORT = str(external_settings['POSTGRES_PORT']).rstrip()
        except:
            raise Exception("Invalid parameter values in config.cfg")

        gv.maxPagesPerSiteLimit = MAX_NUM_PAGES_PER_SITE
        gv.binFolder = BIN_FOLDER
        gv.tikaAppJar = TIKA_APP_JAR
        gv.solrIpAddress = SOLR_IP_ADDRESS
        gv.solrPortNumber = SOLR_PORT_NUMBER
        gv.solrCoreName = SOLR_CORE_NAME
        gv.logLevel = LOG_LEVEL

        gv.pg_database = POSTGRES_DATABASE
        gv.pg_user = POSTGRES_USER
        gv.pg_password = POSTGRES_PASSWORD
        gv.pg_host = POSTGRES_HOST
        gv.pg_port = POSTGRES_PORT

        now = datetime.now()
        dateTime = now.strftime("%Y_%m_%d_%H_%M_%S")
        logFile = LOG_FILE_FOLDER + "/" + "rootJuice2_" + dateTime + ".log"

        logging.basicConfig(
            filename=logFile,
            level=gv.logLevel,
            format='%(asctime)s%(levelname)s: %(message)s'
        )

        custom_settings = {
            'DEPTH_LIMIT': str(DEPTH_LIMIT),
        }

        for arg in sys.argv:
            if str(arg).startswith("JOBDIR"):
                jobdir = str(arg).split("=")
                jobdir = jobdir[1]

    else:
        sys.exit("Configuration file invalid or not provided ! \n USAGE: scrapy crawl rjSpider -a seedFilePath=my_path/seed.tsv -a confFilePath=my_path/config.cfg")

    # =========================================================================================
    # =========================================================================================
    def spider_closed(self, spider, reason):
        if reason == "finished":
            self.logger.info("The spider ended its activity !")
            self.logger.info("Time to delete the JOBDIR " + str(self.jobdir))
            try:
                shutil.rmtree(self.jobdir)
                self.logger.info("JOBDIR " + str(self.jobdir) + " successfully deleted")
            except OSError as e:
                self.logger.error("Error deleting JOBDIR " + str(self.jobdir))
                self.logger.error("Error: %s - %s." % (e.filename, e.strerror))

    def __init__(self, *args, **kwargs):
        global tika_client
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        tika_client = TikaApp(file_jar=gv.tikaAppJar)
        #logging.getLogger('scrapy.core.scraper').setLevel(gv.logLevel)
        logging.getLogger('scrapy').setLevel(gv.logLevel)
        logging.getLogger('protego').setLevel(gv.logLevel)
        logging.getLogger('pysolr').setLevel(gv.logLevel)
        logging.getLogger('tikapp.tikapp').setLevel(gv.logLevel)
        logging.getLogger('urllib3.connectionpool').setLevel(gv.logLevel)
        logging.getLogger('rjSpider').setLevel(gv.logLevel)
        super(RjSpider, self).__init__(*args, **kwargs)

    # =========================================================================================
    # =========================================================================================

    def start_requests(self):

        self.logger.info("start_requests\n\n\n\n\n\n\n\n\n\n")
        seedFilePath = str(sys.argv.__getitem__(3)).split("=")[1]
        with open(seedFilePath, "rt") as f:
            next(f)  # ignore the first line containing the header
            #start_urls = dict([url.split("\t") for url in f.readlines()])
            start_urls = [url.split("\t") for url in f.readlines()]

        #for firm_id, link_pos, url in start_urls.items():
        for firm_id, link_pos, url in start_urls:
            url = url.strip()
            self.logger.debug(firm_id)
            self.logger.debug(link_pos)
            self.logger.debug(url)
            # passo l'id nel parametro meta di Request
            yield Request(url=url, callback=self.parse_item, meta={"firm_id": firm_id, "link_pos": link_pos, "antani": 1})

    # =========================================================================================
    # =========================================================================================

    def parse_item(self, response):

        firm_id = response.meta["firm_id"]
        link_pos = response.meta["link_pos"]
        depth = response.meta["depth"]
        url = response.url

        if not hasattr(response, "text"):

            self.logger.debug("binary file !")
            extension = list(filter(lambda x: response.url.lower().endswith(x), TEXTRACT_EXTENSIONS))
            if extension:

                #lastModified = str(response.headers.get('Last-Modified', f""), 'utf-8')
                lastModified = getLastModifiedAsSolrDate(str(response.headers.get('Last-Modified', "Thu, 01 Jan 1970 00:00:01 GMT"), 'utf-8'))
                firm_id = response.meta["firm_id"]
                depth = response.meta["depth"]
                url = response.url

                page = response.url.split("/")[-1]
                binFolder = gv.binFolder
                subFolder = str(firm_id)
                if not os.path.exists(binFolder + "/" + subFolder):
                    os.makedirs(binFolder + "/" + subFolder)
                filename = str(binFolder) + "/" + str(subFolder) + "/" + str(page)  # +str(extension)
                with open(filename, 'wb') as f:
                    f.write(response.body)
                    f.close()

                extracted_data = tika_client.extract_only_content(f.name)

                item = {}
                item["id"] = str(firm_id) + "*" + str(link_pos) + "*" + str(url)
                item["firmId"] = firm_id
                item["linkPosition"] = link_pos
                item["url"] = url
                item["isBinary"] = "1"
                item["depth"] = depth
                item["indexingDate"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                item["lastModified"] = lastModified
                item["titolo"] = str(page).strip()
                item["corpoPagina"] = extracted_data
                item["metatagDescription"] = ""
                item["metatagKeywords"] = ""
                item["imgsrc"] = [""]
                item["imgalt"] = [""]
                item["links"] = [""]
                item["ahref"] = [""]
                item["inputvalue"] = [""]
                item["inputname"] = [""]
                item["codiceLink"] = link_pos
                item["codiceAzienda"] = firm_id
                item["pageBody"] = extracted_data

                # delete just used file from disk
                os.remove(filename)

                # save item for subsequent uses
                #yield item


                parsed_uri = urlparse(str(response.url))
                domain = '{uri.netloc}/'.format(uri=parsed_uri)
                if gv.scraped_count[domain] >= (gv.maxPagesPerSiteLimit * 2):
                    self.logger.debug('Page Limit reached for {}'.format(domain))
                else:
                    gv.scraped_count[domain] += 1
                    # save item for subsequent uses
                    yield item
        else:

            #lastModified = str(response.headers.get('Last-Modified', f""), 'utf-8')
            lastModified = getLastModifiedAsSolrDate(str(response.headers.get('Last-Modified', "Thu, 01 Jan 1970 00:00:01 GMT"), 'utf-8'))
            html = response.body.decode("utf-8")
            soup = BeautifulSoup(html, 'lxml')  # important to specify lxml for portability

            metatagDescription = ""
            metatagDescription_tag = soup.find_all('meta', attrs={'name': 'description'})
            if len(metatagDescription_tag) != 0:
                #print(metatagDescription_tag[0]["content"])
                metatagDescription = str(metatagDescription_tag[0]["content"])

            metatagKeywords = ""
            metatagKeywords_tag = soup.find_all('meta', attrs={'name': 'keywords'})
            if len(metatagKeywords_tag) != 0:
                #print(metatagKeywords_tag[0]["content"])
                metatagKeywords = str(metatagKeywords_tag[0]["content"])

            imgsrc = []
            imgalt = []
            img_tags = soup.find_all('img')
            for tag in img_tags:
                #print(tag.get("src", ""))
                imgsrc.append(tag.get("src", ""))
                #print(tag.get("alt", ""))
                imgalt.append(tag.get("alt", ""))

            ahref = []
            links = []
            a = soup.find_all('a')
            for tag in a:
                #print(tag.get("href", ""))
                ahref.append(tag.get("href", ""))
                #print(tag.find(text=True))
                #links.append(tag.find(text=True))
                links.append(tag.getText().strip())


            inputname = []
            inputvalue = []
            inputs_tag = soup.find_all('input')
            for tag in inputs_tag:
                #print(tag.get("name", ""))
                inputname.append(tag.get("name", ""))
                #print(tag.get("value", ""))
                inputvalue.append(tag.get("value", ""))



            [s.extract() for s in soup('script')]  # remove javascript text
            text = soup.get_text().strip()
            text = ' '.join(text.split())  # remove spaces
            titolo = str(response.xpath('//title/text()').get()).strip()

            item = {}
            item["id"] = str(firm_id) + "*" + str(link_pos) + "*" + str(url)
            item["firmId"] = firm_id
            item["linkPosition"] = link_pos
            item["url"] = url
            item["isBinary"] = "0"
            item["depth"] = depth
            item["indexingDate"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            item["lastModified"] = lastModified
            item["titolo"] = titolo
            item["corpoPagina"] = text
            item["metatagDescription"] = metatagDescription
            item["metatagKeywords"] = metatagKeywords
            item["imgsrc"] = imgsrc
            item["imgalt"] = imgalt
            item["links"] = links
            item["ahref"] = ahref
            item["inputvalue"] = inputvalue
            item["inputname"] = inputname
            item["codiceLink"] = link_pos
            item["codiceAzienda"] = firm_id
            item["pageBody"] = text

            # Links extraction in order to generate new requests
            parsed_uri = urlparse(str(response.url))
            domain = '{uri.netloc}/'.format(uri=parsed_uri)

            # links = LxmlLinkExtractor(allow=(), deny=()).extract_links(response)
            links = CustomLinkExtractor(allow=(), deny=()).extract_links(response)

            links = [link for link in links if domain in link.url]
            # self.logger.debug(links)
            # a_url_corrente  = str(response.url)
            # a_conteggio = gv.scraped_count[domain]
            # self.logger.debug("SCARICATA LA PAGINA " + str(url) + " con testo = " + str(text[:20]))

            if gv.scraped_count[domain] >= gv.maxPagesPerSiteLimit:
                self.logger.debug('Page Limit reached for {}'.format(domain))
            else:
                gv.scraped_count[domain] += 1
                # a_conteggio = gv.scraped_count[domain]
                # a_numeroLink = len(links)
                for link in links:
                    yield Request(url=link.url, callback=self.parse_item, meta={"firm_id": firm_id, "link_pos": link_pos})

                # save item for subsequent uses
                yield item