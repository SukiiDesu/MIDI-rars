from pydub import AudioSegment
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def convert_wav_to_ogg(source_folder):
    destination_folder = os.path.join(source_folder, "ogg")
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for filename in os.listdir(source_folder):
        if filename.endswith('.wav'):
            wav_file_path = os.path.join(source_folder, filename)
            ogg_file_path = os.path.join(destination_folder, f"{os.path.splitext(filename)[0]}.ogg")

            audio = AudioSegment.from_wav(wav_file_path)

            audio.export(ogg_file_path, format="ogg")
            print(f"Converted {filename} to {ogg_file_path}")


def choose_folders_and_convert():
    root = tk.Tk()
    root.withdraw()

    source_folder = filedialog.askopenfilename(title="Select the MIDI file")

    if not source_folder:
        messagebox.showerror("Error", "No source folder selected")
        return

    convert_wav_to_ogg(source_folder)
    messagebox.showinfo("Done", "All files have been converted.")


choose_folders_and_convert()