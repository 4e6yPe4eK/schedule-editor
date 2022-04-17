from PyQt5.QtWidgets import (QLayout, QScrollArea, QScroller, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSpacerItem, QSizePolicy)

from widgets import Table
import logging
logging.basicConfig(filename='log.log')


def layout_delete(layout: QLayout):
    item = layout.takeAt(0)
    while item:
        if (new_layout := item.layout()) is not None:
            layout_delete(new_layout)
        elif (widget := item.widget()) is not None:
            widget.setParent(None)
            del widget
        else:
            del item
        item = layout.takeAt(0)
    del layout


class WidgetForScrolling(QScrollArea):
    def __init__(self, schedule=None, *args, **kwargs):
        super(WidgetForScrolling, self).__init__(*args, **kwargs)

        self.edited = False

        self.setStyleSheet("""QLineEdit#TimeShow {border-style: solid;}
                              QComboBox#FilledComboBox {border-style: solid; background-color: white;}""")

        QScroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)
        self.setWidgetResizable(True)
        self.resize(1000, 800)

        self.w = QWidget(self)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.w.setLayout(self.layout)
        self.setWidget(self.w)

        self.add_btn = QPushButton("+")
        self.del_btn = QPushButton("-")
        self.add_btn.clicked.connect(self.add_row)
        self.del_btn.clicked.connect(self.del_row)
        layout = QHBoxLayout()
        layout.addWidget(self.add_btn)
        layout.addWidget(self.del_btn)
        self.layout.addLayout(layout)

        self.layout.addItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Expanding))

        if schedule is not None:
            for i in range(schedule['rowNum']):
                self.add_row()
                layout = self.layout.itemAt(self.layout.count() - 4)
                for j in range(schedule['tables'][i]['groupsNum']):
                    self.add_col(layout, schedule['tables'][i]['groups'][j], schedule['tables'][i]['times'])

    @staticmethod
    def add_col(layout, data=None, times=None):
        layout.insertWidget(layout.count() - 2, Table(layout.count() != 2, data, times))

    def del_col(self, layout):
        if layout.count() == 2:
            self.layout.removeItem(layout.spacer)
            self.layout.removeItem(layout)
            layout_delete(layout)
            return
        layout.removeWidget(layout.takeAt(layout.count() - 3).widget())

    def add_col_from_btn(self):
        layout = self.sender().layout
        self.add_col(layout)

    def del_col_from_btn(self):
        layout = self.sender().layout
        self.del_col(layout)

    def add_row(self):
        self.edited = True
        layout = self.new_layout()
        spacer = QSpacerItem(10, 40, QSizePolicy.Fixed, QSizePolicy.Fixed)
        setattr(layout, "spacer", spacer)
        self.layout.insertLayout(self.layout.count() - 2, layout)
        self.layout.insertSpacerItem(self.layout.count() - 2, spacer)

    def del_row(self):
        if self.layout.count() < 3:
            return
        self.layout.removeItem(self.layout.takeAt(self.layout.count() - 3))
        layout_delete(self.layout.takeAt(self.layout.count() - 3))

    def new_layout(self):
        layout = QHBoxLayout()
        layout.setObjectName('table_layout')
        spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
        #layout.addWidget(Table())
        add_btn = QPushButton("+")
        del_btn = QPushButton("-")
        setattr(add_btn, "layout", layout)
        setattr(del_btn, "layout", layout)
        add_btn.clicked.connect(self.add_col_from_btn)
        del_btn.clicked.connect(self.del_col_from_btn)
        add_btn.setStyleSheet("margin-left: 10px; width: 40px; height: 40px;")
        del_btn.setStyleSheet("margin-left: 10px; width: 40px; height: 40px;")
        x = QVBoxLayout()
        x.addWidget(add_btn)
        x.addWidget(del_btn)
        layout.addLayout(x)
        layout.addItem(spacer)
        return layout

    def dump_data(self):
        data = {
            'rowNum': len(self.layout.children()) - 1,
            'tables': []
        }
        for layout in self.layout.findChildren(QHBoxLayout, 'table_layout'):
            if layout.count() == 2:
                row = {
                    "groupsNum": 0,
                }
                data['tables'].append(row)
                continue
            print(layout.count())
            table: Table = layout.itemAt(0).widget()
            row = {
                "groupsNum": layout.count() - 2,
                "num": True,
                "nums": [1, 2, 3, 4, 5, 6, 7, 8],
                "time": True,
                "times": table.get_times(),
                "lessonsNum": table.rowCount() - 1,
                "groups": []
            }
            for ind in range(layout.count() - 2):
                table: Table = layout.itemAt(ind).widget()
                row["groups"].append(table.dump_data())
            data['tables'].append(row)
        return data

