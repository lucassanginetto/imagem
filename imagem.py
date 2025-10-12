#!/usr/bin/env python3

import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea, QFileDialog
)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Image Viewer')
        self.resize(800, 600)

        # Widgets

        self.pixmap_label = QLabel()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.pixmap_label)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.horizontalScrollBar().setStyleSheet('height: 0px;')
        self.scroll_area.verticalScrollBar().setStyleSheet('width: 0px;')

        self.setCentralWidget(self.scroll_area)

        self.statusBar().showMessage('[No image]')

        # Properties

        self.pixmap = QPixmap()

        self.folder_path = ''
        self.folder_files: list[str] = []
        self.file_index = -1

        self.SUPPORTED_EXTS = {'.gif', '.jpeg', '.jpg', '.png', '.svg'}

        self.SCROLL_STEP = 30

    def change_current_file(self, index_increment: int) -> None:
        if not self.folder_files or self.file_index == -1:
            return
        new_index = self.file_index + index_increment
        if 0 <= new_index < len(self.folder_files):
            self.file_index = new_index
            file_path = os.path.join(
                self.folder_path,
                self.folder_files[self.file_index]
            )
            self.load_pixmap_from_file(file_path)

    def file_dialog_path(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Open Image',
            '',
            'Images (*' + ' *'.join(self.SUPPORTED_EXTS) + ')'
        )
        return path

    def load_files_from_folder(self, folder_path: str) -> None:
        files = [
            file for file in os.listdir(folder_path)
            if os.path.splitext(file)[1].lower() in self.SUPPORTED_EXTS
        ]
        files.sort()
        self.folder_files = files

    def load_pixmap_from_file(self, file_path: str) -> None:
        self.pixmap = QPixmap(file_path)
        if self.pixmap.isNull():
            return
        self.update_pixmap_label()

        self.setWindowTitle(os.path.basename(file_path))
        self.statusBar().showMessage(os.path.abspath(file_path))

    def open_folder(self, folder_path: str) -> None:
        self.load_files_from_folder(folder_path)

        if not self.folder_files:
            self.statusBar().showMessage(
                f'[No supported files found in folder "{folder_path}"]'
            )
            return

        file_path = os.path.join(folder_path, self.folder_files[0])
        self.load_pixmap_from_file(file_path)

        self.folder_path = folder_path
        self.file_index = 0

    def open_image(self, file_path: str) -> None:
        folder_path = os.path.dirname(file_path)
        self.load_files_from_folder(folder_path)

        file = os.path.basename(file_path)
        if file not in self.folder_files:
            self.statusBar().showMessage(
                f'[The given file at "{file_path}" isn\'t supported]'
            )
            return

        self.load_pixmap_from_file(file_path)

        self.folder_path = folder_path
        self.file_index = self.folder_files.index(file)

    def update_pixmap_label(self) -> None:
        if self.pixmap:
            self.pixmap_label.setPixmap(self.pixmap)
        self.pixmap_label.adjustSize()

    # -------------------------------------------------------------------------
    # Event overrides

    def keyPressEvent(self, event: QKeyEvent) -> None:
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ControlModifier:
            match event.key():
                case Qt.Key_N:
                    self.statusBar().setHidden(not self.statusBar().isHidden())
                case _:
                    super().keyPressEvent(event)
            return

        if modifiers == Qt.ShiftModifier:
            match event.key():
                case Qt.Key_J:
                    # Go to next file inside folder
                    self.change_current_file(+1)
                case Qt.Key_K:
                    # Go previous file inside folder
                    self.change_current_file(-1)
                case _:
                    super().keyPressEvent(event)
            return

        match event.key():
            case Qt.Key_H | Qt.Key_Left:
                self.scroll_area.horizontalScrollBar().setValue(
                    self.scroll_area.horizontalScrollBar().value()
                    - self.SCROLL_STEP
                )
            case Qt.Key_J | Qt.Key_Down:
                self.scroll_area.verticalScrollBar().setValue(
                    self.scroll_area.verticalScrollBar().value()
                    + self.SCROLL_STEP
                )
            case Qt.Key_K | Qt.Key_Up:
                self.scroll_area.verticalScrollBar().setValue(
                    self.scroll_area.verticalScrollBar().value()
                    - self.SCROLL_STEP
                )
            case Qt.Key_L | Qt.Key_Right:
                self.scroll_area.horizontalScrollBar().setValue(
                    self.scroll_area.horizontalScrollBar().value()
                    + self.SCROLL_STEP
                )

            case Qt.Key_O:
                path = self.file_dialog_path()
                if path:
                    self.load_pixmap_from_file(path)

            case Qt.Key_F11:
                if not self.isFullScreen():
                    self.showFullScreen()
                else:
                    self.showNormal()

            case Qt.Key_Q:
                QApplication.quit()

            case _:
                super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    if len(app.arguments()) > 1:
        path = os.path.abspath(app.arguments()[1])
        if os.path.isdir(path):
            window.open_folder(path)
        elif os.path.isfile(path):
            window.open_image(path)
        else:
            window.statusBar().showMessage(f'[Invalid path "{path}"]')

    app.exec()
