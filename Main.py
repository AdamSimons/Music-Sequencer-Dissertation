import sys
from PySide.QtCore import *
from PySide.QtGui import *
import wave
import os
import mido
import io
from pydub import AudioSegment

import TrackWindow as TW
import RecordingFunctions as RW
import DeleteWindow as DW

class Thread(QRunnable):
    def __init__(self, function, *args):
        super(Thread, self).__init__()
        self._function = function
        self._arguments = args

    def run(self):
        ##print self._arguments
        self._function(*self._arguments)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.minimumSizeHint()
        self.setWindowTitle("Music Sequencer")
        self.setWindowIcon(QIcon('Images/7_7th.png'))

        self.midTrack = mido.MidiFile(type=1)

        self.MAX_MIDI_TRACKS = 5
        self.MAX_AUDIO_TRACKS = 2
        self.audioTracks = []
        self.midiTracks = []

        self.midiTrackNames = []
        self.audioTrackNames = []
        
        self.sounds = []
        self.soundsName = []
        self.threadPool = QThreadPool()
        print "Max threads of this system is:", self.threadPool.maxThreadCount()
        self.recordingFunctions = RW.RecordingFunctions()


        self.image = QLabel(self)
        print(os.getcwd())
        pixMap = QPixmap("Images/0_7th.png")
        pixMap = pixMap.scaled(250,250)
        self.image.setPixmap(pixMap)
        
        self.image.show()


        self.lblAudioTracksRemaining = QLabel("No. of Audio Tracks Remaining:"+str(self.MAX_AUDIO_TRACKS-len(self.audioTracks)), self)
        self.lblMIDITracksRemaining = QLabel("No. of MIDI Tracks Remaining:"+str(self.MAX_MIDI_TRACKS-len(self.midiTracks)), self)
        
        centralWidget = QWidget(self)
        self.gridLayout = QGridLayout(centralWidget)
        
        self.gridLayout.addWidget(self.image,0,0)
        self.gridLayout.addWidget(self.lblAudioTracksRemaining,1,0)
        self.gridLayout.addWidget(self.lblMIDITracksRemaining,2,0)
        self.setCentralWidget(centralWidget)

        
        ## Create Tool bar
        self.iconToolBar = self.addToolBar("Toolbar")
        self.iconToolBar.setMovable(False)
        self.iconToolBar.setContextMenuPolicy(Qt.PreventContextMenu)

        playButton = QAction("Play", self)
        playButton.triggered.connect(self.action_play)

        stopButton = QAction("Stop", self)
        stopButton.triggered.connect(self.action_stop)
        
        self.recordButton = QAction("Record", self)
        self.recordButton.triggered.connect(self.action_record)

        self.newTrackButton = QAction("Add New Track",self)
        self.newTrackButton.triggered.connect(self.action_newTrack)

        self.deleteTrackButton = QAction("Delete Track", self)
        self.deleteTrackButton.triggered.connect(self.action_deleteTrack)

        ## Add buttons to tool bar
        self.iconToolBar.addAction(playButton)
        self.iconToolBar.addAction(stopButton)
        self.iconToolBar.addAction(self.recordButton)
        self.iconToolBar.addSeparator()
        self.iconToolBar.addAction(self.newTrackButton)
        self.iconToolBar.addAction(self.deleteTrackButton)

        self.initialiseMenu()
        
        


    def setImage(self):
        trackCount = len(self.audioTracks) + len(self.midiTracks)
        pixMap = QPixmap("Images/"+str(trackCount)+"_7th.png")
        pixMap = pixMap.scaled(250,250)
        
        self.image.setPixmap(pixMap)
        self.image.update()
        
        
    def action_deleteTrack(self):
        print("Delete Track")

        self.deleteWindow = DW.DeleteWindow(self,self.audioTrackNames,self.midiTrackNames,self.midiTracks, self.audioTracks)
        self.deleteWindow.exec_()
        updatedAudioList = self.deleteWindow.getAudioNames()
        updatedMidiList = self.deleteWindow.getMidiNames()
        self.midTrack = mido.MidiFile(type=1)
        mergeTrack = mido.merge_tracks(self.midiTracks)
        self.midTrack.tracks.append(mergeTrack)
        self.checkNumberOfTracks()

    def action_play(self):
        print("Play pressed")
        if len(self.audioTracks) > 0 or len(self.midiTracks) > 0:
            audioThread = Thread(self.recordingFunctions.playAudio, *(self.midTrack, self.audioTracks))
            self.threadPool.start(audioThread)
        else:
            print("There must be tracks to be able to play")

    def action_stop(self):
        print("Stop Pressed")
        self.recordingFunctions.stop()

        self.threadPool.waitForDone()

        self.recordButton.setEnabled(True)

        track = self.recordingFunctions.getRecording()

        if track:
            self.audioTracks.append(track)
            self.audioTrackNames.append(self.recordingFunctions.getRecordingName())

        self.checkNumberOfTracks()
        
    def action_record(self):
        print("Record Pressed")
        threads = []
        self.recordButton.setEnabled(False)
        recordThread = Thread(self.recordingFunctions.record)
        playThread = Thread(self.action_play)
        threads.append(recordThread)
        threads.append(playThread)
        for x in threads:
            self.threadPool.start(x)

    def action_newTrack(self):
        print("Add new track pressed")
        if len(self.midiTracks) < self.MAX_MIDI_TRACKS:
            self.devices = TW.TrackWindow(self)
            self.devices.exec_()
            track = (self.devices.getTrack())

            if track:
                name = self.devices.getTrackName()
                self.midiTrackNames.append(name)
                self.midiTracks.append(track)
                mergeTrack = mido.merge_tracks(self.midiTracks)
                self.midTrack.tracks.append(mergeTrack)
                self.checkNumberOfTracks()
                print track
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Track Limit Reached")
            msg.setText("You have reached the limit of tracks available")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            
            msg.exec_()
            print("You have reached the limit of tracks available")

    def action_openProject(self):
        print("Opening project file")
        

    def action_importMidiFile(self):
        print("Importing Midi File")
        fileDialog = QFileDialog()
        name = fileDialog.getOpenFileName(self, "Import File","", "MIDI Files (*.mid)")
        
        try:
            midiFile = mido.MidiFile(name[0])

            midiTracks=[]
            for index, i in enumerate(midiFile.tracks):
                midiTracks.append(i)

            mergeTrack = mido.merge_tracks(midiTracks)
            self.midTrack.tracks.append(mergeTrack)
            self.midiTrackNames.append(name[0])
            self.midiTracks.append(mergeTrack)
            self.checkNumberOfTracks()
            print "Import Successful"
            print midiFile
        except Exception as e:
            print "Error importing midi file"
            print e

    def action_importWAVFile(self):
        print "Importing WAV File"
        fileDialog = QFileDialog()
        name = fileDialog.getOpenFileName(self, "Open File","", "WAV Files (*.wav)")

        try:
            with open(name[0],'rb') as f:
                b = bytearray(f.read())
            self.audioTracks.append(b)
            self.audioTrackNames.append(name[0])
            self.checkNumberOfTracks()
            print "Importing file: Successful"
        except Exception as e:
            print "Error trying to import file"
            print e

    def action_saveProject(self):
        print "Saving Project"
        

    def action_closeFile(self):
        self.close()

    def closeEvent(self, event):
        self.recordingFunctions.stop()
        self.threadPool.waitForDone()
        fileName = self.recordingFunctions.getRecordFile()
        if fileName:
            os.remove(fileName)
        for i in enumerate(self.soundsName):
            os.remove(i)

    def checkNumberOfTracks(self):
        if len(self.audioTracks) >= self.MAX_AUDIO_TRACKS:
            self.recordButton.setEnabled(False)
            self.importWAVFile.setEnabled(False)
        else:
            self.recordButton.setEnabled(True)
            self.importWAVFile.setEnabled(True)

        if len(self.midiTracks) >= self.MAX_MIDI_TRACKS:
            self.importMidi.setEnabled(False)
            self.newTrackButton.setEnabled(False)
        else:
            self.importMidi.setEnabled(True)
            self.newTrackButton.setEnabled(True)
        
        if len(self.audioTracks) > 0:
            self.exportWAVFile.setEnabled(True)
        else:
            self.exportWAVFile.setEnabled(False)
            
        if len(self.midiTracks) > 0:
            self.exportMidi.setEnabled(True)
        else:
            self.exportMidi.setEnabled(False)

        self.setImage()

        self.lblAudioTracksRemaining.setText("No. of Audio Tracks Remaining:"+str(self.MAX_AUDIO_TRACKS-len(self.audioTracks)))
        self.lblMIDITracksRemaining.setText("No. of MIDI Tracks Remaining:"+str(self.MAX_MIDI_TRACKS-len(self.midiTracks)))

    def action_exportMidiFile(self):
        print "Export Midi File"
        name = QFileDialog.getSaveFileName(self, "Export Midi file","", "MIDI Files (*.mid)")

        try:
            self.midTrack.save(name[0])

        except Exception as e:
            print "Error exporting Midi file"
            print e

    def action_exportWAVFile(self):
        print "Export WAV File"
        name = QFileDialog.getSaveFileName(self, "Export WAV file","", "WAV Files (*.wav)")

        self.writeToFile()

        try:
            if len(self.audioTracks) == 1:
                self.sounds[0].export(name[0], format="wav")
            elif len(self.audioTracks[0]) >= len(self.audioTracks[1]):
                combined = self.sounds[0].overlay(self.sounds[1])
                combined.export(name[0], format="wav")
            elif len(self.audioTracks[0]) < len(self.audioTracks[1]): 
                combined = self.sounds[1].overlay(self.sounds[0])
                combined.export(name[0], format="wav")

        except BaseException as e:
            print("Error: Trying to export to WAV File")
            print e

    def writeToFile(self):
        for index, i in enumerate(self.audioTracks):
            with open("Track"+str(index)+".wav",'wb') as f: 
                f.write(i)
                self.soundsName.append("Track"+str(index)+".wav")

            self.sounds.append(AudioSegment.from_wav("Track"+str(index)+".wav"))

    def run(self):
        self.show()

    def initialiseMenu(self):
        ## Initialise all the menu components
        menuBar = QMenuBar(self)
        menuBar.setGeometry(QRect(0, 0, 600, 0))

        menu_file = QMenu('File', menuBar)

        self.importWAVFile = QAction("&Import WAV File", self)
        self.importWAVFile.setStatusTip("Import WAV File from your workspace")
        self.importWAVFile.triggered.connect(self.action_importWAVFile)

        openProject = QAction("&Open Project", self)
        openProject.setShortcut("Ctrl+O")
        openProject.setStatusTip("Open Project")
        openProject.triggered.connect(self.action_openProject)

        saveProject = QAction("&Save Project", self)
        saveProject.setShortcut("Ctrl+S")
        saveProject.setStatusTip("Save Project")
        saveProject.triggered.connect(self.action_saveProject)

        self.importMidi = QAction("&Import Midi File", self)
        self.importMidi.setStatusTip("Import Midi File from your workspace")
        self.importMidi.triggered.connect(self.action_importMidiFile)

        self.exportWAVFile = QAction("&Export WAV File", self)
        self.exportWAVFile.setStatusTip("Export the audio recordings to .wav file")
        self.exportWAVFile.triggered.connect(self.action_exportWAVFile)
        self.exportWAVFile.setEnabled(False)

        self.exportMidi = QAction("&Export Midi File", self)
        self.exportMidi.setStatusTip("Export all midi recordings to .mid file")
        self.exportMidi.triggered.connect(self.action_exportMidiFile)
        self.exportMidi.setEnabled(False)

        closeFile = QAction("&Close", self)
        closeFile.setShortcut("Ctrl+Q")
        closeFile.setStatusTip("Close File")
        closeFile.triggered.connect(self.action_closeFile)

        menuBar.addMenu(menu_file)
        menu_file.addAction(openProject)
        menu_file.addAction(saveProject)
        menu_file.addSeparator()
        menu_file.addAction(self.importWAVFile)
        menu_file.addAction(self.importMidi)
        menu_file.addSeparator()
        menu_file.addAction(self.exportWAVFile)
        menu_file.addAction(self.exportMidi)
        menu_file.addSeparator()
        menu_file.addAction(closeFile)

        menu_track = QMenu('Track', menuBar)

        addTrack = QAction("&Add Midi Track", self)
        addTrack.triggered.connect(self.action_newTrack)

        deleteTrack = QAction("&Delete Tracks", self)
        deleteTrack.triggered.connect(self.action_deleteTrack)

        menu_track.addAction(addTrack)
        menu_track.addAction(deleteTrack)

        menuBar.addMenu(menu_track)
        self.setMenuBar(menuBar)
        self.statusBar()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qmw = QMainWindow()
    main = MainWindow(qmw)

    main.show()
    
    sys.exit(app.exec_())
  
