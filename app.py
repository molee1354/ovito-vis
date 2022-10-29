import os
import re
import sys
import json
from random import shuffle

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QApplication, QMainWindow,
    QPushButton, QLineEdit, QWidget, QLabel)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Simulation Player")
        self.setFixedSize( QSize(800,600) )
        self.w = None
        
        # layouts
        view_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        self.files_list = self.generate_file()
        self.file = next(self.files_list)
        self.handle = re.findall("[A-Za-z0-9]+_[A-Za-z0-9]+_",
                            re.findall("[A-Za-z0-9]+_[A-Za-z0-9]+_V[0-9]+\.?[0-9]+_A[0-9]+",
                            self.file)[0])[0]
        self.viewport = self.ovito_viewport(self.file)

        self.progress_text = "Progress : " \
                             f"{self.cur_file}/{self.total_files}"
        self.progress = QLabel(self.progress_text)
        self.progress.setFixedHeight(20)
        sim_window = self.viewport.create_qt_widget()

        buttons_oper = ["|<","<","play","play.5","pause",">",">|"]
        buttons = [self.create_button(b) for b in buttons_oper]

        self.inputbox = QLineEdit()
        self.inputbox.setFixedWidth(100)
        self.inputbox.setMaxLength(4)
        self.inputbox.setPlaceholderText("Behavior")
        self.inputbox.returnPressed.connect(self.return_pressed)

        view_layout.addWidget(self.progress)
        view_layout.addWidget(sim_window)
        for button in buttons:
            input_layout.addWidget(button)
        input_layout.addWidget(self.inputbox)
        sim_window.destroyed.connect(QApplication.instance().quit)

        view_layout.addLayout(input_layout)

        widget = QWidget()
        widget.setLayout(view_layout)
        self.setCentralWidget(widget)

        self.behaviors = {}

    def generate_file(self) -> str:
        try:
            files_dir = sys.argv[1]
        except IndexError:
            files_dir = os.getcwd()
            
        files_list = [ f"{files_dir}\\{f}"
                       for f in os.listdir(files_dir)
                       if "dmp.reg" in f ]
        if len(files_list) < 1:
            print("\nFATAL: Could not find any files in the correct format!")
            exit()
        self.total_files = len(files_list)
        shuffle(files_list)
        for i, file in enumerate(files_list):
            self.cur_file = i+1
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
            self.pipeline = import_file(self.file)
            self.pipeline.add_to_scene()
            self.progress_text = "Progress : " \
                                f"{self.cur_file}/{self.total_files}"
            self.progress.setText(self.progress_text)

            self.viewport.dataset.anim.start_animation_playback(3.)
        except StopIteration:
            self.pipeline.remove_from_scene()
            if self.w is None:
                self.w = SaveWindow(self.behaviors,self.handle)
            self.w.show()

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
        id = re.findall("[V[0-9]+\.?[0-9]+_A[0-9]+",self.file)[0]
        self.behaviors[id] = self.inputbox.text().upper()

        self.inputbox.clear()
        self.reset_viewport()


class SaveWindow(QWidget):
    def __init__(self, data: dict, handles: str) -> None:
        super().__init__()
        self.data = data
        self.handles = handles

        layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        self.label = QLabel("Savefile Name")
        layout.addWidget(self.label)

        self.inputbox = QLineEdit()
        self.inputbox.setFixedWidth(200)
        self.inputbox.setPlaceholderText(f"{self.handles}")
        self.inputbox.returnPressed.connect(self.save_to_json)

        self.ext_label = QLabel(".json")

        self.button = QPushButton("save")
        self.button.setFixedWidth(50)
        self.button.clicked.connect(self.save_to_json)

        input_layout.addWidget(self.inputbox)
        input_layout.addWidget(self.ext_label)
        input_layout.addWidget(self.button)
        layout.addLayout(input_layout)

        self.setLayout(layout)
    
    def save_to_json(self) -> None:
        filename = f"{self.inputbox.text()}.json"
        if len(self.inputbox.text()) < 1:
            filename = f"{self.handles}.json"

        with open(filename,'w') as f:
            json.dump(self.data,f, indent=4)
        exit()



def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
