import sys

import local_paths

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QApplication, QMainWindow, QPushButton, QWidget)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Simulation Player")
        self.setFixedSize( QSize(800,600) )
        layout = QHBoxLayout()

        self.viewport = self.ovito_viewport(local_paths.bennus)

        self.sim_window = self.viewport.create_qt_widget()
        button = QPushButton("Button")
        button.setFixedSize( QSize(200,100))

        layout.addWidget(self.sim_window)
        layout.addWidget(button)

        widg = QWidget()
        widg.setLayout(layout)
        self.setCentralWidget(widg)
        # self.setCentralWidget(self.widget)

    def ovito_viewport(self, filename: str):
        from ovito.io import import_file
        from ovito.vis import Viewport

        pipeline = import_file(filename)
        pipeline.add_to_scene()

        out = Viewport(type=Viewport.Type.Perspective, camera_dir=(0,0,-1))
        out.camera_pos = (0.16,0.2,0.55)

        return out

    def do(self) -> None:
        self.sim_window.show()
        
        self.viewport.dataset.anim.start_animation_playback(3.)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()

    window.do()
    # window.widget.resize(640,480)
    # window.widget.setWindowTitle("Random Impact Player")
    # window.widget.show()
    
    # window.vp.dataset.anim.start_animation_playback(3.)

    window.show()

    app.exec()

if __name__ == "__main__":
    main()
