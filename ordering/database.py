import pymysql
from django.conf import settings


class Database:

    @staticmethod
    def cursor():
        default = settings.DATABASES['default']
        link = pymysql.connect(host=default['HOST'], port=default['POST'], user=default['USER'],
                               passwd=default['PASSWORD'], db=default['NAME'], charset=default['OPTIONS']['charset'])
        return link.cursor(cursor=pymysql.cursors.DictCursor)
