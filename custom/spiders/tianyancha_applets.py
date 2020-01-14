# -*- coding: utf-8 -*-
"""
如果出现大量416，请更换IP
"""
import json
import time
from urllib.parse import unquote

import jsonpath
import redis
import scrapy
import logging

from custom import settings
from custom.work_utils.redis_bloomfilter import BloomFilter

logger = logging.getLogger(__name__)


class TianyanchaAppletsSpider(scrapy.Spider):
    name = 'tianyancha_applets'
    allowed_domains = ['tianyancha.com']
    search_url = 'https://api9.tianyancha.com/services/v3/search/sNorV4/{}?sortType=0&pageSize=30&pageNum=1'

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "charset": "utf-8",
            "Accept-Encoding": "gzip",
            "referer": "https://servicewechat.com/wx9f2867fc22873452/31/page-frame.html",
            "authorization": settings.authorization,
            "version": "TYC-XCX-WX",
            "content-type": "application/json",
            # "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; MI 5 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x2607033D) NetType/WIFI Language/zh_CN Process/appbrand0",
            "Host": "api9.tianyancha.com",
            "Connection": "Keep-Alive",
        },
        "DOWNLOADER_MIDDLEWARES": {
            'custom.middlewares.RandomUserAgentMiddleware': 120,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,  # 禁用默认的代理
            'custom.middlewares.RandomProxyMiddlerware': 160,
            'custom.middlewares.LocalRetryMiddlerware': 180,
        },
        "ITEM_PIPELINES": {
            'custom.pipelines.CustomPipeline': 300,
            'custom.pipelines.MysqlTwistedPipeline': 340,
        },

        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderPriorityQueue",
        "SCHEDULER_PERSIST": True,

        "REDIRECT_ENABLED": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": '9',
        "DOWNLOAD_TIMEOUT": '25',
        "DOWNLOAD_DELAY": '0.08',
    }

    bloomfilter_client = BloomFilter(
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
        小程序-搜索企业入口
        """
        # keyword = '深圳市国富黄金股份有限公司'
        while True:
            keyword = self.redis_client.rpop(self.name + ':keywords').decode()
            if not keyword:
                break
            yield scrapy.Request(
                url=self.search_url.format(keyword),
                meta={'keyword': keyword},
            )

    def parse(self, response):
        """
        搜索结果解析
        :param response: 搜索响应
        """
        keyword = response.meta.get('keyword')
        # 解析结果
        results = json.loads(response.text)
        companyList = results.get('data').get('companyList')

        if not companyList:
            companyList = [{
                    'name': keyword,
                    'id': '',
                }]
        for data in companyList:
            name = data.get('name', '').replace('<em>', '').replace('</em>', '').strip()  # 企业名称
            uuid = data.get('id')  # 企业唯一id

            # 搜索出来的公司名，添加到bloomfiler中
            if self.bloomfilter_client.is_exist(name):
                # print(f"{name}--- 被过滤了")
                logger.info(f"{name}--- 被过滤了")
                continue
            else:
                self.bloomfilter_client.add(name)

            meta_data = {'company_name': name, 'company_id': uuid}
            url_list = [
                # 工商信息(包含基本信息、股东信息、主要人员、变更信息)
                'https://api9.tianyancha.com/services/v3/t/details/appComIcV4/{}?pageSize=1000'.format(uuid),
                # 行政处罚-工商局
                'https://api9.tianyancha.com/services/v3/ar/punishment?name={}&pageNum=1&pageSize=30'.format(name),
                # 行政处罚-信用中国
                'https://api9.tianyancha.com/services/v3/aboutCompany/getCreditChina?cId={}&pageNum=1&pageSize=30'.format(uuid),
                # 股权出质
                'https://api9.tianyancha.com/services/v3/ar/companyEquity?name={}&pageNum=1&pageSize=30'.format(name),
                # 欠税公告
                'https://api9.tianyancha.com/services/v3/ar/companyowntax?id={}&pageNum=1&pageSize=30'.format(uuid),
                # 经营异常
                'https://api9.tianyancha.com/services/v3/expanse/abnormal?id={}&pageNum=1&pageSize=30'.format(uuid),
                # 严重违法失信
                'https://api9.tianyancha.com/services/v3/ar/Illegal?name={}&pageNum=1&pageSize=30'.format(name),
                # 动产抵押
                'https://api9.tianyancha.com/services/v3/ar/companyMortgageV2?name={}&pageNum=1&pageSize=30'.format(name),
            ]

            for link in url_list:
                if 'appComIcV4' in link:
                    yield scrapy.Request(url=link, callback=self.parse_base, meta=meta_data, priority=5)
                elif 'punishment' in link:
                    yield scrapy.Request(url=link, callback=self.parse_punish, meta=meta_data, priority=5)
                elif 'getCreditChina' in link:
                    yield scrapy.Request(url=link, callback=self.parse_credit_china, meta=meta_data, priority=5)
                elif 'companyEquity' in link:
                    yield scrapy.Request(url=link, callback=self.parse_equity, meta=meta_data, priority=5)
                elif "companyowntax" in link:
                    yield scrapy.Request(url=link, callback=self.parse_owntax, meta=meta_data, priority=5)
                elif "abnormal" in link:
                    yield scrapy.Request(url=link, callback=self.parse_abnormal, meta=meta_data, priority=5)
                elif 'Illegal' in link:
                    yield scrapy.Request(url=link, callback=self.parse_illegal, meta=meta_data, priority=5)
                elif 'companyMortgageV2' in link:
                    yield scrapy.Request(url=link, callback=self.parse_mortgage, meta=meta_data, priority=5)

        # 翻页请求
        companyCount = jsonpath.jsonpath(results, expr=r'$.data.companyCount')
        if companyCount:
            total_page = int(int(companyCount[0] / 30)) if int(companyCount[0]) % 30 == 0 else int(int(companyCount[0] / 30)) + 1
            is_first = response.meta.get('is_first', True)
            if is_first and total_page and total_page > 1:
                for page in range(2, total_page + 1):
                    url = 'https://api9.tianyancha.com/services/v3/search/sNorV4/{}?sortType=0&pageSize=30&pageNum={}'.format(keyword, page)
                    yield scrapy.Request(
                        url=url,
                        meta={'keyword': keyword, 'is_first': False},
                    )

    def parse_base(self, response):
        """
        解析基本信息
        :param response: 基本信息响应
        :return: 解析后的item
        """
        results = json.loads(response.text)
        # 工商信息
        baseInfo = results.get('data').get('baseInfo')
        if not baseInfo:
            return None
        contents = json.dumps(baseInfo, ensure_ascii=False)
        name = baseInfo.get('name')  # 公司名
        regCapital = baseInfo.get('regCapital')  # 注册资本
        actualCapital = baseInfo.get('actualCapital')  # 实缴资本
        estiblishTime = baseInfo.get('estiblishTime')  # 成立日期
        if len(str(estiblishTime)) == 13 and estiblishTime:
            estiblishTime = self.handle_timestmp(estiblishTime)
        else:
            estiblishTime = ''
        regStatus = baseInfo.get('regStatus')  # 经营状态
        creditCode = baseInfo.get('creditCode')  # 统一社会信用代码
        regNumber = baseInfo.get('regNumber')  # 工商注册号
        taxNumber = baseInfo.get('regNumber')  # 纳税人识别号
        orgNumber = baseInfo.get('orgNumber')  # 组织机构代码
        companyOrgType = baseInfo.get('companyOrgType')  # 公司类型
        industry = baseInfo.get('industry')  # 行业
        approvedTime = baseInfo.get('approvedTime')  # 核准日期
        regInstitute = baseInfo.get('regInstitute')  # 登记机关
        fromTime = baseInfo.get('fromTime')  # 营业期限开始
        toTime = baseInfo.get('toTime')  # 营业期限截止
        if len(str(fromTime)) == 13 and fromTime:
            fromTime = self.handle_timestmp(fromTime)
        else:
            fromTime = ''
        if len(str(toTime)) == 13 and toTime:
            toTime = self.handle_timestmp(toTime)
        else:
            toTime = ''

        correctCompanyId = baseInfo.get('correctCompanyId')  # 纳税人资质  不确定是不是可能有错误
        staffNumRange = baseInfo.get('staffNumRange')  # 人员规模
        socialStaffNum = baseInfo.get('socialStaffNum', '')  # 参保人数
        historyNames = baseInfo.get('historyNames')  # 曾用名
        property3 = baseInfo.get('property3', '')  # 英文名称
        regLocation = baseInfo.get('regLocation')  # 注册地址
        businessScope = baseInfo.get('businessScope')  # 经营范围
        legalPersonName = baseInfo.get('legalPersonName')  # 法人

        phoneNumber = baseInfo.get('phoneNumber')  # 电话
        phoneList = str(baseInfo.get('phoneList', []))  # 电话列表
        email = baseInfo.get('email')  # 邮箱
        emailList = str(baseInfo.get('emailList', []))  # 邮箱列表
        logo = baseInfo.get('logo', '')  # logo图片地址
        alias = baseInfo.get('alias', '')  # 简称
        websiteList = baseInfo.get('websiteList', '')  # 公司网址

        item = dict(
            name=name,
            reg_capital=regCapital,
            actual_capital=actualCapital,
            estiblish_time=estiblishTime,
            reg_status=regStatus,
            credit_code=creditCode,
            reg_number=regNumber,
            tax_number=taxNumber,
            org_number=orgNumber,
            company_org_type=companyOrgType,
            industry=industry,
            approved_time=approvedTime,
            reg_institute=regInstitute,
            from_time=fromTime,
            to_time=toTime,
            tax_payer=correctCompanyId,  # 该字段可能存在错误
            staff_num_range=staffNumRange,
            social_staff_num=socialStaffNum,
            property=property3,
            reg_location=regLocation,
            business_scope=businessScope,
            legal_person_name=legalPersonName,
            history_names=historyNames,
            phone_number=phoneNumber,
            phone_list=phoneList,
            email=email,
            email_list=emailList,
            logo=logo,
            alias=alias,
            website=str(websiteList),
            url=response.url,
            source_content=contents,
            collection='business_information',  # 表名 pipeline会删除
        )
        # print(item)
        yield item

        # 股东信息
        investorList = results.get('data').get('investorList')
        if not investorList:
            return None
        investor_content = json.dumps(investorList, ensure_ascii=False)
        for investor in investorList:
            partner_name = investor.get('name')  # 股东姓名
            tag_name = jsonpath.jsonpath(investor, expr=r'$.tagList..name')  # 股东标签
            tag_name = tag_name if tag_name else []
            # amomon = jsonpath.jsonpath(investor, expr=r'$.capitalActl..amomon')  # 认缴出资额
            # amomon_time = jsonpath.jsonpath(investor, expr=r'$.capitalActl..time')  # 认缴时间
            amomon = jsonpath.jsonpath(investor, expr=r'$.capital..amomon')  # 认缴出资额
            amomon = amomon if amomon else []
            amomon_time = jsonpath.jsonpath(investor, expr=r'$.capital..time')  # 认缴时间
            amomon_time = amomon_time if amomon_time else []
            percent = jsonpath.jsonpath(investor, expr=r'$.capital..percent')  # 持股比例
            percent = percent if percent else []
            investor_item = dict(
                name=name,
                partner_name=partner_name,
                tag_name=','.join(tag_name),
                amomon=','.join(amomon),
                amomon_time=','.join(amomon_time),
                percent=','.join(percent),
                url=response.url,
                source_content=investor_content,
                collection='investor_information',
            )
            # print(investor_item)
            yield investor_item

        # 主要人员
        staffList = results.get('data').get('staffList')
        if not staffList:
            return None
        staff_content = json.dumps(staffList, ensure_ascii=False)
        for staff in staffList:
            staff_name = staff.get('name')  # 主要人员姓名
            staff_job = staff.get('typeJoin')  # 主要人员职位
            staff_job = staff_job if staff_job else []
            staff_item = dict(
                name=name,
                staff_name=staff_name,
                staff_job=','.join(staff_job),
                url=response.url,
                source_content=staff_content,
                collection='staff_infomation',
            )
            # print(staff_item)
            yield staff_item

        # 变更信息
        comChanInfoList = results.get('data').get('comChanInfoList')
        if not comChanInfoList:
            return None
        comchan_content = json.dumps(comChanInfoList, ensure_ascii=False)
        for comchaninfo in comChanInfoList:
            changeItem = comchaninfo.get('changeItem')  # 变更项目
            contentBefore = comchaninfo.get('contentBefore')  # 变更前
            contentAfter = comchaninfo.get('contentAfter')  # 变更后
            changeTime = comchaninfo.get('changeTime')  # 变更时间
            havePsersion = comchaninfo.get('havePsersion')  # 含义不知道
            comchan_item = dict(
                name=name,
                change_item=changeItem,
                content_before=contentBefore,
                content_after=contentAfter,
                change_time=changeTime,
                have_psersion=havePsersion,
                url=response.url,
                source_content=comchan_content,
                collection='change_infomation',
            )
            # print(comchan_item)
            yield comchan_item

    def parse_punish(self, response):
        """
        解析-行政处罚-工商局
        :param response: 工商局行政处罚响应
        :return: 解析item
        """
        # 解析
        company_name = response.meta.get('company_name')  # 企业名称
        results = json.loads(response.text)
        data_list = results.get('data').get('items')
        if not data_list:
            return None
        for data in data_list:
            name = data.get('name')  # 公司名称有的没有，所以加了source_name搜索词
            punishNumber = data.get('punishNumber')  # 处罚决定文书号
            type = data.get('type')  # 违法行为类型
            legalPersonName = data.get('legalPersonName')  # 法人
            decisionDate = data.get('decisionDate')  # 处罚决定日期
            departmentName = data.get('departmentName')  # 处罚机关
            content = data.get('content')  # 处罚内容
            regNum = data.get('regNum')  # 注册号
            remarks = data.get('remarks')  # 备注
            publishDate = data.get('publishDate')  # 公开日期
            alias = data.get('alias')  # 昵称
            logo = data.get('logo')  # logo图片
            punish_item = dict(
                name=company_name,
                source_name=name,
                punish_number=punishNumber,
                cf_type=type,
                legal_person=legalPersonName,
                decision_date=decisionDate,
                department_name=departmentName,
                content=content,
                reg_num=regNum,
                remarks=remarks,
                publish_date=publishDate,
                alias=alias,
                logo=logo,
                bz='工商局-行政处罚',
                url=unquote(response.url),
                source_content=json.dumps(data, ensure_ascii=False),
                collection='punish_infomation',
            )
            # print(f'工商局:{punish_item}')
            yield punish_item

        # 翻页请求
        is_first = response.meta.get('is_first', True)
        count = results.get('data').get('count')  # 总数
        # historyCount = results.get('data').get('historyCount')  # 历史总数  需要VIP会员
        if is_first and count and int(count) > 0:
            page_count = int(int(count) / 30) if int(count) % 30 == 0 else int(int(count) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/ar/punishment?name={}&pageNum={}&pageSize=30'.format(company_name, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_punish,
                    meta={'is_first': False, 'company_name': company_name},
                    priority=3,
                )

    def parse_credit_china(self, response):
        """
        解析-行政处罚-信用中国
        :param response: 信用中国行政处罚响应
        :return: 解析item
        """
        # 解析
        name = response.meta.get('company_name')  # 企业名称
        company_id = response.meta.get('company_id')  # 企业id
        results = json.loads(response.text)
        data_list = results.get('data').get('list')
        if not data_list:
            return None
        for data in data_list:
            punishNumber = data.get('punishNumber')  # 处罚决定文书号
            reason = data.get('reason')  # 处罚事由
            result = data.get('result')  # 处罚结果
            evidence = data.get('evidence', '')  # 处罚依据
            decisionDate = data.get('decisionDate', '')  # 处罚决定日期
            type = data.get('type')  # 处罚类别1
            departmentName = data.get('departmentName', '')  # 处罚机关
            punishName = data.get('punishName')  # 处罚名称
            areaName = data.get('areaName', '')  # 区域名称
            typeSecond = data.get('typeSecond', '')  # 处罚类别2
            credit_item = dict(
                name=name,
                punish_number=punishNumber,
                reason=reason,
                result=result,
                evidence=evidence,
                decision_date=decisionDate,
                cf_type=type,
                department_name=departmentName,
                punish_name=punishName,
                area_name=areaName,
                cf_type_second=typeSecond,
                url=response.url,
                source_content=json.dumps(data, ensure_ascii=False),
                bz='信用中国-行政处罚',
                collection='punish_infomation',
            )
            # print(f'信用中国:{credit_item}')
            yield credit_item

        # 翻页请求
        is_first = response.meta.get('is_first', True)
        totalCount = results.get('data').get('totalCount')  # 总数
        # historyCount = results.get('data').get('historyCount')  # 历史总数  需要VIP会员
        if is_first and totalCount and int(totalCount) > 0:
            page_count = int(int(totalCount) / 30) if int(totalCount) % 30 == 0 else int(int(totalCount) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/aboutCompany/getCreditChina?cId={}&pageNum={}&pageSize=30'.format(company_id, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_credit_china,
                    meta={'is_first': False, 'company_id': company_id, 'compamy_name': name},
                    priority=3
                )

    def parse_equity(self, response):
        """
        解析股权出质信息
        :param response:股权出质响应内容
        :return: 解析结果
        """
        # 解析
        name = response.meta.get('company_name')  # 企业名称
        results = json.loads(response.text)
        data_list = results.get('data').get('items')
        for data in data_list:
            equityAmount = data.get('equityAmount', '')  # 出质股权数
            putDate = data.get('putDate')  # 股权出质登记日期
            if putDate and len(str(putDate)) == 13:
                putDate = self.handle_timestmp(putDate)
            else:
                putDate = ''
            pledgorStr = data.get('pledgorStr')  # 出质人字符串
            if 'href' in pledgorStr:
                pledgor_url = scrapy.Selector(text=pledgorStr).xpath('//a/@href').get('')
            else:
                pledgor_url = ''

            pledgeeStr = data.get('pledgeeStr')  # 质权人字符串
            if 'href' in pledgorStr:
                pledgee_url = scrapy.Selector(text=pledgeeStr).xpath('//a/@href').get('')
            else:
                pledgee_url = ''

            regDate = data.get('regDate')  # 注册日期
            if regDate and len(str(regDate)) == 13:
                regDate = self.handle_timestmp(regDate)
            else:
                regDate = ''
            state = data.get('state')  # 状态
            remarks = data.get('remarks')  # 备注
            certifNumber = data.get('certifNumber')  # 出质人证件号码
            regNumber = data.get('regNumber')  # 注册号
            pledgee = data.get('pledgee')  # 质权人
            # pledgeeList = data.get('pledgeeList')  # 质权人list
            # pledgorList = data.get('pledgorList')  # 出质人list
            pledgor = data.get('pledgor')  # 出质人
            certifNumberR = data.get('certifNumberR')  # 质权人证件号码
            equity_item = dict(
                name=name,
                pledgor=pledgor,
                pledgor_url=pledgor_url,
                pledgee=pledgee,
                pledgee_url=pledgee_url,
                equity_amount=equityAmount,
                state=state,
                remarks=remarks,
                reg_date=regDate,
                reg_number=regNumber,
                put_date=putDate,
                certif_number_dgor=certifNumber,
                certif_number_dgee=certifNumberR,
                url=unquote(response.url),
                source_content=json.dumps(data, ensure_ascii=False),
                bz='股权出质',
                collection='equity_infomation',
            )
            # print(equity_item)
            yield equity_item

        # 翻页
        is_first = response.meta.get('is_first', True)
        count = results.get('data').get('count')  # 总数
        # historyCount = results.get('data').get('historyCount')  # 历史总数 需要VIP才能获取
        if is_first and count and int(count) > 0:
            page_count = int(int(count) / 30) if int(count) % 30 == 0 else int(int(count) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/ar/companyEquity?name={}&pageNum={}&pageSize=30'.format(name, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_equity,
                    meta={'is_first': False, 'company_name': name},
                    priority=3,
                )

    def parse_owntax(self, response):
        """
        解析欠税公告信息
        :param response: 欠税公告响应内容
        :return: 解析后的item
        """
        # 解析
        company_name = response.meta.get('company_name')  # 企业名称
        company_id = response.meta.get('company_id')  # 企业id
        results = json.loads(response.text)
        data_dict = results.get('data')
        if not data_dict:
            return None
        data_list = data_dict.get('items')
        for data in data_list:
            # name = data.get('name')  # 公司名
            taxIdNumber = data.get('taxIdNumber')  # 纳税人识别号
            type = data.get('type')  # 大分类1
            taxCategory = data.get('taxCategory')  # 欠税税种
            location = data.get('location')  # 公司地址
            personIdNumber = data.get('personIdNumber')  # 个人证件号
            legalpersonName = data.get('legalpersonName')  # 公司法人
            ownTaxBalance = data.get('ownTaxBalance')  # 欠税余额
            publishDate = data.get('publishDate')  # 发布时间
            tax_item = dict(
                name=company_name,
                tax_number=taxIdNumber,
                tax_type=type,
                tax_category=taxCategory,
                location=location,
                person_number=personIdNumber,
                legal_person=legalpersonName,
                owntax_balance=ownTaxBalance,
                publish_date=publishDate,

                url=response.url,
                source_content=json.dumps(data, ensure_ascii=False),
                bz='欠税公告',
                collection='tax_infomation',
            )
            # print(tax_item)
            yield tax_item

        # 翻页请求
        count = data_dict.get('count')  # 总数
        is_first = response.meta.get('is_first', True)
        if is_first and count and int(count) > 0:
            page_count = int(int(count) / 30) if int(count) % 30 == 0 else int(int(count) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/ar/companyowntax?id={}&pageNum={}&pageSize=30'.format(company_id, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_owntax,
                    meta={'is_first': False, 'company_id': company_id, 'compamy_name': company_name},
                    priority=3,
                )

    def parse_abnormal(self, response):
        """
        解析经营异常
        :param response: 经营异常响应
        :return: 解析item
        """
        # 解析
        company_name = response.meta.get('company_name')  # 企业名称
        company_id = response.meta.get('company_id')  # 企业id
        results = json.loads(response.text)
        data_dict = results.get('data')
        if not data_dict:
            return None
        data_list = data_dict.get('result')
        for data in data_list:
            putDate = data.get('putDate')  # 列入日期
            putReason = data.get('putReason')  # 列入原因
            putDepartment = data.get('putDepartment')  # 列入机关
            createTime = data.get('createTime')  # 创建日期/不展示
            removeDate = data.get('removeDate')  # 移除日期
            removeDepartment = data.get('removeDepartment')  # 移除机关
            removeReason = data.get('removeReason')  # 移除原因
            abnormal_item = dict(
                name=company_name,
                put_date=putDate,
                put_reason=putReason,
                put_department=putDepartment,
                remove_date=removeDate,
                remove_reason=removeReason,
                remove_department=removeDepartment,
                create_time=createTime,

                url=response.url,
                source_content=json.dumps(data, ensure_ascii=False),
                bz='经营异常',
                collection='abnormal_infomation',
            )
            # print(abnormal_item)
            yield abnormal_item

        # 翻页请求
        count = results.get('data').get('count')  # 总数
        is_first = response.meta.get('is_first', True)
        if is_first and count and int(count) > 0:
            page_count = int(int(count) / 30) if int(count) % 30 == 0 else int(int(count) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/expanse/abnormal?id={}&pageNum={}&pageSize=30'.format(company_id, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_abnormal,
                    meta={'is_first': False, 'company_name': company_name, 'company_id': company_id},
                    priority=3,
                )

    def parse_illegal(self, response):
        """
        解析严重违法以及翻页
        :param response: 严重违法响应内容
        :return: 解析item
        """
        # 解析
        company_name = response.meta.get('company_name')  # 企业名称
        company_id = response.meta.get('company_id')  # 企业id
        results = json.loads(response.text)
        data_dict = results.get('data')
        if not data_dict:
            return None
        data_list = data_dict.get('items')
        for data in data_list:
            putDate = data.get('putDate')  # 列入日期
            if putDate and len(str(putDate)) == 13:
                putDate = self.handle_timestmp(putDate)
            else:
                putDate = ''
            putDepartment = data.get('putDepartment')  # 列入决定机关
            putReason = data.get('putReason')  # 列入原因
            removeDepartment = data.get('removeDepartment')  # 移出决定机关
            removeReason = data.get('removeReason')  # 移出原因
            removeDate = data.get('removeDate', '')  # 移出日期
            if removeDate and len(str(removeDate)) == 13:
                removeDate = self.handle_timestmp(removeDate)
            else:
                removeDate = ''
            illegal_item = dict(
                name=company_name,
                put_date=putDate,
                put_department=putDepartment,
                put_reason=putReason,
                remove_department=removeDepartment,
                remove_reason=removeReason,
                remove_date=removeDate,

                url=unquote(response.url),
                source_content=json.dumps(data, ensure_ascii=False),
                bz='严重违法',
                collection='illegal_infomation',
            )
            # print(illegal_item)
            yield illegal_item

        # 翻页请求
        count = results.get('data').get('count')  # 总数
        is_first = response.meta.get('is_first', True)
        if is_first and count and int(count) > 0:
            page_count = int(int(count) / 30) if int(count) % 30 == 0 else int(int(count) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/ar/Illegal?name={}&pageNum={}&pageSize=20'.format(company_name, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_illegal,
                    meta={'is_first': False, 'company_name': company_name, 'company_id': company_id},
                    priority=3,
                )

    def parse_mortgage(self, response):
        """
        解析动产抵押信息
        :param response: 动产抵押响应结果
        :return: 解析后item
        """
        # 解析
        mortgage_item = {}
        company_name = response.meta.get('company_name')  # 企业名称
        company_id = response.meta.get('company_id')  # 企业id
        results = json.loads(response.text)
        data_dict = results.get('data')
        if not data_dict:
            return None
        data_list = data_dict.get('items')
        base_item = dict(
            name=company_name,
            url=unquote(response.url),
            bz='动产抵押',
            collection='mortgage_infomation',
        )
        for data in data_list:
            mortgage_item['source_content'] = json.dumps(data, ensure_ascii=False)
            # 登记信息/被担保债权情况 合并项
            baseInfo = data.get('baseInfo')
            mortgage_item['overview_amount'] = baseInfo.get('overviewAmount')  # 被担保债权数额/概况数额
            mortgage_item['scope'] = baseInfo.get('scope')  # 担保范围
            mortgage_item['status'] = baseInfo.get('status')  # 是否有效
            mortgage_item['remark'] = baseInfo.get('remark')  # 备注
            mortgage_item['reg_date'] = baseInfo.get('regDate')  # 登记日期
            mortgage_item['overview_type'] = baseInfo.get('overviewType')  # 被担保债权种类/概况总类
            mortgage_item['type_mortgag'] = baseInfo.get('type')  # 被担保债权种类/概况总类
            mortgage_item['term'] = baseInfo.get('term')  # 债务人履行债务期限
            mortgage_item['reg_department'] = baseInfo.get('regDepartment')  # 登记机关
            mortgage_item['reg_num'] = baseInfo.get('regNum')  # 注册号
            mortgage_item['cancel_reason'] = baseInfo.get('cancelReason')  # 撤销原因 不确定
            # 被担保债权情况
            mortgage_item['overview_scope'] = baseInfo.get('overviewScope')  # 担保范围
            mortgage_item['amount'] = baseInfo.get('amount')  # 概况数额
            mortgage_item['overview_remark'] = baseInfo.get('overviewRemark')  # 备注
            mortgage_item['overview_term'] = baseInfo.get('overviewTerm')  # 债务人履行债务期限

            # 抵押权人情况
            peopleInfo = data.get('peopleInfo')
            for people in peopleInfo:
                mortgage_item['people_name'] = people.get('peopleName', '')  # 抵押权人名称
                mortgage_item['license_num'] = people.get('licenseNum', '')  # 证件/证件号码
                mortgage_item['licese_type'] = people.get('liceseType', '')  # 抵押权人证照/证件类型
            # 抵押物概况
            pawnInfoList = data.get('pawnInfoList')
            for pawn in pawnInfoList:
                mortgage_item['detail'] = pawn.get('detail')  # 数量质量状况所在地
                mortgage_item['ownership'] = pawn.get('ownership')  # 所有权归属
                mortgage_item['pawn_remark'] = pawn.get('remark')  # 备注
                mortgage_item['pawn_name'] = pawn.get('pawnName')  # 抵押物名称

            item = {**base_item, **mortgage_item}
            yield item

        # 翻页请求
        count = results.get('data').get('count')  # 总数
        # historyCount = results.get('data').get('historyCount')  # 历史总数  需要VIP
        is_first = response.meta.get('is_first', True)
        if is_first and count and int(count) > 0:
            page_count = int(int(count) / 30) if int(count) % 30 == 0 else int(int(count) / 30) + 1
            for page in range(2, page_count + 1):
                url = 'https://api9.tianyancha.com/services/v3/ar/companyMortgageV2?name={}&pageNum={}&pageSize=30'.format(company_name, page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_mortgage,
                    meta={'is_first': False, 'company_name': company_name, 'company_id': company_id},
                    priority=3,
                )

    def handle_timestmp(self, timestamp):
        """
        处理13位时间戳
        :param timestmp:
        :return:
        """
        timestamps = float(timestamp / 1000)
        time_local = time.localtime(timestamps)
        result = time.strftime("%Y-%m-%d", time_local)
        return result