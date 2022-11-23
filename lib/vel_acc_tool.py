from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class VelAccTool(QDialog):
    def __init__(self, parent=None):
        super(VelAccTool, self).__init__(parent)

        self.setWindowTitle('Velocity and Acceleration')
