import glob
import os

from pydub import AudioSegment

def convert_to_wav(mp3_file, output_folder):
    audio = AudioSegment.from_mp3(mp3_file)
    audio = audio.set_frame_rate(44100)
    output_file = os.path.join(
        output_folder, 
        os.path.splitext(os.path.basename(mp3_file))[0] + ".wav"
    )
    audio.export(output_file, format="wav", overwrite=True)
    print(f"Arquivo {mp3_file} convertido com sucesso para {output_file}")


def convert_folder_to_wav(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    mp3_list = glob.glob(os.path.join(input_folder, "*.mp3"))

    for mp3_file in mp3_list:
        convert_to_wav(mp3_file, output_folder)


input_folder = "./new_audio"

output_folder = "./resource"

convert_folder_to_wav(input_folder, output_folder)