import wave
import pyaudio
import pygame
import io
import mido
import threading
import datetime

class RecordingFunctions():
    def __init__(self):
        print "RecordingFunctions Class Instanciated"
        pygame.mixer.pre_init(44100,16,8,4096)
        pygame.init()

        self.FORMAT = pyaudio.paInt16
        self.WIDTH = 2
        self.CHANNELS = 2
        self.RATE = 44100
        self.CHUNK = 1024
             
        global status
        status = 1
        self.recording = 0
        self.fileName = ""

        self.now = datetime.datetime.now()


    def playAudio(self, midiTracks, audioTracks):
        threads = []
        byteStream = io.BytesIO()
        midiTracks._save(byteStream)
        byteStream.seek(0)

        threads.append(threading.Thread(target=self.audioPlayer, args=(0, byteStream)))

        for index, i in enumerate(audioTracks):
            threads.append(threading.Thread(target=self.audioPlayer, args=(index+1,i)))
        for x in threads:
            x.start()
        for x in threads:
            x.join()

    def audioPlayer(self, channel, byteStream):
        try:
            if channel == 0:
                pygame.mixer.music.load(byteStream)
                pygame.mixer.music.play()
            else:
                pygame.mixer.Channel(channel).play(pygame.mixer.Sound(byteStream))
        except pygame.error as e:
            print "pygame playing error"
            print e

    def record(self):
        global status
        status = 1
        p = pyaudio.PyAudio()
        stream = p.open(format = self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)

        frames = []

        print "Recording"
        count = 0
        stream.start_stream()
        while True:
            global status
            print count 
            count +=1
            if status == 0:
                print "Stop recording"
                break
            else:
                data = stream.read(self.CHUNK)
                frames.append(data)
        
        stream.stop_stream()
        stream.close()

        byteStream = io.BytesIO()
        wf = wave.open(byteStream, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(''.join(frames))
        byteStream.seek(0)
        wf.close()

        
        self.fileName = str(self.now.year)+'_'+str(self.now.month)+".wav"

        with open(self.fileName, 'wb') as f: ## Save to a file 
            f.write(byteStream.read())

        b = bytearray()
        with open(self.fileName, 'rb') as f: ## read from a file 
            b = bytearray(f.read())

        self.recording = b
        p.terminate()
        print "Finished Recording"
    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        
        global status
        status = 0

    def getRecording(self):
        audioTrack = self.recording
        self.recording = 0
        return audioTrack

    def getRecordingName(self):
        now = datetime.datetime.now()
        return "AudioTrack"

    def getRecordFile(self):
        print self.fileName
        return self.fileName
  