# 配置定时任务
class Config(object):
    JOBS = [
        {
            'id': 'soft_real_time',
            'func': '__main__:time_exceed_delete',
            'trigger': 'interval',
            'seconds': 30,
        }
    ]