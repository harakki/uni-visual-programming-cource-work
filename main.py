import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow,
                             QPushButton, QBoxLayout, QVBoxLayout, QHBoxLayout, QTextEdit)

from PyQt6.QtCore import Qt


class PlantCareEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 700, 500
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle('Редактор справочника по растениям')
        self.setStyleSheet('''
                           QWidget {
                               font-size: 17px;
                           }
                           ''')

        self.main_window = QWidget()
        self.layout = QHBoxLayout(self.main_window)
        self.setCentralWidget(self.main_window)

        self.init_ui()
        self.init_cfg_signals()

    def init_ui(self):
        self.md_editor = QTextEdit()
        self.md_viewer = QTextEdit(readOnly=True)

        self.layout.addWidget(self.md_editor)
        self.layout.addWidget(self.md_viewer)

    def init_cfg_signals(self):
        self.md_editor.textChanged.connect(self.md_update)

    def md_update(self):
        self.md_viewer.setMarkdown(self.md_editor.toPlainText())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
                      QWidget {
                          font-size: 14px;
                      }
    ''')

    PlantCareEditor = PlantCareEditor()
    PlantCareEditor.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
