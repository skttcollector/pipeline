'''

PIPELINE 

BETA 1.0.0

Project manager for Maya

Ahutor: Lior Ben Horin
All rights reserved (c) 2016 
    
liorbenhorin.ghost.io
liorbenhorin@gmail.com

---------------------------------------------------------------------------------------------

install:

Place the pipeline folder in your maya scripts folder. Run these lines in a python tab in the script editor:
 
from pipeline import pipeline
reload(pipeline)
pipeline.show()

---------------------------------------------------------------------------------------------

You are using PIPELINE on you own risk. 
Things can allways go wrong, and under no circumstances the author
would be responsible for any damages cuesed from the use of this software.
When using this beta program you hearby agree to allow this program to collect 
and send usage data to the author.

---------------------------------------------------------------------------------------------  

The coded instructions, statements, computer programs, and/or related
material (collectively the "Data") in these files are subject to the terms 
and conditions defined by
Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License:
   http://creativecommons.org/licenses/by-nc-nd/4.0/
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt

---------------------------------------------------------------------------------------------  

'''


from PySide import QtCore, QtGui
import os

def set_icons():
    localIconPath = os.path.join(os.path.dirname(__file__), 'icons')
    if not os.path.exists(localIconPath):
        return 
    
    global warning_icon
    global simple_warning_icon
    global massage_icon
    global users_icon
    global archive_icon
    global new_icon
    global logo
    
    warning_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"critical")) 
    simple_warning_icon =  QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"warning"))
    massage_icon =  QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"massage"))
    users_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"users"))
    archive_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"archive"))
    new_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"new"))
    logo = QtGui.QPixmap(os.path.join(localIconPath, "%s.png"%"pipeline_logo"))
    
def warning(icon, title, message ):
    
    if icon == "critical":
        dlg_icon = warning_icon
    elif icon == "warning":
        dlg_icon = simple_warning_icon
    else:
        dlg_icon = warning_icon            
    
    reply = QtGui.QMessageBox()
    reply.setIconPixmap(dlg_icon)

    reply.setText(message)
    #reply.setInformativeText("This is additional information")
    reply.setWindowTitle(title)
    #reply.setDetailedText("The details are as follows:")
    reply.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    
    result = reply.exec_()
    if result == QtGui.QMessageBox.Yes:
        return True
    else:
        return False      
        
def massage(icon, title, message ):
    
    reply = QtGui.QMessageBox()
    
    if icon == "critical":
        reply.setIconPixmap(warning_icon)

    elif icon == "warning":
        reply.setIconPixmap(simple_warning_icon)

    elif icon == "massage":
        reply.setIconPixmap(massage_icon)
   
    reply.setText(message)
    reply.setWindowTitle(title)
    reply.setStandardButtons(QtGui.QMessageBox.Close)
    
    result = reply.exec_()
 
        
set_icons()


class about(QtGui.QDialog):
    def __init__(self, parent = None, title = None):
        super(about, self).__init__(parent)                    

        self.setMaximumWidth(330) 
        self.setMinimumWidth(330)        
        self.setMaximumHeight(300) 

        layout = QtGui.QVBoxLayout(self)

        self.logo_label = QtGui.QLabel()
        self.logo_label.setPixmap(logo.scaled(250,56))         
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)

        self.version_label = QtGui.QLabel("<b>V 1.0</b>")
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.title_label = QtGui.QLabel("<b>A SIMPLE PROJECTS MANAGER FOR MAYA</b>")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.info_label = QtGui.QLabel("<a href='http://pipeline.nnl.tv'><font color='white'>http://pipeline.nnl.tv</font></a><br><br>All rights reserved to Lior Ben Horin 2016")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok,
            QtCore.Qt.Horizontal, self)
        
        buttons.setCenterButtons(True)
        buttons.accepted.connect(self.accept)
        
        layout.addWidget(self.logo_label)
        layout.addWidget(self.version_label)  
        layout.addWidget(HLine())
        layout.addWidget(self.title_label)
        layout.addWidget(self.info_label)
        layout.addWidget(buttons)


class Create_from_selection(QtGui.QDialog):
    def __init__(self, parent = None, title = None):
        super(Create_from_selection, self).__init__(parent)
        
        
        
        self.setMaximumWidth(200) 
        self.setMinimumWidth(200)        
        self.setMaximumHeight(50) 

        self.label = QtGui.QLabel()
        self.label.setPixmap(new_icon)

        layout = QtGui.QVBoxLayout(self)
        self.item_name = QtGui.QLabel(title)
        self.text_input = QtGui.QLineEdit()
        self.include_radio = QtGui.QRadioButton("Include all connections")
        self.include_radio.setChecked(True)
        self.exclude_radio = QtGui.QRadioButton("Include only textures")
        
        

        layout.addWidget(self.item_name)
        layout.addWidget(self.text_input)
        layout.addWidget(self.include_radio)
        layout.addWidget(self.exclude_radio)

        
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def radio_selection(self):
        if self.include_radio.isChecked():
            return "include"
        else:
            return "exclude"

    def result(self):
        return self.text_input.text(), self.radio_selection()
        
class collect_component_options(QtGui.QDialog):
    def __init__(self, parent = None, title = None):
        super(collect_component_options, self).__init__(parent)
        
    
        self.setMaximumWidth(200) 
        self.setMinimumWidth(200)        
        self.setMaximumHeight(50) 

        #self.label = QtGui.QLabel()
        #self.label.setPixmap(archive_icon)

        layout = QtGui.QVBoxLayout(self)
        self.item_name = QtGui.QLabel(title)

        self.include_reference = QtGui.QCheckBox("Include referenced files")
        self.include_reference.setChecked(True)
        self.include_textures = QtGui.QCheckBox("Include textures")
        self.include_textures.setChecked(True)
        
        
        #layout.addWidget(self.label)
        #layout.addStretch()
        layout.addWidget(self.item_name)

        layout.addWidget(HLine())
        layout.addWidget(self.include_reference)
        layout.addWidget(self.include_textures)
        
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def options(self):
        references = False
        textures = False
               
        if self.include_reference.isChecked():
            references = True
        if self.include_textures.isChecked():
            textures = True 
            
        return references, textures  


    def result(self):
        return self.options()        


    
class Login(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        self.setMaximumWidth(200) 
        self.setMinimumWidth(200)        
        self.setMaximumHeight(50) 
        
        self.label = QtGui.QLabel()
        self.label.setPixmap(users_icon)
        
        self.label_user = QtGui.QLabel("Username:")
        self.label_password = QtGui.QLabel("Password:")
        
        self.textName = QtGui.QLineEdit(self)
        self.textName.setMinimumSize(QtCore.QSize(0, 30))
        self.textPass = QtGui.QLineEdit(self)
        self.textPass.setMinimumSize(QtCore.QSize(0, 30))

        self.textPass.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        self.textPass.setEchoMode(QtGui.QLineEdit.Password)
    
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.label)
        layout.addWidget(HLine())
        layout.addWidget(self.label_user)
        layout.addWidget(self.textName)
        layout.addWidget(self.label_password)
        layout.addWidget(self.textPass)
        
        log = QtGui.QPushButton("Login")
        log.setDefault(True)
        
        canc = QtGui.QPushButton("Cancel")
        
       
        buttons = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
        buttons.addButton(log, QtGui.QDialogButtonBox.AcceptRole)
        buttons.addButton(canc, QtGui.QDialogButtonBox.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        

    def result(self):
        return self.textName.text(), self.textPass.text()


        
class playblast_options(QtGui.QDialog):
    def __init__(self, parent = None, title = None, hud = True, offscreen = True, formats = None, format = "movie", compressions = None, compression = "H.264", scale = 50):
        super(playblast_options, self).__init__(parent)
        
    
        self.setMaximumWidth(200) 
        self.setMinimumWidth(200)        
        self.setMaximumHeight(50) 


        layout = QtGui.QVBoxLayout(self)
        self.item_name = QtGui.QLabel(title)

        self.include_hud = QtGui.QCheckBox("Record HUD")
        self.include_hud.setChecked(hud)
        
        self.render_offscreen = QtGui.QCheckBox("Record Offscreen")
        self.render_offscreen.setChecked(offscreen)

        
        self.scaleLayout = QtGui.QHBoxLayout(self)
        
        self.scale_label = QtGui.QLabel("Scale:")
        
        self.scaleSlider = QtGui.QSlider()
        self.scaleSlider.setOrientation(QtCore.Qt.Horizontal)
        self.scaleSlider.setMinimum(10)
        self.scaleSlider.setMaximum(100)
        self.scaleSlider.setValue(scale)       
        
        self.scaleSpinbox = QtGui.QSpinBox()
        self.scaleSpinbox.setMinimum(10)
        self.scaleSpinbox.setMaximum(100)
        self.scaleSpinbox.setValue(scale)
        
        self.scaleSlider.valueChanged.connect(self.sacle_spinbox_value)
        self.scaleSpinbox.valueChanged.connect(self.sacle_slider_value)

        
        self.scaleLayout.addWidget(self.scaleSpinbox)
        self.scaleLayout.addWidget(self.scaleSlider)
        
        self.format_label = QtGui.QLabel("Format:")    
            
        self.format_combo = QtGui.QComboBox()
        self.format_combo.setEditable(False)
        if formats:
            self.format_combo.addItems(formats)
        else:
            self.format_combo.addItems([format])
                  
        i = self.format_combo.findText(format, QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.format_combo.setCurrentIndex(i)

        self.compression_label = QtGui.QLabel("Compression:")  

        self.compression_combo = QtGui.QComboBox()
        self.compression_combo.setEditable(False)
        if formats:
            self.compression_combo.addItems(compressions)
        else:
            self.compression_combo.addItems([compression])
                  
        i = self.compression_combo.findText(compression, QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.compression_combo.setCurrentIndex(i)

        
        layout.addWidget(self.item_name)

        layout.addWidget(HLine())
        layout.addWidget(self.include_hud)
        layout.addWidget(self.render_offscreen)
        layout.addWidget(self.scale_label)
        layout.addLayout(self.scaleLayout)
        layout.addWidget(self.format_label)
        layout.addWidget(self.format_combo)
        layout.addWidget(self.compression_label)
        layout.addWidget(self.compression_combo)
                
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def sacle_spinbox_value(self,value):
        self.scaleSpinbox.setValue(value)

    def sacle_slider_value(self,value):
        self.scaleSlider.setValue(value)
    
    def options(self):
        options = {}
        hud = False
        offscreen = False
        
        if self.include_hud.isChecked():
            hud = True
        if self.render_offscreen.isChecked():
            offscreen = False
        
        options["hud"] = hud
        options["offscreen"] = offscreen
        options["format"] = self.format_combo.currentText() 
        options["compression"] = self.compression_combo.currentText()
        options["scale"] = self.scaleSpinbox.value()
            
        return options
        
    def result(self):
        return self.options()   


def HLine():
    toto = QtGui.QFrame()
    toto.setFrameShape(QtGui.QFrame.HLine)
    toto.setFrameShadow(QtGui.QFrame.Sunken)
    return toto    