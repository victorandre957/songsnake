from tkinter import *
from tkinter import filedialog
import pygame
import os


root = Tk()
root.title("Songsnake")
root.geometry("500x350")

pygame.mixer.init()

menubar = Menu(root)
root.config(menu=menubar)

songs = []
current_song = ""
paused = False

def load_music():
    global current_song
    root.directory = filedialog.askdirectory()

    for song in os.listdir(root.directory):
        name, ext = os.path.splitext(song)
        if ext == ".mp3":
            songs.append(song)

    for song in songs:
        songlist.insert("end", song)

    songlist.selection_set(0)
    current_song = songs[songlist.curselection()[0]]

def play_music():
    global current_song, paused

    if not paused:
        pygame.mixer.music.load(os.path.join(root.directory, current_song))
        pygame.mixer.music.unpause()
        paused = False

def pause_music():
    global paused
    pygame.mixer.music.pause()
    paused = True
    

def next_music():
    global current_song, paused

    try:
        songlist.selection_clear(0, END)
        songlist.selection_set(songs.index(current_song) + 1)
        current_song = songs[songlist.curselection()[0]]
        play_music()
    except:
        pass

def previous_music():
    global current_song, paused

    try:
        songlist.selection_clear(0, END)
        songlist.selection_set(songs.index(current_song) - 1)
        current_song = songs[songlist.curselection()[0]]
        play_music()
    except:
        pass

organise_menu = Menu(menubar)
organise_menu.add_command(label="Select folder", command=load_music)
menubar.add_cascade(label="Organise", menu=organise_menu)

songlist = Listbox(root, bg="black", fg="gray", width="100", height="15")
songlist.pack()

play_button_image = PhotoImage(file="./assets/play.png")
pause_button_image = PhotoImage(file="./assets/pause.png")
next_button_image = PhotoImage(file="./assets/next.png")
previous_button_image = PhotoImage(file="./assets/previous.png")

control_frame = Frame(root)
control_frame.pack()

play_button = Button(control_frame, image=play_button_image, borderwidth=0, command=play_music)
pause_button = Button(control_frame, image=pause_button_image, borderwidth=0, command=pause_music)
next_button = Button(control_frame, image=next_button_image, borderwidth=0, command=next_music)
previous_button = Button(control_frame, image=previous_button_image, borderwidth=0, command=previous_music)

play_button.grid(row=0, column=1, padx=7, pady=10)
pause_button.grid(row=0, column=2, padx=7, pady=10)
next_button.grid(row=0, column=3, padx=7, pady=10)
previous_button.grid(row=0, column=0, padx=7, pady=10)

root.mainloop()