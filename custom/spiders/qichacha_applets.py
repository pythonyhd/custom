# -*- coding: utf-8 -*-
import json

import scrapy


class QichachaSpider(scrapy.Spider):
    name = 'qichacha_applets'
    allowed_domains = ['qichacha.com']

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "charset": "utf-8",
            "Accept-Encoding": "gzip",
            "content-type": "application/json",
            "Host": "xcx.qichacha.com",
            "Connection": "Keep-Alive",
        },
        "DOWNLOADER_MIDDLEWARES": {
            'custom.middlewares.RandomUserAgentMiddleware': 120,
            # 'custom.middlewares.TianyanchaCookiesMiddleware': 140,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,  # 禁用默认的代理
            'custom.middlewares.RandomProxyMiddlerware': 160,
            # 'custom.middlewares.LocalRetryMiddlerware': 180,
        },
        # "ITEM_PIPELINES": {
            # 'custom.pipelines.CustomPipeline': 300,
            # 'custom.pipelines.MongodbIndexPipeline': 320,
            # 'custom.pipelines.MysqlTwistedPipeline': 340,
        # },
        "REDIRECT_ENABLED": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": '9',
        "DOWNLOAD_TIMEOUT": '25',
        # "DOWNLOAD_DELAY": '0.05',
    }

    token = 'd33c8b89cec958aa272422e0a9a56276'  # 有效时间30分钟左右，爬虫意义不大，除非大量账号

    def start_requests(self):
        """ 搜索接口 """
        headers = {
            "referer": "https://servicewechat.com/wx395200814fcd7599/80/page-frame.html",
        }
        keyword = '小米'
        search_url = 'https://xcx.qichacha.com/wxa/v1/base/advancedSearchNew?searchKey={}&searchIndex=&sortField=&isSortAsc=false&province=&cityCode=&countyCode=&industryCode=&subIndustryCode=&industryV3=&token={}&startDateBegin=&startDateEnd=&registCapiBegin=&registCapiEnd=&insuredCntStart=&insuredCntEnd=&coyType=&statusCode=&hasPhone=&hasMobilePhone=&hasEmail=&hasTM=&hasPatent=&hasSC=&hasShiXin=&hasFinance=&hasIPO=&pageIndex=1&searchType=0'.format(keyword, self.token)
        yield scrapy.Request(
            url=search_url,
            headers=headers,
            meta={'keyword': keyword},
        )

    def parse(self, response):
        """ 解析翻页 """
        name = response.meta.get('keyword', '')  # 公司名
        # 解析
        results = json.loads(response.text)
        data_list = results.get('result').get('Result')
        if not data_list:
            data_list = [{
                'id': '',
                'name': name,
            }]
        for data in data_list:
            uuid = data.get('KeyNo')
            name = data.get('Name', '').replace("<em>", "").replace("</em>", "").strip()
            meta_data = {'company_name': name, 'company_id': uuid}

            url_list = [
                # 工商信息
                'https://xcx.qichacha.com/wxa/v1/base/getEntDetailNew?unique={}&token={}'.format(uuid, self.token),
            ]
            for url in url_list:
                if 'getEntDetailNew' in url and 'unique' in url:
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_base,
                        meta=meta_data,
                        priority=5,
                    )

    def parse_base(self, response):
        """ 工商基本信息 """
        print(f'内容:{response.text}')