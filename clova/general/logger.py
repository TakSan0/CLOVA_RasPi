# ==================================
#           ロガークラス
# ==================================


class Logger:
    def __init__(self, name):
        self._loggerName = name

    def log(self, componentName, data):
        print("[{}:{}] {}".format(self._loggerName, componentName, data))


# ==================================
#         ログベースクラス
# ==================================


class BaseLogger:
    def __init__(self):
        self._parentClassName = self.__class__.__name__
        self._logger = Logger(self._parentClassName)
        self.log('CTOR', 'Creating <{}> class'.format(self._parentClassName))

    def __del__(self):
        self.log('DTOR', 'Destructing <{}> class'.format(self._parentClassName))

    def log(self, componentName, data):
        self._logger.log(componentName, data)
