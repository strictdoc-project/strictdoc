import inspect


class Logger:
    available_loggers = []
    enabled_loggers = []

    def __init__(self, logger_class):
        assert isinstance(logger_class, str)
        assert logger_class not in Logger.available_loggers
        Logger.available_loggers.append(logger_class)
        self.logger_class_name = logger_class

    def info(self, message):
        if self.logger_class_name not in self.enabled_loggers:
            return

        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        # print(curframe)
        # print(calframe[1])

        caller_file = calframe[1][1]
        caller_line = calframe[1][2]
        caller_name = calframe[1][3]

        print(
            '{}.{}>\n"""\n{}\n"""\n{}:{}\n\n'.format(
                self.logger_class_name,
                caller_name,
                message,
                caller_file,
                caller_line,
            )
        )
