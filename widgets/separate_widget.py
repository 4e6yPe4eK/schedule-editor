from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt


class SeparatedWidget(QWidget):
    def __init__(self, words_str="", separator='/', *args, **kwargs):
        super(SeparatedWidget, self).__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.separator = separator
        self.words = words_str.split(self.separator)

        first = True

        for word in self.words:
            if not word:
                continue
            if not first:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setLineWidth(1)
                self.layout().addWidget(line)

            label = QLabel()
            label.setText(word)
            label.setAlignment(Qt.AlignCenter)
            self.layout().addWidget(label)
            first = False

    def text(self):
        return self.separator.join(self.words)

    def setText(self, words_str):
        self.words = words_str.split(self.separator)

        first = True

        for word in self.words:
            if not word:
                continue
            if not first:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setLineWidth(1)
                self.layout().addWidget(line)

            label = QLabel()
            label.setText(word)
            label.setAlignment(Qt.AlignCenter)
            self.layout().addWidget(label)
            first = False
