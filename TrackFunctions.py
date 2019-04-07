import pygame.midi
import thread
import mido

class TrackFunctions():
    def __init__(self):
        print "TrackFunctions Class Instanciated"
        pygame.midi.init()
        self.musicPlayer = pygame.midi.Output(0)


        self.tempoValue = mido.bpm2tempo(120)
        self.stopTick = 0
        self.startTick = 0
        self.instrument = []
        networkFile = open("Instruments2.txt", "r") ## Read file

        for line in networkFile:
            self.instrument.append((line.strip('\n')))

        self.savedTrack = 0
        self.initMidi()

    def initMidi(self):
        self.track = mido.MidiTrack()

    def getInstrumentList(self):
        return self.instrument
    
    def printNote(self, e):
        print e + " pressed"

    def playNote(self, instrument, channel, note, velocity, record, time):
        self.musicPlayer.set_instrument(instrument, channel)
        self.musicPlayer.note_on(note,velocity, channel)
        
        if record:
            tick = self.startTick = self.timeToTickConverter(time)
            tick = tick - self.stopTick
            thread.start_new_thread(self.setOnNote,(instrument, channel, velocity, note, tick))

    def stopNote(self, note, velocity, channel, record, time):
        self.musicPlayer.note_off(note, velocity, channel)

        if record:
            
            self.stopTick = self.timeToTickConverter(time)
            tick = self.stopTick - self.startTick
            thread.start_new_thread(self.setOffNote, (note, tick, channel, velocity))

    def setOnNote(self, instrument, channel, velocity, note, tick):
        self.track.append(mido.Message('note_on', channel=channel, note=note, velocity=velocity, time=tick))
       

    def setOffNote(self, note, tick, channel, velocity):
        self.track.append(mido.Message('note_off', channel=channel, note=note, velocity=velocity, time=tick)) 

    def saveTrack(self):
        self.savedTrack = self.track

    def setInstrument(self, tick, channel, instrument):
        tick = self.timeToTickConverter(tick)
        self.track.append(mido.Message('program_change', channel=channel, program=instrument, time=tick))
        
    def timeToTickConverter(self, time):
        tick = mido.second2tick(time, ticks_per_beat=480, tempo=self.tempoValue)
       
        tick = int(tick)
        return tick

    def redoTrack(self):
        self.initMidi()

    def getTrack(self):
        return self.savedTrack

    def destroy(self):
        self.musicPlayer.close()