# -*- coding: utf-8 -*-
"""
天眼查-网页端MySQL表
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


class TianyanchaXzcfCollection(Base):
    """
    天眼查-行政处罚表
    """
    __tablename__ = 'xzcf'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='企业名称')
    pname = Column(String(length=32), nullable=True, comment='法人代表')
    cf_wsh = Column(String(length=128), nullable=True, comment='文书号')
    cf_yj = Column(TEXT, nullable=True, comment='处罚依据')
    cf_sy = Column(TEXT, nullable=True, comment='处罚事由')
    cf_jg = Column(TEXT, nullable=True, comment='处罚结果')
    reg_num = Column(String(length=64), nullable=True, comment='注册号')
    cf_xzjg = Column(String(length=64), nullable=True, comment='处罚机关')
    area_name = Column(String(length=64), nullable=True, comment='地区名称')
    cf_jdrq = Column(String(length=16), nullable=True, comment='处罚决定日期')
    description = Column(LONGTEXT, nullable=True, comment='简单描述')
    cf_cfmc = Column(String(length=256), nullable=True, comment='案件名称')
    cf_type = Column(TEXT, nullable=True, comment='违法行为类型')
    cf_type_second = Column(String(length=64), nullable=True, comment='处罚类型2')
    bz = Column(String(length=128), nullable=True, comment='备注')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaXzcfCollection %r>" % self.oname


class TianyanchaGqczCollection(Base):
    """
    天眼查-股权出质表
    """
    __tablename__ = 'gqcz'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='主体名称')
    zqr = Column(String(length=128), nullable=True, index=True, comment='质权人')
    czr = Column(String(length=128), nullable=True, index=True, comment='出质人')
    reg_num = Column(String(length=64), nullable=True, comment='注册号')
    state = Column(String(length=32), nullable=True, comment='状态')
    cf_jdrq = Column(String(length=16), nullable=True, comment='处罚决定日期')
    equity_amount = Column(String(length=32), nullable=True, comment='出质股权数额')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaGqczCollection %r>" % self.oname


class TianyanchaYzwfsxCollection(Base):
    """
    天眼查-严重违法失信
    """
    __tablename__ = 'yzwfsx'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='主体名称')
    cf_xzjg = Column(String(length=64), nullable=True, comment='处罚机关')
    cf_sy = Column(TEXT, nullable=True, comment='事由')
    cf_jdrq = Column(String(length=16), nullable=True, comment='处罚决定日期')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaYzwfsxCollection %r>" % self.oname


class TianyanchaQsggCollection(Base):
    """
    天眼查-欠税公告
    """
    __tablename__ = 'qsgg'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='主体名称')
    name = Column(String(length=128), nullable=True, comment='名称')
    uccode = Column(String(length=64), nullable=True, comment='证件号')
    pname = Column(String(length=32), nullable=True, comment='法人代表')
    location = Column(String(length=64), nullable=True, comment='地区名称')
    tax_num = Column(String(length=64), nullable=True, comment='纳税人识别号')
    cf_type = Column(String(length=64), nullable=True, comment='税父分类')
    cf_category = Column(String(length=64), nullable=True, comment='欠税税种')
    qs_ye = Column(String(length=32), nullable=True, comment='欠税余额')
    fb_rq = Column(String(length=16), nullable=True, comment='发布日期')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaQsggCollection %r>" % self.oname


class TianyanchaJyycCollection(Base):
    """
    天眼查-经营异常
    """
    __tablename__ = 'jyyc'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='主体名称')
    cf_sy = Column(TEXT, nullable=True, comment='处罚事由')
    cf_jdrq = Column(String(length=16), nullable=True, comment='处罚决定日期')
    cf_xzjg = Column(String(length=64), nullable=True, comment='处罚机关')
    yc_sy = Column(TEXT, nullable=True, comment='移除事由')
    yc_jdrq = Column(String(length=16), nullable=True, comment='移除日期')
    yc_xzjg = Column(String(length=64), nullable=True, comment='移除机关')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaJyycCollection %r>" % self.oname


class TianyanchaHbcfCollection(Base):
    """
    天眼查-环保处罚
    """
    __tablename__ = 'hbcf'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='主体名称')
    cf_yj = Column(TEXT, nullable=True, comment='处罚依据')
    cf_sy = Column(TEXT, nullable=True, comment='处罚事由')
    cf_jg = Column(TEXT, nullable=True, comment='处罚结果')
    law_break = Column(TEXT, nullable=True, comment='违反法律')
    cf_jdrq = Column(String(length=16), nullable=True, comment='处罚决定日期')
    cf_xzjg = Column(String(length=64), nullable=True, comment='处罚机关')
    cf_wsh = Column(String(length=128), nullable=True, comment='文书号')
    execution = Column(String(length=64), nullable=True, comment='执行情况')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaHbcfCollection %r>" % self.oname


class TianyanchaGqdjCollection(Base):
    """
    天眼查-股权冻结
    """
    __tablename__ = 'gqdj'
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    oname = Column(String(length=128), nullable=True, index=True, comment='主体名称')
    name = Column(String(length=128), nullable=True, comment='名称')
    equity_amount = Column(String(length=16), nullable=True, comment='处罚决定日期')
    zxfy = Column(String(length=64), nullable=True, comment='执行法院')
    cf_wsh = Column(String(length=128), nullable=True, comment='文书号')
    zx_wsh = Column(String(length=128), nullable=True, comment='执行文书号')
    zx_sx = Column(String(length=64), nullable=True, comment='执行事项')
    lince_type = Column(String(length=64), nullable=True, comment='被执行人证件种类')
    uccode = Column(String(length=64), nullable=True, comment='被执行人证件号码')
    begin_date = Column(String(length=16), nullable=True, comment='冻结期限自')
    end_date = Column(String(length=16), nullable=True, comment='冻结期限至')
    fb_rq = Column(String(length=16), nullable=True, comment='公示日期')

    wbbz = Column(String(length=16), nullable=True, comment='外部备注')
    ws_nr_txt = Column(LONGTEXT, nullable=True, comment='原始详情内容')
    url = Column(String(length=128), nullable=False, comment='详情url')
    base_url = Column(String(length=128), nullable=False, comment='天眼查原始链接')
    spider_time = Column(DATETIME, nullable=False, default=datetime.now, comment='抓取时间')
    process_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    upload_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')
    alter_status = Column(Integer, default=0, nullable=True, onupdate=1, comment='状态')

    def __repr__(self):
        return "<TianyanchaGqdjCollection %r>" % self.oname


if __name__ == '__main__':
    Base.metadata.create_all(engine)  # 新建表
    # Base.metadata.drop_all(engine)  # 删除表