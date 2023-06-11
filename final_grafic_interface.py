import tkinter as tk
import pickle
import socket
import pyaudio
import threading
import time
from PIL import Image, ImageTk

class Music:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename
        
class MusicPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SongSnake")
        self.root.geometry("500x380")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.songlist = tk.Listbox(self.root, bg="black", fg="white", width="100", height="15")
        self.songlist.pack()

        self.error_label = tk.Label(self.root, text="", fg="red")
        self.error_label.pack()

        self.play_button_image = ImageTk.PhotoImage(file="./assets/play.png")
        self.pause_button_image = ImageTk.PhotoImage(file="./assets/pause.png")
        self.stop_button_image = ImageTk.PhotoImage(file="./assets/stop.png")

        control_frame = tk.Frame(self.root)
        control_frame.pack()

        self.play_button = tk.Button(control_frame, image=self.play_button_image, borderwidth=0, command=self.play_music)

        self.pause_button = tk.Button(control_frame, image=self.pause_button_image, borderwidth=0, command=self.pause_music)

        self.stop_button = tk.Button(control_frame, image=self.stop_button_image, borderwidth=0, command=self.stop_music)

        self.play_button.grid(row=0, column=1, padx=7, pady=10)
        self.pause_button.grid(row=0, column=0, padx=7, pady=10)
        self.stop_button.grid(row=0, column=2, padx=7, pady=10)


        self.music_list = []
        self.current_song = None

        self.server = "127.0.0.2"
        self.port = 5544

        self.set_connection()

        self.p = pyaudio.PyAudio()

        self.paused = False
        self.load_music_list()


    def serialize_and_send(self, data):
        attempts = 3
        while attempts > 0:
            try:
                self.socket.send(pickle.dumps(data))
                return
            except:
                attempts -= 1
        self.error_label.config(text="Não foi possível se conectar com o servidor, clique no botão 'Reconectar'")

    def load_music_list(self):
        try:
            response = pickle.loads(self.socket.recv(1024))
            if response["type"] == "MusicList":
                self.music_list = response["data"]
                for music in self.music_list:
                    self.songlist.insert(tk.END, music.filename)
        except socket.error:
            self.error_label.config(text="Não foi possível se conectar com o servidor, clique no botão 'Reconectar'")
            return

    def play_music(self):
        is_connected = self.is_socket_connected()
        if (not is_connected):
            self.error_label.config(text="Não foi possível se conectar com o servidor, clique no botão 'Reconectar'")
            return 
        
        if self.paused:
            self.serialize_and_send("pause/play")
            self.paused = False
            
        selected_song_index = self.songlist.curselection()
        if selected_song_index:
            if (self.current_song and self.current_song != self.music_list[selected_song_index[0]]):
                self.stop_music()
                time.sleep(0.5)
            elif (self.current_song and self.current_song == self.music_list[selected_song_index[0]]):
                return
            self.current_song = self.music_list[selected_song_index[0]]
            self.serialize_and_send(self.current_song.id)
            threading.Thread(target=self.receive_audio).start()

    def receive_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        self.paused = False

        stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )

        while self.current_song != None and not self.paused:
            try:
                self.audio_data = self.socket.recv(CHUNK)
                stream.write(self.audio_data)
            except socket.error:
                self.error_label.config(text="Não foi possível se conectar com o servidor, clique no botão 'Reconectar'")
                break

        stream.stop_stream()
        stream.close()
        self.current_song = None

    def pause_music(self):
        self.paused = True
        self.serialize_and_send("pause/play")

    def stop_music(self):
        self.current_song = None
        self.clear_socket_buffer()
        self.serialize_and_send("stop")

    def close_connection(self):
        if (self.is_socket_connected()):
            if (self.paused):
                self.stop_music()
            self.serialize_and_send("end")

            attempts = 3
            while attempts >0:
                try:
                    response = pickle.loads(self.socket.recv(1024))
                    if (response["data"] == "Encerrando conexão"):
                        break
                except:
                    attempts -= 1
            time.sleep(0.5)
            self.socket.close()

    def set_connection(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect((self.server, self.port))
            time.sleep(0.5)
        except:
            pass
    
    def reconnect(self):
        self.error_label.config(text="")
        if (self.current_song):
            self.stop_music()
        self.songlist.delete(0, tk.END)
        self.close_connection()
        self.set_connection()
        self.load_music_list()
        
    def run(self):
        reconnect_button = tk.Button(self.root, text="Reconectar", command=self.reconnect)
        reconnect_button.pack()

        self.root.mainloop()

    def on_close(self):
        if (self.current_song):
            self.stop_music()
        self.songlist.delete(0, tk.END)
        self.close_connection()
        self.root.destroy()

    def clear_socket_buffer(self):
        data_pending = True
        if self.is_socket_connected():
            while data_pending:
                self.socket.settimeout(0.1)

                try:
                    data = self.socket.recv(1024)
                    if not data:
                        data_pending = False
                except socket.timeout:
                    data_pending = False

    def is_socket_connected(self):
        attempts = 3
        while attempts > 0:
            try:
                self.socket.send(b'')
                return True
            except:
                if (attempts == 1):
                    return False
                else:
                    attempts -= 1
        return False


if __name__ == "__main__":
    player = MusicPlayer()
    player.run()
