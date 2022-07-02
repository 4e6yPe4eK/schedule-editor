import ctypes
import json
import sys
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QAction, QMessageBox)
from PyQt5.QtCore import QFile

from widgets import WidgetForScrolling


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.load_ui()
        self.load_menu()

        self.filename = None
        self.last_data = self.dump_data()
        with open('./style.qss') as style_file:
            self.setStyleSheet(style_file.read())

    def load_ui(self):
        self.setWindowTitle("Редактор расписания")
        self.resize(1000, 800)

        self.setCentralWidget(WidgetForScrolling())

        self.statusBar().messageChanged.connect(self.statusbar_changed)
        self.statusBar().hide()

    def statusbar_changed(self, message):
        if not message:
            self.statusBar().hide()
            return
        self.statusBar().show()

    def load_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")

        create_file_action = QAction("Создать", self)
        create_file_action.setShortcut("Ctrl+N")
        create_file_action.triggered.connect(self.create_file)

        open_file_action = QAction("Открыть...", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file)

        save_file_action = QAction("Сохранить", self)
        save_file_action.setShortcut("Ctrl+S")
        save_file_action.triggered.connect(self.save_file)

        save_as_file_action = QAction("Сохранить как...", self)
        save_as_file_action.setShortcut("Ctrl+Shift+S")
        save_as_file_action.triggered.connect(self.save_as_file)

        file_menu.addAction(create_file_action)
        file_menu.addAction(open_file_action)
        file_menu.addAction(save_file_action)
        file_menu.addAction(save_as_file_action)

    def save_as_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        filename, trash = dialog.getSaveFileName(filter="Расписание (*.json)")
        if not filename:
            return False
        self.filename = filename
        data = self.dump_data()
        json.dump(data, open(filename, 'w', encoding="UTF-8"))
        self.last_data = data
        self.statusBar().showMessage("Сохранено", 3000)
        return True

    def save_file(self):
        if not self.filename:
            return self.save_as_file()
        data = self.dump_data()
        json.dump(data, open(self.filename, 'w', encoding="UTF-8"))
        self.last_data = data
        self.statusBar().showMessage("Сохранено", 3000)
        return True

    def create_file(self):
        canceled = self.save_if_changed()
        if canceled:
            return False
        self.setCentralWidget(WidgetForScrolling())
        self.last_data = self.dump_data()
        self.filename = None
        return True

    def open_file(self):
        canceled = self.save_if_changed()
        if canceled:
            return False
        filename, trash = QFileDialog.getOpenFileName(filter="Расписание (*.json)")
        if not filename:
            return False
        self.filename = filename
        data = json.load(open(filename, encoding='UTF-8'))
        schedule = data['schedule']
        self.setCentralWidget(WidgetForScrolling(schedule))
        self.last_data = self.dump_data()
        return True

    def save_if_changed(self):
        data = self.dump_data()
        if data != self.last_data:
            dialog = QMessageBox()
            dialog.setWindowTitle("Сохранение")
            dialog.setText("Вы хотите сохранить изменения в файле?")
            dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            save_btn = dialog.button(QMessageBox.Save)
            save_btn.setText("Сохранить")

            discard_btn = dialog.button(QMessageBox.Discard)
            discard_btn.setText("Не сохранять")

            cancel_btn = dialog.button(QMessageBox.Cancel)
            cancel_btn.setText('Отмена')

            ret = dialog.exec_()
            if ret == QMessageBox.Save:
                return not self.save_file()
            elif ret == QMessageBox.Cancel:
                return True
        return False

    def get_config(self):
        return {}

    def dump_data(self):
        return {
            "schedule": self.centralWidget().dump_data(),
            "config": self.get_config()
        }

    def closeEvent(self, event) -> None:
        cancel = self.save_if_changed()
        if cancel:
            event.ignore()
            return
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())