import mido
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog


def ticks_to_ms_with_tempo(start_tick, duration_ticks, tempo_changes, ticks_per_beat):
    end_tick = start_tick + duration_ticks
    elapsed_ms = 0

    for i in range(len(tempo_changes)):
        t_tick, t_tempo = tempo_changes[i]
        next_t_tick = tempo_changes[i + 1][0] if i + 1 < len(tempo_changes) else float('inf')

        if end_tick <= t_tick:
            break

        seg_start = max(start_tick, t_tick)
        seg_end = min(end_tick, next_t_tick)

        if seg_end > seg_start:
            ticks_in_segment = seg_end - seg_start
            ms = (ticks_in_segment * t_tempo) / ticks_per_beat / 1000
            elapsed_ms += ms

    return elapsed_ms


def get_tempo_changes(midi):
    tempo_changes = [(0, 500000)]  # default tempo = 120bpm
    current_tick = 0

    for msg in midi.tracks[0]:
        current_tick += msg.time
        if msg.type == 'set_tempo':
            tempo_changes.append((current_tick, msg.tempo))

    return tempo_changes

def convert_midi_to_rars(filepath):
    if not filepath.lower().endswith(".mid"):
        messagebox.showerror("Invalid File", "Selected file is not a .mid file.")
        return

    try:
        midi = mido.MidiFile(filepath)
        print(f"Reading MIDI file: {filepath}")

        ticks_per_beat = midi.ticks_per_beat
        tempo_changes = get_tempo_changes(midi)

        all_events = []
        for i, track in enumerate(midi.tracks):
            sample_id = simpledialog.askinteger(
                "Sample ID",
                f"Enter sample ID for Track {i} ({track.name if track.name else 'No Name'}):",
                minvalue=0, maxvalue=127
            )

            print(f"\n=== Track {i}: {track.name if track.name else 'No Name'} ===")

            current_tick = 0
            notes_on = {}

            for msg in track:
                print(msg)
                current_tick += msg.time

                if msg.type == 'note_on' and msg.velocity > 0:
                    notes_on[msg.note] = (current_tick, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in notes_on:
                        start_tick, velocity = notes_on.pop(msg.note)
                        duration = current_tick - start_tick
                        pitch = msg.note

                        start_ms = ticks_to_ms_with_tempo(0, start_tick, tempo_changes, ticks_per_beat)
                        duration_ms = ticks_to_ms_with_tempo(start_tick, duration, tempo_changes, ticks_per_beat)

                        all_events.append((start_ms, pitch, duration_ms, sample_id, velocity))
                    else:
                        print(f"Warning: note_off for note {msg.note} without matching note_on")

        all_events.sort(key=lambda e: e[0])
        with open("output.txt", "w") as f:
            last_start_time = 0
            for i, (start_ms, pitch, duration_ms, sample_id, velocity) in enumerate(all_events):
                gap = start_ms - last_start_time
                if gap > 0:
                    f.write(f"0, {int(gap)}, 0, 0")
                    if i < len(all_events) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")

                f.write(f"{pitch}, {int(duration_ms)}, {sample_id}, {velocity}")
                if i < len(all_events) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")

                last_start_time = start_ms


    except Exception as e:
        messagebox.showerror("Error", f"Failed to read MIDI file:\n{e}")


def choose_folders_and_convert():
    root = tk.Tk()
    root.withdraw()

    source_file = filedialog.askopenfilename(
        title="Select the folder containing WAV files",
        filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")]
    )

    if not source_file:
        messagebox.showerror("Error", "No source folder selected")
        return

    convert_midi_to_rars(source_file)
    messagebox.showinfo("Done", "File has been converted.")

if __name__ == "__main__":
    choose_folders_and_convert()
