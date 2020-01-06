# -*- coding: utf-8 -*-
from scrapy import cmdline


# 天眼查-部分维度数据抓取
# cmdline.execute('scrapy crawl tianyancha'.split())
# 天眼查-小程序-部分维度数据抓取
cmdline.execute('scrapy crawl tianyancha_applets'.split())