import os
import re
import sys
import json
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
        view_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        self.files_list = self.generate_file()
        self.file = next(self.files_list)
        self.viewport = self.ovito_viewport(self.file)

        sim_window = self.viewport.create_qt_widget()
        view_layout.addWidget(sim_window)
        sim_window.destroyed.connect(QApplication.instance().quit)

        buttons_oper = ["|<","<","play","play.5","pause",">",">|"]
        buttons = [self.create_button(b) for b in buttons_oper]

        self.inputbox = QLineEdit()
        self.inputbox.setFixedWidth(100)
        self.inputbox.setMaxLength(4)
        self.inputbox.setPlaceholderText("Behavior")
        self.inputbox.returnPressed.connect(self.return_pressed)

        for button in buttons:
            input_layout.addWidget(button)
        input_layout.addWidget(self.inputbox)

        view_layout.addLayout(input_layout)

        widget = QWidget()
        widget.setLayout(view_layout)
        self.setCentralWidget(widget)

        self.behaviors = {}

    def generate_file(self) -> str:
        files_list = [ f"{local_paths.files_dir}{f}"
                       for f in os.listdir(local_paths.files_dir)
                       if "dmp.reg" in f ]
        shuffle(files_list)
        for file in files_list[:5]:
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

        try:
            self.file = next(self.files_list)
        except StopIteration:
            print(self.behaviors)
            with open("behaviors.json", 'w') as f:
                json.dump(self.behaviors,f, indent=4)
            exit()

        self.pipeline = import_file(self.file)
        self.pipeline.add_to_scene()

        self.viewport.dataset.anim.start_animation_playback(3.)

    def play(self) -> None:
        #TODO self.view_layout.removeWidget(self.sim_window)
        #TODO reset simulation on button click
        self.viewport.dataset.anim.start_animation_playback(3.)
    
    def create_button(self, name: str) -> QPushButton:
        out = QPushButton(name)
        out.setFixedWidth(50)

        oper = self.button_operation()
        out.clicked.connect(oper[name])
        return out

    def button_operation(self) -> dict:
        out = {"play"  : self.play,
               "play.5": self.playslow,
               "pause" : self.pause,
               ">"     : self.step_up,
               "<"     : self.step_down,
               "|<"    : self.jump_start,
               ">|"    : self.jump_end}
        return out
    
    def play(self) -> None:
        self.viewport.dataset.anim.start_animation_playback(3.)
    def playslow(self) -> None:
        self.viewport.dataset.anim.start_animation_playback(0.5)
    def pause(self) -> None:
        self.viewport.dataset.anim.stop_animation_playback()
    def step_up(self) -> None:
        self.viewport.dataset.anim.jump_to_next_frame()
    def step_down(self) -> None:
        self.viewport.dataset.anim.jump_to_previous_frame()
    def jump_start(self) -> None:
        self.viewport.dataset.anim.jump_to_animation_start()
    def jump_end(self) -> None:
        self.viewport.dataset.anim.jump_to_animation_end()
    
    def return_pressed(self) -> None:
        behavior = self.inputbox.text()
        if behavior.upper() not in ["FS","RC","RO"]:
            self.inputbox.clear()
            return
        print(self.inputbox.text())
        id = re.findall("V[0-9]+\.?[0-9]+_A[0-9]+",self.file)[0]
        self.behaviors[id] = self.inputbox.text().upper()

        self.inputbox.clear()
        self.reset_viewport()
        print(self.file)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
