'''
store all file to play in the "resource" sub directory where the server file exists
run using command in linux : "python3 server.py"
the audio should be of .wav format with 44100 Hz frequency
'''

import pickle
import socket
import pyaudio
import fnmatch
import select
import wave
import os
from _thread import *

class Music:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename
        
class Server():
    def __init__(self, conn, address):
        self.conn = conn
        address = address
        print("<", address, ">  connected ")

        self.music_to_play = None
        self.pause_music = False
        self.playing_music = False
        self.run_process()

    def get_response(self):
        try:
            res = pickle.loads(self.conn.recv(1024))
        except:
            res = None
        return res

    def run_process(self):
        self.set_files_list()
        self.send_music_list()            

        while True:
            try:
                if select.select([self.conn], [], [], 0)[0]:
                    res = self.get_response()
                    if res == "stop":
                        if (self.music_to_play != None):
                            self.stop_music()
                            break
                    elif res == "pause/play":
                        if (self.music_to_play != None):
                            self.pause_or_play_music()
                    elif res == "update":
                        self.restart_process()
                        break
                    elif res == "end":
                        self.end_process()
                        break
                    elif res != None:
                        self.chose_music_to_play(res)
            except:
                pass

            if (self.music_to_play != None and not self.playing_music):
                self.play_music()

    def filter_files(self, files_list):
        wav_files = []
        for file in files_list:
            if fnmatch.fnmatch(file, '*.wav'):
                wav_files.append(file)
        return wav_files
        
    def set_files_list(self):
        resource = self.filter_files(os.listdir("./resource"))
        self.music_list =  []
        index = 1
        for music in resource:
            self.music_list.append(Music(str(index), music[:-4]))
            index += 1
    
    def send_music_list(self):
        self.data_list = pickle.dumps(self.music_list)
        self.conn.send(self.data_list)

    def chose_music_to_play(self, response):
        for music in self.music_list:
            if response == music.id:
                self.music_to_play = music.filename
                self.conn.send(pickle.dumps("\n Reproduzindo..."))
                break
            self.music_to_play = None
            
        if (self.music_to_play == None):
            self.conn.send(pickle.dumps("\n Musica não encontada"))
            
    def play_music(self):
        self.playing_music = True

        wf = wave.open("./resource/" + self.music_to_play + ".wav", 'rb')

        self.play = pyaudio.PyAudio()

        CHUNK = 2048
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        self.stream = self.play.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        data = 1
        while True:
            data = wf.readframes(CHUNK)

            if not self.pause_music and self.playing_music:
                self.conn.send(data)

            if data.count == 0:
                self.end_music()
                break

    def end_music(self):
        self.stream.stop_stream()
        self.stream.close()
        self.play.terminate()
        self.playing_music = False
        self.music_to_play = None
        self.conn.send(pickle.dumps("\n A Musica acabou"))
        self.send_music_list()

    def stop_music(self):
        self.playing_music = False
        self.music_to_play = None
        self.stream.stop_stream()
        self.stream.close()
        self.play.terminate()
        self.conn.send(pickle.dumps("\n A reproução foi encerrada"))
        self.send_music_list()

    def pause_or_play_music(self):
        if (not self.pause_music):
            self.conn.send(pickle.dumps("\n Pausado"))
        else:
            self.conn.send(pickle.dumps("\n Tocando..."))
        self.pause_music = not self.pause_music

    def restart_process(self):
        self.music_to_play = None
        if (self.playing_music):
            self.end_music()
        self.run_process()

    def end_process(self):
        if (self.playing_music):
            self.playing_music = False
            self.music_to_play = None
            self.stream.stop_stream()
            self.stream.close()
            self.play.terminate()
            
        self.conn.close()

while True:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", 5544))
    server_socket.listen(10)
    conn, address = server_socket.accept()
    server = Server(conn, address)