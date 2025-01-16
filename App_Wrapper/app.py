import sys, os, re
from scripts import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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
        global i_c_dir, nr_r_dir, logs_dir
        global i_c_files, nr_r_files, nr_r_storeys
        global SZHP_list, DOAS_list, DOAS_count
        DOAS_count = 1
        i_c_dir = ""
        nr_r_dir = logs_dir = r"C:/"
        i_c_files = nr_r_files = nr_r_storeys = []

        super().__init__()
        self.setWindowTitle("2022 CBECC Editors")

        self.maintab = QTabWidget()

        # Tab 1: IES to CBECC
        self.iestocbecc = QWidget()
        self.maintab.addTab(self.iestocbecc,"IES to CBECC")
        self.tab1_UI()
        # Tab 2: Multifamily Workflow
        self.combine_nr_r = QWidget()
        self.maintab.addTab(self.combine_nr_r,"Multifamily Workflow")
        self.tab2_UI()
        # Tab 3: SZHP Generator
        self.szhp_generator = QWidget()
        self.maintab.addTab(self.szhp_generator,"SZHP System Generator")
        self.tab3_UI()
        # Tab 4: DOAS Generator
        self.doas_generator = QWidget()
        self.maintab.addTab(self.doas_generator,"DOAS System Generator")
        self.tab4_UI()
        # Tab 5: Results Compiler
        self.results_compiler = QWidget()
        self.maintab.addTab(self.results_compiler,"Results Compiler")
        self.tab5_UI()
        
        self.setCentralWidget(self.maintab)

    def tab1_UI(self):
        frame_layout = QVBoxLayout()
        outer_layout = QHBoxLayout()
        ch_layout = QGridLayout()

        # TOP MOST LABELS ABOUT WHAT TO DO BEFORE RUNNING
        labtitle = QLabel("IES to CBECC")
        font_labtitle = labtitle.font()
        font_labtitle.setPointSize(30)
        font_labtitle.setBold(True)
        labtitle.setFont(font_labtitle)
        labtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(labtitle)
        lab1 = QLabel("!!! BEFORE RUNNING ANYTHING !!!\nFor all files, open it in CBECC and save as a .cibd22x file to have CBECC default some values. This also means if working file type is .xml, import it into CBECC and save it as a .cibd22x file to make any edits.")
        lab1.setWordWrap(True)
        lab1.setMinimumHeight(50)
        lab1.setStyleSheet("background-color: red")
        lab1.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(lab1)
        lab2 = QLabel("\n[1] Select .cibd22x file on the left. Change output name in textbox below if you don't want it to overwrite the original file\n\
                      [2] Select / change checkboxes on the right to customize the run\n\
                      [3] Click run to run the script on the file")
        lab2.setWordWrap(True)
        lab2.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(lab2)

        # LEFT LAYOUT BOX
        folder_select = QPushButton("Select File")
        folder_select.clicked.connect(self.i_c_open_folder_clicked)
        ch_layout.addWidget(folder_select,0,0)
        self.curr_folder = QLabel("No File Selected")
        font_curr_folder = self.curr_folder.font()
        font_curr_folder.setItalic(True)
        self.curr_folder.setFont(font_curr_folder)
        self.curr_folder.setMinimumHeight(50)
        self.curr_folder.setWordWrap(True)
        self.curr_folder.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        ch_layout.addWidget(self.curr_folder,1,0)

        l2 = QLabel("Enter Output Filename:")
        l2.setFixedSize(250,25)
        ch_layout.addWidget(l2,2,0)
        self.f_output = QLineEdit()
        self.f_output.setEnabled(False)
        self.f_output.setFixedSize(250,25)
        self.f_output.textChanged.connect(self.in_f_changed)
        ch_layout.addWidget(self.f_output,3,0)

        blank_lab = QLabel("")
        blank_lab.setFixedWidth(25)
        ch_layout.addWidget(blank_lab,0,1)
        
        # RIGHT LAYOUT BOX
        self.fen_check = QCheckBox("Custom Fenestration Values")
        self.fen_check.setMaximumWidth(300)
        self.fen_check.setToolTip("Check to set custom values for U-Value, SHGC, for fenestration. Default unchecked.")
        ch_layout.addWidget(self.fen_check, 0, 2, 1, 2)
        self.fen_check.checkStateChanged.connect(self.customfen)
        uvalue_label = QLabel("\tU-Value:")
        uvalue_label.setMaximumWidth(100)
        ch_layout.addWidget(uvalue_label,1,2)
        self.f_uvalue = QLineEdit("0.45")
        self.f_uvalue.setMaximumWidth(100)
        ch_layout.addWidget(self.f_uvalue,1,3)
        self.f_uvalue.setStyleSheet("background-color: gray")
        self.f_uvalue.setReadOnly(True)
        
        shgc_label = QLabel("\tSHGC:")
        shgc_label.setMaximumWidth(100)
        ch_layout.addWidget(shgc_label,2,2)
        self.f_shgc = QLineEdit("0.30")
        self.f_shgc.setMaximumWidth(100)
        ch_layout.addWidget(self.f_shgc,2,3)
        self.f_shgc.setStyleSheet("background-color: gray")
        self.f_shgc.setReadOnly(True)

        self.attic_check = QCheckBox("Keep Attics")
        self.attic_check.setToolTip("Check to keep existing attics in the model. Default unchecked.")
        self.attic_check.setMaximumWidth(500)
        ch_layout.addWidget(self.attic_check, 3, 2, 1, 2)

        ch_layout.setContentsMargins(0,50,50,50)
        ch_layout.totalMaximumSize()

        outer_layout.addLayout(ch_layout)
        frame_layout.addLayout(outer_layout)

        # RUN BUTTON
        self.i_c_button = QPushButton("Run")
        self.i_c_button.setFixedHeight(50)
        frame_layout.addWidget(self.i_c_button)
        if len(self.f_output.text()) > 0:
            self.i_c_button.setEnabled(True)
        else:
            self.i_c_button.setEnabled(False)
        self.i_c_button.clicked.connect(self.i_c_button_clicked)
        
        # OUTPUT LOG
        self.output_log = QLabel()
        self.output_log.setToolTip("Not Editable. Displays run success and outputs.")
        self.output_log.setStyleSheet("background-color: gray")
        self.output_log.setWordWrap(True)
        frame_layout.addWidget(self.output_log)

        frame_layout.setContentsMargins(100,50,100,50)
        self.iestocbecc.setLayout(frame_layout)

    def tab2_UI(self):
        frame_layout = QVBoxLayout()
        input_layout = QGridLayout()
        
        # TOP MOST LABELS ABOUT WHAT TO DO BEFORE RUNNING
        labtitle = QLabel("Multifamily Workflow")
        font_labtitle = labtitle.font()
        font_labtitle.setPointSize(30)
        font_labtitle.setBold(True)
        labtitle.setFont(font_labtitle)
        labtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(labtitle)
        lab1 = QLabel("Combines the Non-Residential and Residential files for a multi-family workflow.\
                      \n\n[1] Select folder path and files. Update output name if you don't want the files to be overwritten\
                      \n[2] Click Load in Storeys button and then select from the drop-down how to split NR/R\
                      \n[3] Click Run to combine the NR and R files")
        lab1.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        lab1.setWordWrap(True)
        frame_layout.addWidget(lab1)

        # FOLDER SELECT
        nr_r_folder_select = QPushButton("Select Folder")
        nr_r_folder_select.clicked.connect(self.nr_r_open_folder_clicked)
        nr_r_folder_select.setMaximumWidth(500)
        input_layout.addWidget(nr_r_folder_select, 0, 1, 1, 3)
        self.nr_r_curr_folder = QLabel("No Folder Selected")
        font_nr_r_curr_folder = self.nr_r_curr_folder.font()
        font_nr_r_curr_folder.setItalic(True)
        self.nr_r_curr_folder.setFont(font_nr_r_curr_folder)
        self.nr_r_curr_folder.setMaximumWidth(500)
        self.nr_r_curr_folder.setWordWrap(True)
        self.nr_r_curr_folder.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        input_layout.addWidget(self.nr_r_curr_folder, 1, 1, 1, 3)

        # LEFT LAYOUT BOX
        l_nr = QLabel("Select Non-Residential Input File:")
        l_nr.setFixedSize(200,25)
        input_layout.addWidget(l_nr, 2, 0, 1, 2)
        self.f_nr_input = QComboBox()
        self.f_nr_input.addItems(nr_r_files)
        self.f_nr_input.currentTextChanged.connect(self.in_nr_r_changed)
        self.f_nr_input.setFixedSize(200,25)
        input_layout.addWidget(self.f_nr_input, 3, 0, 1, 2)
        self.nr_pre_check = QCheckBox("Run IES to CBECC script on NR file?")
        self.nr_pre_check.setToolTip("Default Unchecked. If unchecked, will run the ies-to-cbecc script with default values on the NR file before further processing. If checked, won't.")
        input_layout.addWidget(self.nr_pre_check, 4, 0, 1, 2)
        
        # RIGHT LAYOUT BOX
        l_r = QLabel("Select Residential Input File:")
        l_r.setFixedSize(200,25)
        input_layout.addWidget(l_r, 2, 3, 1, 2)
        self.f_r_input = QComboBox()
        self.f_r_input.addItems(nr_r_files)
        self.f_r_input.currentTextChanged.connect(self.in_nr_r_changed)
        self.f_r_input.setFixedSize(200,25)
        input_layout.addWidget(self.f_r_input, 3, 3, 1, 2)
        self.r_pre_check = QCheckBox("Run IES to CBECC script on R file?")
        self.r_pre_check.setToolTip("Default Unchecked. If unchecked, will run the ies-to-cbecc script with default values on the R file before further processing. If checked, won't.")
        input_layout.addWidget(self.r_pre_check, 4, 3, 1, 2)

        # Output File Label
        l_out = QLabel("\nEnter Output Filename:")
        input_layout.addWidget(l_out, 5, 1, 1, 3)
        self.f_nr_r_output = QLineEdit(self.f_nr_input.currentText())
        self.f_nr_r_output.setMaximumWidth(500)
        input_layout.addWidget(self.f_nr_r_output, 6, 1, 1, 3)

        input_layout.addWidget(QLabel(""),7,1)

        # PRELOAD BUTTON
        self.nr_r_story_button = QPushButton("Load in Storeys to select Split Point\n(select first Res floor)")
        if len(self.f_nr_input)*len(self.f_r_input) > 0:
            self.nr_r_story_button.setEnabled(True)
        else:
            self.nr_r_story_button.setEnabled(False)
        self.nr_r_story_button.setMinimumSize(250,50)
        input_layout.addWidget(self.nr_r_story_button, 8, 1, 1, 3)
        self.nr_r_story_button.clicked.connect(self.nr_r_story_button_clicked)
        self.nr_r_story_select = QComboBox()
        self.nr_r_story_select.addItems(nr_r_storeys)
        self.nr_r_story_select.setToolTip("Select the FIRST Residential Floor. All previous entries will be kept on the NR file, all following entries will be kept on the R file.\nNOTE: Floors sorted alphabetically / in the order IES exported them. If something looks wrong, either your files are incorrect or you need to rename the floors.")
        self.nr_r_story_select.setStyleSheet("background-color: gray")
        input_layout.addWidget(self.nr_r_story_select, 9, 1, 1, 3)

        input_layout.setContentsMargins(50,50,50,50)

        frame_layout.addLayout(input_layout)

        # RUN BUTTON
        self.nr_r_button = QPushButton("Run")
        self.nr_r_button.setEnabled(False)
        self.nr_r_button.setFixedHeight(50)
        frame_layout.addWidget(self.nr_r_button)
        self.nr_r_button.clicked.connect(self.nr_r_button_clicked)

        # OUTPUT LOG
        self.nr_r_output_log = QLabel()
        self.nr_r_output_log.setStyleSheet("background-color: gray")
        self.nr_r_output_log.setWordWrap(True)
        self.nr_r_output_log.setToolTip("Not Editable. Displays run success and outputs.")
        frame_layout.addWidget(self.nr_r_output_log)

        frame_layout.setContentsMargins(100,50,100,50)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combine_nr_r.setLayout(frame_layout)

    def tab3_UI(self):
        frame_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # TOP MOST LABELS ABOUT WHAT TO DO BEFORE RUNNING
        labtitle = QLabel("SZHP HVAC Systems Generator")
        font_labtitle = labtitle.font()
        font_labtitle.setPointSize(30)
        font_labtitle.setBold(True)
        labtitle.setFont(font_labtitle)
        labtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(labtitle)
        lab1 = QLabel("Generates SZHP AirSystems as part of the Mechanical systems in CBECC.\
                      \n\n[1] Select folder and .cibd22x file on the left. Change output name if you don't want it to overwrite the original\
                      \n[2] Optional: Click Button to Manually Select which Thermal Zones to create SZHP for. (Default is all Conditioned Thermal Zones)\
                      \n[3] Click Run to generate SZHP airsystems and write to output file name.")
        lab1.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        lab1.setWordWrap(True)
        frame_layout.addWidget(lab1)

        # Select SZHP File
        szhp_file_select = QPushButton("Select File")
        szhp_file_select.clicked.connect(self.szhp_open_folder_clicked)
        szhp_file_select.setMaximumWidth(400)
        grid_layout.addWidget(szhp_file_select,0,0)
        self.szhp_curr_file = QLabel("No File Selected")
        font_szhp_curr_file = self.szhp_curr_file.font()
        font_szhp_curr_file.setItalic(True)
        self.szhp_curr_file.setFont(font_szhp_curr_file)
        self.szhp_curr_file.setWordWrap(True)
        self.szhp_curr_file.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(self.szhp_curr_file,1,0)
        self.szhp_pre_check = QCheckBox("Run IES to CBECC script on file?")
        self.szhp_pre_check.setToolTip("Default Unchecked. If unchecked, will run the ies-to-cbecc script with default values on the file before further processing. If checked, won't.")
        grid_layout.addWidget(self.szhp_pre_check,2,0)

        blank_lab = QLabel("")
        blank_lab.setFixedWidth(25)
        grid_layout.addWidget(blank_lab,0,1)
        
        # Output File
        l2 = QLabel("Enter Output Filename:")
        l2.setMaximumWidth(300)
        grid_layout.addWidget(l2,0,3)
        self.szhp_f_output = QLineEdit()
        if self.szhp_curr_file.text() != "No File Selected":
            self.szhp_f_output.setText(self.szhp_curr_file.text())
        else:
            self.szhp_f_output.setText("")
        self.szhp_f_output.setMaximumWidth(300)
        grid_layout.addWidget(self.szhp_f_output,1,3)

        grid_layout.setContentsMargins(50,50,50,50)
        frame_layout.addLayout(grid_layout)

        # PRELOAD BUTTON
        self.szhp_tz_button = QPushButton("[OPTIONAL]\nManually Select Thermal Zones")
        if self.szhp_curr_file.text() != "No File Selected":
            self.szhp_tz_button.setEnabled(True)
        else:
            self.szhp_tz_button.setEnabled(False)
        self.szhp_tz_button.setMinimumSize(250,50)
        grid_layout.addWidget(self.szhp_tz_button,2,3)
        self.szhp_tz_button.clicked.connect(self.szhp_tz_select_button_clicked)
        
        # RUN BUTTON
        self.szhp_r_button = QPushButton("Run")
        self.szhp_r_button.setFixedHeight(50)
        frame_layout.addWidget(self.szhp_r_button)
        if self.szhp_curr_file.text() != "No File Selected":
            self.szhp_r_button.setEnabled(True)
        else:
            self.szhp_r_button.setEnabled(False)
        self.szhp_r_button.clicked.connect(self.szhp_r_button_clicked)

        # OUTPUT LOG
        self.szhp_output_log = QLabel()
        self.szhp_output_log.setToolTip("Not Editable. Displays run success and outputs.")
        self.szhp_output_log.setStyleSheet("background-color: gray")
        self.szhp_output_log.setWordWrap(True)
        frame_layout.addWidget(self.szhp_output_log)

        frame_layout.setContentsMargins(150,50,150,50)
        self.szhp_generator.setLayout(frame_layout)

    def tab4_UI(self):
        frame_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # TOP MOST LABELS ABOUT WHAT TO DO BEFORE RUNNING
        labtitle = QLabel("DOAS HVAC Systems Generator")
        font_labtitle = labtitle.font()
        font_labtitle.setPointSize(30)
        font_labtitle.setBold(True)
        labtitle.setFont(font_labtitle)
        labtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(labtitle)
        lab1 = QLabel("Generates DOAS AirSystems as part of the Mechanical systems in CBECC.\
                      \n\n[1] Select folder and .cibd22x file on the left. Change output name if you don't want it to overwrite the original\
                      \n[2] Click Create DOAS System Button, to create a DOAS system and which Thermal Zones to add to it. This can be done as many times as needed.\
                      \n[3] Click Save to save the updated file with systems to the output file name.")
        lab1.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        lab1.setWordWrap(True)
        frame_layout.addWidget(lab1)

        # Select DOAS File
        doas_file_select = QPushButton("Select File")
        doas_file_select.clicked.connect(self.doas_open_folder_clicked)
        doas_file_select.setMaximumWidth(400)
        grid_layout.addWidget(doas_file_select,0,0)
        self.doas_curr_file = QLabel("No File Selected")
        font_doas_curr_file = self.doas_curr_file.font()
        font_doas_curr_file.setItalic(True)
        self.doas_curr_file.setFont(font_doas_curr_file)
        self.doas_curr_file.setWordWrap(True)
        self.doas_curr_file.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(self.doas_curr_file,1,0)
        self.doas_pre_check = QCheckBox("Run IES to CBECC script on file?")
        self.doas_pre_check.setToolTip("Default Unchecked. If unchecked, will run the ies-to-cbecc script with default values on the file before further processing. If checked, won't.")
        grid_layout.addWidget(self.doas_pre_check,2,0)

        blank_lab = QLabel("")
        blank_lab.setFixedWidth(25)
        grid_layout.addWidget(blank_lab,0,1)
        
        # Output File
        l2 = QLabel("Enter Output Filename:")
        l2.setMaximumWidth(300)
        grid_layout.addWidget(l2,0,3)
        self.doas_f_output = QLineEdit()
        if self.doas_curr_file.text() != "No File Selected":
            self.doas_f_output.setText(self.doas_curr_file.text())
        else:
            self.doas_f_output.setText("")
        self.doas_f_output.setMaximumWidth(300)
        grid_layout.addWidget(self.doas_f_output,1,3)

        grid_layout.setContentsMargins(50,50,50,50)
        frame_layout.addLayout(grid_layout)

        # PRELOAD BUTTON
        self.doas_tz_button = QPushButton("Create DOAS: Select Thermal Zones")
        if self.doas_curr_file.text() != "No File Selected":
            self.doas_tz_button.setEnabled(True)
        else:
            self.doas_tz_button.setEnabled(False)
        self.doas_tz_button.setMinimumSize(250,50)
        grid_layout.addWidget(self.doas_tz_button,2,3)
        self.doas_tz_button.clicked.connect(self.doas_tz_select_button_clicked)
        
        # RUN BUTTON
        self.doas_r_button = QPushButton("Save")
        self.doas_r_button.setFixedHeight(50)
        frame_layout.addWidget(self.doas_r_button)
        if self.doas_curr_file.text() != "No File Selected":
            self.doas_r_button.setEnabled(True)
        else:
            self.doas_r_button.setEnabled(False)
        self.doas_r_button.clicked.connect(self.doas_r_button_clicked)

        # OUTPUT LOG
        self.doas_output_log = QLabel()
        self.doas_output_log.setToolTip("Not Editable. Displays run success and outputs.")
        self.doas_output_log.setStyleSheet("background-color: gray")
        self.doas_output_log.setWordWrap(True)
        frame_layout.addWidget(self.doas_output_log)

        frame_layout.setContentsMargins(150,50,150,50)
        self.doas_generator.setLayout(frame_layout)

    def tab5_UI(self):
        frame_layout = QVBoxLayout()

        # TOP MOST LABELS ABOUT WHAT TO DO BEFORE RUNNING
        labtitle = QLabel("Results Compiler")
        font_labtitle = labtitle.font()
        font_labtitle.setPointSize(30)
        font_labtitle.setBold(True)
        labtitle.setFont(font_labtitle)
        labtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(labtitle)
        lab1 = QLabel("Finds all CBECC generated log files (including in subfolders) and pulls all results and pre-processes them to be ready for pasting directly into a T24 CBECC-2024 Results Excel Template.")
        lab1.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        lab1.setWordWrap(True)
        frame_layout.addWidget(lab1)

        # Select Log Folder
        logs_folder_select = QPushButton("Select Folder")
        logs_folder_select.clicked.connect(self.logs_open_folder_clicked)
        frame_layout.addWidget(logs_folder_select)
        self.logs_curr_folder = QLabel("No Folder Selected")
        font_logs_curr_folder = self.logs_curr_folder.font()
        font_logs_curr_folder.setItalic(True)
        self.logs_curr_folder.setFont(font_logs_curr_folder)
        self.logs_curr_folder.setMinimumHeight(50)
        self.logs_curr_folder.setWordWrap(True)
        self.logs_curr_folder.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        frame_layout.addWidget(self.logs_curr_folder)
        # Log File Count
        self.log_count = 0
        self.lab_log_count = QLabel("Number of Log Files found: --")
        self.lab_log_count.setStyleSheet("background-color: gray")
        self.lab_log_count.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(self.lab_log_count)

        # RUN BUTTON
        self.log_button = QPushButton("&Run")
        self.log_button.setFixedHeight(50)
        frame_layout.addWidget(self.log_button)
        if self.log_count > 0:
            self.log_button.setEnabled(True)
        else:
            self.log_button.setEnabled(False)
        self.log_button.clicked.connect(self.log_button_clicked)

        frame_layout.setContentsMargins(200,150,200,250)

        self.results_compiler.setLayout(frame_layout)

    def in_f_changed(self, s):
        global i_c_dir
        
        self.output_log.setStyleSheet("background-color: gray")
        self.output_log.setText("")

        if len(s)*len(i_c_dir) > 0:
                self.i_c_button.setEnabled(True)
        else:
            self.i_c_button.setEnabled(False)
    
    def in_nr_r_changed(self, s):
        self.f_nr_r_output.setText(s)
        self.nr_r_output_log.setStyleSheet("background-color: gray")
        self.nr_r_output_log.setText("")
        self.nr_r_story_select.clear()
        self.nr_r_story_select.setStyleSheet("background-color: gray")
        if len(self.f_nr_input)*len(self.f_r_input) > 0:
            self.nr_r_story_button.setEnabled(True)
        else:
            self.nr_r_story_button.setEnabled(False)

    def i_c_button_clicked(self):
        self.input_filename = i_c_dir
        self.output_filname = str(re.findall(r"(.*/).*$",i_c_dir)[0]) + self.f_output.text()
        self.uvalue = self.f_uvalue.text()
        self.shgc = self.f_shgc.text()
        
        self.output_log.setText("Running IES to CBECC script...")

        ies_to_cbecc_run(self.input_filename, self.output_filname, self.uvalue, self.shgc, self.attic_check.checkState() == Qt.CheckState.Checked)
        
        self.output_log.setText(self.output_log.text()+"\nRun Successful. Output file to: "+self.output_filname)
        self.output_log.setStyleSheet("background-color: green")
    
    def nr_r_story_button_clicked(self):
        global nr_r_storeys
        self.nr_input_filename = nr_r_dir + self.f_nr_input.currentText()
        self.r_input_filename = nr_r_dir + self.f_r_input.currentText()
        
        # A little aside to run ies-to-cbecc fix if checkboxes true
        if self.nr_pre_check.checkState() == Qt.CheckState.Checked:
            ies_to_cbecc_run(self.nr_input_filename, self.nr_input_filename, 0.45, 0.3, False)
        if self.r_pre_check.checkState() == Qt.CheckState.Checked:
            ies_to_cbecc_run(self.r_input_filename, self.r_input_filename, 0.45, 0.3, False)

        print("Running...")
        nr_r_storeys = nr_r_precheck(self.nr_input_filename, self.r_input_filename)
        self.nr_r_story_select.addItems(nr_r_storeys)
        self.nr_r_story_select.setStyleSheet("background-color: orange")
        self.nr_r_button.setEnabled(True)
    
    def nr_r_button_clicked(self):
        global nr_r_storeys
        self.nr_r_output_filname = nr_r_dir + self.f_nr_r_output.text()
        outname = self.nr_r_output_filname
        split_ind = nr_r_storeys.index(str(self.nr_r_story_select.currentText()))
     
        self.nr_r_output_log.setText("Running NR and R Combination Script...")
        self.nr_r_output_log.setText(self.nr_r_output_log.text()+"\nSplitting NR / R at "+str(self.nr_r_story_select.currentText()))

        nr_r_run(self.nr_r_output_filname, split_ind)
        
        self.nr_r_output_log.setStyleSheet("background-color: green")
        self.nr_r_output_log.setText(self.nr_r_output_log.text()+"\nRun Successful. Output file to: "+outname)

    def szhp_tz_select_button_clicked(self):
        global SZHP_list

        dlg = SZHP_Dialog()
        dlg.setWindowTitle("SZHP Thermal Zones Select")
        if dlg.exec():
            print("SZHP TZ List Changed")
            self.szhp_tz_list = SZHP_list
        else:
            print("Canceled SZHP TZ List Change")
            SZHP_list = self.szhp_tz_list

    def szhp_r_button_clicked(self):
        self.szhp_output_filename = str(re.findall(r"(.*/).*$",szhp_file)[0]) + self.szhp_f_output.text()

        # A little aside to run ies-to-cbecc fix if checkboxes true
        if self.szhp_pre_check.checkState() == Qt.CheckState.Checked:
            ies_to_cbecc_run(szhp_file, szhp_file, 0.45, 0.3, False)

        szhp_generator_run(szhp_file, self.szhp_tz_list, self.szhp_output_filename)

        self.szhp_output_log.setStyleSheet("background-color: green")
        self.szhp_output_log.setText("Running SZHP addition Script...")
        self.szhp_output_log.setText(self.szhp_output_log.text()+"\nRun Successful. Output file to: "+str(self.szhp_output_filename))
    
    def doas_tz_select_button_clicked(self):
        global DOAS_list, to_add_DOAS, DOAS_count

        # A little aside to run ies-to-cbecc fix if checkboxes true
        if self.doas_pre_check.checkState() == Qt.CheckState.Checked:
            ies_to_cbecc_run(doas_file, doas_file, 0.45, 0.3, False)

        dlg = DOAS_Dialog()
        dlg.setWindowTitle("DOAS Thermal Zones Select")
        if dlg.exec():
            print("DOAS TZ List Changed")
            self.doas_tz_list = DOAS_list

            doas_generator_run(to_add_DOAS, DOAS_count)
            DOAS_count = DOAS_count + 1
            to_add_DOAS = []
        else:
            print("Canceled DOAS TZ List Change")
            DOAS_list = self.doas_tz_list

    def doas_r_button_clicked(self):
        global DOAS_count

        self.doas_output_filename = str(re.findall(r"(.*/).*$",doas_file)[0]) + self.doas_f_output.text()

        doas_save(self.doas_output_filename)

        self.doas_output_log.setStyleSheet("background-color: green")
        self.doas_output_log.setText("Running DOAS addition Script...")
        self.doas_output_log.setText(self.doas_output_log.text()+"\nRun Successful. Output file to: "+str(self.doas_output_filename))
        DOAS_count = 1

    def log_button_clicked(self):
        global logs_dir
        
        logs_compile_run(logs_dir)
        self.lab_log_count.setText("Successfully logged "+self.log_count+" files to:"+str(logs_dir)+"Logs.csv")
        self.lab_log_count.setStyleSheet("background-color: green")

    def customfen(self):
        if self.fen_check.checkState() == Qt.CheckState.Checked:
            self.f_uvalue.setReadOnly(False)
            self.f_shgc.setReadOnly(False)
            self.f_uvalue.setStyleSheet("")
            self.f_shgc.setStyleSheet("")
        else:
            self.f_uvalue.setReadOnly(True)
            self.f_uvalue.setText("0.45")
            self.f_uvalue.setStyleSheet("background-color: gray")
            self.f_shgc.setReadOnly(True)
            self.f_shgc.setText("0.30")
            self.f_shgc.setStyleSheet("background-color: gray")
        
    def i_c_open_folder_clicked(self):
        global i_c_dir, f_output

        self.curr_folder.setText("No File Selected")
        self.f_output.setText("")
        self.f_output.setEnabled(False)

        i_c_dir = ""
        i_c_dir, end_discard = QFileDialog.getOpenFileName(self, "Select File",r"C://","2022 CBECC Files (*.cibd22x)")

        if len(i_c_dir) != 0:
            if re.search(".cibd22x",i_c_dir):
                self.curr_folder.setText(i_c_dir)
                self.f_output.setText(re.findall(r".*/(.*$)",i_c_dir)[0])
                
                self.f_output.setEnabled(True)
                self.i_c_button.setEnabled(True)

                self.output_log.setStyleSheet("background-color: gray")
                self.output_log.setText("")
                
    def nr_r_open_folder_clicked(self):
        global nr_r_dir
        global nr_r_files

        nr_r_dir = QFileDialog.getExistingDirectory(self, "Select Folder")
        if len(nr_r_dir) != 0:
            self.f_input.clear()

            nr_r_dir = nr_r_dir + r"/"
            print(nr_r_dir)
            nr_r_files = list()
            for f in os.listdir(nr_r_dir):
                f_path = nr_r_dir + f
                if(os.path.isfile(f_path)):
                    if re.search(".cibd22x",f):
                        nr_r_files.append(str(f))
            self.f_nr_input.addItems(nr_r_files)
            self.nr_r_curr_folder.setText(nr_r_dir)
            self.f_r_input.addItems(nr_r_files)
            self.nr_r_curr_folder.setText(nr_r_dir)
    
    def szhp_open_folder_clicked(self):
        global szhp_file, SZHP_list

        self.szhp_output_log.setStyleSheet("background-color: gray")
        self.szhp_output_log.setText("")
        self.szhp_curr_file.setText("No File Selected")
        self.szhp_f_output.setText("")
        self.szhp_tz_list = SZHP_list = []
        self.szhp_tz_button.setEnabled(False)
        self.szhp_r_button.setEnabled(False)
        
        szhp_file, end_discard = QFileDialog.getOpenFileName(self, "Select File",r"C:\\","2022 CBECC Files (*.cibd22x)")
        if len(szhp_file) != 0:
            if re.search(".cibd22x",szhp_file):
                print(szhp_file)
                self.szhp_curr_file.setText(szhp_file)
                self.szhp_f_output.setText(re.findall(r".*/(.*$)",szhp_file)[0])
                self.szhp_tz_list = szhp_tz_loader(szhp_file)
                SZHP_list = self.szhp_tz_list

                self.szhp_tz_button.setEnabled(True)
                self.szhp_r_button.setEnabled(True)

    def doas_open_folder_clicked(self):
        global doas_file, DOAS_list, DOAS_count

        self.doas_output_log.setStyleSheet("background-color: gray")
        self.doas_output_log.setText("")
        self.doas_curr_file.setText("No File Selected")
        self.doas_f_output.setText("")
        self.doas_tz_list = DOAS_list = []
        self.doas_tz_button.setEnabled(False)
        self.doas_r_button.setEnabled(False)
        DOAS_count = 1

        doas_file, end_discard = QFileDialog.getOpenFileName(self, "Select File",r"C:\\","2022 CBECC Files (*.cibd22x)")
        if len(doas_file) != 0:
            if re.search(".cibd22x",doas_file):
                print(doas_file)
                self.doas_curr_file.setText(doas_file)
                self.doas_f_output.setText(re.findall(r".*/(.*$)",doas_file)[0])
                self.doas_tz_list = doas_tz_loader(doas_file)
                DOAS_list = self.doas_tz_list
                
                self.doas_tz_button.setEnabled(True)
                self.doas_r_button.setEnabled(True)

    def logs_open_folder_clicked(self):
        global logs_dir

        self.lab_log_count.setStyleSheet("background-color: gray")
        self.lab_log_count.setText("Number of Log Files found: --")
        self.log_count = 0

        logs_dir = QFileDialog.getExistingDirectory(self, "Select Folder")
        if len(logs_dir) != 0:
            logs_dir = logs_dir + r"/"
            print(logs_dir)
            self.logs_curr_folder.setText(logs_dir)
            self.log_count = found_log_count(logs_dir)
            self.lab_log_count.setText("Number of Log Files found: "+str(self.log_count))
            
            if int(self.log_count) > 0:
                self.log_button.setEnabled(True)
            else:
                self.log_button.setEnabled(False)

class SZHP_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        global SZHP_list

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QGridLayout()
        message = QLabel("Thermal Zones on File:\n(Removal is Permanent until File Reload)")
        layout.addWidget(message,0,0)
        self.widget_SZHP = QListWidget()
        self.widget_SZHP.addItems(SZHP_list)
        layout.addWidget(self.widget_SZHP,1,0,1,2)

        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(self.remove)
        layout.addWidget(remove_button,2,0)

        layout.addWidget(self.buttonBox,2,1)

        self.setLayout(layout)

    def remove(self):
        global SZHP_list

        current_row = self.widget_SZHP.currentRow()
        if current_row >= 0:
            current_item = self.widget_SZHP.takeItem(current_row)
            del current_item

        SZHP_list = [self.widget_SZHP.item(x).text() for x in range(self.widget_SZHP.count())]

class DOAS_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        global DOAS_list, to_add_DOAS, DOAS_count

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QGridLayout()
        message = QLabel("Thermal Zones on File:")
        layout.addWidget(message,0,0)
        self.existing_tz = QListWidget()
        self.existing_tz.addItems(DOAS_list)
        layout.addWidget(self.existing_tz,1,0,4,1)

        add_button = QPushButton('Add ->')
        add_button.clicked.connect(self.add)
        layout.addWidget(add_button,1,1)

        remove_button = QPushButton('<- Remove')
        remove_button.clicked.connect(self.remove)
        layout.addWidget(remove_button,2,1)

        doas_message = QLabel("DOAS #"+str(DOAS_count)+":")
        layout.addWidget(doas_message,0,2)
        self.doas_tz = QListWidget()
        layout.addWidget(self.doas_tz,1,2,4,1)

        layout.addWidget(self.buttonBox,5,2)

        self.setLayout(layout)

    def add(self):
        global DOAS_list
        global to_add_DOAS

        current_row = self.existing_tz.currentRow()
        if current_row >= 0:
            current_item = self.existing_tz.takeItem(current_row)
            self.doas_tz.addItem(current_item)
            del current_item

        DOAS_list = [self.existing_tz.item(x).text() for x in range(self.existing_tz.count())]
        to_add_DOAS = [self.doas_tz.item(x).text() for x in range(self.doas_tz.count())]
    
    def remove(self):
        global DOAS_list
        global to_add_DOAS

        current_row = self.doas_tz.currentRow()
        if current_row >= 0:
            current_item = self.doas_tz.takeItem(current_row)
            self.existing_tz.addItem(current_item)
            del current_item

        DOAS_list = [self.existing_tz.item(x).text() for x in range(self.existing_tz.count())]
        to_add_DOAS = [self.doas_tz.item(x).text() for x in range(self.doas_tz.count())]

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()