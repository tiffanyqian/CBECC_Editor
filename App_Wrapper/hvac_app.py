import sys, re
import xml.etree.ElementTree as ET
import hvac_scripts as hvac
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QWidget
)

class MainWindow(QMainWindow):
    def __init__(self):
        global cbecc_file, ET_tree, ET_root, TZ_list, AS_list, ZS_list
        TZ_list = []
        AS_list = []
        ZS_list = []

        super().__init__()
        self.setWindowTitle("2022 CBECC Mechanical System Creator")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        frame_layout = QVBoxLayout()
        folder_layout = QGridLayout()
        grid_layout = QGridLayout()

        # TOP MOST LABELS
        labtitle = QLabel("CBECC 2022 HVAC Generator")
        font_labtitle = labtitle.font()
        font_labtitle.setPointSize(24)
        font_labtitle.setBold(True)
        labtitle.setFont(font_labtitle)
        labtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(labtitle)

        # File Select
        folder_select = QPushButton("Select File")
        folder_select.clicked.connect(self.open_file_clicked)
        folder_select.setFixedSize(250,25)
        folder_layout.addWidget(folder_select,0,0)
        self.curr_folder = QLabel("No File Selected")
        font_curr_folder = self.curr_folder.font()
        font_curr_folder.setItalic(True)
        self.curr_folder.setFont(font_curr_folder)
        self.curr_folder.setMinimumHeight(50)
        self.curr_folder.setWordWrap(True)
        self.curr_folder.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        folder_layout.addWidget(self.curr_folder,1,0)

        # blank_lab = QLabel("")
        # blank_lab.setFixedWidth(25)
        # folder_layout.addWidget(blank_lab,0,1)

        lab_out = QLabel("Enter Output Filename:")
        lab_out.setFixedSize(250,25)
        folder_layout.addWidget(lab_out,0,2)
        self.f_output = QLineEdit()
        self.f_output.setEnabled(False)
        self.f_output.setFixedSize(250,25)
        # self.f_output.textChanged.connect(self.in_f_changed)
        folder_layout.addWidget(self.f_output,1,2)
        folder_layout.setContentsMargins(50,50,50,0)
        frame_layout.addLayout(folder_layout)

        # Thermal Zone List Reference
        TZ_label = QLabel("ThermalZones on File:")
        grid_layout.addWidget(TZ_label,1,0)
        self.TZ_widget = QListWidget()
        self.TZ_widget.addItems(TZ_list)
        self.TZ_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        grid_layout.addWidget(self.TZ_widget,2,0,4,1)
        # Air System List Reference
        AS_label = QLabel("AirSystems on File:")
        grid_layout.addWidget(AS_label,1,1)
        self.AS_widget = QListWidget()
        self.AS_widget.addItems(AS_list)
        self.AS_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        grid_layout.addWidget(self.AS_widget,2,1)
        # Zone System List Reference
        ZS_label = QLabel("ZoneSystems on File:")
        grid_layout.addWidget(ZS_label,1,2)
        self.ZS_widget = QListWidget()
        self.ZS_widget.addItems(ZS_list)
        self.ZS_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        grid_layout.addWidget(self.ZS_widget,2,2)

        # Create Multi Zone AirSys Button
        self.create_mz_as_button = QPushButton("Create Multi-Zone AirSystem\n(DOAS, VAV, PVAV)")
        grid_layout.addWidget(self.create_mz_as_button,3,1)
        self.create_mz_as_button.setEnabled(False)
        self.create_mz_as_button.clicked.connect(self.create_mz_as_button_clicked)

        # Create Single Zone AirSys Button
        self.create_sz_as_button = QPushButton("Create Single Zone AirSystem\n(SZHP, SZAC, SZVAVHP, SZVAVAC, Exhaust)")
        grid_layout.addWidget(self.create_sz_as_button,4,1)
        self.create_sz_as_button.setEnabled(False)
        self.create_sz_as_button.clicked.connect(self.create_sz_as_button_clicked)

        # Create Zone System Button
        self.create_sz_zs_button = QPushButton("Create ZoneSystem\n(SZHP, FPFC, VRF, Exhaust, etc.)")
        grid_layout.addWidget(self.create_sz_zs_button,3,2)
        self.create_sz_zs_button.setEnabled(False)
        self.create_sz_zs_button.clicked.connect(self.create_sz_zs_button_clicked)

        grid_layout.setContentsMargins(50,20,50,50)
        frame_layout.addLayout(grid_layout)

        # RUN BUTTON
        self.run_button = QPushButton("Save Changes")
        self.run_button.setFixedHeight(50)
        frame_layout.addWidget(self.run_button)
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.run_button_clicked)

        frame_layout.setContentsMargins(100,50,100,50)
        central_widget.setLayout(frame_layout)

    def open_file_clicked(self):
        global cbecc_file, ET_tree, ET_root, TZ_list, AS_list, ZS_list
        ET_root = 0

        # Clearing inputs / lists
        self.curr_folder.setText("No File Selected")
        self.f_output.setText("")
        self.f_output.setEnabled(False)
        self.run_button.setEnabled(False)
        self.create_sz_as_button.setEnabled(False)
        self.create_sz_zs_button.setEnabled(False)
        self.create_mz_as_button.setEnabled(False)
        TZ_list = []
        AS_list = []
        ZS_list = []

        # Taking in the new CBECC file
        cbecc_file = ""
        cbecc_file, end_discard = QFileDialog.getOpenFileName(self, "Select File",r"C://","2022 CBECC Files (*.cibd22x)")

        # Loading stuff in
        if len(cbecc_file) != 0:
            if re.search(".cibd22x",cbecc_file):
                self.curr_folder.setText(cbecc_file)
                self.f_output.setText(re.findall(r".*/(.*$)",cbecc_file)[0])
                
                self.f_output.setEnabled(True)
                self.create_sz_as_button.setEnabled(True)
                self.create_mz_as_button.setEnabled(True)
                self.create_sz_zs_button.setEnabled(True)

                ET_tree = ET.parse(cbecc_file)
                ET_root = ET_tree.getroot()
        
        self.TZ_widget.clear()
        if ET_root != 0:
            for tz in ET_root.findall(".//ThrmlZn"):
                if tz[1].text == "Conditioned":
                    TZ_list.append(tz[0].text)
            self.TZ_widget.addItems(TZ_list)
            self.update_lists()

    def update_lists(self):
        global TZ_list, AS_list, ZS_list, ET_root

        self.AS_widget.clear()
        self.ZS_widget.clear()
        
        for airsys in ET_root.findall(".//AirSys"):
            AS_list.append(airsys[0].text)
        for zs in ET_root.findall(".//ZnSys"):
            ZS_list.append(zs[0].text)

        self.AS_widget.addItems(AS_list)
        self.ZS_widget.addItems(ZS_list)

    def create_sz_as_button_clicked(self):
        dlg = SZ_AS_Dialog()
        dlg.setWindowTitle("Single Zone AirSystem Creation")
        if dlg.exec():
            print("Completed Single Zone AirSystem Creation")
            self.update_lists()
            self.run_button.setEnabled(True)
        else:
            print("Canceled Single Zone AirSystem Creation")

    def create_mz_as_button_clicked(self):
        dlg = MZ_AS_Dialog()
        dlg.setWindowTitle("Multi-Zone AirSystem Creation")
        if dlg.exec():
            print("Completed Multi-Zone AirSystem Creation")
            self.update_lists()
            self.run_button.setEnabled(True)
        else:
            print("Canceled Multi-Zone AirSystem Creation")

    def create_sz_zs_button_clicked(self):
        dlg = SZ_ZS_Dialog()
        dlg.setWindowTitle("Single Zone ZoneSystem Creation")
        if dlg.exec():
            print("Completed Single Zone ZoneSystem Creation")
            self.update_lists()
            self.run_button.setEnabled(True)
        else:
            print("Canceled Single Zone ZoneSystem Creation")

    def run_button_clicked(self):
        global cbecc_file, ET_tree

        output_filename = str(re.findall(r"(.*/).*$",cbecc_file)[0]) + self.f_output.text()
        
        hvac.save_changes(ET_tree, output_filename)
        print("File saved to:", output_filename)

class SZ_AS_Dialog(QDialog):
    global TZ_list, ET_root
    def __init__(self):
        super().__init__()
        
        self.tz_list = TZ_list

        layout = QGridLayout()

        layout.addWidget(QLabel("Select Type:"),0,0)
        self.sz_as_type = QComboBox()
        self.sz_as_type.addItems(["SZHP","SZAC","SZVAVHP","SZVAVAC","Exhaust"])
        self.sz_as_type.currentTextChanged.connect(self.type_changed)
        layout.addWidget(self.sz_as_type,1,0)

        self.tab = QTabWidget(self)

        # SZHP, SZAC, SZVAVHP, SZVAVAC Specifics
        self.sz_hp_ac_tab = QWidget()
        sz_hp_ac_layout = QGridLayout()
        self.sz_hp_ac_tab.setLayout(sz_hp_ac_layout)
        sz_hp_ac_layout.addWidget(QLabel("Supply AirSegment"),1,0)
        sz_hp_ac_layout.addWidget(QLabel("\tCoilCooling: "),2,0)
        self.sz_hp_ac_CC_box = QComboBox()
        self.sz_hp_ac_CC_box.addItems(["DirectExpansion","ChilledWater","VRF"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_CC_box,2,1)
        sz_hp_ac_layout.addWidget(QLabel("\tCoilHeating: "),3,0)
        self.sz_hp_ac_CH_box = QComboBox()
        self.sz_hp_ac_CH_box.addItems(["HeatPump","HotWater","Resistance","VRF"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_CH_box,3,1)
        sz_hp_ac_layout.addWidget(QLabel("\tFan: "),4,0)
        self.sz_hp_ac_s_fan_box = QComboBox()
        self.sz_hp_ac_s_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_s_fan_box,4,1)
        sz_hp_ac_layout.addWidget(QLabel("Return AirSegment"),5,0)
        sz_hp_ac_layout.addWidget(QLabel("\tFan: "),6,0)
        self.sz_hp_ac_r_fan_box = QComboBox()
        self.sz_hp_ac_r_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_r_fan_box,6,1)
        sz_hp_ac_layout.addWidget(QLabel("OutsideAirControl"),7,0)
        self.sz_hp_ac_oac_box = QComboBox()
        self.sz_hp_ac_oac_box.addItems(["DifferentialDryBulb","FixedDryBulb","NoEconomizer","DifferentialEnthalpy","DifferentialDryBulbAndEnthalpy"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_oac_box,7,1)

        # Exhaust Specifics
        self.exh_tab = QWidget()
        exh_layout = QGridLayout()
        self.exh_tab.setLayout(exh_layout)
        exh_layout.addWidget(QLabel("Exhaust System Control:"),0,0)
        self.exh_sys_ctrl = QComboBox()
        self.exh_sys_ctrl.addItems(["-- DEFAULT --","VariableFlowVariableSpeedFan","VariableFlowConstantSpeedFan","ConstantFlowConstantSpeedFan"])
        exh_layout.addWidget(self.exh_sys_ctrl,0,1)
        exh_layout.addWidget(QLabel("Exhaust AirSegment"),1,0)
        exh_layout.addWidget(QLabel("\tFan:"),2,0)
        self.exh_fan_box = QComboBox()
        self.exh_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        exh_layout.addWidget(self.exh_fan_box,2,1)

        self.tab.addTab(self.sz_hp_ac_tab, "Edit Specifics")
        self.tab.addTab(self.exh_tab, "Edit Specifics")
        self.tab.setTabVisible(0,True)
        self.tab.setTabVisible(1,False)
        layout.addWidget(self.tab,2,0,1,2)

        wip_label = QLabel("*** NOTE ***\nSystems including HotWater, ChilledWater, VRF, etc. currently require\nmanual connection to Fluid Segments/VRF systems in CBECC")
        layout.addWidget(wip_label,3,0,1,1)
        
        layout.addWidget(QLabel("Select Thermal Zones to create AirSystems for:"),0,2)
        self.widget_tz = QListWidget()
        self.widget_tz.addItems(self.tz_list)
        self.widget_tz.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.widget_tz.itemSelectionChanged.connect(self.tz_selection_changed)
        layout.addWidget(self.widget_tz,1,2,7,1)

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.clicked.connect(self.button_clicked)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout.addWidget(self.buttonBox,9,2)

        self.setLayout(layout)

    def type_changed(self, s):
        # print(s)
        if s == "SZHP" or s == "SZAC" or s == "SZVAVHP" or s == "SZVAVAC":
            self.tab.setTabVisible(0,True)
            self.tab.setTabVisible(1,False)
            self.tab.setCurrentWidget(self.sz_hp_ac_tab)
        elif s == "Exhaust":
            self.tab.setTabVisible(0,False)
            self.tab.setTabVisible(1,True)
            self.tab.setCurrentWidget(self.exh_tab)

    def tz_selection_changed(self):
        if len(self.widget_tz.selectedItems()) > 0:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def button_clicked(self, button):
        global ET_root, ET_tree

        role = self.buttonBox.standardButton(button)

        if role == QDialogButtonBox.StandardButton.Cancel:
            self.buttonBox.rejected.connect(self.reject)
        elif role == QDialogButtonBox.StandardButton.Ok:
            sz_type = self.sz_as_type.currentText()
            bldg = ET_root.findall(".//Bldg")[0]

            self.tz_list = [x.text() for x in self.widget_tz.selectedItems()]
            print("SELECTED THERMAL ZONES:", self.tz_list)

            if sz_type == "SZHP" or sz_type == "SZAC" or sz_type == "SZVAVHP" or sz_type == "SZVAVAC":
                for tz in ET_root.findall(".//ThrmlZn"):
                    if tz[0].text in self.tz_list:
                        hvac.SZ_HP_AC_VAV(bldg, tz, cc=self.sz_hp_ac_CC_box.currentText(), ch=self.sz_hp_ac_CH_box.currentText(), oac=self.sz_hp_ac_oac_box.currentText(),
                        fan_in=self.sz_hp_ac_s_fan_box.currentText(), fan_out=self.sz_hp_ac_r_fan_box.currentText(), sz_as_type = sz_type)
                # TESTING OUTPUTS: This writes the changes made to a testing output file
                # ET.indent(ET_tree)
                # ET_tree.write("./xtras/testing.cibd22x")
            elif sz_type == "Exhaust":
                for tz in ET_root.findall(".//ThrmlZn"):
                    if tz[0].text in self.tz_list:
                        hvac.AS_Exhaust(bldg, tz, exh_ctrl = self.exh_sys_ctrl.currentText(), fan_out=self.exh_fan_box.currentText())
            self.buttonBox.accepted.connect(self.accept)

class MZ_AS_Dialog(QDialog):
    global TZ_list, ET_root
    def __init__(self):
        super().__init__()
        
        self.tz_list = TZ_list

        layout = QGridLayout()

        layout.addWidget(QLabel("Select Type: "),0,0)
        self.mz_as_type = QComboBox()
        self.mz_as_type.addItems(["PVAV","VAV","DOASVAV"])
        layout.addWidget(self.mz_as_type,0,1)

        layout.addWidget(QLabel("Name: "),1,0)
        self.mz_name = QLineEdit()
        layout.addWidget(self.mz_name,1,1)

        self.tab = QTabWidget(self)

        # Specifics
        self.mz_tab = QWidget()
        mz_layout = QGridLayout()
        self.mz_tab.setLayout(mz_layout)
        mz_layout.addWidget(QLabel("Supply AirSegment"),1,0)
        mz_layout.addWidget(QLabel("\tCoilCooling: "),2,0)
        self.mz_CC_box = QComboBox()
        self.mz_CC_box.addItems(["DirectExpansion","ChilledWater","VRF"])
        mz_layout.addWidget(self.mz_CC_box,2,1)
        mz_layout.addWidget(QLabel("\tCoilHeating: "),3,0)
        self.mz_CH_box = QComboBox()
        self.mz_CH_box.addItems(["HeatPump","HotWater","Resistance","VRF"])
        mz_layout.addWidget(self.mz_CH_box,3,1)
        mz_layout.addWidget(QLabel("\tFan: "),4,0)
        self.mz_s_fan_box = QComboBox()
        self.mz_s_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        mz_layout.addWidget(self.mz_s_fan_box,4,1)
        mz_layout.addWidget(QLabel("Return AirSegment"),5,0)
        mz_layout.addWidget(QLabel("\tFan: "),6,0)
        self.mz_r_fan_box = QComboBox()
        self.mz_r_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        mz_layout.addWidget(self.mz_r_fan_box,6,1)
        mz_layout.addWidget(QLabel("OutsideAirControl"),7,0)
        self.mz_oac_box = QComboBox()
        self.mz_oac_box.addItems(["DifferentialDryBulb","FixedDryBulb","NoEconomizer","DifferentialEnthalpy","DifferentialDryBulbAndEnthalpy"])
        mz_layout.addWidget(self.mz_oac_box,7,1)
        mz_layout.addWidget(QLabel("\nVavReheatBox TU CoilHeating:"),8,0)
        self.rh_ch_type_box = QComboBox()
        self.rh_ch_type_box.addItems(["HeatPump","HotWater","Resistance","VRF"])
        mz_layout.addWidget(self.rh_ch_type_box,8,1)

        # Tab
        self.tab.addTab(self.mz_tab, "Edit Specifics")
        self.tab.setTabVisible(0,True)
        layout.addWidget(self.tab,2,0,5,2)
        
        wip_label = QLabel("*** NOTE ***\nSystems including HotWater, ChilledWater, VRF, etc. currently require\nmanual connection to Fluid Segments/VRF systems in CBECC")
        layout.addWidget(wip_label,7,0,1,1)
        
        # List of available thermal zones
        layout.addWidget(QLabel("Available Thermal Zones:"),0,2,1,1)
        self.widget_tz = QListWidget()
        self.widget_tz.addItems(self.tz_list)
        self.widget_tz.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.widget_tz.itemSelectionChanged.connect(self.tz_selection_changed)
        layout.addWidget(self.widget_tz,1,2,7,1)

        # TU: VAV Reheat Buttons
        layout.addWidget(QLabel("TerminalUnit:VAVReheatBox"),0,4,1,1)
        add_tu_yes_rh_button = QPushButton('ADD -->')
        add_tu_yes_rh_button.clicked.connect(self.add_tu_yes_rh)
        layout.addWidget(add_tu_yes_rh_button,1,4,1,1)
        rem_tu_yes_rh_button = QPushButton('<-- REMOVE')
        rem_tu_yes_rh_button.clicked.connect(self.rem_tu_yes_rh)
        layout.addWidget(rem_tu_yes_rh_button,2,4,1,1)
        self.widget_yes_rh = QListWidget()
        self.widget_yes_rh.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.widget_yes_rh,1,5,3,1)

        # TU: VAV No Reheat Buttons
        layout.addWidget(QLabel("TerminalUnit:VAVNoReheatBox"),4,4,1,1)
        add_tu_no_rh_button = QPushButton('ADD -->')
        add_tu_no_rh_button.clicked.connect(self.add_tu_no_rh)
        layout.addWidget(add_tu_no_rh_button,5,4,1,1)
        rem_tu_no_rh_button = QPushButton('<-- REMOVE')
        rem_tu_no_rh_button.clicked.connect(self.rem_tu_no_rh)
        layout.addWidget(rem_tu_no_rh_button,6,4,1,1)
        self.widget_no_rh = QListWidget()
        self.widget_no_rh.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.widget_no_rh,5,5,3,1)

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.clicked.connect(self.button_clicked)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout.addWidget(self.buttonBox,9,5)

        self.setLayout(layout)

    def tz_selection_changed(self):
        if self.widget_yes_rh.count()+self.widget_no_rh.count() > 0:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def add_tu_yes_rh(self):
        swap_l = [x.text() for x in self.widget_tz.selectedItems()]
        for it in swap_l:
            if len(self.widget_yes_rh.findItems(it,Qt.MatchFlag.MatchExactly)) == 0:
                if len(self.widget_no_rh.findItems(it,Qt.MatchFlag.MatchExactly)) == 0:
                    self.widget_yes_rh.addItem(it)
        self.widget_tz.clearSelection()

    def rem_tu_yes_rh(self):
        for it in self.widget_yes_rh.selectedItems():
            self.widget_yes_rh.takeItem(self.widget_yes_rh.row(it))

    def add_tu_no_rh(self):
        swap_l = [x.text() for x in self.widget_tz.selectedItems()]
        for it in swap_l:
            if len(self.widget_no_rh.findItems(it,Qt.MatchFlag.MatchExactly)) == 0:
                if len(self.widget_yes_rh.findItems(it,Qt.MatchFlag.MatchExactly)) == 0:
                    self.widget_no_rh.addItem(it)
        self.widget_tz.clearSelection()

    def rem_tu_no_rh(self):
        for it in self.widget_no_rh.selectedItems():
            self.widget_no_rh.takeItem(self.widget_no_rh.row(it))

    def button_clicked(self, button):
        global ET_root, ET_tree

        role = self.buttonBox.standardButton(button)

        if role == QDialogButtonBox.StandardButton.Cancel:
            self.buttonBox.rejected.connect(self.reject)
        elif role == QDialogButtonBox.StandardButton.Ok:
            sz_type = self.mz_as_type.currentText()
            bldg = ET_root.findall(".//Bldg")[0]

            yes_rh_tz_list = [self.widget_yes_rh.item(x).text() for x in range(self.widget_yes_rh.count())]
            no_rh_tz_list = [self.widget_no_rh.item(x).text() for x in range(self.widget_no_rh.count())]
            
            if len(self.mz_name.text()) == 0:
                search_type = ".//"+self.mz_as_type.currentText()
                mz_name = self.mz_as_type.currentText() + " " + str(len(bldg.findall(search_type))+1)
            else:
                mz_name = self.mz_name.text()
            
            hvac.mz_VAV(bldg, mz_name, yes_rh_tz_list, no_rh_tz_list, cc=self.mz_CC_box.currentText(), ch=self.mz_CH_box.currentText(), oac=self.mz_oac_box.currentText(),
            fan_in=self.mz_s_fan_box.currentText(), fan_out=self.mz_r_fan_box.currentText(), mz_as_type = self.mz_as_type.currentText(),
            rh_ch_type = self.rh_ch_type_box.currentText())

            # TESTING OUTPUTS: This writes the changes made to a testing output file
            # ET.indent(ET_tree)
            # ET_tree.write("./xtras/testing.cibd22x")

            self.buttonBox.accepted.connect(self.accept)

class SZ_ZS_Dialog(QDialog):
    global TZ_list, ET_root
    def __init__(self):
        super().__init__()
        
        self.tz_list = TZ_list

        layout = QGridLayout()

        layout.addWidget(QLabel("Select Type:"),0,0)
        self.sz_zs_type = QComboBox()
        self.sz_zs_type.addItems(["SZHP","SZAC","FPFC","PTHP","PTAC","VRF","MiniSplitAC","MiniSplitHP","Exhaust"])
        self.sz_zs_type.currentTextChanged.connect(self.type_changed)
        layout.addWidget(self.sz_zs_type,1,0)

        self.tab = QTabWidget(self)

        # SZHP, SZAC, etc. Specifics
        self.sz_hp_ac_tab = QWidget()
        sz_hp_ac_layout = QGridLayout()
        self.sz_hp_ac_tab.setLayout(sz_hp_ac_layout)
        sz_hp_ac_layout.addWidget(QLabel("\tCoilCooling: "),2,0)
        self.sz_hp_ac_CC_box = QComboBox()
        self.sz_hp_ac_CC_box.addItems(["DirectExpansion","ChilledWater","VRF"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_CC_box,2,1)
        sz_hp_ac_layout.addWidget(QLabel("\tCoilHeating: "),3,0)
        self.sz_hp_ac_CH_box = QComboBox()
        self.sz_hp_ac_CH_box.addItems(["HeatPump","HotWater","Resistance","VRF"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_CH_box,3,1)
        sz_hp_ac_layout.addWidget(QLabel("\tFan: "),4,0)
        self.sz_hp_ac_s_fan_box = QComboBox()
        self.sz_hp_ac_s_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        sz_hp_ac_layout.addWidget(self.sz_hp_ac_s_fan_box,4,1)

        # Exhaust Specifics
        self.exh_tab = QWidget()
        exh_layout = QGridLayout()
        self.exh_tab.setLayout(exh_layout)
        exh_layout.addWidget(QLabel("Exhaust System Control:"),0,0)
        self.exh_sys_ctrl = QComboBox()
        self.exh_sys_ctrl.addItems(["-- DEFAULT --","VariableFlowVariableSpeedFan","VariableFlowConstantSpeedFan","ConstantFlowConstantSpeedFan"])
        exh_layout.addWidget(self.exh_sys_ctrl,0,1)
        exh_layout.addWidget(QLabel("Exhaust AirSegment"),1,0)
        exh_layout.addWidget(QLabel("\tFan:"),2,0)
        self.exh_fan_box = QComboBox()
        self.exh_fan_box.addItems(["VariableSpeedDrive","ConstantVolume"])
        exh_layout.addWidget(self.exh_fan_box,2,1)

        self.tab.addTab(self.sz_hp_ac_tab, "Edit Specifics")
        self.tab.addTab(self.exh_tab, "Edit Specifics")
        self.tab.setTabVisible(0,True)
        self.tab.setTabVisible(1,False)
        layout.addWidget(self.tab,2,0,1,2)

        wip_label = QLabel("*** NOTE ***\nSystems including HotWater, ChilledWater, VRF, etc. currently require\nmanual connection to Fluid Segments/VRF systems in CBECC")
        layout.addWidget(wip_label,3,0,1,1)
        
        layout.addWidget(QLabel("Select Thermal Zones to create ZoneSystems for:"),0,2)
        self.widget_tz = QListWidget()
        self.widget_tz.addItems(self.tz_list)
        self.widget_tz.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.widget_tz.itemSelectionChanged.connect(self.tz_selection_changed)
        layout.addWidget(self.widget_tz,1,2,7,1)

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.clicked.connect(self.button_clicked)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout.addWidget(self.buttonBox,9,2)

        self.setLayout(layout)

    def type_changed(self, s):
        # print(s)
        if s == "Exhaust":
            self.tab.setTabVisible(0,False)
            self.tab.setTabVisible(1,True)
            self.tab.setCurrentWidget(self.exh_tab)
        else:
            self.tab.setTabVisible(0,True)
            self.tab.setTabVisible(1,False)
            self.tab.setCurrentWidget(self.sz_hp_ac_tab)

            if s == "FPFC":
                self.sz_hp_ac_CH_box.clear()
                self.sz_hp_ac_CH_box.addItems(["HotWater","Resistance"])
            elif s == "VRF":
                self.sz_hp_ac_CH_box.clear()
                self.sz_hp_ac_CH_box.addItems(["VRF"])
                self.sz_hp_ac_CC_box.clear()
                self.sz_hp_ac_CC_box.addItems(["VRF"])
            else:
                if self.sz_hp_ac_CH_box.count() < 3:
                    self.sz_hp_ac_CH_box.clear()
                    self.sz_hp_ac_CH_box.addItems(["HeatPump","HotWater","Resistance","VRF"])
                if self.sz_hp_ac_CC_box.count() < 3:
                    self.sz_hp_ac_CC_box.clear()
                    self.sz_hp_ac_CC_box.addItems(["DirectExpansion","ChilledWater","VRF"])

    def tz_selection_changed(self):
        if len(self.widget_tz.selectedItems()) > 0:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def button_clicked(self, button):
        global ET_root, ET_tree

        role = self.buttonBox.standardButton(button)

        if role == QDialogButtonBox.StandardButton.Cancel:
            self.buttonBox.rejected.connect(self.reject)
        elif role == QDialogButtonBox.StandardButton.Ok:
            sz_type = self.sz_zs_type.currentText()
            bldg = ET_root.findall(".//Bldg")[0]

            self.tz_list = [x.text() for x in self.widget_tz.selectedItems()]
            print("SELECTED THERMAL ZONES:", self.tz_list)

            if sz_type == "Exhaust":
                for tz in ET_root.findall(".//ThrmlZn"):
                    if tz[0].text in self.tz_list:
                        hvac.ZS_Exhaust(bldg, tz, exh_ctrl = self.exh_sys_ctrl.currentText(), fan_out=self.exh_fan_box.currentText())
            else:
                for tz in ET_root.findall(".//ThrmlZn"):
                    if tz[0].text in self.tz_list:
                        hvac.ZS_Sys(bldg, tz, cc=self.sz_hp_ac_CC_box.currentText(), ch=self.sz_hp_ac_CH_box.currentText(), fan=self.sz_hp_ac_s_fan_box.currentText(),
                        sz_zs_type = sz_type)
                # TESTING OUTPUTS: This writes the changes made to a testing output file
                # ET.indent(ET_tree)
                # ET_tree.write("./xtras/testing.cibd22x")
            self.buttonBox.accepted.connect(self.accept)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()