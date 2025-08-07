# main.py
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, Menu, messagebox

from scheda_giocatore import SchedaPersonaggio
from dnd_diary import DiarioNote

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestione Personaggio D&D – Main")
        self.geometry("1920x1080")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # 1) moduli
        self.scheda = SchedaPersonaggio()
        self.diario = DiarioNote()

        # 2) menu + UI
        self._build_menu()
        self._build_ui()

        # 3) binding autosave & Ctrl+S
        self.bind_all("<Control-s>", lambda e: self.salva_scheda())
        self.after(300_000, self._autosave)

    def _build_menu(self):
        men = Menu(self)

        filem = Menu(men, tearoff=0)
        filem.add_command(label="Nuova Scheda",          command=self.nuova_scheda)
        filem.add_command(label="Carica Scheda",         command=self.carica_scheda)
        filem.add_command(label="Salva Scheda",          command=self.salva_scheda)
        filem.add_command(label="Salva Scheda con Nome", command=self.salva_scheda)
        filem.add_separator()
        men.add_cascade(label="File", menu=filem)

        dadim = Menu(men, tearoff=0)
        dadim.add_command(label="Lancia Dadi", command=self.apri_dadi3d)
        men.add_cascade(label="Dadi", menu=dadim)

        self.config(menu=men)

    def _build_ui(self):
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.grid(row=0, column=0, columnspan=2,
                  sticky="nsew", padx=10, pady=10)

        # scheda a sinistra
        pleft = ttk.PanedWindow(pane, orient=tk.VERTICAL)
        fsch = ttk.Frame(pleft)
        self.scheda.crea_scheda(fsch)
        pleft.add(fsch, weight=1)
        pane.add(pleft, weight=1)

        # notebook a destra
        note = ttk.Notebook(pane)
        feq  = ttk.Frame(note); note.add(feq,  text="Equipaggiamento")
        fab  = ttk.Frame(note); note.add(fab,  text="Abilità")
        finc = ttk.Frame(note); note.add(finc, text="Incantesimi")
        self.scheda.crea_equipaggiamento(feq)
        self.scheda.crea_abilita(fab)
        self.scheda.crea_incantesimi(finc)

        # diario tab
        pd   = ttk.PanedWindow(note, orient=tk.HORIZONTAL)
        fdi  = ttk.Frame(pd)
        fap  = ttk.Frame(pd)
        pd.add(fdi, weight=3)
        pd.add(fap, weight=2)
        note.add(pd, text="Diario")
        self.diario.crea_diario(fdi, anteprima_frame=fap, con_eliminazione=True)

        pane.add(note, weight=2)

    def _get_next_diary_id(self):
        folder = os.path.join(os.getcwd(), "data/Diari")
        files = os.listdir(folder)
        nums = [int(m.group(1)) for f in files
                if (m := __import__('re').match(r"diary_(\d+)\.json$", f))]
        return str(max(nums)+1 if nums else 1)

    def nuova_scheda(self):
        if not messagebox.askyesno("Conferma", "Creare nuova scheda e diario incrementale?"):
            return
        self.scheda.reset_scheda()
        nid = self._get_next_diary_id()
        ent = self.scheda.entries["id_diario"]
        ent.config(state="normal")
        ent.delete(0, tk.END)
        ent.insert(0, nid)
        ent.config(state="readonly")
        self.diario.set_diary_id(nid)

    def carica_scheda(self):
        self.scheda.carica_tutto()
        iid = self.scheda.entries["id_diario"].get().strip()
        self.diario.set_diary_id(iid)

    def salva_scheda(self):
        self.scheda.salva_tutto()

    def apri_dadi3d(self):
        # Esegue il modulo dice_roller.py
        dice_script = os.path.join(os.path.dirname(__file__), "dice_roller.py")
        if not os.path.isfile(dice_script):
            messagebox.showerror("Errore", f"File non trovato: {dice_script}")
            return
        subprocess.Popen([sys.executable, dice_script])

    def _autosave(self):
        self.salva_scheda()
        self.after(300_000, self._autosave)

    def on_close(self):
        self.destroy()

if __name__ == "__main__":
    MainApp().mainloop()
