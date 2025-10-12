#!/usr/bin/env python3

import sys
import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QKeyEvent, QWheelEvent
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

        self.zoom_label = QLabel('')
        self.statusBar().addPermanentWidget(self.zoom_label)

        # Properties

        self.pixmap = QPixmap()
        self.zoom: float = 1.0

        self.folder_path = ''
        self.folder_files: list[str] = []
        self.file_index = -1

        self.SUPPORTED_EXTS = {'.gif', '.jpeg', '.jpg', '.png', '.svg'}

        self.SCROLL_STEP = 30

        self.MAX_ZOOM: float = 5.0
        self.ZOOM_IN_FACTOR: float = 1.25
        self.ZOOM_OUT_FACTOR: float = 0.8

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

    def fit_zoom_to_height(self) -> None:
        viewport_height = self.scroll_area.viewport().height()
        pixmap_height = self.pixmap.height()
        if pixmap_height > 0:
            self.set_zoom(viewport_height / pixmap_height)

    def fit_zoom_to_width(self) -> None:
        viewport_width = self.scroll_area.viewport().width()
        pixmap_width = self.pixmap.width()
        if pixmap_width > 0:
            self.set_zoom(viewport_width / pixmap_width)

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

        self.set_zoom(1.0)
        self.update_zoom_label()

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

    def set_zoom(self, zoom: float) -> None:
        if not self.pixmap:
            return

        if zoom > self.MAX_ZOOM:
            return

        if QSize.isEmpty(self.pixmap.size() * zoom):
            return

        hbar = self.scroll_area.horizontalScrollBar()
        vbar = self.scroll_area.verticalScrollBar()

        old_hval = hbar.value()
        old_vval = vbar.value()

        old_pixmap_size = self.pixmap_label.pixmap().size()
        if old_pixmap_size.isEmpty():
            return

        viewport = self.scroll_area.viewport()

        center_point = viewport.rect().center()

        rel_x: float = (old_hval + center_point.x()) / old_pixmap_size.width()
        rel_y: float = (old_vval + center_point.y()) / old_pixmap_size.height()

        self.zoom = zoom
        self.update_pixmap_label()
        self.update_zoom_label()

        new_pixmap_size = self.pixmap_label.pixmap().size()

        new_hval: float = rel_x * new_pixmap_size.width() - center_point.x()
        new_vval: float = rel_y * new_pixmap_size.height() - center_point.y()

        hbar.setValue(int(new_hval))
        vbar.setValue(int(new_vval))

    def update_pixmap_label(self) -> None:
        if self.pixmap:
            new_size = self.zoom * self.pixmap.size()
            scaled_pixmap = self.pixmap.scaled(
                new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.pixmap_label.setPixmap(scaled_pixmap)
        self.pixmap_label.adjustSize()

    def update_zoom_label(self) -> None:
        self.zoom_label.setText(f'{int(self.zoom * 100)}%')

    def zoom_in(self) -> None:
        self.set_zoom(self.zoom * self.ZOOM_IN_FACTOR)

    def zoom_out(self) -> None:
        self.set_zoom(self.zoom * self.ZOOM_OUT_FACTOR)

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

            case Qt.Key_Plus:
                self.zoom_in()
            case Qt.Key_Minus:
                self.zoom_out()
            case Qt.Key_Equal:
                self.set_zoom(1.0)

            case Qt.Key_A:
                self.fit_zoom_to_height()
            case Qt.Key_S:
                self.fit_zoom_to_width()

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

    def wheelEvent(self, event: QWheelEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)


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
