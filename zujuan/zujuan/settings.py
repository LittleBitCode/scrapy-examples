# -*- coding: utf-8 -*-

# Scrapy settings for zujuan project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import sys
import os
from os.path import dirname
path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)

from misc.log import *

BOT_NAME = 'zujuan'

SPIDER_MODULES = ['zujuan.spiders']
NEWSPIDER_MODULE = 'zujuan.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zujuan (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# 自动传递cookies与打印cookies设置
COOKIES_ENABLED = True
COOKIES_DEBUG   = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
#     'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'zujuan.middlewares.ZujuanSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'misc.middleware.CustomHttpProxyFromMysqlMiddleware' : 400,
    # 'misc.middleware.CustomUserAgentMiddleware'          : 401,
#     'misc.middleware.DownloadImageMiddleware'            : 543,
#     'scrapy_splash.SplashCookiesMiddleware': 723,
#     'scrapy_splash.SplashMiddleware': 725,
#     'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'zujuan.pipelines.ZujuanPipeline'        : 300,
   'zujuan.pipelines.DownloadImagesPipeline' : 5,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

MYSQL_HOST    = "127.0.0.1"
MYSQL_USER    = "root"
MYSQL_PASSWD  = "123456"
MYSQL_PORT    = 3306
MYSQL_CHARSET = "utf8"
MYSQL_DBNAME  = "spider"

# SPLASH_URL='http://127.0.0.1:8050'
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

IMAGES_STORE      = './myimages'
# 该字段的值为ImageItem中定义的存储图片链接的image_urls字段
#IMAGES_URLS_FIELD='image_urls'
# 该字段的值为ImageItem中定义的存储图片信息的images字段
#IMAGES_RESULT_FIELD='images'
# 避免下载最近90天已经下载过的文件内容,单位:天(可选)
# IMAGES_EXPIRES    = 90
# 设置图片缩略图(可选)
IMAGES_THUMBS = {
    'small' : (50, 50),
    'big'   : (250, 250),
}
# 图片过滤器，最小高度和宽度，低于此尺寸不下载(可选)
#IMAGES_MIN_HEIGHT = 100
#IMAGES_MIN_WIDTH  = 100
# 是否允许重定向(可选)
# MEDIA_ALLOW_REDIRECTS = True