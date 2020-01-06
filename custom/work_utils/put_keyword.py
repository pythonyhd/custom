# -*- coding: utf-8 -*-
import pymysql
import redis

# MYSQL_HOST = '114.115.128.41'
MYSQL_HOST = '49.4.86.151'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
# MYSQL_PWD = 'mysql@Axinyong123'
MYSQL_PWD = 'root'
# MYSQL_DB = 'wecat_gjqyxx'
MYSQL_DB = 'company_name'
MYSQL_CHARSET = 'utf8'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_PWD = ''
REDIS_DB = 1

mysql_client = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PWD, db=MYSQL_DB, charset=MYSQL_CHARSET)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB)


def custom_keyword():
    query_sql = "select name from oname where xcx_zt=0 limit 10000"
    cursor = mysql_client.cursor()
    num = 0
    try:
        cursor.execute(query_sql)
        mysql_client.commit()
        keywords = cursor.fetchall()
        for keyword in keywords:
            num += 1
            # print(keyword[0])
            redis_client.lpush('tianyancha:keywords', keyword[0])
            # redis_client.lpush('tianyancha_applets:keywords', keyword[0])
            print('插入第{}条'.format(num))
    except Exception as e:
        mysql_client.rollback()
        print('出错:{}'.format(repr(e)))
        custom_keyword()
    finally:
        cursor.close()
        mysql_client.close()


if __name__ == '__main__':
    custom_keyword()