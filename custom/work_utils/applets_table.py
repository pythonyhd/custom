# -*- coding: utf-8 -*-
"""
天眼查小程序-MySQL表
"""
from datetime import datetime
import warnings

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from custom.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Column, Integer, String, TEXT, DATETIME, SMALLINT, ForeignKey

warnings.filterwarnings("ignore")
Base = declarative_base()
# 初始化数据库连接:
engine = create_engine(
    "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset={charset}".format(username=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, db=DB_NAME, charset=DB_CHARSET),
    # echo=True,  # 打印过程
    # max_overflow=0,  # 超过连接池大小外最多创建的连接
    # pool_size=5,  # 连接池大小
    # pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    # pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收(重置)
)


class AppletsBusinessCollection(Base):
    """
    天眼查小程序-工商信息表
    """
    __tablename__ = 'business_information'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    reg_capital = Column(String(length=64), nullable=True, comment='注册资本')
    actual_capital = Column(String(length=64), nullable=True, comment='实缴资本')
    estiblish_time = Column(String(length=16), nullable=True, comment='成立日期')
    reg_status = Column(String(length=16), nullable=True, comment='经营状态')
    credit_code = Column(String(length=64), nullable=True, comment='统一社会信用代码')
    reg_number = Column(String(length=64), nullable=True, comment='工商注册号')
    tax_number = Column(String(length=64), nullable=True, comment='纳税人识别号')
    org_number = Column(String(length=64), nullable=True, comment='组织机构代码')
    company_org_type = Column(String(length=128), nullable=True, comment='公司类型')
    industry = Column(String(length=16), nullable=True, comment='行业')
    approved_time = Column(String(length=16), nullable=True, comment='核准日期')
    reg_institute = Column(String(length=64), nullable=True, comment='登记机关')
    from_time = Column(String(length=16), nullable=True, comment='营业期限开始')
    to_time = Column(String(length=16), nullable=True, comment='营业期限截止')
    tax_payer = Column(String(length=128), nullable=True, comment='纳税人资质')
    staff_num_range = Column(String(length=64), nullable=True, comment='人员规模')
    social_staff_num = Column(String(length=32), nullable=True, comment='参保人数')
    property = Column(String(length=128), nullable=True, comment='曾用名')
    reg_location = Column(String(length=128), nullable=True, comment='英文名称')
    business_scope = Column(TEXT, nullable=True, comment='注册地址')
    legal_person_name = Column(LONGTEXT, nullable=True, comment='经营范围')
    history_names = Column(TEXT, nullable=True, comment='法人')
    phone_number = Column(String(length=32), nullable=True, comment='电话')
    phone_list = Column(TEXT, nullable=True, comment='电话列表')
    email = Column(String(length=32), nullable=True, comment='邮箱')
    email_list = Column(TEXT, nullable=True, comment='邮箱列表')
    logo = Column(String(length=128), nullable=True, comment='logo图片地址')
    alias = Column(String(length=64), nullable=True, comment='简称')
    website = Column(String(length=32), nullable=True, comment='公司网址')

    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsBusinessCollection %r>" % self.name


class AppletsInvestorCollection(Base):
    """
    天眼查小程序-股东信息表
    """
    __tablename__ = 'investor_information'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    partner_name = Column(String(length=128), nullable=True, comment='股东姓名')
    tag_name = Column(String(length=128), nullable=True, comment='股东标签')
    amomon = Column(String(length=128), nullable=True, comment='认缴出资额')
    amomon_time = Column(String(length=128), nullable=True, comment='认缴时间')
    percent = Column(String(length=128), nullable=True, comment='持股比例')

    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsInvestorCollection %r>" % self.name


class AppletsStaffCollection(Base):
    """
    天眼查小程序-主要人员表
    """
    __tablename__ = 'staff_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    staff_name = Column(String(length=128), nullable=True, comment='主要人员姓名')
    staff_job = Column(String(length=128), nullable=True, comment='主要人员职位')

    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsStaffCollection %r>" % self.name


class AppletsChangeCollection(Base):
    """
    天眼查小程序-变更表
    """
    __tablename__ = 'change_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    change_item = Column(TEXT, nullable=True, comment='变更项目')
    content_before = Column(LONGTEXT, nullable=True, comment='变更前')
    content_after = Column(LONGTEXT, nullable=True, comment='变更后')
    change_time = Column(String(length=64), nullable=True, comment='变更时间')
    have_psersion = Column(String(length=128), nullable=True, comment='')

    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsChangeCollection %r>" % self.name


class AppletsPunishCollection(Base):
    """
    天眼查小程序-行政处罚表
    """
    __tablename__ = 'punish_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    punish_name = Column(TEXT, nullable=True, comment='处罚名称')
    punish_number = Column(String(length=32), nullable=True, comment='处罚决定文书号')
    cf_type = Column(LONGTEXT, nullable=True, comment='违法行为类型/处罚类别1')
    cf_type_second = Column(TEXT, nullable=True, comment='处罚类别2')
    legal_person = Column(String(length=64), nullable=True, comment='法人')
    decision_date = Column(String(length=16), nullable=True, comment='处罚决定日期')
    department_name = Column(String(length=64), nullable=True, comment='处罚机关')
    content = Column(LONGTEXT, nullable=True, comment='处罚内容')
    evidence = Column(TEXT, nullable=True, comment='处罚依据')
    reason = Column(TEXT, nullable=True, comment='处罚事由')
    result = Column(TEXT, nullable=True, comment='处罚结果')
    reg_num = Column(String(length=64), nullable=True, comment='注册号')
    area_name = Column(String(length=128), nullable=True, comment='地区名称')
    remarks = Column(LONGTEXT, nullable=True, comment='备注信息')
    publish_date = Column(String(length=16), nullable=True, comment='公开日期')
    alias = Column(String(length=64), nullable=True, comment='昵称')
    logo = Column(String(length=128), nullable=True, comment='公司logo')
    source_name = Column(String(length=128), nullable=True, index=True, comment='公司名/可能不存在')

    bz = Column(String(length=12), nullable=True, comment='自己的备注')
    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsPunishCollection %r>" % self.name


class AppletsEquityCollection(Base):
    """
    天眼查小程序-股权出质表
    """
    __tablename__ = 'equity_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    pledgor = Column(String(length=128), nullable=True, comment='出质人')
    pledgor_url = Column(String(length=128), nullable=True, comment='出质人url')
    pledgee = Column(String(length=128), nullable=True, comment='质权人')
    pledgee_url = Column(String(length=128), nullable=True, comment='质权人url')
    equity_amount = Column(TEXT, nullable=True, comment='出质股权数')
    state = Column(String(length=64), nullable=True, comment='状态')
    remarks = Column(LONGTEXT, nullable=True, comment='备注信息')
    reg_date = Column(String(length=16), nullable=True, comment='注册日期')
    reg_number = Column(String(length=64), nullable=True, comment='注册号')
    put_date = Column(String(length=16), nullable=True, comment='放入日期')
    certif_number_dgor = Column(String(length=64), nullable=True, comment='出质人证件号码')
    certif_number_dgee = Column(String(length=64), nullable=True, comment='质权人证件号码')

    bz = Column(String(length=12), nullable=True, comment='自己的备注')
    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsEquityCollection %r>" % self.name


class AppletsTaxCollection(Base):
    """
    天眼查小程序-欠税公告表
    """
    __tablename__ = 'tax_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    tax_number = Column(String(length=64), nullable=True, comment='纳税人识别号')
    tax_type = Column(String(length=32), nullable=True, comment='大分类1')
    tax_category = Column(String(length=32), nullable=True, comment='欠税税种')
    location = Column(String(length=256), nullable=True, comment='公司地址')
    person_number = Column(String(length=64), nullable=True, comment='个人证件号')
    legal_person = Column(String(length=128), nullable=True, comment='公司法人')
    owntax_balance = Column(String(length=256), nullable=True, comment='欠税余额')
    publish_date = Column(String(length=16), nullable=True, comment='发布时间')

    bz = Column(String(length=12), nullable=True, comment='自己的备注')
    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsTaxCollection %r>" % self.name


class AppletsAbnormalCollection(Base):
    """
    天眼查小程序-经营异常表
    """
    __tablename__ = 'abnormal_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    put_date = Column(String(length=16), nullable=True, comment='列入日期')
    put_reason = Column(TEXT, nullable=True, comment='列入原因')
    put_department = Column(String(length=64), nullable=True, comment='列入机关')
    remove_date = Column(String(length=16), nullable=True, comment='移除日期')
    remove_reason = Column(TEXT, nullable=True, comment='移除机关')
    remove_department = Column(String(length=64), nullable=True, comment='移除原因')
    create_time = Column(String(length=16), nullable=True, comment='创建日期')

    bz = Column(String(length=12), nullable=True, comment='自己的备注')
    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsAbnormalCollection %r>" % self.name


class AppletsIllegalCollection(Base):
    """
    天眼查小程序-严重违法表
    """
    __tablename__ = 'illegal_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    put_date = Column(String(length=16), nullable=True, comment='列入日期')
    put_reason = Column(TEXT, nullable=True, comment='列入原因')
    put_department = Column(String(length=64), nullable=True, comment='列入机关')
    remove_date = Column(String(length=16), nullable=True, comment='移除日期')
    remove_reason = Column(TEXT, nullable=True, comment='移除机关')
    remove_department = Column(String(length=64), nullable=True, comment='移除原因')
    create_time = Column(String(length=16), nullable=True, comment='创建日期')

    bz = Column(String(length=12), nullable=True, comment='自己的备注')
    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsIllegalCollection %r>" % self.name


class AppletsMortgageCollection(Base):
    """
    天眼查小程序-动产抵押表
    """
    __tablename__ = 'mortgage_infomation'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    overview_amount = Column(String(length=32), nullable=True, comment='被担保债权数额/概况数额')
    scope = Column(TEXT, nullable=True, comment='担保范围')
    status = Column(String(length=32), nullable=True, comment='是否有效')
    remark = Column(TEXT, nullable=True, comment='备注')
    reg_date = Column(String(length=32), nullable=True, comment='登记日期')
    overview_type = Column(String(length=32), nullable=True, comment='被担保债权种类/概况总类')
    type_mortgag = Column(String(length=16), nullable=True, comment='被担保债权种类/概况总类')
    term = Column(TEXT, nullable=True, comment='债务人履行债务期限')
    reg_department = Column(String(length=64), nullable=True, comment='登记机关')
    reg_num = Column(String(length=32), nullable=True, comment='注册号')
    cancel_reason = Column(TEXT, nullable=True, comment='撤销原因')
    overview_scope = Column(TEXT, nullable=True, comment='担保范围')
    amount = Column(String(length=32), nullable=True, comment='概况数额')
    overview_remark = Column(TEXT, nullable=True, comment='备注')
    overview_term = Column(TEXT, nullable=True, comment='债务人履行债务期限')
    people_name = Column(String(length=64), nullable=True, comment='抵押权人名称')
    license_num = Column(String(length=64), nullable=True, comment='证件/证件号码')
    licese_type = Column(String(length=32), nullable=True, comment='抵押权人证照/证件类型')
    detail = Column(TEXT, nullable=True, comment='数量质量状况所在地')
    ownership = Column(String(length=64), nullable=True, comment='所有权归属')
    pawn_remark = Column(TEXT, nullable=True, comment='备注')
    pawn_name = Column(TEXT, nullable=True, comment='抵押物名称')

    bz = Column(String(length=12), nullable=True, comment='自己的备注')
    source_content = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<AppletsMortgageCollection %r>" % self.name


if __name__ == '__main__':
    Base.metadata.create_all(engine)  # 新建表
    # Base.metadata.drop_all(engine)  # 删除表