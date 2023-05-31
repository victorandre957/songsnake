'''
Change the ip address to the one on which server file is running
run using command in linux : "python3 client.py"

enter sample to run the sample audio

'''

import socket
import pyaudio
import sys
import select

p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)
while True:
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client_socket.connect(("127.0.0.1", 5544))

	res=client_socket.recv(1024).decode('utf-8')
	print(res)
	print("Well come to Songsnake")
	sys.stdout.flush()
	x=input(
""" type it:
	0 - to exit
	1 -  to update the list
	name of the song to play: """
	)
	if (x == "0"):
		print("\n Bye see you later!")
		break
	if (x == "1"):
		# busca de novo
		pass
	client_socket.send(x.encode())
	ch=int(client_socket.recv(1024).decode())
	if ch==0:
		print("!!! Choose a legal song number !!!")
		continue
	if ch==1:
		print(" Track !!  ",x,"  !! Playing \n")
		pausado = False
		print("type 0 to pause/play or 1 to stop: ")
		while True:
				if select.select([sys.stdin], [], [], 0)[0]:
					user_input = input()
					if (user_input == "0"):
						pausado = not pausado
					if (user_input == "1"):
						break
				if not pausado:
					data = client_socket.recv(1024)
					stream.write(data)

stream.stop_stream()
stream.close()
p.terminate()