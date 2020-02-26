# -*- coding: utf-8 -*-
from pathlib import Path

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath('.')))

FILE_PATH = Path(__file__ or ".settings.py").resolve()

ROOT_DJANGO_PROJECT = FILE_PATH.parent.parent.parent
sys.path.append(str(ROOT_DJANGO_PROJECT))


os.environ['DJANGO_SETTINGS_MODULE'] = 'boxguru.settings'
import django
django.setup()


# Base path of scrapingboxes project
BASE_PATH_SCRAPINGBOXES = FILE_PATH.parent.parent

BOT_NAME = "scrapingboxes"

SPIDER_MODULES = ["scrapingboxes.spiders"]
NEWSPIDER_MODULE = "scrapingboxes.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'scrapingboxes (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

SELENIUM_DRIVER_NAME = "chrome"

SELENIUM_DRIVER_EXECUTABLE_PATH = os.environ.get('CHROMEDRIVER_PATH', BASE_PATH_SCRAPINGBOXES / 'selenium_driver' / 'chromedriver' / 'chromedriver')
# SELENIUM_DRIVER_EXECUTABLE_PATH = '/app/.chromedriver/bin/chromedriver'

if os.environ.get('GOOGLE_CHROME_BIN'):
    SELENIUM_BROWSER_EXECUTABLE_PATH = os.environ['GOOGLE_CHROME_BIN']

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'scrapingboxes.middlewares.ScrapingboxesSpiderMiddleware': 543,
# }

# Retry many times since proxies often fail
RETRY_TIMES = 20
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408, 429]  # 429 added since dozen.nl

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapingboxes.middlewares.ScrapingboxesDownloaderMiddleware': 543,
    # "scrapingboxes.middlewares.SeleniumMiddleware": 80,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy_proxies.RandomProxy': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}
# Proxy list containing entries like
# http://host1:port
# http://username:password@host2:port
# http://host3:port
# ...
_PROXY_LIST = FILE_PATH.parent / 'data' / 'proxies' / 'proxies.txt'
PROXY_LIST = str(_PROXY_LIST.resolve())
# Proxy mode
# 0 = Every requests have different proxy
# 1 = Take only one proxy from the list and assign it to every requests
# 2 = Put a custom proxy to use in the settings
PROXY_MODE = 0

# If proxy mode is 2 uncomment this sentence :
# CUSTOM_PROXY = "http://host1:port"

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#     'scrapy.extensions.closespider.CloseSpider': 500,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'scrapingboxes.pipelines.ScrapingboxesPipeline': 300,
    'scrapingboxes.pipelines.DjangoTestPipeline': 310,
    #  'scrapingboxes.pipelines.JsonLinesPipeline': 400,
    # 'scrapy.pipelines.images.ImagesPipeline': 1,
}

# IMAGES_STORE = '/Users/manueloostveen/PycharmProjects/boxguru/products/static/products/images'
IMAGES_STORE = str(BASE_PATH_SCRAPINGBOXES.parent / 'products' / 'static' / 'products' / 'images')
MEDIA_ALLOW_REDIRECTS = True


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [429]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# # custom log formatter: https://stackoverflow.com/questions/13527921/scrapy-silently-drop-an-item
# LOG_FORMATTER = 'scrapingboxes.middlewares.BoxLogFormatter'

# TESTING
class TestSettings:
    TESTING = True
    SETTINGS = {
        'ITEM_PIPELINES': {
            'scrapingboxes.pipelines.ScrapingboxesPipeline': 300,
        }
    }
    MAX_ROWS = 3