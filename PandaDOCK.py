
# -*- coding: utf-8 -*-

import sys
import shutil
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QMenu, QFileDialog, QListWidget, QDockWidget, QMessageBox, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFrame)
from PySide6.QtGui import QIcon, QActionGroup, QAction, QKeySequence, QPixmap, QMovie
from PySide6.QtCore import Qt, QProcess, QTimer, QPropertyAnimation, QEasingCurve, QRect
from pymol._gui import PyMOLDesktopGUI
from view import PymolGLWidget
from styles import PROFESSIONAL_THEME, MAIN_COLORS, LOADING_ANIMATION_STYLE, get_loading_spinner_html
import os
from Bio.PDB import PDBParser, PDBIO, Select
import subprocess

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
    os.path.dirname(sys.executable), "Lib", "site-packages", "PySide6", "plugins", "platforms"
)
os.environ["PYTHONIOENCODING"] = "utf-8"

if getattr(sys, 'frozen', False):
    import pyi_splash
    

mainpath = os.path.dirname(__file__)
image_icon_path = os.path.join(mainpath, "Images", "pandaicon.ico")
footer = os.path.join(mainpath, "Images", "Bluefooter.png")
sphere = os.path.join(mainpath, "Images", "Sphere.png")
pandapng = os.path.join(mainpath, "Images", "logo_new.png")
pandapos = os.path.join(mainpath, "Images", "Pandaposter.png")
template = os.path.join(mainpath, "Templates")


def show_stylish_messagebox(parent, title, message, icon=QMessageBox.Information):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    
    # Add the new logo to the message box
    msg_box.setIconPixmap(QPixmap(pandapng).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    msg_box.setStyleSheet("""
        QMessageBox {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #ffffff, stop: 1 #f8fafc);
            color: #1e293b;
            font-size: 14px;
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        QLabel {
            color: #1e293b;
            font-size: 14px;
            font-weight: 500;
            padding: 12px;
            line-height: 1.5;
        }
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #6366f1, stop: 1 #4f46e5);
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 13px;
            font-weight: 600;
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            min-width: 100px;
            border: none;
            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #5b56f0, stop: 1 #4338ca);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.25);
        }
        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #4338ca, stop: 1 #3730a3);
            transform: translateY(0px);
            box-shadow: 0 1px 2px -1px rgba(0, 0, 0, 0.2);
        }
    """)
    msg_box.exec_()

class QTextEditLogger(QtCore.QObject):
    """Redirects sys.stdout/sys.stderr to a QTextEdit."""
    write_signal = QtCore.Signal(str)

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.write_signal.connect(self._append_text)

    def write(self, text):
        self.write_signal.emit(str(text))

    def flush(self):
        pass

    def _append_text(self, text):
        self.text_edit.moveCursor(QtGui.QTextCursor.End)
        self.text_edit.insertPlainText(text)
        self.text_edit.moveCursor(QtGui.QTextCursor.End)

class PyMOLOnlyWindow(QMainWindow, PyMOLDesktopGUI):
    def __init__(self):
        super().__init__()
           
        self.setWindowTitle("PandaDock - Molecular Docking Suite")
        self.setWindowIcon(QIcon(image_icon_path)) 
        self.setAcceptDrops(True)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowTabbedDocks)
        
        # Apply professional theme
        self.setStyleSheet(PROFESSIONAL_THEME + """
            QMainWindow::separator {
                background: #cbd5e1;
                width: 1px;
                height: 1px;
            }
            QMainWindow::separator:hover {
                background: #6366f1;
            }
        """)
        # After creating your main window (in __init__ of PyMOLOnlyWindow)
        
        self.pymol_viewer = PymolGLWidget(self)
        # self.cmd has basically everything we need, but need to study it properly
        global CMD
        self.cmd = self.pymol_viewer.cmd
        CMD = self.cmd
        self.setCentralWidget(self.pymol_viewer)

        # Appended Objects in SideBar
        self.newwidget = QWidget()
        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(self.on_object_selected)
        self.object_list_dock = QDockWidget("Loaded Ligands / Protein", self)
        self.object_list_dock.setWidget(self.object_list)
        self.object_list_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.object_list_dock.setStyleSheet(f"""
            QDockWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['background']}, stop: 1 {MAIN_COLORS['surface']});
                border-radius: 12px;
                border: 1px solid {MAIN_COLORS['border']};
                box-shadow: 0 4px 6px -1px {MAIN_COLORS['shadow']};
            }}
            QDockWidget::title {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
                color: white;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                padding: 12px 16px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                text-align: center;
                letter-spacing: 0.025em;
            }}
        """)
        self.object_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {MAIN_COLORS['background']};
                color: {MAIN_COLORS['text']};
                border: none;
                font-size: 13px;
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: {MAIN_COLORS['primary']};
            }}
            QListWidget::item {{
                background: transparent;
                padding: 12px 16px;
                border-bottom: 1px solid {MAIN_COLORS['border']};
                border-radius: 6px;
                margin: 2px 0;
                transition: all 0.2s ease;
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
                color: {MAIN_COLORS['background']};
                border: none;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background: {MAIN_COLORS['surface']};
                color: {MAIN_COLORS['text']};
                border: 1px solid {MAIN_COLORS['border']};
            }}
            QScrollBar:vertical {{
                background: {MAIN_COLORS['surface']};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {MAIN_COLORS['text_secondary']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {MAIN_COLORS['text']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        # Enhanced title with modern typography
        bold_title = QLabel("PandaDock")
        bold_title.setStyleSheet(f"""
            font-weight: 700; 
            font-size: 28px;
            color: {MAIN_COLORS['text']};
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            margin-left: 12px;
            letter-spacing: -0.025em;
        """)
        bold_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Larger, better quality logo
        image = QtGui.QPixmap(pandapng)
        image = image.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        icon_label = QLabel()
        icon_label.setPixmap(image)
        icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        icon_label.setStyleSheet("margin-right: 10px;")
        
        # Create a layout to combine the icon and title
        title_layout = QHBoxLayout()
        title_layout.addWidget(icon_label)
        title_layout.addWidget(bold_title)
        title_layout.addStretch()
        title_layout.setContentsMargins(10, 5, 10, 5)

        # Create a QWidget to hold the layout with modern design
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        title_widget.setStyleSheet(f"""
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {MAIN_COLORS['background']}, stop: 1 {MAIN_COLORS['surface']});
            border-radius: 12px;
            border: 1px solid {MAIN_COLORS['border']};
            padding: 8px;
            box-shadow: 0 2px 4px -1px {MAIN_COLORS['shadow']};
        """)
        
        # --- Add log dock widget at the bottom (do this ONCE here) ---
        global log_text_edit
        self.log_text_edit = QTextEdit()
        log_text_edit = self.log_text_edit
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #0f172a, stop: 1 #1e293b);
                color: #e2e8f0;
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid {MAIN_COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                selection-background-color: {MAIN_COLORS['primary']};
                selection-color: white;
                line-height: 1.4;
            }}
        """)
        self.log_dock = QDockWidget("", self)
        self.log_dock.setWidget(self.log_text_edit)
        self.log_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.log_dock.setStyleSheet(f"""
            QDockWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #263238, stop: 1 #37474F);
                border-radius: 10px;
                border: 2px solid {MAIN_COLORS['success']};
            }}
            QDockWidget::title {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['success']}, stop: 1 #059669);
                color: white;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                padding: 8px 12px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                text-align: center;
            }}
            QTextEdit {{
                background: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }}
            QScrollBar:vertical, QScrollBar:horizontal {{
                background: #333;
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal  {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['success']}, stop: 1 #059669);
                min-height: 24px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #06b6d4, stop: 1 #0891b2);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, 
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{                          
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        # Redirect sys.stdout and sys.stderr
        self.stdout_logger = QTextEditLogger(self.log_text_edit)
        sys.stdout = self.stdout_logger
        sys.stderr = self.stdout_logger
        print("\n" + "═"*60)
        print("🚀 Welcome to PandaDock - Molecular Docking Suite")
        print("Version 2.0 - Professional GUI Edition")
        print("Ready for molecular docking simulations...")
        print("═"*60 + "\n")
        self.newwidget_bg = QDockWidget(self)
        self.newwidget_bg.setTitleBarWidget(title_widget)  # Set the custom title bar widget
        self.newwidget_bg.setWidget(self.newwidget)
        self.newwidget_bg.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Disable floatable and closable
        self.newwidget_bg.setAllowedAreas(Qt.NoDockWidgetArea)  # Prevent sliding
        self.newwidget_bg.setFixedSize(320, 550)  # Increased height for 6 buttons
        self.newwidget_bg.setStyleSheet(f"""
            QDockWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['background']}, stop: 1 {MAIN_COLORS['surface']});
                border-radius: 16px;
                border: 1px solid {MAIN_COLORS['border']};
                box-shadow: 0 10px 15px -3px {MAIN_COLORS['shadow']};
            }}
        """)
        newwidget_layout = QVBoxLayout()
        newwidget_layout.setSpacing(4)  # Reduced spacing between items
        newwidget_layout.setContentsMargins(8, 8, 8, 8)  # Reduced margins around the entire layout

        # Create button variables for dynamic enabling/disabling
        self.start_button = QPushButton("Initialize Session")
        self.start_button.setStyleSheet("color: black;")
        self.ligand_button = QPushButton("Load Ligands")
        self.protein_button = QPushButton("Load Protein")
        global BindingButton
        self.binding_site_button = QPushButton("Define Binding Site")
        BindingButton = self.binding_site_button
        global DockingButton
        self.run_button = QPushButton("Execute Docking")
        DockingButton = self.run_button
        self.results_button = QPushButton("View Results")
        self.results_button.setEnabled(False)  # Initially disabled

        # Create professional button styles for direct application
        self.enabled_button_style = f"""
        QPushButton {{
            color: white;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
            border-radius: 10px;
            border: 2px solid {MAIN_COLORS['primary_dark']};
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            min-height: 36px;
            min-width: 180px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #5b56f0, stop: 1 #4338ca);
            transform: translateY(-1px);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #4338ca, stop: 1 #3730a3);
        }}
        """
        
        self.disabled_button_style = f"""
        QPushButton {{
            color: {MAIN_COLORS['text']};
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {MAIN_COLORS['surface']}, stop: 1 #e2e8f0);
            border-radius: 10px;
            border: 1px solid {MAIN_COLORS['border']};
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            min-height: 36px;
            min-width: 180px;
        }}
        """

        # Initially enable only the Start button and apply styles
        self.start_button.setEnabled(True)
        self.start_button.setStyleSheet(self.enabled_button_style)
        
        self.ligand_button.setEnabled(False)
        self.ligand_button.setStyleSheet(self.disabled_button_style)
        
        self.protein_button.setEnabled(False)
        self.protein_button.setStyleSheet(self.disabled_button_style)
        
        self.binding_site_button.setEnabled(False)
        self.binding_site_button.setStyleSheet(self.disabled_button_style)
        
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet(self.disabled_button_style)
        
        self.results_button.setEnabled(False)
        self.results_button.setStyleSheet(self.disabled_button_style)

        # Define button functions
        def start_new_session():
            try:
                self.object_list.clear()
                self.cmd.reinitialize()
                global main_directory
                main_directory = QFileDialog.getExistingDirectory(self, "Select Directory", ".")
                if main_directory:
                    show_stylish_messagebox(self, "New Session", "New session started in: {}".format(main_directory))
                    print("New session started in: {}".format(main_directory))
                    self.status_bar.showMessage("Session initialized - Ready to load ligands")
                    self.ligand_button.setEnabled(True)  # Enable the Ligand button
                    self.ligand_button.setStyleSheet(self.enabled_button_style)
                    self.protein_button.setEnabled(False)
                    self.binding_site_button.setEnabled(False)
                    self.run_button.setEnabled(False)
                else:
                    show_stylish_messagebox(self, "No Directory Selected", "Please select a directory to start a new session.")
                    print("No directory selected.")
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred: {}".format(str(e)))

        def get_ligand_file():
            try:
                ligand_files, _ = QFileDialog.getOpenFileNames(self, "Select Ligand File", ".", "SDF Files (*.sdf);;Mol Files (*.mol)")
                if ligand_files:
                    total_files = len(ligand_files)
                    self.ligand_button.setEnabled(False)
                    self.ligand_button.setStyleSheet(self.disabled_button_style)
                    self.protein_button.setEnabled(True)  # Enable the Protein button
                    self.protein_button.setStyleSheet(self.enabled_button_style)
                    global new_folder
                    new_folder = os.path.join(main_directory, "Ligand")
                    if os.path.exists(new_folder):
                        shutil.rmtree(new_folder)
                    os.makedirs(new_folder, exist_ok=True)

                    for file in ligand_files:
                        # Copy the ligand file to the Ligand folder
                        shutil.copy(file, new_folder)
                        file_name = os.path.basename(file)
                        real_file_name = os.path.splitext(file_name)[0]
                        final_name = "Ligand-" + real_file_name
                        # Add the file path as a hidden data attribute to the object list item
                        item = QtWidgets.QListWidgetItem(final_name)
                        item.setData(Qt.UserRole, os.path.join(new_folder, file_name))
                        self.object_list.addItem(item)

                    show_stylish_messagebox(self, "Ligand File Selected", "Selected {} Ligand Files.".format(total_files))
                    print("Ligand Selection Complete. {} Ligand Files Added.".format(total_files))
                    self.status_bar.showMessage("Ligands loaded ({} files) - Ready to load protein".format(total_files))
                else:
                    show_stylish_messagebox(self, "No File Selected", "Please select a ligand file.")
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred: {}".format(str(e)))

        def is_het(residue):
            res = residue.id[0]
            return res not in (" ", "W")

        def extract_ligands_from_pdb(pdb_path, output_directory):
            try:
                # Parse the provided PDB file
                pdb_file = os.path.basename(pdb_path)
                pdb_id = os.path.splitext(pdb_file)[0].upper()
                
                pdb = PDBParser().get_structure(pdb_id, pdb_path)
                
                io = PDBIO()

                # Iterate through the PDB file to extract ligands
                for model in pdb:
                    for chain in model:
                        for residue in chain:
                            if is_het(residue):
                                
                                chain_id = chain.get_id()
                                ligand_resname = residue.get_resname()
                                ligand_filename = "{}_{}.pdb".format(ligand_resname, chain_id)
                                ligand_path = os.path.join(output_directory, ligand_filename)

                                # Save the ligand as a separate PDB file
                                io.set_structure(residue)
                                io.save(ligand_path)
                                print("Ligands/Co-Factors/Ions present in the protein - {}".format(ligand_resname))
            except Exception as e:
                show_stylish_messagebox(self, "PandaDock", str(e))

        def load_from_file():
            try:
                # Open a file dialog to select a protein file
                protein_file, _ = QFileDialog.getOpenFileName(self, "Select Protein File", ".", "PDB Files (*.pdb)")
                if protein_file:
                    # Extract the protein name and add the prefix "Protein-"
                    file_name = os.path.basename(protein_file)
                    base_name = os.path.splitext(file_name)[0]
                    sanitized_name = base_name[:4]  # Limit to the first 4 characters
                    protein_name = "Protein-{}".format(sanitized_name)
                  

                    # Load the protein file into PyMOL
                    self.cmd.load(protein_file, protein_name)
                    self.cmd.show("cartoon", protein_name)  # Show the protein in "cartoon" representation
                    self.cmd.orient(protein_name)          # Orient the view to the protein

                    # Disable all other objects and enable only the protein
                    self.cmd.disable("all")
                    self.cmd.enable(protein_name)

                    # Add the protein to the object list
                    item = QtWidgets.QListWidgetItem(protein_name)
                    item.setData(Qt.UserRole, protein_file)  # Store the file path as hidden data
                    self.object_list.addItem(item)

                    # Save the protein file in the "Protein" folder
                    global protein_folder
                    protein_folder = os.path.join(main_directory, "Protein")
                    if os.path.exists(protein_folder):
                        shutil.rmtree(protein_folder)
                    os.makedirs(protein_folder, exist_ok=True)
                    shutil.copy(protein_file, protein_folder)

                    # Extract heteroatoms from the protein file
                    global heteroatoms_dir
                    heteroatoms_dir = os.path.join(main_directory, "Heteroatoms")
                    if os.path.exists(heteroatoms_dir):
                        shutil.rmtree(heteroatoms_dir)
                    os.makedirs(heteroatoms_dir, exist_ok=True)

                    # Extract ligands/heteroatoms from the protein file
                    extract_ligands_from_pdb(protein_file, heteroatoms_dir)

                    # Add heteroatoms to the object list
                    for file in os.listdir(heteroatoms_dir):
                        if file.endswith(".pdb"):
                            heteroatoms_file = os.path.join(heteroatoms_dir, file)
                            heteroatoms_name = "Heteroatoms-{}".format(os.path.splitext(file)[0])
                            item = QtWidgets.QListWidgetItem(heteroatoms_name)
                            item.setData(Qt.UserRole, heteroatoms_file)  # Store the file path as hidden data
                            self.object_list.addItem(item)

                    # Enable the Binding Site button
                    self.protein_button.setEnabled(False)  # Disable the Protein button
                    self.protein_button.setStyleSheet(self.disabled_button_style)
                    self.binding_site_button.setEnabled(True)
                    self.binding_site_button.setStyleSheet(self.enabled_button_style)

                    show_stylish_messagebox(self, "Protein File", "Selected Protein File: {}".format(protein_file))
                    print("Protein File Loaded: {}".format(protein_file))
                    self.status_bar.showMessage("Protein loaded - Ready to define binding site")
                else:
                    show_stylish_messagebox(self, "No File Selected", "Please select a protein file.")
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred: {}".format(str(e)))

        def define_binding_site():
            try:
                print("Defining binding site...")
                self.status_bar.showMessage("Configuring binding site parameters...")
                # Access the global function
                global dialogxfrom
                dialogxfrom()
                # Enable the Execute Docking button after binding site is defined
                self.binding_site_button.setEnabled(False)
                self.binding_site_button.setStyleSheet(self.disabled_button_style)
                self.run_button.setEnabled(True)
                self.run_button.setStyleSheet(self.enabled_button_style)
                self.status_bar.showMessage("Binding site configured - Ready to execute docking")
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred while defining the binding site: {}".format(str(e)))
       
        def run_docking_dialog():
            try:
                # Access the global function
                global dialogxdock
                dialogxdock()
                self.status_bar.showMessage("Docking parameters configured - Ready to view results")
                # Disable execute button and enable results button
                self.run_button.setEnabled(False)
                self.run_button.setStyleSheet(self.disabled_button_style)
                self.results_button.setEnabled(True)
                self.results_button.setStyleSheet(self.enabled_button_style)
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred while running docking: {}".format(str(e)))
                       
        def view_results():
            try:
                # Check if results exist
                if hasattr(self, 'main_directory') and main_directory:
                    output_dir = os.path.join(main_directory, "output")
                    if os.path.exists(output_dir):
                        # Open file dialog to select result files
                        result_files, _ = QFileDialog.getOpenFileNames(
                            self, "Select Result Files", output_dir, 
                            "All Files (*.*);;PDB Files (*.pdb);;SDF Files (*.sdf);;CSV Files (*.csv);;Log Files (*.log)"
                        )
                        if result_files:
                            for file_path in result_files:
                                if file_path.endswith(('.pdb', '.sdf')):
                                    # Load molecular structure files into PyMOL
                                    filename = os.path.basename(file_path)
                                    self.cmd.load(file_path, filename)
                                    self.object_list.addItem(f"Result: {filename}")
                                    self.status_bar.showMessage(f"Loaded result: {filename}")
                                else:
                                    # For other files, show in a text viewer
                                    self.show_file_viewer(file_path)
                        else:
                            show_stylish_messagebox(self, "No Files Selected", "Please select result files to view.")
                    else:
                        show_stylish_messagebox(self, "No Results Found", "No output directory found. Please run docking first.")
                else:
                    show_stylish_messagebox(self, "No Session", "Please initialize a session first.")
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred while viewing results: {}".format(str(e)))
            
        # Connect buttons to their respective functions
      
        self.start_button.clicked.connect(start_new_session)
        self.ligand_button.clicked.connect(get_ligand_file)
        self.protein_button.clicked.connect(load_from_file)
        self.binding_site_button.clicked.connect(define_binding_site)
        self.run_button.clicked.connect(run_docking_dialog)
        self.results_button.clicked.connect(view_results)

        # Enhanced button layout with improved spacing and styling
        button_descriptions = [
            "Initialize New Docking Session", 
            "Load Small Molecule Ligands", 
            "Load Target Protein Structure", 
            "Configure Binding Site Parameters", 
            "Execute Docking Simulation",
            "View and Analyze Results"
        ]
        
        buttons_list = [self.start_button, self.ligand_button, self.protein_button, self.binding_site_button, self.run_button, self.results_button]
        
        for i, (button, description) in enumerate(zip(buttons_list, button_descriptions)):
            # Create a container for each button-label pair
            button_container = QWidget()
            button_container.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 {MAIN_COLORS['background']}, stop: 1 {MAIN_COLORS['surface']});
                    border-radius: 12px;
                    border: 1px solid {MAIN_COLORS['border']};
                    margin: 1px;
                    padding: 6px;
                    box-shadow: 0 1px 3px 0 {MAIN_COLORS['shadow']};
                }}
                QWidget:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 {MAIN_COLORS['surface']}, stop: 1 #f1f5f9);
                    border-color: {MAIN_COLORS['primary']};
                    transform: translateY(-1px);
                }}
            """)
            
            container_layout = QVBoxLayout(button_container)
            container_layout.setSpacing(3)
            container_layout.setContentsMargins(6, 6, 6, 6)
            
            # Add button
            button.setFixedHeight(38)
            button.setMinimumWidth(200)  # Ensure minimum width
            container_layout.addWidget(button)
            
            # Add description label
            label = QLabel(description)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"""
                QLabel {{
                    font-size: 11px;
                    color: {MAIN_COLORS['text_secondary']};
                    font-style: normal;
                    font-weight: 400;
                    margin: 0;
                    padding: 2px 0;
                    line-height: 1.4;
                }}
            """)
            label.setWordWrap(True)
            container_layout.addWidget(label)
            
            newwidget_layout.addWidget(button_container)

        # Set the layout for the new widget
        self.newwidget.setLayout(newwidget_layout)
        self.addDockWidget(Qt.RightDockWidgetArea, self.object_list_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.newwidget_bg)

        # Menus and shortcuts
        self.undo_stack = []
   
        # Add status bar with modern styling
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
                color: white;
                font-size: 12px;
                font-weight: 500;
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                padding: 8px 16px;
                border-top: 1px solid {MAIN_COLORS['primary_dark']};
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)
        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {MAIN_COLORS['border']};
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                font-size: 11px;
                color: {MAIN_COLORS['text']};
                background-color: {MAIN_COLORS['surface']};
                height: 16px;
                max-width: 200px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
                border-radius: 6px;
                margin: 2px;
            }}
        """)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready - Initialize a new session to begin molecular docking | PandaDOCK Professional")
        
        self.create_shortcuts()

        self.show()

    # Menu File to Save and Load


    
    def run_exe_vs(self ,args, ligand_path, protein_file, output_directory, x, y, z, radius):
          
        process = QProcess(self)
        process.setProgram("pandadock")
        process.setArguments(args + [
            "--protein", protein_file,
            "--screen", ligand_path,
            "--center", str(x), str(y), str(z),
            "--size", "20", "20", "20",
            "--out", output_directory
        ])
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(lambda: self.log_text_edit.append(process.readAllStandardOutput().data().decode()))
        process.readyReadStandardError.connect(lambda: self.log_text_edit.append("<span style='color:red;'>{}</span>".format(process.readAllStandardError().data().decode())))
        process.errorOccurred.connect(lambda err: self.log_text_edit.append("<span style='color:red;'>Process error: {}</span>".format(err)))
        def on_finished():
            self.log_text_edit.append("<span style='color:green;'>Process finished.</span>")
            show_stylish_messagebox(self, "Simulation Complete", "Simulation Complete.")
        process.finished.connect(on_finished)
        process.start()
        if not hasattr(self, "processes"):
            self.processes = []
        self.processes.append(process)

    def run_exe_vs_pocket(self ,args, ligand_path, protein_file, output_directory):
          
        process = QProcess(self)
        process.setProgram("pandadock")
        process.setArguments(args + [
            "--protein", protein_file,
            "--screen", ligand_path,
            "--out", output_directory 
            ])
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(lambda: self.log_text_edit.append(process.readAllStandardOutput().data().decode()))
        process.readyReadStandardError.connect(lambda: self.log_text_edit.append("<span style='color:red;'>{}</span>".format(process.readAllStandardError().data().decode())))
        process.errorOccurred.connect(lambda err: self.log_text_edit.append("<span style='color:red;'>Process error: {}</span>".format(err)))
        def on_finished():
            self.log_text_edit.append("<span style='color:green;'>Process finished.</span>")
            show_stylish_messagebox(self, "Simulation Complete", "Simulation Complete.")
        process.finished.connect(on_finished)
        process.start()
        if not hasattr(self, "processes"):
            self.processes = []
        self.processes.append(process)
   

    def run_exe(self ,args, ligand_path, protein_file, output_directory, x, y, z, radius, ligand_queue):
            # Example: Replace with your actual .exe path
            process = QProcess(self)
            process.setProgram("pandadock")
            process.setArguments(args + [
            "--ligand", ligand_path,
            "--protein", protein_file,
            "--center", str(x), str(y), str(z),
            "--size", "20", "20", "20",
            "--out", output_directory
             ])
            process.setProcessChannelMode(QProcess.MergedChannels)  # Merge stdout and stderr

            # Connect signals
            process.readyReadStandardOutput.connect(lambda: self.log_text_edit.append(process.readAllStandardOutput().data().decode()))
            process.readyReadStandardError.connect(lambda: self.log_text_edit.append("<span style='color:red;'>{}</span>".format(process.readAllStandardError().data().decode())))
            process.finished.connect(lambda: self.process_next_ligand(args, ligand_queue, protein_file, output_directory, x, y, z, radius))
            process.start()
            self.current_process = process
    def run_exe_pocket(self ,args, ligand_path, protein_file, output_directory, ligand_queue):
            # Example: Replace with your actual .exe path
            process = QProcess(self)
            process.setProgram("pandadock")
            process.setArguments(args + [
            "--ligand", ligand_path,
            "--protein", protein_file,
            "--out", output_directory
             ])
            process.setProcessChannelMode(QProcess.MergedChannels)  # Merge stdout and stderr

            # Connect signals
            process.readyReadStandardOutput.connect(lambda: self.log_text_edit.append(process.readAllStandardOutput().data().decode()))
            process.readyReadStandardError.connect(lambda: self.log_text_edit.append("<span style='color:red;'>{}</span>".format(process.readAllStandardError().data().decode())))
            process.finished.connect(lambda: self.process_next_ligand_pocket(args, ligand_queue, protein_file, output_directory, x, y, z, radius))
            process.start()
            self.current_process = process

    

  

        # Connect buttons to their respective functions
    def process_next_ligand(self, args, ligand_queue, protein_file, output_directory, x, y, z, radius):
            if not ligand_queue:
                print("Simulation Has Been Completed.")
                show_stylish_messagebox(self, "Simulation Complete", "Simulation Complete.")
                return
            
            
            ligand_path = ligand_queue.pop(0)
            print("Docking Ligand: {}".format(ligand_path))
            self.run_exe( args, ligand_path, protein_file, output_directory, x, y, z, radius, ligand_queue)

    def process_next_ligand_pocket(self,args, ligand_queue, protein_file, output_directory, x, y, z, radius):
            if not ligand_queue:
                print("Simulation Has Been Completed.")
                show_stylish_messagebox(self, "Simulation Complete", "Simulation Complete.")
                return
            
            
            ligand_path = ligand_queue.pop(0)
            print("Docking Ligand: {}".format(ligand_path))
            self.run_exe_pocket(args, ligand_path, protein_file, output_directory, ligand_queue)

                
    def create_shortcuts(self):
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z")) # Press Ctrl+Z to Undo
        undo_action.triggered.connect(self.undo)
        self.addAction(undo_action)
        orient_action = QAction("Orient Object", self)
        orient_action.setShortcut(QKeySequence("Ctrl+O")) # Press Ctrl+Shift+O to Orietn Properly
        orient_action.triggered.connect(self.orient_current_object)
        self.addAction(orient_action)

    def show_file_viewer(self, file_path):
        """Show a simple file viewer dialog for text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                content = "Cannot read file - binary or unsupported format"
        except Exception as e:
            content = f"Error reading file: {str(e)}"
        
        # Create a dialog to show the file content
        dialog = QMessageBox(self)
        dialog.setWindowTitle(f"File Viewer - {os.path.basename(file_path)}")
        dialog.setText(content[:1000] + "..." if len(content) > 1000 else content)
        dialog.setDetailedText(content)
        dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

    def on_object_selected(self, item):
        try:
            # Get the file path stored in the item's data
            file_path = item.data(Qt.UserRole)
            obj_name = item.text()  # Use the item's text as the object name

            # Check if the object is already loaded in PyMOL
            if obj_name not in self.cmd.get_object_list():
                self.cmd.load(file_path, obj_name)  # Load the file into PyMOL

            # Determine the representation based on the object type
            if obj_name.startswith("Ligand-"):
                self.cmd.show("sticks", obj_name)
                self.cmd.orient(obj_name)
                self.cmd.disable('all') 
                self.cmd.enable(obj_name) # Show ligands in "sticks" representation
            elif obj_name.startswith("Protein-"):
                self.cmd.show("cartoon", obj_name) 
                    # Disable all other objects and enable only the selected one
                self.cmd.disable("all")
                self.cmd.enable(obj_name)
                self.cmd.orient(obj_name)  # Orient the view to the selected object

                print("Loaded and displayed object: {}".format(obj_name))
            elif obj_name.startswith("Heteroatoms-"):
                self.cmd.show("sticks", obj_name)  # Show heteroatoms in "sticks" representation
                self.cmd.zoom(obj_name) 
                 # Zoom into the heteroatom
                self.cmd.clip("slab", 50)  # Apply big clipping for better visualization

                # Load the parent protein if not already loaded
                protein_file = os.path.join(protein_folder, os.listdir(protein_folder)[0])
                man = os.path.basename(protein_file)
                base_name = os.path.splitext(man)[0]
                sanitized_name = base_name[:4]  # Limit to the first 4 characters
                protein_name = "Protein-{}".format(sanitized_name)
                if protein_name not in self.cmd.get_object_list():
                    self.cmd.load(protein_file, protein_name)
                    self.cmd.show("cartoon", protein_name)  # Show the protein in "cartoon" representation

                # Enable both the heteroatom and the parent protein
                self.cmd.enable(protein_name)
                self.cmd.enable(obj_name)

             

            
        except Exception as e:
            show_stylish_messagebox(self, "Error", "An error occurred while loading the object: {}".format(str(e)))

    
    def undo(self):
        if not self.undo_stack:
            print("Undo stack is empty.")
            return

        action, obj_name = self.undo_stack.pop()
        if action == 'load':
            # Delete the object from PyMOL
            self.cmd.delete(obj_name)
            # Find and remove the corresponding item from the object list
            items = self.object_list.findItems(obj_name, Qt.MatchExactly)
            for item in items:
                self.object_list.takeItem(self.object_list.row(item))
            print("Undo: deleted object {}.".format(obj_name))
        elif action == 'orient':
            print("Undo: orientation reset for object {}.".format(obj_name))

    def orient_current_object(self):
        selected_items = self.object_list.selectedItems()
        if not selected_items:
            print("No object selected to orient.")
            return

        item = selected_items[0]
        obj_name = item.text()
        file_path = item.data(Qt.UserRole)  # Retrieve the file path stored in the item's data

        # Check if the object is already loaded in PyMOL
        if obj_name not in self.cmd.get_object_list():
            self.cmd.load(file_path, obj_name)  # Load the file into PyMOL
            self.cmd.show("sticks", obj_name)  # Show the object in "sticks" representation
            print("Loaded object: {}".format(obj_name))

        # Orient the selected object
        self.cmd.orient(obj_name)
        print("Oriented object: {}".format(obj_name))

        # Add the action to the undo stack
        


def show_exit_confirmation(event):
         msg_box = QtWidgets.QMessageBox()
         icon1 = QtGui.QIcon()
         icon1.addPixmap(QtGui.QPixmap(image_icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
         msg_box.setWindowTitle("PandaDock - Exit Confirmation")
         msg_box.setWindowIcon(icon1)
         
         # Use the new logo with better scaling
         pixmap = QtGui.QPixmap(pandapng) 
         scaled_pixmap = pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
         msg_box.setIconPixmap(scaled_pixmap)
         
         msg_box.setText("Are you sure you want to exit PandaDock?")
         msg_box.setInformativeText("Any unsaved work will be lost.")
         msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
         msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
         
         msg_box.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #F8F9FA, stop: 1 #E9ECEF);
                color: #2C3E50;
                font-size: 14px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                border-radius: 15px;
                border: 2px solid #4CAF50;
            }
            QLabel {
                color: #2C3E50;
                font-size: 16px;
                font-weight: 600;
                padding: 10px;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #66BB6A, stop: 1 #4CAF50);
                color: white;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 90px;
                border: none;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #5CBB60, stop: 1 #388E3C);
            }
            QPushButton[text="No"] {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #FF7043, stop: 1 #F4511E);
            }
            QPushButton[text="No"]:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #FF5722, stop: 1 #D84315);
            }
        """)
            
         reply = msg_box.exec_()
         if reply == QtWidgets.QMessageBox.Yes:
           QtWidgets.QApplication.quit()
         else:
           event.ignore()

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(963, 368)
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setGeometry(QtCore.QRect(30, 110, 181, 141))
        self.listWidget.setObjectName("listWidget")
        for file in os.listdir(heteroatoms_dir):
            if file.endswith(".pdb"):    
                heteroatoms_name = os.path.basename(file)
                filename = os.path.splitext(heteroatoms_name)[0]
                self.listWidget.addItem(filename)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(30, 80, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        def create_sphere_in_pymol():
            try:
                # Ensure global variables x, y, z, and radius are defined
                global x, y, z, radius
                if not all([x, y, z, radius]):
                    QMessageBox.warning(self, "Missing Data", "Please ensure the coordinates and radius are defined.")
                    return

                # Create a sphere in PyMOL using the pseudoatom command
                sphere_name = "binding_site_sphere"
                CMD.pseudoatom(
                    sphere_name,
                    pos=[x, y, z],  # Position of the sphere
                    vdw=radius       # Radius of the sphere
                )

                # Show the sphere as a surface
                CMD.show("spheres", sphere_name)
                CMD.set("sphere_transparency", 0.5, sphere_name)  # Make the sphere semi-transparent
                CMD.color("yellow", sphere_name)  # Set the color of the sphere
                # Orient the view to the protein and sphere
                CMD.orient()

                show_stylish_messagebox(self, "Sphere Created", "Sphere created at ({}, {}, {}) with radius {}.".format(x, y, z, radius))
            except Exception as e:
                show_stylish_messagebox(self, "Error", "An error occurred while creating the sphere: {}".format(str(e)))
        def choose_cocrystal_ligand_and_calculate_radius(ligand_input):
            try:
                # Parse the input (e.g., "SAG_A")
                global x, y, z, radius 
                ligand_name, chain_id = ligand_input.split("_")

                # Parse the PDB file
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("protein", pdb_)

                # Iterate through the structure to find the specified ligand
                for model in structure:
                    chain = model[chain_id]  # Select the specified chain
                    for residue in chain:
                        if residue.resname == ligand_name and residue.id[0] != " ":  # Match ligand name and ensure it's a heteroatom
                            # Extract coordinates of all atoms in the ligand
                            atom_coords = [atom.coord for atom in residue.get_atoms()]
                            
                            # Calculate the centroid of the ligand
                        
                            x = sum(coord[0] for coord in atom_coords) / len(atom_coords)
                            y = sum(coord[1] for coord in atom_coords) / len(atom_coords)
                            z = sum(coord[2] for coord in atom_coords) / len(atom_coords)

                            # Calculate the radius (maximum distance from centroid to any atom)
                            radiusog = max(
                                ((coord[0] - x) ** 2 + (coord[1] - y) ** 2 + (coord[2] - z) ** 2) ** 0.5
                                for coord in atom_coords
                            )
                            buffer = self.lineEdit_5.text()
                            if buffer:
                                radius = radiusog + float(buffer)
                                chain.detach_child(residue.id)

                                # Save the modified PDB file
                                io = PDBIO()
                                io.set_structure(structure)
                                io.save(pdb_)

                            return x, y, z, radius

                # If the ligand is not found, show an error message
                show_stylish_messagebox(Form, "Error", "Ligand {} in chain {} not found.".format(ligand_name, chain_id))

            except Exception as e:
                show_stylish_messagebox(Form, "Error", "An error occurred: {}".format(str(e)))
        def ret_coord():
            try:
                
                selected_items = self.listWidget.selectedItems()
                if selected_items:
                    selected_item_text = selected_items[0].text()
                    x,y,z,radius = choose_cocrystal_ligand_and_calculate_radius(selected_item_text)
                    protein_file = os.path.join(protein_folder, os.listdir(protein_folder)[0])
                    man = os.path.basename(protein_file)
                    base_name = os.path.splitext(man)[0]
                    sanitized_name = base_name[:4]  # Limit to the first 4 characters
                    protein_name = "Protein-{}".format(sanitized_name)
                    if protein_name not in CMD.get_object_list():
                        CMD.load(protein_file, protein_name)
                        CMD.show("cartoon", protein_name)  # Show the protein in "cartoon" representation
                    sphere_name = "binding_site_sphere"
                    CMD.pseudoatom(
                        sphere_name,
                        pos=[x, y, z],  # Position of the sphere
                        vdw=radius       # Radius of the sphere
                    )

                    # Show the sphere as a surface
                    CMD.show("spheres", sphere_name)
                    CMD.set("sphere_transparency", 0.5, sphere_name)  # Make the sphere semi-transparent
                    CMD.color("yellow", sphere_name)  # Set the color of the sphere

                    # Enable both the heteroatom and the parent protein
                    CMD.enable(protein_name)
                    CMD.enable(sphere_name)

                    # Orient the view to include both the protein and the sphere
                    CMD.orient()
                    global sitemethod
                    sitemethod = 'Co-crystal'
                    show_stylish_messagebox(Form, "PandaDock", "Coordinates: ({}, {}, {}), Radius: {}".format(x, y, z, radius))
                    BindingButton.setEnabled(False)
                    DockingButton.setEnabled(True)  # Enable the Binding Site button
                    dialogfromx.close()  # Close the dialog
                else:
                    show_stylish_messagebox(Form, "No Item Selected", "Please select an item from the list.")
            except Exception as e:
                show_stylish_messagebox(Form, "PandaDock", str(e))
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(30, 330, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton.clicked.connect(ret_coord)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 411, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(240, 70, 20, 301))
        self.line.setLineWidth(5)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(410, 30, 591, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.listWidget_2 = QtWidgets.QListWidget(Form)
        self.listWidget_2.setGeometry(QtCore.QRect(390, 111, 131, 211))
        self.listWidget_2.setObjectName("listWidget_2")
        parser = PDBParser(QUIET=True)
        for file in os.listdir(protein_folder):
            if file.endswith(".pdb"):
                pdb_ = os.path.join(protein_folder, file)
                # Load the PDB file
        structure = parser.get_structure('protein', pdb_)
        chain_resid_resname_strings = set()
            
        # Iterate over all models in the structure (assuming a single model)
        for model in structure:
            # Iterate over all chains in the model
            for chain in model:
                chain_id = chain.id
                # Iterate over all residues in the chain
                for residue in chain:
                    residue_id = residue.id
                    resname = residue.resname
                    # Include the insertion code in the string
                    chain_resid_resname_string = "{}:{}{}:{}".format(chain_id, residue_id[1], residue_id[2], resname)
                    
                    chain_resid_resname_strings.add(chain_resid_resname_string)
                    

        sorted_resid_resname = sorted(chain_resid_resname_strings, key=lambda x: int(x.split(":")[1]))
        self.listWidget_2.addItems(sorted_resid_resname)

        

            
         
        def gencoord():
           try:
                

                global x, y, z, radius 
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("protein", pdb_)

                x_coords = []
                y_coords = []
                z_coords = []

                for i in range(self.listWidget_3.count()):
                    item_text = self.listWidget_3.item(i).text()  # Get the text from QListWidget item
                    chain_id, res_num, res_name = item_text.split(":")  # Split the string
                    res_num = int(res_num)  # Convert residue number to integer

                    for model in structure:
                        chain = model[chain_id]  # Select chain
                        if res_num in chain:
                            residue = chain[res_num]
                            if "CA" in residue:
                                # Use the CA atom if it exists
                                ca_atom = residue["CA"]
                                x, y, z = ca_atom.coord  # Extract coordinates
                            else:
                                # Fallback: Calculate the centroid of all atoms in the residue
                                atom_coords = [atom.coord for atom in residue.get_atoms()]
                                x = sum(coord[0] for coord in atom_coords) / len(atom_coords)
                                y = sum(coord[1] for coord in atom_coords) / len(atom_coords)
                                z = sum(coord[2] for coord in atom_coords) / len(atom_coords)

                            # Append the coordinates
                            x_coords.append(x)
                            y_coords.append(y)
                            z_coords.append(z)
                            break
                max_x = max(x_coords)   
                min_x = min(x_coords) 
                max_y = max(y_coords) 
                min_y = min(y_coords)
                max_z = max(z_coords)
                min_z = min(z_coords)   
                lengthx = (max_x - min_x) + 1
                lengthy = (max_y - min_y) + 1
                lengthz = (max_z - min_z) + 1
                lenx = max_x + min_x
                leny = max_y + min_y
                lenz = max_z + min_z
                cenx = lenx/2
                ceny = leny/2
                cenz = lenz/2
                roundx = round(abs(lengthx))
                roundy = round(abs(lengthy))
                roundz = round(abs(lengthz))
                radius = max(roundx, roundy, roundz) / 2
                added_radius = radius + 2
                absradius = abs(radius)
                self.lineEdit.setText(str(round(cenx, 3)))
                self.lineEdit_2.setText(str(round(ceny, 3)))
                self.lineEdit_3.setText(str(round(cenz, 3)))
                self.lineEdit_4.setText(str(absradius))
               
             
           except Exception as e:
              show_stylish_messagebox(Form, "PandaDock", str(e))
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(310, 80, 51, 41))
        self.lineEdit.setObjectName("lineEdit")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(280, 90, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(QtGui.QFont.Bold)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(280, 140, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(QtGui.QFont.Bold)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(310, 130, 51, 41))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(280, 190, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(QtGui.QFont.Bold)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.lineEdit_3 = QtWidgets.QLineEdit(Form)
        self.lineEdit_3.setGeometry(QtCore.QRect(310, 180, 51, 41))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(310, 240, 51, 41))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setGeometry(QtCore.QRect(280, 250, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(QtGui.QFont.Bold)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.listWidget_3 = QtWidgets.QListWidget(Form)
        self.listWidget_3.setGeometry(QtCore.QRect(530, 111, 191, 211))
        self.listWidget_3.setObjectName("listWidget_3")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setGeometry(QtCore.QRect(390, 80, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setGeometry(QtCore.QRect(530, 80, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        def item_selected():
  
          selected_items = self.listWidget_2.selectedItems()

          if selected_items:
              selected_item_text = selected_items[0].text()
              self.listWidget_3.addItem(selected_item_text)

        def remove_items():
          selected_items = self.listWidget_3.selectedItems()

          for item in selected_items:
              self.listWidget_3.takeItem(self.listWidget_3.row(item))

        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(390, 330, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton_2.clicked.connect(item_selected)
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(530, 330, 93, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton_3.clicked.connect(remove_items)
        def confrim_coords():
            try:
             
                x = float(self.lineEdit.text())
                y = float(self.lineEdit_2.text())
                z = float(self.lineEdit_3.text())
                radius = float(self.lineEdit_4.text())  
                print("Coordinates: ({}, {}, {}), Radius: {}".format(x, y, z, radius))
                QMessageBox.information(Form, "Coordinates Confirmed", "Coordinates: ({}, {}, {}), Radius: {}".format(x, y, z, radius))
                global sitemethod
                sitemethod = "AminoAcidSphere"
                protein_file = os.path.join(protein_folder, os.listdir(protein_folder)[0])
                man = os.path.basename(protein_file)
                base_name = os.path.splitext(man)[0]
                sanitized_name = base_name[:4]  # Limit to the first 4 characters
                protein_name = "Protein-{}".format(sanitized_name)
                if protein_name not in CMD.get_object_list():
                    CMD.load(protein_file, protein_name)
                    CMD.show("cartoon", protein_name)  # Show the protein in "cartoon" representation
                sphere_name = "binding_site_sphere"
                CMD.pseudoatom(
                    sphere_name,
                    pos=[x, y, z],  # Position of the sphere
                    vdw=radius       # Radius of the sphere
                )

                # Show the sphere as a surface
                CMD.show("spheres", sphere_name)
                CMD.set("sphere_transparency", 0.5, sphere_name)  # Make the sphere semi-transparent
                CMD.color("yellow", sphere_name)  # Set the color of the sphere

                # Enable both the heteroatom and the parent protein
                CMD.enable(protein_name)
                CMD.enable(sphere_name)

                # Orient the view to include both the protein and the sphere
                CMD.orient()
                BindingButton.setEnabled(False) 
                DockingButton.setEnabled(True)
                dialogfromx.close() # Enable the Binding Site button

            except ValueError:
                show_stylish_messagebox(Form, "Invalid Input", "Please enter valid numeric values.")
        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(280, 330, 93, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton_4.clicked.connect(confrim_coords)
        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setGeometry(QtCore.QRect(630, 330, 93, 28))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton_5.clicked.connect(gencoord)
        self.line_3 = QtWidgets.QFrame(Form)
        self.line_3.setGeometry(QtCore.QRect(740, 70, 20, 301))
        self.line_3.setLineWidth(5)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
       
        
        def detectpocket():
            try:
                # Call the detect_pocket function from the main script   
                global sitemethod
                sitemethod = "Detect" 
                show_stylish_messagebox(Form, "Pocket Detection", "Binding Pocket Detection Enabled Successfully.")
                dialogfromx.close()
                BindingButton.setEnabled(False) 
                DockingButton.setEnabled(True)
            except Exception as e:
                show_stylish_messagebox(Form, "Error", "An error occurred during pocket detection: {}".format(str(e)))
        self.pushButton_7 = QtWidgets.QPushButton(Form)
        self.pushButton_7.setGeometry(QtCore.QRect(770, 160, 161, 28))
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton_7.clicked.connect(detectpocket)
        self.label_9 = QtWidgets.QLabel(Form)
        self.label_9.setGeometry(QtCore.QRect(30, 280, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(QtGui.QFont.Bold)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.lineEdit_5 = QtWidgets.QLineEdit(Form)
        self.lineEdit_5.setGeometry(QtCore.QRect(50, 270, 51, 41))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setGeometry(QtCore.QRect(780, 200, 161, 171))
        self.label_10.setText("")
        self.label_10.setPixmap(QtGui.QPixmap(sphere))
        self.label_10.setScaledContents(True)
        self.label_10.setObjectName("label_10")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "PandaDock"))
        self.label.setText(_translate("Form", "Choose Co-Crystal"))
        self.pushButton.setText(_translate("Form", "Confirm"))
        self.label_2.setText(_translate("Form", "Binding Site Configuration"))
        self.lineEdit.setText(_translate("Form", "0"))
        self.label_3.setText(_translate("Form", "X"))
        self.label_4.setText(_translate("Form", "Y"))
        self.lineEdit_2.setText(_translate("Form", "0"))
        self.label_5.setText(_translate("Form", "Z"))
        self.lineEdit_3.setText(_translate("Form", "0"))
        self.lineEdit_4.setText(_translate("Form", "10"))
        self.label_6.setText(_translate("Form", "R"))
        self.label_7.setText(_translate("Form", "Amino Acids"))
        self.label_8.setText(_translate("Form", "Selected"))
        self.pushButton_2.setText(_translate("Form", "Add"))
        self.pushButton_3.setText(_translate("Form", "Remove"))
        self.pushButton_4.setText(_translate("Form", "Confirm"))
        self.pushButton_5.setText(_translate("Form", "Generate"))
        self.pushButton_7.setText(_translate("Form", "Detect Pocket"))
        self.label_9.setText(_translate("Form", "R"))
        self.lineEdit_5.setText(_translate("Form", "4"))
class dialogfrom(QtWidgets.QDialog):
         def __init__(self, parent=None):
          super(dialogfrom, self).__init__(parent)
          self.ui = Ui_Form()
          self.ui.setupUi(self)
          self.setWindowTitle("PandaDock")
          self.setWindowIcon(QIcon(image_icon_path))
          
          

          

         pass  # Remove the incorrectly placed function definition

# Define dialogxfrom at module level for proper accessibility
def dialogxfrom():
    """Create and show the binding site configuration dialog"""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    
    global dialogfromx
    dialogfromx = dialogfrom()
    dialogfromx.setWindowTitle("PandaDock - Binding Site Configuration")
    dialogfromx.setWindowIcon(QIcon(image_icon_path))
    dialogfromx.exec_()

class Ui_Formdock(object):
    def setupUidock(self, dock):
        dock.setObjectName("dock")
        dock.resize(972, 524)
        self.label = QtWidgets.QLabel(dock)
        self.label.setGeometry(QtCore.QRect(30, 60, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Nirmala UI")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.listWidget = QtWidgets.QListWidget(dock)
        self.listWidget.setGeometry(QtCore.QRect(30, 100, 921, 211))
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        def run_exe_vs(parent, args ,ligand_path, protein_file, output_directory, x, y, z, radius):
            # Example: Replace with your actual .exe path
            if not hasattr(parent, "processes"):
              parent.processes = []
            process = QProcess(parent)
            process.setProgram("pandadock")
            process.setArguments(args + ["--ligand-library", ligand_path,"-p", protein_file, "-o", output_directory, "-s", str(x), str(y), str(z), "--grid-radius", str(radius)])
            print(process.arguments())
            process.setProcessChannelMode(QProcess.MergedChannels)
            process.readyReadStandardOutput.connect(lambda: log_text_edit.append(process.readAllStandardOutput().data().decode()))
            process.readyReadStandardError.connect(lambda: log_text_edit.append("<span style='color:red;'>{}</span>".format(process.readAllStandardError().data().decode())))
            process.errorOccurred.connect(lambda err: log_text_edit.append("<span style='color:red;'>Process error: {}</span>".format(err)))
            process.finished.connect(lambda: log_text_edit.append("<span style='color:green;'>Process finished.</span>"))
            process.start()
            parent.processes.append(process)

        self.listWidget.addItem(item)
        self.listWidget.setStyleSheet("""
            QListWidget {
                background-color: #181818;
                color: #e0e0e0;
                border: 1px solid #333;
                font-size: 15px;
                font-family: 'Consolas', 'Segoe UI', monospace;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                background: transparent;
                padding: 8px 4px;
                border-bottom: 1px solid #222;
            }
            QListWidget::item:selected {
                background: #4CAF50;
                color: #fff;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background: #333;
                color: #fff;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #222;
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal  {
                background: #4CAF50;
                min-height: 24px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: #388E3C;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, 
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {                          
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(dock)
        self.plainTextEdit.setGeometry(QtCore.QRect(30, 360, 921, 111))
        
        self.dictx = { 
            "Fast Mode - PandaCore": "--mode fast --scoring pandacore --num-poses 9 --exhaustiveness 8",
            "Balanced Mode - PandaML": "--mode balanced --scoring pandaml --num-poses 20 --exhaustiveness 16 --ml-rescoring",
            "Precise Mode - PandaPhysics": "--mode precise --scoring pandaphysics --num-poses 50 --exhaustiveness 32 --side-chain-flexibility",
            "Virtual Screening - Fast": "--mode fast --scoring pandacore --num-poses 5 --exhaustiveness 4 --save-poses",
            "Virtual Screening - Balanced": "--mode balanced --scoring pandaml --num-poses 10 --exhaustiveness 8 --ml-rescoring --save-poses",
            "High-Precision Docking": "--mode precise --scoring pandaphysics --num-poses 100 --exhaustiveness 64 --side-chain-flexibility --save-complex",
            "Flexible Residue Docking": "--mode balanced --scoring pandaml --num-poses 20 --exhaustiveness 16 --side-chain-flexibility --ml-rescoring",
            "GPU-Accelerated Docking": "--mode fast --scoring pandacore --num-poses 20 --exhaustiveness 16 --gpu",
            "Complete Analysis Suite": "--mode balanced --scoring pandaml --num-poses 20 --exhaustiveness 16 --ml-rescoring --pandamap --pandamap-3d --all-outputs --plots --interaction-maps",
            "Metal Complex Docking": "--mode precise --scoring pandaphysics --num-poses 50 --exhaustiveness 32 --side-chain-flexibility --save-complex --pandamap",
        }
        font = QtGui.QFont()
        font.setPointSize(11)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setPlainText("")
        self.plainTextEdit.setObjectName("plainTextEdit")
        
        def choose():
            try:
                self.plainTextEdit.clear()
                clicked = self.listWidget.currentItem()
                if clicked:
                    selected_text = clicked.text()
                    if selected_text in self.dictx:
                        command = self.dictx[selected_text]
                        sitemethod_val = globals().get("sitemethod", None)
                        
                        # Add flexible residue support if available
                        if hasattr(self, 'flexres_string') and self.flexres_string:
                            command += " --flexible-residues \"{}\"".format(self.flexres_string)
                        
                        if sitemethod_val == 'Detect':
                            full_command = command  # Pocket detection is now handled by the scoring function
                        else:
                            if self.radioButton.isChecked():
                                full_command = "{} --gpu".format(command)
                            else:
                                full_command = command
                        self.plainTextEdit.setPlainText(full_command)
                    else:
                        self.plainTextEdit.setPlainText("Command not found.")
            except Exception as e:
                import traceback
                show_stylish_messagebox(dock, "Error", "An error occurred: {}\n{}".format(str(e), traceback.format_exc()))

        def run_docking_end():
            
                show_stylish_messagebox(dock, "Docking", "Click OK to Start Simulations.")
                command = self.plainTextEdit.toPlainText()
                
                # Check if this is a virtual screening task
                is_virtual_screening = "Virtual Screening" in self.listWidget.currentItem().text() if self.listWidget.currentItem() else False
                
                if is_virtual_screening:
                    # For virtual screening, use --screen parameter
                    ligand_path = os.path.join(main_directory, 'Ligand')
                    protein_file = os.path.join(protein_folder, os.listdir(protein_folder)[0])
                    output_directory = os.path.join(main_directory, 'output')
                    dialogdockx.close()
                    main_window = dock.parent()  # dock is the dialog, its parent is the main window
                    if main_window:
                        if sitemethod == 'Detect':
                            main_window.run_exe_vs_pocket(
                                command.split(), ligand_path, protein_file, output_directory
                            )
                        else:
                            main_window.run_exe_vs(
                                command.split(), ligand_path, protein_file, output_directory, x, y, z, radius
                            )
                        
                else:
                    # For single ligand docking, use --ligand parameter
                    output_directory = os.path.join(main_directory, "output")
                    protein_file = os.path.join(protein_folder, os.listdir(protein_folder)[0])
                   
                    if os.path.exists(output_directory):
                            shutil.rmtree(output_directory)
                    os.makedirs(output_directory)
                    ligand_queue = [
                            os.path.join(new_folder, ligand_file)
                            for ligand_file in os.listdir(new_folder)
                            if ligand_file.endswith(".sdf") or ligand_file.endswith(".mol")
                        ]
                    print(ligand_queue)
                    dialogdockx.close()
                    main_window = dock.parent() 
                    if main_window:
                        if sitemethod == 'Detect':
                            main_window.process_next_ligand_pocket( command.split(), ligand_queue , protein_file, output_directory ) 
                        else:
                            main_window.process_next_ligand( command.split(), ligand_queue , protein_file, output_directory, x, y, z, radius )
            
        self.pushButton = QtWidgets.QPushButton(dock)
        self.pushButton.setGeometry(QtCore.QRect(860, 480, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton.clicked.connect(run_docking_end)
        self.radioButton = QtWidgets.QRadioButton(dock)
        self.radioButton.setGeometry(QtCore.QRect(140, 320, 95, 31))
        self.radioButton.setObjectName("radioButton")
        self.pushButton_2 = QtWidgets.QPushButton(dock)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 320, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #FFFFFF;
            }
        """)
        self.pushButton_2.clicked.connect(choose)
        
      

        self.retranslateUi(dock)
        QtCore.QMetaObject.connectSlotsByName(dock)

    def retranslateUi(self, dock):
        _translate = QtCore.QCoreApplication.translate
        dock.setWindowTitle(_translate("dock", "dock"))
        self.label.setText(_translate("dock", "Template"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("dock", "Fast Mode - PandaCore"))
        item = self.listWidget.item(1)
        item.setText(_translate("dock", "Balanced Mode - PandaML"))
        item = self.listWidget.item(2)
        item.setText(_translate("dock", "Precise Mode - PandaPhysics"))
        item = self.listWidget.item(3)
        item.setText(_translate("dock", "Virtual Screening - Fast"))
        item = self.listWidget.item(4)
        item.setText(_translate("dock", "Virtual Screening - Balanced"))
        item = self.listWidget.item(5)
        item.setText(_translate("dock", "High-Precision Docking"))
        item = self.listWidget.item(6)
        item.setText(_translate("dock", "Flexible Residue Docking"))
        item = self.listWidget.item(7)
        item.setText(_translate("dock", "GPU-Accelerated Docking"))
        item = self.listWidget.item(8)
        item.setText(_translate("dock", "Complete Analysis Suite"))
        item = self.listWidget.item(9)
        item.setText(_translate("dock", "Metal Complex Docking"))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.pushButton.setText(_translate("dock", "Execute"))
        self.radioButton.setText(_translate("dock", "GPU"))
        self.pushButton_2.setText(_translate("dock", "Choose"))
        

class dialogdock(QtWidgets.QDialog):
         def __init__(self, parent=None):
          super(dialogdock, self).__init__(parent)
          self.ui = Ui_Formdock()
          self.ui.setupUidock(self)
          self.setWindowTitle("PandaDock")
          self.setWindowIcon(QIcon(image_icon_path))
          
          

          

         pass  # Remove the incorrectly placed function definition

# Define dialogxdock at module level for proper accessibility
def dialogxdock():
    """Create and show the docking configuration dialog"""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    
    global dialogdockx, window
    dialogdockx = dialogdock(parent=window)
    dialogdockx.setWindowTitle("PandaDock - Docking Configuration")
    dialogdockx.setWindowIcon(QIcon(image_icon_path))
    dialogdockx.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyMOLOnlyWindow()
    window.closeEvent = show_exit_confirmation
    if getattr(sys, 'frozen', False):
          pyi_splash.close()
    window.show()
    sys.exit(app.exec_())
