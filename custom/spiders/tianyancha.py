# -*- coding: utf-8 -*-
import json
import re
import time
from urllib.parse import unquote

import jsonpath
import redis
import scrapy
import logging

from custom import settings
from custom.work_utils.redis_bloomfilter import BloomFilter

logger = logging.getLogger(__name__)


class TianyanchaSpider(scrapy.Spider):
    name = 'tianyancha'
    allowed_domains = ['tianyancha.com']
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'custom.middlewares.RandomUserAgentMiddleware': 120,
            'custom.middlewares.TianyanchaCookiesMiddleware': 140,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,  # 禁用默认的代理
            'custom.middlewares.RandomProxyMiddlerware': 160,
            'custom.middlewares.LocalRetryMiddlerware': 180,
        },
        "ITEM_PIPELINES": {
            'custom.pipelines.CustomPipeline': 300,
            # 'custom.pipelines.MongodbIndexPipeline': 320,
            'custom.pipelines.MysqlTwistedPipeline': 340,
        },
        "REDIRECT_ENABLED": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": '9',
        "DOWNLOAD_TIMEOUT": '25',
        "DOWNLOAD_DELAY": '0.05',
    }

    bloomfilter = BloomFilter(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        blockNum=1,
        key=name + ":bloomfilter"
    )

    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
    )

    def start_requests(self):
        """
        搜索入口，获取天眼查公司对应的唯一ID
        """
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://www.tianyancha.com/vipintro/?jsid=SEM-BAIDU-PZ1907-SY-000100",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "sp0.tianyancha.com",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "version": "TYC-Web",
            "Connection": "keep-alive",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "version, X-Auth-Token",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Origin": "https://www.tianyancha.com",
            "X-Auth-Token": settings.auth_token,
        }
        # keywords = ['河北融投创业投资有限公司', '深圳市伟雄奥展运输有限公司', '恒大地产集团有限公司', '深圳市尚金缘珠宝实业有限公司', '深圳市明星康桥投资有限公司', '深圳市万港物流发展有限公司', '江苏华罗贸易有限公司', '唐山榕丰钢铁有限公司']
        # for keyword in keywords:
        while True:
            keyword = self.redis_client.rpop(self.name + ':keywords').decode()
            if not keyword:
                break
            url = 'https://sp0.tianyancha.com/search/suggestV2.json?key={}&_={}'.format(keyword, int(time.time()))
            yield scrapy.Request(
                url=url,
                headers=headers,
                meta={'keyword': keyword},
            )

    def parse(self, response):
        """
        解析搜索接口
        :param response:关键词搜索的json数据
        :return:
        """
        results = json.loads(response.text)
        data_list = jsonpath.jsonpath(obj=results, expr='$.data')[0]  # 搜索结果
        name = response.meta.get('keyword', '')  # 公司名

        if not data_list:
            data_list = [{
                'id': '',
                'name': name,
            }]

        for data in data_list:
            name = data.get('name', '').replace("<em>", "").replace("</em>", "").strip()
            id = data.get('id')

            # 搜索出来的公司名，添加到bloomfiler中
            if self.bloomfilter.is_exist(name):
                # print(f"{name}--- 被过滤了")
                logger.info(f"{name}--- 被过滤了")
                continue
            else:
                self.bloomfilter.add(name)

            meta_data = {'company_name': name, 'company_id': id}

            url_list = [
                # 行政处罚-工商局
                "https://www.tianyancha.com/pagination/punish.xhtml?ps=30&pn=1&name={}".format(name),
                # 行政处罚-信用中国
                "https://www.tianyancha.com/pagination/punishmentCreditchina.xhtml?ps=30&pn=1&id={}".format(id),
                # 股权出质
                "https://www.tianyancha.com/pagination/equity.xhtml?ps=30&pn=1&name={}".format(name),
                # 动产抵押-失效
                # "https://www.tianyancha.com/pagination/mortgage.xhtml?ps=10&pn=1&name={}".format(name),
                # 严重违法
                "https://www.tianyancha.com/pagination/illegal.xhtml?ps=30&pn=1&name={}".format(name),
                # 欠税公告
                "https://www.tianyancha.com/pagination/towntax.xhtml?ps=30&pn=1&id={}".format(id),
                # 经营异常
                "https://www.tianyancha.com/pagination/abnormal.xhtml?ps=30&pn=1&id={}".format(id),
                # 环保处罚
                "https://www.tianyancha.com/pagination/environmentalPenalties.xhtml?ps=30&pn=1&id={}".format(id),
                # 司法协助-股权冻结
                "https://www.tianyancha.com/pagination/judicialAid.xhtml?ps=30&pn=1&id={}".format(id),
            ]

            for link in url_list:
                if 'punish' in link and 'name' in link:
                    yield scrapy.Request(url=link, callback=self.parse_punish, meta=meta_data, priority=5)

                elif 'punishmentCreditchina' in link and 'id' in link:
                    yield scrapy.Request(url=link, callback=self.punishment_creditchina, meta=meta_data, priority=5)

                elif 'equity' in link:
                    yield scrapy.Request(url=link, callback=self.parse_equity, meta=meta_data, priority=5)

                elif 'illegal' in link:
                    yield scrapy.Request(url=link, callback=self.parse_illegal, meta=meta_data, priority=5)

                elif 'towntax' in link:
                    yield scrapy.Request(url=link, callback=self.parse_towntax, meta=meta_data, priority=5)

                elif 'abnormal' in link:
                    yield scrapy.Request(url=link, callback=self.parse_abnormal, meta=meta_data, priority=5)

                elif 'environmentalPenalties' in link:
                    yield scrapy.Request(url=link, callback=self.parse_environmental, meta=meta_data, priority=5)

                elif 'judicialAid' in link:
                    yield scrapy.Request(url=link, callback=self.parse_judicial, meta=meta_data, priority=3)

    def parse_punish(self, response):
        """
        解析工商局-行政处罚
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        results = selector.xpath('//script//text()').getall()
        if results:
            for data in results:
                source_data = json.loads(data)
                punish_number = source_data.get('punishNumber', '')  # 文书号
                remarks = source_data.get('remarks', '')  # 备注
                decision_date = source_data.get('decisionDate', '')  # 处罚决定日期
                legal_person_name = source_data.get('legalPersonName', '')  # 法人
                type = source_data.get('type', '')  # 违法行为类型
                department_name = source_data.get('departmentName', '')  # 决定机关
                reg_num = source_data.get('regNum', '')  # 注册号
                content = source_data.get('content', '')  # 行政处罚内容
                if content:
                    content = content.strip().replace("\r\n", "")
                description = source_data.get('description', '')  # 简单描述
                ws_nr_txt = json.dumps(source_data, ensure_ascii=False)
                item = dict(
                    oname=oname,
                    cf_wsh=punish_number,
                    cf_jdrq=decision_date,
                    cf_xzjg=department_name,
                    reg_num=reg_num,
                    cf_jg=content,
                    cf_sy='',
                    bz=remarks,
                    pname=legal_person_name,
                    cf_type=type,
                    url=unquote(response.url),
                    base_url=base_url,

                    description=description,
                    ws_nr_txt=ws_nr_txt,
                    wbbz='工商局-行政处罚',
                    collection='xzcf',  # 用来分表存储
                )
                # print(item)
                yield item

        # 翻页
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/punish.xhtml?ps=30&pn={}&name={}'.format(page_num, oname)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_punish,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该企业无工商局处罚数据:{response.url}')

    def punishment_creditchina(self, response):
        """
        解析信用中国-行政处罚
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        results = selector.xpath('//script//text()').getall()
        if results:
            for data in results:
                source_data = json.loads(data)
                result = source_data.get('result')  # 处罚结果
                punish_number = source_data.get('punishNumber')  # 决定书文号
                reason = source_data.get('reason')  # 处罚事由
                evidence = source_data.get('evidence')  # 处罚依据
                decision_date = source_data.get('decisionDate')  # 处罚决定日期
                type = source_data.get('type')  # 处罚类别1
                type_second = source_data.get('typeSecond')  # 处罚类别2
                department_name = source_data.get('departmentName')  # 处罚机关
                punish_name = source_data.get('punishName')  # 处罚名称
                area_name = source_data.get('areaName')  # 地区名称

                ws_nr_txt = json.dumps(source_data, ensure_ascii=False)
                item = dict(
                    oname=oname,
                    cf_wsh=punish_number,
                    cf_sy=reason,
                    cf_yj=evidence,
                    cf_jg=result,
                    cf_jdrq=decision_date,
                    cf_type=type,
                    cf_type_second=type_second,
                    cf_xzjg=department_name,
                    cf_cfmc=punish_name,
                    area_name=area_name,
                    url=unquote(response.url),
                    base_url=base_url,
                    ws_nr_txt=ws_nr_txt,
                    wbbz='信用中国-行政处罚',
                    collection='xzcf',  # 用来分表存储
                )
                # print(item)
                yield item
        # 翻页
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/punishmentCreditchina.xhtml?ps=30&pn={}&id={}'.format(page_num, company_id)
                    yield scrapy.Request(
                        url=url,
                        callback=self.punishment_creditchina,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无信用中国处罚数据:{response.url}')

    def parse_equity(self, response):
        """
        解析股权出质
        :param response:
        :return:
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        results = selector.xpath('//script//text()').getall()
        if results:
            for data in results:
                source_data = json.loads(data)
                equityAmount = source_data.get('equityAmount', '')  # 出质股权数额
                pledgee = source_data.get("pledgee", "")  # 质权人
                pledgor = source_data.get("pledgor", "")  # 出质人
                if not pledgor:
                    continue
                reg_num = source_data.get("regNumber", "")  # 登记编号
                state = source_data.get("state", "")  # 状态
                regDate = self.handle_timestmp(source_data.get("regDate"))  # 股权出质设立登记日期
                ws_nr_txt = json.dumps(source_data, ensure_ascii=False)
                item = dict(
                    oname=oname,
                    zqr=pledgee,
                    czr=pledgor,
                    reg_num=reg_num,
                    state=state,
                    cf_jdrq=regDate,
                    equity_amount=equityAmount,
                    url=unquote(response.url),
                    base_url=base_url,
                    wbbz='股权出质',

                    ws_nr_txt=ws_nr_txt,
                    collection='gqcz',
                )
                # print(item)
                yield item

        # 翻页请求
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/equity.xhtml?ps=30&pn={}&name={}'.format(page_num, oname)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_equity,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无股权出质数据:{response.url}')

    def parse_illegal(self, response):
        """
        解析严重违法失信
        :param response:
        :return:
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        base_table = selector.css('.table tbody tr')
        for tr in base_table:
            cf_jdrq = tr.css('td:nth-child(2)::text').get()  # 列入日期
            cf_sy = tr.css('td:nth-child(3)::text').get()  # 列入严重违法失信企业名单原因
            cf_xzjg = tr.xpath('./td[last()]/text()').get()  # 列入决定机关
            item = dict(
                oname=oname,
                cf_jdrq=cf_jdrq,
                cf_sy=cf_sy,
                cf_xzjg=cf_xzjg,
                url=unquote(response.url),
                base_url=base_url,
                wbbz='严重违法失信',
                ws_nr_txt=tr.get(),
                collection='yzwfsx',
            )
            # print(item)
            yield item

        # 翻页请求
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/illegal.xhtml?ps=30&pn={}&name={}'.format(page_num, oname)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_illegal,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无严重违法失信数据:{response.url}')

    def parse_towntax(self, response):
        """
        解析欠税公告
        :param response:
        :return:
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        results = selector.xpath('//script//text()').getall()
        if results:
            for data in results:
                source_data = json.loads(data)
                personIdNumber = source_data.get('personIdNumber')  # 证件号码
                legalpersonName = source_data.get('legalpersonName')  # 负责人姓名
                location = source_data.get('location')  # 经营地点
                taxIdNumber = source_data.get('taxIdNumber')  # 纳税人识别号
                type = source_data.get('type')  # 税父分类
                taxCategory = source_data.get('taxCategory')  # 欠税税种
                name = source_data.get('name')  # 公司名
                ownTaxBalance = source_data.get('ownTaxBalance')  # 欠税余额
                publishDate = source_data.get('publishDate')  # 发布日期
                ws_nr_txt = json.dumps(source_data, ensure_ascii=False)
                item = dict(
                    oname=oname,
                    name=name,
                    uccode=personIdNumber,
                    pname=legalpersonName,
                    location=location,
                    tax_num=taxIdNumber,
                    cf_type=type,
                    cf_category=taxCategory,
                    qs_ye=ownTaxBalance,
                    fb_rq=publishDate,
                    url=unquote(response.url),
                    base_url=base_url,
                    ws_nr_txt=ws_nr_txt,
                    wbbz='欠税公告',
                    collection='qsgg',  # 用来分表存储
                )
                # print(item)
                yield item

        # 翻页请求
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/towntax.xhtml?ps=30&pn={}&id={}'.format(page_num, company_id)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_towntax,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无欠税公告数据:{response.url}')

    def parse_abnormal(self, response):
        """
        解析经营异常
        :param response:
        :return:
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        base_table = selector.css('table[class=table] tbody tr')
        for tr in base_table:
            cf_jdrq = tr.css('td:nth-child(2)::text').get()  # 列入日期
            cf_sy = tr.css('td:nth-child(3)::text').get()  # 列入经营异常名录原因
            cf_xzjg = tr.css('td:nth-child(4)::text').get()  # 列入决定机关
            yc_jdrq = tr.css('td:nth-child(5)::text').get()  # 移除日期
            yc_sy = tr.css('td:nth-child(6)::text').get()  # 移出经营异常名录原因
            yc_xzjg = tr.css('td:last-child::text').get()  # 移出决定机关

            item = dict(
                oname=oname,
                cf_jdrq=cf_jdrq,
                cf_sy=cf_sy,
                cf_xzjg=cf_xzjg,
                yc_jdrq=yc_jdrq,
                yc_sy=yc_sy,
                yc_xzjg=yc_xzjg,
                url=unquote(response.url),
                base_url=base_url,
                wbbz='经营异常',
                ws_nr_txt=tr.get(),
                collection='jyyc',
            )
            # print(item)
            yield item
        # 翻页请求
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/abnormal.xhtml?ps=30&pn={}&id={}'.format(page_num, company_id)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_abnormal,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无经营异常数据:{response.url}')

    def parse_environmental(self, response):
        """
        解析环保处罚
        :param response:
        :return:
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        is_first = response.meta.get('is_first', True)
        # 解析
        selector = scrapy.Selector(text=response.text)
        results = selector.xpath('//script//text()').getall()
        if results:
            for data in results:
                source_data = json.loads(data)
                punish_content = source_data.get('punish_content')  # 处罚结果
                punish_department = source_data.get('punish_department')  # 处罚单位
                publish_time = source_data.get('publish_time')  # 处罚日期
                if publish_time:
                    publish_time = self.handle_timestmp(publish_time)
                else:
                    publish_time = None
                punish_basis = source_data.get('punish_basis')  # 处罚依据
                punish_number = source_data.get('punish_number')  # 决定书文号
                punish_reason = source_data.get('punish_reason')  # 处罚事由
                lawbreaking = source_data.get('lawbreaking')  # 违反法律
                execution = source_data.get('execution')  # 执行情况
                ws_nr_txt = json.dumps(source_data, ensure_ascii=False)

                item = dict(
                    oname=oname,
                    cf_jg=punish_content,
                    cf_xzjg=punish_department,
                    cf_jdrq=publish_time,
                    cf_yj=punish_basis,
                    cf_wsh=punish_number,
                    cf_sy=punish_reason,
                    law_break=lawbreaking,
                    execution=execution,
                    url=unquote(response.url),
                    base_url=base_url,
                    ws_nr_txt=ws_nr_txt,
                    wbbz='环保处罚',
                    collection='hbcf',  # 用来分表存储
                )
                # print(item)
                yield item
        # 翻页请求
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/environmentalPenalties.xhtml?ps=30&pn={}&id={}'.format(page_num, company_id)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_environmental,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无环保处罚数据:{response.url}')

    def parse_judicial(self, response):
        """
        再次请求-股权冻结
        :param response:
        :return:
        """
        oname = response.meta.get('company_name')
        company_id = response.meta.get('company_id')
        base_url = 'https://www.tianyancha.com/company/' + str(company_id)
        selector = scrapy.Selector(text=response.text)
        # 获取详情参数
        uuid = re.findall(r'openJudicialAidDetail\("(.*?)"\)', response.text, re.S)
        if uuid:
            for data in uuid:
                url = 'https://www.tianyancha.com/company/judicialAidDetail.json?id={}'.format(data)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_judicial_detail,
                    meta={'oname': oname, 'base_url': base_url},
                    priority=7
                )
        else:
            logger.debug('无股权冻结信息')

        # 翻页
        is_first = response.meta.get('is_first', True)
        total_page = selector.xpath('//ul[@class="pagination"]/@page-total').get()
        if total_page:
            page = int(int(total_page) / 30) if int(total_page) % 30 == 0 else int(int(total_page) / 30) + 1
            if is_first and page:
                for page_num in range(2, page + 1):
                    url = 'https://www.tianyancha.com/pagination/judicialAid.xhtml?ps=30&pn={}&id={}'.format(page_num, company_id)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_judicial,
                        meta={'is_first': False, 'company_name': oname, 'company_id': company_id},
                        priority=3,
                    )
        else:
            logger.debug(f'该公司无环保处罚数据:{response.url}')

    def parse_judicial_detail(self, response):
        """
        解析股权冻结
        :param response:
        :return:
        """
        oname = response.meta.get('oname', '')
        base_url = response.meta.get('base_url', '')
        results = json.loads(response.text)
        frozen = results.get('data').get('frozen')
        if isinstance(frozen, dict):
            ws_nr_txt = json.dumps(frozen, ensure_ascii=False)
            executedPerson = frozen.get('executedPerson', '')  # 被执行人
            equityAmountOther = frozen.get('equityAmountOther', '')  # 股权数额
            executiveCourt = frozen.get('executiveCourt', '')  # 执行法院
            executeNoticeNum = frozen.get('executeNoticeNum', '')  # 执行通知书文号
            executeOrderNum = frozen.get('executeOrderNum', '')  # 执行裁定书文号
            implementationMatters = frozen.get('implementationMatters', '')  # 执行事项
            licenseType = frozen.get('licenseType', '')  # 被执行人证件种类
            executedPersonCid = frozen.get('executedPersonCid', '')  # 被执行人证件号码
            fromDate = frozen.get('fromDate', '')  # 冻结期限自
            toDate = frozen.get('toDate', '')  # 冻结期限至
            publicityAate = frozen.get('publicityAate', '')  # 公示日期
            item = dict(
                oname=oname,
                name=executedPerson,
                equity_amount=equityAmountOther,
                zxfy=executiveCourt,
                cf_wsh=executeNoticeNum,
                zx_wsh=executeOrderNum,
                zx_sx=implementationMatters,
                lince_type=licenseType,
                uccode=executedPersonCid,
                begin_date=fromDate,
                end_date=toDate,
                fb_rq=publicityAate,

                url=unquote(response.url),
                base_url=base_url,
                ws_nr_txt=ws_nr_txt,
                wbbz='股权冻结',
                collection='gqdj',  # 用来分表存储
            )
            yield item

    def handle_timestmp(self, timestamp):
        """
        处理13位时间戳
        :param timestmp:
        :return:
        """
        timestamps = float(timestamp / 1000)
        time_local = time.localtime(timestamps)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        # dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        dt = time.strftime("%Y-%m-%d", time_local)
        return dt