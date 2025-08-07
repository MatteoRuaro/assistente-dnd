import re
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from playsound import playsound 
except ImportError:
    playsound = lambda *args, **kwargs: None


def parse_notation(notation):
    #esempio notazione 1d6+1d20
    parts = re.findall(r'\s*([0-9]+)[dD]([0-9]+)\s*', notation)
    return [(int(cnt), int(sides)) for cnt, sides in parts]


def roll_dice(notation):
    rolls = []
    for count, sides in parse_notation(notation):
        for _ in range(count):
            rolls.append(random.randint(1, sides))
    return rolls


class DiceRollerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dice Roller")
        self.geometry("300x200")
        self.resizable(False, False)

        # Percorsi file audio (cartella 'sfx' accanto allo script)
        script_dir = os.path.dirname(__file__)
        sfx_dir = os.path.join(script_dir, 'sfx')
        self.roll_sound = os.path.join(sfx_dir, 'roll.mp3')
        self.crit_sound = os.path.join(sfx_dir, 'crit.mp3')

        # Label e entry per notazione
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Notazione dadi:").grid(row=0, column=0, sticky=tk.W)
        self.notation_var = tk.StringVar(value="1d20")
        entry = ttk.Entry(frame, textvariable=self.notation_var, width=15)
        entry.grid(row=0, column=1, sticky=tk.W)

        # Bottone Roll
        roll_btn = ttk.Button(frame, text="Roll", command=self.on_roll)
        roll_btn.grid(row=1, column=0, columnspan=2, pady=10)

        # Risultati
        self.result_text = tk.Text(frame, height=4, width=30, state=tk.DISABLED)
        self.result_text.grid(row=2, column=0, columnspan=2)

    def on_roll(self):
        notation = self.notation_var.get().strip()
        if not notation:
            messagebox.showwarning("Input richiesto", "Inserisci la notazione (es. 3d6+1d4)")
            return

        # Riproduce suono lancio
        try:
            playsound(self.roll_sound, block=False)
        except Exception:
            pass

        # Calcola rolls
        rolls = roll_dice(notation)
        total = sum(rolls)

        # Se è esattamente 1d20 e risulta 20, suono critico
        if notation.lower() in ('1d20',) and rolls and rolls[0] == 20:
            try:
                playsound(self.crit_sound, block=False)
            except Exception:
                pass

        # Visualizza risultati
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f"Risultati: {rolls}\nTotale: {total}")
        self.result_text.config(state=tk.DISABLED)


def main():
    app = DiceRollerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
