from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import sys
print(sys.path.append('/Users/manueloostveen/PycharmProjects/boxguru/scrapingboxeshome'))

from spiders.dozen import DozenSpider
from spiders.europresto import EuroprestoSpider
from spiders.kartonnendozen123 import Kartonnendozen123Spider
from spiders.paardekooper import PaardekooperSpider
from spiders.pacoverpakkingen import PacoverpakkingenSpider
from spiders.rajapack import RajapackSpider
from spiders.tarra import TarraSpider
from spiders.tupak import TupakSpider
from spiders.vermeij import VermeijSpider
from spiders.viv import VivSpider
from spiders.vvs import VvsSpider

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(DozenSpider)
    yield runner.crawl(EuroprestoSpider)
    yield runner.crawl(Kartonnendozen123Spider)
    yield runner.crawl(PaardekooperSpider)
    yield runner.crawl(PacoverpakkingenSpider)
    yield runner.crawl(RajapackSpider)
    yield runner.crawl(TarraSpider)
    yield runner.crawl(TupakSpider)
    yield runner.crawl(VermeijSpider)
    yield runner.crawl(VivSpider)
    yield runner.crawl(VvsSpider)
    reactor.stop()

crawl()
reactor.run()
