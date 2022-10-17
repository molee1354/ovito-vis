import sys, os
from time import sleep
# Future versions of OVITO will use Qt6 & PySide6, older versions use Qt5 & PySide2.
# Please pick the right PySide version for import.
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

myapp = QApplication(sys.argv)

# Note: Import the ovito package AFTER the QApplication object
# has been created. Otherwise, Ovito would automatically create its own 
# QCoreApplication object, which won't let us display GUI widgets.
from ovito.io import import_file
from ovito.vis import Viewport

# Import model and add it to visualization scene.
import local_paths
pipeline = import_file(local_paths.filename)
pipeline.add_to_scene()

# Create a virtual Viewport.
vp = Viewport(type=Viewport.Type.Perspective, camera_dir=(0, 0, -1))
vp.camera_pos = (0.160,0.2,0.55)

# Create a visible GUI widget associated with the viewport.
widget = vp.create_qt_widget()
widget.resize(640, 480)
widget.setWindowTitle("Random Impact Player")
widget.show()
sleep(1.0)
vp.dataset.anim.start_animation_playback(3.)

# Shut down application when the user closes the viewport widget.
widget.destroyed.connect(QApplication.instance().quit)

# sys.exit(myapp.exec_()) 
sys.exit(myapp.exec())
