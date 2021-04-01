import time
import datetime
from order.models import OrderExport
from order.serializers import OrderExportSerializer


class BookingStatus:

    """
    查询最近三天的订餐是否允许预约
    预约状态：
    0：允许预约/修改
    1：不允许预约/修改，但允许管理员预约/修改
    2： 已超时，所有人不可修改
    """
    @staticmethod
    def booking_status(date=None):
        today = datetime.date.today()
        if date:
            res = [0, 0, 0]
            export = OrderExport.objects.filter(export_date=date)
            s = OrderExportSerializer(export, many=True)
            exports = s.data

            # 修改对应日期的导出状态
            for item in exports:
                res[item['meal_type'] - 1] = 1

            if str(date) == str(today):
                # 如果是今天的时间，是否已经超时
                now = time.strftime("%H:%M:%S")
                if now > '08:00:00':
                    res[0] = 2
                if now > '11:30:00':
                    res[1] = 2
                if now > '17:30:00':
                    res[2] = 2
            return res

        # 取今天和后三天的日期
        day1 = today + datetime.timedelta(days=1)
        day2 = today + datetime.timedelta(days=2)
        day3 = today + datetime.timedelta(days=3)

        # 查询导出状态
        export = OrderExport.objects.filter(export_date__gte=today, export_date__lte=day3)
        s = OrderExportSerializer(export, many=True)
        exports = s.data

        dates = {
            str(today): [0, 0, 0],
            str(day1): [0, 0, 0],
            str(day2): [0, 0, 0],
            str(day3): [0, 0, 0],
        }

        # 修改对应日期的导出状态
        for item in exports:
            dates[item['export_date']][item['meal_type'] - 1] = 1

        # 今天的时间，是否已经超时
        now = time.strftime("%H:%M:%S")
        if now > '08:00:00':
            dates[str(today)][0] = 2
        if now > '11:30:00':
            dates[str(today)][1] = 2
        if now > '17:30:00':
            dates[str(today)][2] = 2

        return dates
