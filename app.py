import os
import sys
from random import shuffle
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
        
        # layouts
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()

        # simulations
        # self.file = f"{local_paths.files_dir}/{random.choice(os.listdir(local_paths.files_dir))}"

        self.files_list = self.generate_file()
        self.file = next(self.files_list)
        self.viewport = self.ovito_viewport(self.file)

        self.sim_window = self.viewport.create_qt_widget()
        layout1.addWidget(self.sim_window)
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

        layout1.addLayout(layout2)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)

    def generate_file(self) -> str:
        files_list = [ f"{local_paths.files_dir}{f}"
                       for f in os.listdir(local_paths.files_dir) ]
        shuffle(files_list)
        for i,file in enumerate(files_list):
            print(i)
            yield file

    def ovito_viewport(self, filename: str):
        from ovito.vis import Viewport
        from ovito.io import import_file

        self.pipeline = import_file(filename)
        self.pipeline.add_to_scene()

        out = Viewport(type=Viewport.Type.Perspective)
        out.camera_dir=(0,0,-1)
        out.camera_pos = (0.16,0.2,0.55)

        return out
    
    def reset_viewport(self) -> None:
        from ovito.io import import_file
        self.pipeline.remove_from_scene()

        # filename = f"{local_paths.files_dir}/{random.choice(os.listdir(local_paths.files_dir))}"
        self.file = next(self.files_list)
        print(self.file)
        self.pipeline = import_file(self.file)
        self.pipeline.add_to_scene()

        self.viewport.dataset.anim.start_animation_playback(3.)

    def play(self) -> None:
        #TODO self.layout1.removeWidget(self.sim_window)
        #TODO reset simulation on button click
        self.viewport.dataset.anim.start_animation_playback(3.)
    
    def return_pressed(self) -> None:
        self.reset_viewport()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
