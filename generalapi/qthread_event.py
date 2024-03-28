from PyQt5.QtCore import QObject


class QThreadEvent(QObject):

    def __init__(self, parent):
        super(QThreadEvent, self).__init__(parent)
        self.__is_set = False

    def set(self):
        self.__is_set = True

    def clear(self):
        self.__is_set = False

    def is_set(self):
        return self.__is_set
