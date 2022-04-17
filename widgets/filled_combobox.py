from PyQt5.QtWidgets import QComboBox


class FilledComboBox(QComboBox):
    def __init__(self, suggestions, *args, **kwargs):
        super(FilledComboBox, self).__init__(*args, **kwargs)
        self.setObjectName("FilledComboBox")
        self.addItems(suggestions)
