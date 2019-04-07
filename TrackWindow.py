import sys
from PySide.QtCore import *
from PySide.QtGui import *

import TrackFunctions as TF

class TrackWindow(QDialog):
    def __init__(self, parent=None):
        super(TrackWindow, self).__init__(parent)
        self.trackFunctions = TF.TrackFunctions()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("TrackWindow")
        self.initUI()
        self.boolRecord = False
        self.trackSaved = False
        self.trackName = ""
        self.channel = 0
        self.TIMER_AMOUNT_MINUTES = 5
         

    def initUI(self):
        ## Returns the list of instruments
        self.instruments = self.trackFunctions.getInstrumentList()

        self.__initWidgets__()

        deviceLayout = QGridLayout()

        recordTimerGridLayout = QGridLayout()
        grpBoxNotesGridLayout = QGridLayout()
        grpBoxPatternGridLayout = QGridLayout()
        grpBoxSettingsGridLayout = QGridLayout()

        deviceLayout.addWidget(self.frameTimer,0,0)
        deviceLayout.addWidget(self.grpBoxNotes,1,0)
        deviceLayout.addWidget(self.grpBoxPattern,0,1,0,1)
        deviceLayout.addWidget(self.grpBoxSettings,2,0)

        recordTimerGridLayout.addWidget(self.btnRecord,0,0)
        recordTimerGridLayout.addWidget(self.lblTimer,0,1)
        recordTimerGridLayout.addWidget(self.lblTimerConstant,0,2)

        grpBoxNotesGridLayout.addWidget(self.btnC,1,0)
        grpBoxNotesGridLayout.addWidget(self.btnCSharp,0,1)
        grpBoxNotesGridLayout.addWidget(self.btnD,1,2)
        grpBoxNotesGridLayout.addWidget(self.btnDSharp,0,3)
        grpBoxNotesGridLayout.addWidget(self.btnE,1,4)
        grpBoxNotesGridLayout.addWidget(self.btnF,1,5)
        grpBoxNotesGridLayout.addWidget(self.btnFSharp,0,6)
        grpBoxNotesGridLayout.addWidget(self.btnG,1,7)
        grpBoxNotesGridLayout.addWidget(self.btnGSharp,0,8)
        grpBoxNotesGridLayout.addWidget(self.btnA,1,9)
        grpBoxNotesGridLayout.addWidget(self.btnASharp,0,10)
        grpBoxNotesGridLayout.addWidget(self.btnB,1,11)

        grpBoxPatternGridLayout.addWidget(self.lstPattern,0,0,3,4)
        grpBoxPatternGridLayout.addWidget(self.btnSave,4,0)
        grpBoxPatternGridLayout.addWidget(self.btnRedo,4,1)
        grpBoxPatternGridLayout.addWidget(self.txtName,5,0,2,0)

        grpBoxSettingsGridLayout.addWidget(self.lblInstrument,0,0)
        grpBoxSettingsGridLayout.addWidget(self.comboInstruments,0,1)
        grpBoxSettingsGridLayout.addWidget(self.lblVelocity,1,0)
        grpBoxSettingsGridLayout.addWidget(self.velocitySlider,1,1)
        grpBoxSettingsGridLayout.addWidget(self.lblVelocityCounter,1,2)
        grpBoxSettingsGridLayout.addWidget(self.lblOctave,2,0)
        grpBoxSettingsGridLayout.addWidget(self.comboOctave,2,1)
        grpBoxSettingsGridLayout.addWidget(self.checkPercussion,2,2)
        grpBoxSettingsGridLayout.addWidget(self.lblChannel,3,0)
        grpBoxSettingsGridLayout.addWidget(self.comboChannel,3,1)

        self.grpBoxNotes.setLayout(grpBoxNotesGridLayout)
        self.grpBoxPattern.setLayout(grpBoxPatternGridLayout)
        self.grpBoxSettings.setLayout(grpBoxSettingsGridLayout)
        self.frameTimer.setLayout(recordTimerGridLayout)
        

        self.setLayout(deviceLayout)
        print "New track window created!"

    def __initWidgets__(self):
        ##Toolbar section
        self.btnRecord = QPushButton("Record",self)
        self.btnRecord.setCheckable(True)
        
        ## Timer
        self.initTimer()
        self.lblTimer = QLabel("00:00:000")
        self.lblTimerConstant = QLabel("The maximum recording time for each track is 5 minutes")

        ## Group Notes
        self.grpBoxNotes = QGroupBox("Notes")
        self.btnC = QPushButton('C', self)
        self.btnCSharp = QPushButton('C#', self)
        self.btnD = QPushButton('D', self)
        self.btnDSharp = QPushButton('D#', self)
        self.btnE = QPushButton('E', self)
        self.btnF = QPushButton('F', self)
        self.btnFSharp = QPushButton('F#', self)
        self.btnG = QPushButton('G', self)
        self.btnGSharp = QPushButton('G#', self)
        self.btnA = QPushButton('A', self)
        self.btnASharp = QPushButton('A#', self)
        self.btnB = QPushButton('B', self)
        
        ## Group Pattern
        self.grpBoxPattern = QGroupBox("Pattern")
        self.lstPattern = QListView()
        
        self.itemModel = QStandardItemModel(self.lstPattern)
        self.lstPattern.setModel(self.itemModel)

        self.btnSave = QPushButton("Save Track", self)
        self.btnSave.setEnabled(False)
        self.btnRedo = QPushButton("Redo Track", self)
        self.txtName = QLineEdit()
        self.txtName.setPlaceholderText("Enter Track Name")

        ## Group Settings
        self.grpBoxSettings = QGroupBox("Note Settings")
        self.lblVelocity = QLabel("Velocity (0-127):")
        self.velocitySlider = QSlider(Qt.Horizontal, self)
        self.velocitySlider.setMaximum(127)
        self.velocitySlider.setMinimum(1)
        self.velocitySlider.setValue(50)
        self.lblVelocityCounter = QLabel()
        self.lblOctave = QLabel("Octave (1-10):")
        self.comboOctave = QComboBox(self)
        for i in range(1,10+1):
            self.comboOctave.addItem(str(i))
        self.lblInstrument = QLabel("Instrument")
        self.comboInstruments = QComboBox()
        for i in range(len(self.instruments)):
            self.comboInstruments.addItem(self.instruments[i])
        self.checkPercussion = QCheckBox("Percussion")
        self.lblChannel = QLabel("Channel", self)
        self.comboChannel = QComboBox(self)
        for i in range(0,15+1):
            if i != 9:
                self.comboChannel.addItem(str(i))

        ## Set the buttons to there actions
        self.setClickEvents()

    def initTimer(self):
        ## Timer
        self.frameTimer = QFrame()
        self.frameTimer.setFrameShape = QFrame.NoFrame
        self.timer = QTimer(self)
        self.time = QTime(0,0,0,0)
        self.timer.timeout.connect(self.timerFunction)

    def setClickEvents(self):
        ## Set Instrument change action
        self.comboInstruments.currentIndexChanged.connect(lambda:self.action_InstrumentChange(self.comboInstruments))
        ## Set percussion checkbox
        self.checkPercussion.stateChanged.connect(self.action_PercussionChange)
        ## Set Record button
        self.btnRecord.clicked[bool].connect(self.action_Record)
        ## Set Save button
        self.btnSave.clicked.connect(self.action_SaveTrack)
        ## Set Redo button
        self.btnRedo.clicked[bool].connect(self.action_RedoTrack)
        ## Set Channel
        self.comboChannel.currentIndexChanged.connect(lambda:self.action_channelChange(self.comboChannel))
        self.txtName.textChanged.connect(self.action_changeText)
        ## Set note buttons
        self.btnC.pressed.connect(lambda:self.action_on_press(self.btnC))
        self.btnC.released.connect(lambda:self.action_on_released(self.btnC))


        self.btnCSharp.pressed.connect(lambda:self.action_on_press(self.btnCSharp))
        self.btnCSharp.released.connect(lambda:self.action_on_released(self.btnCSharp))


        self.btnD.pressed.connect(lambda:self.action_on_press(self.btnD))
        self.btnD.released.connect(lambda:self.action_on_released(self.btnD))


        self.btnDSharp.pressed.connect(lambda:self.action_on_press(self.btnDSharp))
        self.btnDSharp.released.connect(lambda:self.action_on_released(self.btnDSharp))


        self.btnE.pressed.connect(lambda:self.action_on_press(self.btnE))
        self.btnE.released.connect(lambda:self.action_on_released(self.btnE))


        self.btnF.pressed.connect(lambda:self.action_on_press(self.btnF))
        self.btnF.released.connect(lambda:self.action_on_released(self.btnF))


        self.btnFSharp.pressed.connect(lambda:self.action_on_press(self.btnFSharp))
        self.btnFSharp.released.connect(lambda:self.action_on_released(self.btnFSharp))


        self.btnG.pressed.connect(lambda:self.action_on_press(self.btnG))
        self.btnG.released.connect(lambda:self.action_on_released(self.btnG))


        self.btnGSharp.pressed.connect(lambda:self.action_on_press(self.btnGSharp))
        self.btnGSharp.released.connect(lambda:self.action_on_released(self.btnGSharp))


        self.btnA.pressed.connect(lambda:self.action_on_press(self.btnA))
        self.btnA.released.connect(lambda:self.action_on_released(self.btnA))


        self.btnASharp.pressed.connect(lambda:self.action_on_press(self.btnASharp))
        self.btnASharp.released.connect(lambda:self.action_on_released(self.btnASharp))


        self.btnB.pressed.connect(lambda:self.action_on_press(self.btnB))
        self.btnB.released.connect(lambda:self.action_on_released(self.btnB))


    def timerFunction(self):
        self.time = self.time.addMSecs(1)
        self.lblTimer.setText(self.time.toString("mm:ss:zzz"))
        if self.time.minute() == self.TIMER_AMOUNT_MINUTES:
            self.timer.stop()
            self.boolRecord = False
            self.btnRecord.setEnabled(False)
            self.btnRedo.setEnabled(True)
            
            if self.itemModel.rowCount() > 0 and len(self.txtName.text()) > 0:
                self.btnSave.setEnabled(True)  

    
    @Slot()
    def action_on_press(self, e):
        note = self.findCorrectNote(e.text())
        time = self.calculateCorrectTime(self.time.minute(),self.time.second(), self.time.msec())
        self.trackFunctions.playNote(self.comboInstruments.currentIndex(), self.channel, note, self.velocitySlider.value(), self.boolRecord, time)

        print(e.text() + " was pressed")

    @Slot()
    def action_on_released(self, e):
        note = self.findCorrectNote(e.text())
        time = self.calculateCorrectTime(self.time.minute(),self.time.second(), self.time.msec())
        self.trackFunctions.stopNote(note, self.velocitySlider.value(), self.channel, self.boolRecord, time)

        ## For the list view
        if self.boolRecord:
            item = QStandardItem(e.text())
            self.itemModel.appendRow(item)
            ##self.btnSave.setEnabled(True)

        print(e.text() + " button was released")

    ## Gets the correct note from the correct note press
    def findCorrectNote(self, e):
        note = -1
        if e == 'C':
            note = 0
        elif e == 'C#':
            note = 1
        elif e == 'D':
            note = 2
        elif e == 'D#':
            note = 3
        elif e == 'E':
            note = 4
        elif e == 'F':
            note = 5
        elif e == 'F#':
            note = 6
        elif e == 'G':
            note = 7
        elif e == 'G#':
            note = 8
        elif e == 'A':
            note = 9
        elif e == 'A#':
            note = 10
        elif e == 'B':
            note = 11
        else:
            note = -1

        return note + ((int(self.comboOctave.currentText()) - 1) * 12)

    def calculateCorrectTime(self, mins, secs, mSec):
        seconds = (mins * 60) + secs + (float(mSec) / 1000)
        return seconds

    def keyPressEvent(self, e):
        if e.isAutoRepeat():
            return
        ## Keys for playing notes
        if e.key() == Qt.Key_A:
            self.action_on_press(self.btnC)
        if e.key() == Qt.Key_W:
            self.action_on_press(self.btnCSharp)
        if e.key() == Qt.Key_S:
            self.action_on_press(self.btnD)
        if e.key() == Qt.Key_E:
            self.action_on_press(self.btnDSharp)
        if e.key() == Qt.Key_D:
            self.action_on_press(self.btnE)
        if e.key() == Qt.Key_F:
            self.action_on_press(self.btnF)
        if e.key() == Qt.Key_T:
            self.action_on_press(self.btnFSharp)
        if e.key() == Qt.Key_G:
            self.action_on_press(self.btnG)
        if e.key() == Qt.Key_Y:
            self.action_on_press(self.btnGSharp)
        if e.key() == Qt.Key_H:
            self.action_on_press(self.btnA)
        if e.key() == Qt.Key_U:
            self.action_on_press(self.btnASharp)
        if e.key() == Qt.Key_J:
            self.action_on_press(self.btnB)

        ## Changing Octaves
        if e.key() == Qt.Key_PageUp:
            index = self.comboOctave.currentIndex()
            if index < 10 - 1:
                self.comboOctave.setCurrentIndex(index+1)
        if e.key() == Qt.Key_PageDown:
            index = self.comboOctave.currentIndex()
            if index > 1 - 1:
                self.comboOctave.setCurrentIndex(index-1)
        e.accept()

    def keyReleaseEvent(self, e):
        if e.isAutoRepeat():
            return
        ## Keys for playing notes
        if e.key() == Qt.Key_A:
            self.action_on_released(self.btnC)
        if e.key() == Qt.Key_W:
            self.action_on_released(self.btnCSharp)
        if e.key() == Qt.Key_S:
            self.action_on_released(self.btnD)
        if e.key() == Qt.Key_E:
            self.action_on_released(self.btnDSharp)
        if e.key() == Qt.Key_D:
            self.action_on_released(self.btnE)
        if e.key() == Qt.Key_F:
            self.action_on_released(self.btnF) 
        if e.key() == Qt.Key_T:
            self.action_on_released(self.btnFSharp)
        if e.key() == Qt.Key_G:
            self.action_on_released(self.btnG)
        if e.key() == Qt.Key_Y:
            self.action_on_released(self.btnGSharp)
        if e.key() == Qt.Key_H:
            self.action_on_released(self.btnA)
        if e.key() == Qt.Key_U:
            self.action_on_released(self.btnASharp)
        if e.key() == Qt.Key_J:
            self.action_on_released(self.btnB)
        e.accept()
    
    def action_Record(self, e):
        sender = self.sender()
        if e == True:
            self.boolRecord = True
            self.timer.start(1)
            self.btnRedo.setEnabled(False)
            self.btnSave.setEnabled(False)
        else:
            self.boolRecord = False
            self.timer.stop()
            self.btnRedo.setEnabled(True)
            if len(self.txtName.text()) > 0:
                self.btnSave.setEnabled(True)

    def action_SaveTrack(self):
        print("Saving track")
        self.timer.stop()
        self.setTrackName()
        self.trackFunctions.saveTrack()
        self.trackFunctions.destroy()
        TrackWindow.close(self)
    
    def setTrackName(self):
        self.trackName = self.txtName.text()

    def getTrackName(self):
        return self.trackName

    def action_RedoTrack(self):
        print("Redo Track")
        self.trackFunctions.redoTrack()
        self.itemModel.clear()
        self.btnRecord.setEnabled(True)
        self.lblTimer.setText("00:00:000")
        self.initTimer()

    def action_changeText(self):
        if not self.boolRecord and self.itemModel.rowCount() > 0:
            self.btnSave.setEnabled(True)
        else:
            self.btnSave.setEnabled(False)

    def closeEvent(self, event):
        self.trackFunctions.redoTrack()
        self.trackFunctions.destroy()
        print "Quitted"

    def action_PercussionChange(self):
        if self.checkPercussion.isChecked():
            self.comboOctave.clear()
            for i in range(3,8 + 1):
                self.comboOctave.addItem(str(i))
                self.channel = 9
        else:
            self.comboOctave.clear()
            for i in range(1,10+1):
                self.comboOctave.addItem(str(i))
                self.channel = (int(self.comboChannel.currentText()))

    @Slot()
    def action_channelChange(self, e):
        self.channel = (int(self.comboChannel.currentText()))

    @Slot()
    def action_InstrumentChange(self, e):
        time = self.calculateCorrectTime(self.time.minute(),self.time.second(), self.time.msec())
        self.trackFunctions.setInstrument(time, self.channel, e.currentIndex())

    def getTrack(self):
        track = self.trackFunctions.getTrack()
        return track
