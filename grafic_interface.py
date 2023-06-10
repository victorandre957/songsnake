import socket
import pyaudio
import pickle
import sys
import time
from PyQt5 import QtWidgets

class Music:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename

class ClientWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cliente")

        # Definir valores padrão do servidor e porta
        self.server = "127.0.0.1"
        self.port = 5544
        
        self.create_widgets()
        self.create_layout()
        
        self.send_button.clicked.connect(self.send_message)
        self.update_button.clicked.connect(self.update_process)
        self.exit_button.clicked.connect(self.exit_application)
        self.stop_button.clicked.connect(self.stop_playing)
        self.pause_button.clicked.connect(self.pause_resume_playing)
        
        self.pausado = False
        self.client_socket = None
        self.set_stream()
        self.connect_to_server()

    def set_stream(self):
        self.p = pyaudio.PyAudio()
        CHUNK = 1024 * 30
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )

    def get_response_string(self):
        received_data = self.client_socket.recv(1024)
        try:
            data = pickle.loads(received_data)
            if (data["type"] == "String"):
                res = data["data"]
            else:
                res = ""
        except pickle.UnpicklingError:
            res = ""
        return res
    
    def get_response_List(self):
        received_data = self.client_socket.recv(1024)
        try:
            data = pickle.loads(received_data)
            if (data["type"] == "MusicList"):
                res = data["data"]
            else:
                res = []
        except pickle.UnpicklingError:
            res = []
        return res
    
    def get_response_AudioData(self, audio_data):
        CHUNK = 1024 * 30
        new_audio_data = audio_data
        received_data = self.client_socket.recv(CHUNK)
        try:
            _ = pickle.loads(received_data)
        except:
            new_audio_data = received_data
        return new_audio_data

    def create_widgets(self):
        self.message_label = QtWidgets.QLabel("Mensagem:")
        self.message_entry = QtWidgets.QLineEdit()
        self.send_button = QtWidgets.QPushButton("Enviar")

        self.update_button = QtWidgets.QPushButton("Atualizar")
        self.exit_button = QtWidgets.QPushButton("Sair")  # Botão "Sair"
        self.stop_button = QtWidgets.QPushButton("Parar")  # Botão "Parar"
        self.pause_button = QtWidgets.QPushButton("Pausar/Reproduzir")  # Botão "Pausar/Reproduzir"

        self.status_label = QtWidgets.QLabel()
        
    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()
        
        layout.addWidget(self.message_label)
        layout.addWidget(self.message_entry)
        layout.addWidget(self.send_button)
        
        layout.addWidget(self.update_button)
        layout.addWidget(self.exit_button)  # Adicione o botão "Sair" ao layout
        layout.addWidget(self.stop_button)  # Adicione o botão "Parar" ao layout
        layout.addWidget(self.pause_button)  # Adicione o botão "Pausar/Reproduzir" ao layout

        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def show_music_list(self, music_list_obj):
        music_list = ""
        for music in music_list_obj:
            music_list+= "\n" + f"{music.id}" " - " + music.filename
        return music_list

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.connect((self.server, self.port))

        res = self.get_response_List()
        self.status_label.setText(self.show_music_list(res))
    
    def send_message(self):
        if not self.client_socket:
            return
        
        self.message = self.message_entry.text()
        self.client_socket.send(pickle.dumps(self.message))
        
        ch = self.get_response_string()
        if ch == "\n Musica não encontada":
            self.status_label.setText(ch)
        elif ch == "\n Reproduzindo...":
            self.playing = True
            self.playing_music()

    def playing_music(self):
        self.status_label.setText(f"\n Tocando {self.message} ...")
        time.sleep(2)
        self.pausado = False
        audio_data = b""
        while True:
            QtWidgets.QApplication.processEvents()

            if self.pausado:
                continue
        
            if self.playing:
                audio_data = self.get_response_AudioData(audio_data)
                if audio_data:
                    self.stream.write(audio_data)
                else:
                    break
    
        self.stop_stream()

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        self.playing = False

    def update_process(self):
        self.client_socket.send(pickle.dumps("update"))
        self.message_entry.setText("")
        res = self.get_response_list()
        self.status_label.setText(self.show_music_list(res))
    
    def exit_application(self):
        self.client_socket.send(pickle.dumps("end"))
        self.message_entry.setText("")
        self.stop_stream()
        self.close()

    def stop_playing(self):
        self.stop_stream()
        self.client_socket.send(pickle.dumps("stop"))
        self.message_entry.setText("")
        res = self.get_response_list()
        self.status_label.setText(self.show_music_list(res))
        self.status_label.setText("A Reprodução foi encerrada")

    def pause_resume_playing(self):
        self.client_socket.send(pickle.dumps("pause/play"))
        if (self.pausado):
            self.stream.start_stream()
            self.status_label.setText("Reproduzindo...")
        else:
            self.stream.stop_stream()
            self.status_label.setText("Pausado")

        self.pausado = not self.pausado


if __name__ == "__main__":
    while True:
        app = QtWidgets.QApplication(sys.argv)
        window = ClientWindow()
        window.show()
        sys.exit(app.exec_())
