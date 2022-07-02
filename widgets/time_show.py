from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette


class TimeShow(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(TimeShow, self).__init__(*args, **kwargs)

        self.setObjectName("TimeShow")
        self.setProperty('state', 'ok')

        self.last_ln = 0
        # self.setPlaceholderText("hh:mm-hh:mm")
        # self.setValidator(QRegExpValidator(QRegExp("(2[0-3]|[01][0-9]):([0-5]?[0-9])-(2[0-3]|[01]?[0-9]):([0-5]?[0-9])")))
        self.textEdited.connect(self.on_edit)
        self.editingFinished.connect(self.colorize_errors)
        self.setMaxLength(11)
        self.selectionChanged.connect(self.anti_user)
        self.cursorPositionChanged.connect(self.anti_user)
        self.setAlignment(Qt.AlignCenter)

    def anti_user(self):
        self.deselect()
        self.setCursorPosition(len(self.text()))

    def on_edit(self, x):
        ln = len(self.text())
        if self.last_ln > ln:
            self.last_ln = ln
            return

        new_text = self.gen_new_text(self.text())

        self.setText(new_text)
        self.last_ln = len(new_text)

    @staticmethod
    def gen_new_text(last_text: str) -> str:
        ln = len(last_text)
        text = last_text[:-1]
        c = last_text[-1]
        new_text = "ERROR"
        if ln == 1 or ln == 7:
            if not c.isdigit():
                new_text = text
            elif c not in '012':
                new_text = text + '0' + c + ':'
            else:
                new_text = text + c
        elif ln == 2 or ln == 8:
            if not c.isdigit():
                new_text = text
            elif text[-1] == '2':
                if c in '0123':
                    new_text = text + c + ':'
                else:
                    new_text = text
            else:
                new_text = text + c + ':'
        elif ln == 3 or ln == 9:
            if c != ':':
                new_text = text
            else:
                new_text = text + c
        elif ln == 4 or ln == 10:
            if not c.isdigit():
                new_text = text
            elif c in '6789':
                new_text = text + '0' + c + '-'
            else:
                new_text = text + c
        elif ln == 5 or ln == 11:
            if not c.isdigit():
                new_text = text
            elif ln == 11:
                new_text = text + c
            else:
                new_text = text + c + '-'
        elif ln == 6:
            if c != '-':
                new_text = text
            else:
                new_text = text + c

        return new_text

    def set_state(self, state: str = 'ok'):
        """
        :param state: One of following states: ("ok", "invalid", "collision")
        :return: None
        """
        if state in ("ok", "invalid", "collision"):
            self.setProperty('state', state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def colorize_errors(self):
        if 0 < len(self.text()) < 11:
            self.set_state('invalid')
        else:
            self.set_state('ok')
            self.parent().parent().global_check()

