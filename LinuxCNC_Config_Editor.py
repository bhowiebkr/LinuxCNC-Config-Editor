import sys
import logging
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

from lib.linuxcnc_config import LinuxCNCConfig
from lib.linuxcnc_doc_reader import LinuxCNCDocs
from lib.vel_acc_tool import VelAccTool


DEBUG = False

Docs = LinuxCNCDocs()


class TableModel(QAbstractTableModel):
    def __init__(self, data, section):
        super(TableModel, self).__init__()

        self.horizontalHeaders = [""] * 3
        self.setHeaderData(0, Qt.Horizontal, "Variable")
        self.setHeaderData(1, Qt.Horizontal, "Value")
        self.setHeaderData(2, Qt.Horizontal, "Comment")

        self._data = data
        self.section = section
        self.clean_section = self.section[1:-1].split("_")[0]  # just get the main name

    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except:
                pass
        return super().headerData(section, orientation, role)

    def data(self, index, role):
        if index.isValid():

            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self._data.get_variables(self.section)[index.row()][
                    index.column()
                ]

            elif role == Qt.TextAlignmentRole:
                if index.column() == 0:
                    return Qt.AlignVCenter | Qt.AlignRight
                elif index.column() == 1:
                    return Qt.AlignCenter
                elif index.column() == 2:
                    return Qt.AlignVCenter | Qt.AlignLeft

            elif role == Qt.ToolTipRole:
                variable = self._data.get_variables(self.section)[index.row()][0]
                tip = Docs.get_variable_docs(self.clean_section, variable)
                return tip

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            variable = self._data.get_variables(self.section)[index.row()][
                index.column() - 1
            ]
            self._data.edit_variable(self.section, variable, value)
            return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def rowCount(self, index):
        return len(self._data.get_variables(self.section))

    def columnCount(self, index):
        return 3


class SectionTab(QWidget):
    def __init__(self, name, config, parent=None):
        super(SectionTab, self).__init__(parent)
        self.name = name
        self.config = config

        self.model = TableModel(self.config, section=name)

        # layouts
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Widgets
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        clean_name = self.name[1:-1].split("_")[0]  # just get the main name
        # self.description = QLabel(Docs.get_section_doc(section=clean_name))
        self.description = QWebEngineView()
        # self.description.setWordWrap(True)
        html = Docs.get_section_doc(section=clean_name)
        local_url = QUrl.fromLocalFile(os.path.realpath(__file__))
        print("local URL:", local_url)
        self.description.setHtml(html, local_url)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.verticalHeader().setVisible(False)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.horizontalHeader().setStretchLastSection(True)

        # add widgets
        main_layout.addWidget(self.splitter)
        self.splitter.addWidget(self.description)
        self.splitter.addWidget(self.table)
        self.splitter.setSizes([30,3])


        # self.load_values()

    @staticmethod
    def nice_name(name):
        return name[1:-1].replace("_", " ")

    def get_nice_name(self):
        return self.nice_name(self.name)


class Editor(QMainWindow):
    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)
        self.setWindowTitle("LinuxCNC Config Editor")

        self.workingFolder = None

        self.settings = QSettings("LinuxCNC_Config_Editor", "LinuxCNC_Config_Editor")
        self.config = None

        # Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        data_layout = QVBoxLayout()

        try:
            self.restoreGeometry(self.settings.value("geometry"))
            self.workingFolder = self.settings.value('working_folder')
            #print(f'working folder set to: {self.workingFolder}')

        except Exception as e:
            logging.warning(
                "Unable to load settings. First time opening the tool?\n" + str(e)
            )

        # Widgets
        self.tabs = QTabWidget()
        self.filter_line = QLineEdit()
        filter_Layout = QHBoxLayout()
        filter_Layout.addWidget(QLabel("Filter Sections"))
        filter_Layout.addWidget(self.filter_line)

        # Menu
        file_menu = self.menuBar().addMenu('File')

        file_actions = []
        open = QAction('Open', self)
        open.triggered.connect(self.load_config)
        file_actions.append(open)

        save = QAction('Save', self)
        save.triggered.connect(self.save_config)
        file_actions.append(save)

        exit = QAction('Exit', self)
        exit.triggered.connect(self.close)
        file_actions.append(exit)

        file_menu.addActions(file_actions)

        tool_menu = self.menuBar().addMenu('Tools')
        tool_actions = []
        velocity_acceleration = QAction('Velocity and Acceleration', self)
        velocity_acceleration.triggered.connect(self.vel_acc_tool)
        tool_actions.append(velocity_acceleration)

        tool_menu.addActions(tool_actions)


        # Add Widgets
        main_layout.addLayout(data_layout)
        data_layout.addLayout(filter_Layout)
        data_layout.addWidget(self.tabs)

        self.filter_line.textChanged.connect(self.upate_section_filter)

        if DEBUG:
            self.load_config()

    def vel_acc_tool(self):
        vel_tool = VelAccTool()
        vel_tool.exec()

    def upate_section_filter(self):
        f = self.filter_line.text().upper().split(",")
        f = [x.strip() for x in f]
        self.build_tabs(filter=f)

    def save_config(self):

        if DEBUG:
            self.config.write(
                save_path=os.path.join("example_config", "cnc_machine_DEBUG.ini")
            )

        else:

            if self.workingFolder:
                root = self.workingFolder
            else:
                root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dialog = QFileDialog.getSaveFileName(
                self,
                "Save Config File",
                root,
                "LinuxCNC Config File (*.INI)",
            )
            save_path = dialog[0]
            if not save_path:
                return

            self.config.write(save_path=save_path)

    def load_config(self):

        # Open the configuration file
        if DEBUG:
            self.config = LinuxCNCConfig(
                os.path.join("example_config", "cnc_machine.ini")
            )

        else:

            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if os.path.exists(self.workingFolder):
                root = self.workingFolder
            dialog = QFileDialog.getOpenFileName(
                self,
                "Open Config File",
                root,
                "LinuxCNC Config File (*.INI)",
            )
            config_path = dialog[0]
            self.config = LinuxCNCConfig(config_path)
            self.workingFolder = os.path.dirname(config_path)
            #print(f'working folder {self.workingFolder}')

        # Build the GUI
        self.build_tabs(filter="")

    def build_tabs(self, filter):
        if not self.config:
            return

        self.tabs.clear()
        for section in self.config.sections():
            if not filter:
                tab = SectionTab(name=section, config=self.config)
                self.tabs.addTab(tab, tab.get_nice_name())
                continue

            nice_name = SectionTab.nice_name(section)

            for f in filter:
                if f in nice_name:
                    tab = SectionTab(name=section, config=self.config)
                    self.tabs.addTab(tab, tab.get_nice_name())

    def closeEvent(self, event):
        self.settings = QSettings("LinuxCNC_Config_Editor", "LinuxCNC_Config_Editor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue('working_folder', self.workingFolder)
        #print(f'saving working folder: {self.workingFolder}')
        QWidget.closeEvent(self, event)


def main():
    app = QApplication(sys.argv)
    editor = Editor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
