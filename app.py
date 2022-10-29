import os
import sys
import random

import local_paths

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QApplication, QMainWindow,
    QPushButton, QLineEdit, QWidget)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Simulation Player")
        self.setFixedSize( QSize(800,600) )
        self.layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()

        self.file = f"{local_paths.files_dir}/{random.choice(os.listdir(local_paths.files_dir))}"
        self.viewport = self.ovito_viewport(self.file)

        self.sim_window = self.viewport.create_qt_widget()
        self.layout1.addWidget(self.sim_window)
        self.sim_window.destroyed.connect(QApplication.instance().quit)

        button = QPushButton("Button")
        button.setFixedSize( QSize(200,100))
        button.clicked.connect(self.play)

        inputbox = QLineEdit()
        inputbox.setFixedWidth(100)
        inputbox.setMaxLength(4)
        inputbox.setPlaceholderText("Behavior")
        inputbox.returnPressed.connect(self.return_pressed)
        layout2.addWidget(button)
        layout2.addWidget(inputbox)

        self.layout1.addLayout(layout2)

        widget1 = QWidget()
        widget1.setLayout(self.layout1)
        self.setCentralWidget(widget1)

    def ovito_viewport(self, filename: str):
        from ovito.io import import_file
        from ovito.vis import Viewport

        pipeline = import_file(filename)
        pipeline.add_to_scene()

        out = Viewport(type=Viewport.Type.Perspective)
        out.camera_dir=(0,0,-1)
        out.camera_pos = (0.16,0.2,0.55)

        return out

    def play(self) -> None:
        #TODO self.layout1.removeWidget(self.sim_window)
        #TODO reset simulation on button click
        self.viewport.dataset.anim.start_animation_playback(3.)
    
    def return_pressed(self) -> None:
        print("return pressed")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
