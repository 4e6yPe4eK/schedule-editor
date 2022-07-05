from PyQt5.QtWidgets import (QLayout, QScrollArea, QScroller, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSpacerItem, QSizePolicy)

from widgets import Table
import logging
logging.basicConfig(filename='log.log')


def parse_time(time: str) -> tuple:
    try:
        if len(time) < 11:
            raise ValueError
        time_start, time_end = time.split('-')

        time_start = time_start.split(':')
        time_start = int(time_start[0]) * 60 + int(time_start[1])

        time_end = time_end.split(':')
        time_end = int(time_end[0]) * 60 + int(time_end[1])

        return time_start, time_end
    except (IndexError, ValueError):
        return None, None



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


class RowWithTablesLayout(QHBoxLayout):
    def __init__(self, parent, *args, **kwargs):
        super(RowWithTablesLayout, self).__init__(*args, **kwargs)
        self.parent = parent
        self.setObjectName('table_layout')
        spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
        add_btn = QPushButton("+")
        del_btn = QPushButton("-")
        add_btn.setObjectName("ColButton")
        del_btn.setObjectName("ColButton")
        setattr(add_btn, "layout", self)
        setattr(del_btn, "layout", self)
        add_btn.clicked.connect(self.add_col)
        del_btn.clicked.connect(self.del_col)
        x = QVBoxLayout()
        x.addWidget(add_btn)
        x.addWidget(del_btn)
        self.addLayout(x)
        self.addItem(spacer)

    def add_col(self, trash, data=None, times=None):
        self.insertWidget(self.count() - 2, Table(self.count() != 2, data, times))

    def del_col(self):
        if self.count() == 2:
            self.parent.layout.removeItem(self.spacer)
            self.parent.layout.removeItem(self)
            layout_delete(self)
            return
        self.removeWidget(self.takeAt(self.count() - 3).widget())


class WidgetForScrolling(QScrollArea):
    def __init__(self, schedule=None, *args, **kwargs):
        super(WidgetForScrolling, self).__init__(*args, **kwargs)

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
                    layout.add_col(None, schedule['tables'][i]['groups'][j], schedule['tables'][i]['times'])
            self.global_check()

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
        layout = RowWithTablesLayout(self)
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

    def global_check(self):
        data = self.dump_data()
        classrooms, teachers = [], []
        for table_ind, table in enumerate(data['tables']):
            if table['groupsNum'] == 0:
                continue
            times = table['times']
            table_widget: RowWithTablesLayout = self.layout.itemAt(2 * table_ind)
            for group_ind, group in enumerate(table['groups']):
                group_widget: Table = table_widget.itemAt(group_ind).widget()
                for row_ind, row in enumerate(group['rows']):
                    for column in range(group_widget.columnCount()):
                        widget = group_widget.cellWidget(row_ind + 1, column)
                        if widget:
                            widget.set_state('ok')
                    time_start, time_end = parse_time(times[row_ind])
                    if time_start is None:
                        continue
                    classroom = row['classroom']
                    teacher = row['teacher']
                    if time_start < time_end:
                        if classroom:
                            classrooms.append((time_start, 1, classroom, (table_ind, group_ind, row_ind)))
                            classrooms.append((time_end, -1, classroom, (table_ind, group_ind, row_ind)))
                        if teacher:
                            teachers.append((time_start, 1, teacher, (table_ind, group_ind, row_ind)))
                            teachers.append((time_end, -1, teacher, (table_ind, group_ind, row_ind)))
                    else:
                        if classroom:
                            classrooms.append((time_start, 1, classroom, (table_ind, group_ind, row_ind)))
                            classrooms.append((86399, -1, classroom, (table_ind, group_ind, row_ind)))
                            classrooms.append((0, 1, classroom, (table_ind, group_ind, row_ind)))
                            classrooms.append((time_end, -1, classroom, (table_ind, group_ind, row_ind)))
                        if teacher:
                            teachers.append((time_start, 1, teacher, (table_ind, group_ind, row_ind)))
                            teachers.append((86399, -1, teacher, (table_ind, group_ind, row_ind)))
                            teachers.append((0, 1, teacher, (table_ind, group_ind, row_ind)))
                            teachers.append((time_end, -1, teacher, (table_ind, group_ind, row_ind)))
        used = {}
        count = {}
        bad = set()
        classrooms.sort()
        teachers.sort()
        for data in (classrooms, teachers):
            for time, tp, name, ind in data:
                if tp == 1:
                    if name in used:
                        bad.add(ind)
                        bad.add(used[name])
                    used[name] = ind
                    if name not in count:
                        count[name] = 1
                    else:
                        count[name] += 1
                else:
                    count[name] -= 1
                    if count[name] == 0:
                        used.pop(name)
        for table_ind, group_ind, row_ind in bad:
            table: RowWithTablesLayout = self.layout.itemAt(2 * table_ind)
            group: Table = table.itemAt(group_ind).widget()
            for column in range(group.columnCount()):
                widget = group.cellWidget(row_ind + 1, column)
                if widget:
                    widget.set_state('collision')
