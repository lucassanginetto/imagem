#!/usr/bin/env python3

import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea, QFileDialog
)


class MainWindow(QMainWindow):
    image_label: QLabel
    scroll_area: QScrollArea

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Image Viewer')
        self.resize(800, 600)

        self.image_label = QLabel()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.horizontalScrollBar().setStyleSheet('height: 0px;')
        self.scroll_area.verticalScrollBar().setStyleSheet('width: 0px;')

        self.setCentralWidget(self.scroll_area)

        self.statusBar().showMessage('[No image]')

    def open_image(self, path: str) -> None:
        path = os.path.abspath(path)

        if not os.path.exists(path):
            return

        self.image_label.setPixmap(QPixmap(path))
        self.image_label.adjustSize()

        self.setWindowTitle(os.path.basename(path))
        self.statusBar().showMessage(path)

    def file_dialog_path(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Open Image',
            '',
            'Images (*.gif *.jpeg *.jpg *.png *.svg)'
        )
        return path

    # -------------------------------------------------------------------------
    # Event overrides

    def keyPressEvent(self, event: QKeyEvent) -> None:
        match event.key():
            case Qt.Key_O:
                path: str = self.file_dialog_path()
                if path:
                    self.open_image(path)
            case _:
                super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    if len(app.arguments()) > 1:
        window.open_image(app.arguments()[1])

    app.exec()
