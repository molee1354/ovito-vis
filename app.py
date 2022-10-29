from email.charset import QP
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
        layout1 = QVBoxLayout()
        layout2 = QHBoxLayout()

        self.files_list = self.generate_file()
        self.file = next(self.files_list)
        self.viewport = self.ovito_viewport(self.file)

        sim_window = self.viewport.create_qt_widget()
        layout1.addWidget(sim_window)
        sim_window.destroyed.connect(QApplication.instance().quit)

        # button = QPushButton("Play")
        # # button.setFixedSize( QSize(200,100))
        # button.setFixedWidth(50)
        # button.clicked.connect(self.play)
        buttons_oper = ["|<","<","play","pause",">",">|"]
        buttons = [self.create_button(b) for b in buttons_oper]

        self.inputbox = QLineEdit()
        self.inputbox.setFixedWidth(100)
        self.inputbox.setMaxLength(4)
        self.inputbox.setPlaceholderText("Behavior")
        self.inputbox.returnPressed.connect(self.return_pressed)

        for button in buttons:
            layout2.addWidget(button)
        layout2.addWidget(self.inputbox)

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

        self.file = next(self.files_list)
        self.pipeline = import_file(self.file)
        self.pipeline.add_to_scene()

        self.viewport.dataset.anim.start_animation_playback(3.)

    def play(self) -> None:
        #TODO self.layout1.removeWidget(self.sim_window)
        #TODO reset simulation on button click
        self.viewport.dataset.anim.start_animation_playback(3.)
    
    def create_button(self, name: str) -> QPushButton:
        out = QPushButton(name)
        out.setFixedWidth(50)

        oper = self.button_operation()
        out.clicked.connect(oper[name])
        return out

    def button_operation(self) -> dict:
        out = {"play" : self.play,
               "pause": self.pause,
               ">"    : self.step_up,
               "<"    : self.step_down,
               "|<"   : self.jump_start,
               ">|"   : self.jump_end}
        return out
    
    def play(self):
        self.viewport.dataset.anim.start_animation_playback(3.)
    def pause(self):
        self.viewport.dataset.anim.stop_animation_playback()
    def step_up(self):
        self.viewport.dataset.anim.jump_to_next_frame()
    def step_down(self):
        self.viewport.dataset.anim.jump_to_previous_frame()
    def jump_start(self):
        self.viewport.dataset.anim.jump_to_animation_start()
    def jump_end(self):
        self.viewport.dataset.anim.jump_to_animation_end()
    
    def return_pressed(self) -> None:
        print(self.inputbox.text())
        self.inputbox.clear()
        self.reset_viewport()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
