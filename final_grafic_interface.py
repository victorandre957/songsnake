import tkinter as tk
import pickle
import socket
import pyaudio
import threading
from PIL import Image, ImageTk

class Music:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename
        
class MusicPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SongSnake")
        self.root.geometry("500x350")

        self.songlist = tk.Listbox(self.root, bg="black", fg="gray", width="100", height="15")
        self.songlist.pack()

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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p = pyaudio.PyAudio()

        self.paused = False
        self.load_music_list()

    def load_music_list(self):
        try:
            self.socket.connect(("localhost", 5544))
            self.socket.send(pickle.dumps("update"))
            response = pickle.loads(self.socket.recv(1024))
            if response["type"] == "MusicList":
                self.music_list = response["data"]
                for music in self.music_list:
                    self.songlist.insert(tk.END, music.filename)
        except socket.error as e:
            print(f"Failed to connect to the server: {e}")
            return

    def play_music(self):
        if self.paused:
            self.socket.send(pickle.dumps("pause/play"))
            self.paused = False
            
        selected_song_index = self.songlist.curselection()
        if selected_song_index:
            self.current_song = self.music_list[selected_song_index[0]]
            self.socket.send(pickle.dumps(self.current_song.id))
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

        while self.current_song and not self.paused:
            try:
                data = self.socket.recv(CHUNK)
                stream.write(data)
            except socket.error as e:
                print(f"Error receiving audio data: {e}")
                break

        stream.stop_stream()
        stream.close()

    def pause_music(self):
        self.paused = True
        self.socket.send(pickle.dumps("pause/play"))

    def stop_music(self):
        self.current_song = None
        self.socket.send(pickle.dumps("stop"))
    
    def reconnect(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.load_music_list()

    def run(self):
        reconnect_button = tk.Button(self.root, text="Reconnect", command=self.reconnect)
        reconnect_button.pack()

        self.root.mainloop()


if __name__ == "__main__":
    player = MusicPlayer()
    player.run()
