import ctypes

from PyQt5.QtWidgets import (QWidget, QLineEdit, QCompleter, QTableWidget, QTableWidgetItem)

from const import SEP, TEACHERS, LESSONS, ROOMS
from widgets import TimeShow, FilledComboBox, SeparatedWidget

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QStringListModel


def get_text_dimensions(text, points, font):
    class SIZE(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    hdc = ctypes.windll.user32.GetDC(0)
    hfont = ctypes.windll.gdi32.CreateFontA(points, points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
    hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

    size = SIZE(0, 0)
    ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

    ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
    ctypes.windll.gdi32.DeleteObject(hfont)

    return size.cx


def set_suggestions(line: QLineEdit, suggestions: list[str]):
    completer = line.completer()
    if not completer:
        completer = QCompleter()
    model = QStringListModel()
    model.setStringList(suggestions)
    completer.setModel(model)
    line.setCompleter(completer)


class Table(QTableWidget):
    def __init__(self, hidden=False, data=None, times=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = data
        self.times = times

        self.last = None
        self.line = None
        self.line_last_text = None

        self.setColumnCount(5)
        self.setRowCount(9)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.setColumnHidden(0, hidden)
        self.setColumnHidden(1, hidden)

        texts = ["урок", "время", None, "каб.", "учитель"]
        groups = ["10.1 Т", "10.2 ЕН", "10.2 СЭ", "10.2 ГУМ", "9.1"]

        self.group = FilledComboBox(groups)
        self.setCellWidget(0, 2, self.group)

        self.cellClicked.connect(self.on_click)
        self.itemDelegate().closeEditor.connect(self.on_change)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in range(1, 9):
            item = QTableWidgetItem(str(i))
            item.setFlags(Qt.ItemIsEnabled)
            self.setItem(i, 0, item)
            self.setCellWidget(i, 1, TimeShow(self))
            self.setCellWidget(i, 2, SeparatedWidget("", SEP, self))
            self.setCellWidget(i, 3, SeparatedWidget("", SEP, self))
            self.setCellWidget(i, 4, SeparatedWidget("", SEP, self))
        for i in range(5):
            if not texts[i]:
                continue
            item = QTableWidgetItem(texts[i])
            item.setFlags(Qt.ItemIsEnabled)
            self.setItem(0, i, item)

        self.set_col_size()
        self.setFont(QFont("Times New Roman", 10))

        self.config_teacher = True
        self.config_classroom = True

        if self.data is not None:
            self.config_teacher = self.data["teacher"]
            self.config_classroom = self.data["classroom"]
            self.load_data()
            if not self.config_teacher:
                self.hideColumn(4)
            if not self.config_classroom:
                self.hideColumn(3)

    def set_col_size(self):
        size = 10
        # column_width
        n = get_text_dimensions("урок", size, "Times New Roman") + 1
        self.setColumnWidth(0, n)  # "урок"
        n = get_text_dimensions("00:00-00:00", size, "Times New Roman") + 1
        self.setColumnWidth(1, n)  # "время"
        n = get_text_dimensions("ЗПС по информатике/", size, "Times New Roman") + 1
        self.setColumnWidth(2, n + 1)  # "ЗПС по информатике/"
        n = get_text_dimensions("каб.", size, "Times New Roman") + 1
        self.setColumnWidth(3, n + 1)  # "каб."
        n = get_text_dimensions("Красноперова", size, "Times New Roman") + 1
        self.setColumnWidth(4, n + 1)  # "Красноперова"
        # row_height
        size = 25
        self.setRowHeight(0, size)
        for i in range(1, 9):
            self.setRowHeight(i, size * 2)
        w = 2
        for i in range(5):
            w += self.columnWidth(i)
        h = 2
        for i in range(9):
            h += self.rowHeight(i)
        self.setFixedSize(w, h)

    def load_data(self):
        self.group.setCurrentText(self.data['group'])
        for i in range(len(self.times)):
            self.cellWidget(i + 1, 1).setText(self.times[i])
            self.cellWidget(i + 1, 2).setText(self.data['rows'][i]['lesson'])
            self.cellWidget(i + 1, 3).setText(self.data['rows'][i]['classroom'])
            self.cellWidget(i + 1, 4).setText(self.data['rows'][i]['teacher'])

    def dump_data(self):
        data = {
            'classroom': self.config_classroom,
            'teacher': self.config_teacher,
            'group': self.group.currentText(),
            'rows': []
        }
        for i in range(1, self.rowCount()):
            row = {
                "lesson": self.cellWidget(i, 2).text(),
                "classroom": self.cellWidget(i, 3).text(),
                "teacher": self.cellWidget(i, 4).text()
            }
            data['rows'].append(row)
        return data

    def get_times(self):
        times = []
        for i in range(1, self.rowCount()):
            times.append(self.cellWidget(i, 1).text())
        return times

    def on_click(self, row, col):
        if col < 2:
            return
        widget = self.cellWidget(row, col)
        if not widget:
            return
        item = QTableWidgetItem(widget.text())
        self.removeCellWidget(row, col)
        self.setItem(row, col, item)
        self.last = (row, col)
        self.edit(self.currentIndex())
        lines: list[QLineEdit] = self.findChild(QWidget, "qt_scrollarea_viewport").findChildren(QLineEdit, "", Qt.FindDirectChildrenOnly)
        for line in lines:
            if line.hasFocus():
                self.line = line
                break
        self.line_last_text = ""
        if col == 2:
            self.suggestions = LESSONS
        elif col == 3:
            self.suggestions = ROOMS
        elif col == 4:
            self.suggestions = TEACHERS
        set_suggestions(self.line, self.suggestions)
        self.line.textEdited.connect(self.line_edited)

    def on_change(self, data):
        row, col = self.last
        widget = SeparatedWidget(data.text(), SEP)
        self.setItem(row, col, None)
        self.setCellWidget(row, col, widget)

    def line_edited(self, text):
        if not text and not self.line_last_text:
            c = ''
        elif len(text) < len(self.line_last_text):
            c = self.line_last_text[-1]
        else:
            c = text[-1]
        extra = '/'
        if '/' not in text:
            extra = ''
        self.line_last_text = text
        if c == SEP:
            buf = text.rsplit(SEP, 1)
            if len(buf) < 2:
                buf.clear()
                buf.append("")
            suggestions = []
            for suggest in self.suggestions:
                suggestions.append(buf[0] + extra + suggest)
            set_suggestions(self.line, suggestions)