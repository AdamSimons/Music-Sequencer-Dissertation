import sys
from PySide.QtCore import *
from PySide.QtGui import *

class DeleteWindow(QDialog):
    def __init__(self, parent, audioNames, midiNames, midiTracks, audioTracks):
        super(DeleteWindow, self).__init__(parent)
        self.setWindowTitle("Delete Tracks")
        self.setWindowModality(Qt.ApplicationModal)

        self.audioTrackNames = audioNames
        self.midiTrackNames = midiNames
        self.midiTracks = midiTracks
        self.audioTracks = audioTracks
        self.initUI()

    def initUI(self):

        self.__initWidgets__()

        dialogLayout = QGridLayout()
        grpBoxPatternGridLayout = QGridLayout()

        dialogLayout.addWidget(self.grpBoxPattern,0,0)

        grpBoxPatternGridLayout.addWidget(self.lstView,0,0,3,4)
        grpBoxPatternGridLayout.addWidget(self.btnDelete,4,0)
        self.grpBoxPattern.setLayout(grpBoxPatternGridLayout)
        self.setLayout(dialogLayout)
        

    def __initWidgets__(self):
        self.grpBoxPattern = QGroupBox("Tracks")
        self.lstView = QListView()
        self.itemModel = QStandardItemModel(self.lstView)
        self.lstView.setModel(self.itemModel)
        self.lstView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lstView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.btnDelete = QPushButton("Delete",self)
        self.btnDelete.setEnabled(False)

        for i in enumerate(self.audioTrackNames):
            item = QStandardItem('A'+str(i[0])+ " " + i[1])
            self.itemModel.appendRow(item)
        for i in enumerate(self.midiTrackNames):
            item = QStandardItem('M'+str(i[0])+ " "+ i[1])
            self.itemModel.appendRow(item)

        self.lstView.clicked.connect(self.action_onClickedList)
        self.btnDelete.clicked.connect(self.action_deleteTrack)

    def action_onClickedList(self, index):
        if index:
            self.btnDelete.setEnabled(True)
        else: 
            self.btnDelete.setEnabled(False)
    
    def action_deleteTrack(self):
        index = self.lstView.selectedIndexes()
        for i in index:
            type, indexValue = str(i.data())[:2]
            self.itemModel.removeRow(i.row())

            
            self.deleteFromList(type, indexValue)

    def deleteFromList(self, type, index):
        index = int(index)
        if type =='A':
            del self.audioTrackNames[index]
            del self.audioTracks[index]
        elif type == 'M':
            del self.midiTrackNames[index]
            del self.midiTracks[index]
        else:
            print "Error in deleting track"
        self.reloadData()

    def reloadData(self):
        self.itemModel.clear()
        for i in enumerate(self.audioTrackNames):
            item = QStandardItem('A'+str(i[0])+ " " + i[1])
            self.itemModel.appendRow(item)
        for i in enumerate(self.midiTrackNames):
            item = QStandardItem('M'+str(i[0])+ " "+ i[1])
            self.itemModel.appendRow(item)

        if self.itemModel.rowCount() <= 0:
            self.btnDelete.setEnabled(False)

    def getAudioNames(self):
        return self.audioTrackNames
    def getMidiNames(self):
        return self.midiTrackNames
        
        



      
        


