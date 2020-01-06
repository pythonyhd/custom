# -*- coding: utf-8 -*-


BOT_NAME = 'custom'

SPIDER_MODULES = ['custom.spiders']
NEWSPIDER_MODULE = 'custom.spiders'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
scrapy基本配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'INFO'

# 天眼查登录后的cookie信息，如果账号多可以放到redis做成cookie池
cookies = 'Cookie:'
# 天眼查请求头token认证
auth_token = ""

# 天眼查小程序唯一认证，获取微信的标识，账号越多越好
authorization = ""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
数据存储 相关配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 存储到mongodb
MONGO_URI = '127.0.0.1'
MONGO_DATA_BASE = 'crawl_tianyancha'
# 存储到MySQL
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'crawl_tianyancha'
DB_CHARSET = 'utf8'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
redis 运行数据缓存端口参数
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
REDIS_DB = 1
REDIS_PARAMS = {
    "password": "",
    "db": 1,
}
# REDIS_URL = 'redis://root:axy@2019@localhost:6379/3'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
redis 代理池配置参数
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
REDIS_PROXIES_HOST = '117.78.35.12'
REDIS_PROXIES_PORT = 6379
REDIS_PROXIES_PASSWORD = ''
REDIS_PROXIES_DB = 15

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
scrapy请求头
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
RANDOM_UA_TYPE = "random"

