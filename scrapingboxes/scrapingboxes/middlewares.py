# -*- coding: utf-8 -*-
from importlib import import_module

from scrapy import signals
from scrapy.exceptions import NotConfigured, IgnoreRequest
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait

from scrapingboxes.utils import SeleniumRequest
import logging
from scrapy import logformatter


# class BoxLogFormatter(logformatter.LogFormatter):
#     def dropped(self, item, exception, response, spider):
#         return {
#             'level': logging.INFO,
#             'msg': logformatter.DROPPEDMSG,
#             'args': {
#                 "exception": exception,
#                 "item": item,
#             }
#         }

class SeleniumMiddleware:
    """Scrapy middleware handling the requests using selenium"""

    def __init__(
            self,
            driver_name,
            driver_executable_path,
            driver_arguments,
            browser_executable_path,
    ):
        """Initialize the selenium webdriver

        Parameters
        ----------
        driver_name: str
            The selenium ``WebDriver`` to use
        driver_executable_path: str
            The path of the executable binary of the driver
        driver_arguments: list
            A list of arguments to initialize the driver
        browser_executable_path: str
            The path of the executable binary of the browser
        """

        webdriver_base_path = f"selenium.webdriver.{driver_name}"

        driver_klass_module = import_module(f"{webdriver_base_path}.webdriver")
        driver_klass = getattr(driver_klass_module, "WebDriver")

        driver_options_module = import_module(f"{webdriver_base_path}.options")
        driver_options_klass = getattr(driver_options_module, "Options")

        driver_options = driver_options_klass()
        if browser_executable_path:
            driver_options.binary_location = browser_executable_path
        for argument in driver_arguments:
            driver_options.add_argument(argument)

        driver_kwargs = {
            "executable_path": driver_executable_path,
            f"{driver_name}_options": driver_options,
        }

        self.driver = driver_klass(**driver_kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        driver_name = crawler.settings.get("SELENIUM_DRIVER_NAME")
        driver_executable_path = crawler.settings.get("SELENIUM_DRIVER_EXECUTABLE_PATH")
        browser_executable_path = crawler.settings.get(
            "SELENIUM_BROWSER_EXECUTABLE_PATH"
        )
        driver_arguments = crawler.settings.get("SELENIUM_DRIVER_ARGUMENTS")

        if not driver_name or not driver_executable_path:
            raise NotConfigured(
                "SELENIUM_DRIVER_NAME and SELENIUM_DRIVER_EXECUTABLE_PATH must be set"
            )

        middleware = cls(
            driver_name=driver_name,
            driver_executable_path=driver_executable_path,
            driver_arguments=driver_arguments,
            browser_executable_path=browser_executable_path,
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie({"name": cookie_name, "value": cookie_value})

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(request.wait_until)

        if request.screenshot:
            request.meta["screenshot"] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({"driver": self.driver})

        return HtmlResponse(
            self.driver.current_url, body=body, encoding="utf-8", request=request
        )

    def spider_closed(self):
        """Shutdown the driver when spider is closed"""

        self.driver.quit()


class ScrapingboxesSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapingboxesDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        return None

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class UrlFilter(object):
    start_requests = []

    def check_url(self, url):
        pass_urls = ['doos', 'dozen', 'verzend', 'fixeer', 'koker']
        for word in pass_urls:
            if word in url:
                return True
        return False

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        for url in self.start_requests:
            if response.url == url:
                return None

        if response.url == "https://www.paardekooper.nl/nl_NL/industrie/2634/":
            return None
        elif self.check_url(response.url):
            return None
        else:
            raise IgnoreRequest()

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            self.start_requests.append(r)
            yield r
