import pickle
import socket
import pyaudio
import fnmatch
import select
import wave
import os
import time
from _thread import *

class Music:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename
        
class Server():
    def __init__(self, conn, address):
        self.conn = conn
        self.address = address
        print("<", self.address, ">  connected ")

        self.stream = None
        self.music_to_play = None
        self.pause_music = False
        self.playing_music = False
        self.last_activity_time = time.time()
        self.run_process()

    def get_response(self):
        try:
            res = pickle.loads(self.conn.recv(1024))
        except:
            res = None
        return res
    
    def serialize_and_send(self, type, data):
        try:
            self.conn.send(pickle.dumps({"type": type, "data": data}))
        except (BrokenPipeError, ConnectionResetError):
            pass

    def run_process(self):
        self.set_files_list()
        self.send_music_list()            

        while True:
            if self.conn:
                try:
                    if select.select([self.conn], [], [], 0)[0]:
                        self.last_activity_time = time.time()
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

                    else:
                        if time.time() - self.last_activity_time > 600:
                            print("Fechando conexão por inatividade")
                            self.end_process()
                            break
                except:
                    if (self.music_to_play != None):
                        self.stop_music()
                        self.end_process()
                        break

                if (self.music_to_play != None and not self.playing_music):
                    self.play_music()

            else:
                break

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
        self.serialize_and_send("MusicList", self.music_list)

    def chose_music_to_play(self, response):
        for music in self.music_list:
            if response == music.id:
                self.music_to_play = music.filename
                break
            self.music_to_play = None
            
        if (self.music_to_play == None):
            self.serialize_and_send("String", "\n Musica não encontada")
            
    def play_music(self):
        self.playing_music = True
        wf = wave.open("./resource/" + self.music_to_play + ".wav", 'rb')

        self.play = pyaudio.PyAudio()

        CHUNK = 1024 * 20
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
        while data:
            if self.conn:
                try:
                    if select.select([self.conn], [], [], 0)[0]:
                        res = self.get_response()
                        if res == "stop":
                            self.stop_music()
                            break
                        elif res == "pause/play":
                            self.pause_or_play_music()
                        elif res == "update":
                            self.restart_process()
                        elif res == "end":
                            self.end_process()
                except:
                    break
            else:
                break

            if not self.pause_music:
                data = wf.readframes(CHUNK)
                if self.playing_music:
                    try:
                        self.conn.send(data)
                    except:
                        break

        self.end_music()

    def end_music(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.play.terminate()
        
        self.playing_music = False
        self.music_to_play = None

    def stop_music(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.play.terminate()

        self.playing_music = False
        self.music_to_play = None

    def pause_or_play_music(self):
        if (not self.pause_music):
            self.stream.stop_stream()
        else:
            self.stream.start_stream()
        self.pause_music = not self.pause_music

    def restart_process(self):
        self.music_to_play = None
        if (self.playing_music):
            self.end_music()
        self.run_process()

    def end_process(self):
        self.serialize_and_send("String", "Encerrando conexão")
        print("<", self.address, ">  disconnected ")
        self.playing_music = False
        self.music_to_play = None

        if (self.stream):
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