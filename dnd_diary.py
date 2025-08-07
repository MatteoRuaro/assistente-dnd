# dnd_diary.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class DiarioNote:
    def __init__(self, file_diario="diary.json"):
        self.file_diario   = file_diario
        self.note          = self._load_notes()
        self.editing_index = None

    def _load_notes(self):
        if os.path.exists(self.file_diario):
            with open(self.file_diario, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def salva_su_file(self):
        with open(self.file_diario, "w", encoding="utf-8") as f:
            json.dump(self.note, f, ensure_ascii=False, indent=2)

    def set_diary_id(self, diary_id: str):
        # diary_<id>.json se id non vuoto, altrimenti diary.json
        self.file_diario = f"data/Diari/diary_{diary_id}.json" if diary_id else "diary.json"
        self.note = self._load_notes()
        try:
            self.aggiorna_lista()
            self.pulisci_campi()
        except:
            pass

    def crea_diario(self, container, anteprima_frame=None, con_eliminazione=False):
        # campo Titolo, Testo, Categoria, Tags
        self.titolo_entry   = tk.Entry(container, width=40)
        self.testo_text     = tk.Text(container, height=4, width=60)
        self.categoria_combo = ttk.Combobox(
            container,
            values=["Generale", "Sessione", "Personaggio", "Luogo"],
            state="readonly"
        )
        self.categoria_combo.set("Generale")
        self.tags_entry     = tk.Entry(container, width=40)

        tk.Label(container, text="Titolo:").grid(row=0, column=0, sticky="e")
        self.titolo_entry.grid(row=0, column=1, sticky="w")
        tk.Label(container, text="Categoria:").grid(row=1, column=0, sticky="e")
        self.categoria_combo.grid(row=1, column=1, sticky="w")
        tk.Label(container, text="Tag (virgola):").grid(row=2, column=0, sticky="e")
        self.tags_entry.grid(row=2, column=1, sticky="w")
        tk.Label(container, text="Testo:").grid(row=3, column=0, sticky="ne")
        self.testo_text.grid(row=3, column=1, pady=5)
        tk.Button(container, text="Salva Nota", command=self.salva_nota).grid(row=4, column=1, sticky="e")

        # listbox + modifica + elimina
        self.lista_note = tk.Listbox(container, width=80)
        self.lista_note.grid(row=5, column=0, columnspan=2)
        tk.Button(container, text="Modifica Selezione", command=self.modifica_selezione).grid(row=6, column=1, sticky="e")
        if con_eliminazione:
            tk.Button(container, text="Elimina Nota", command=self.elimina_nota).grid(row=6, column=0, sticky="w")

        # filtri
        self.filtro_categoria = ttk.Combobox(
            container,
            values=["Tutte", "Generale", "Sessione", "Personaggio", "Luogo"],
            state="readonly"
        )
        self.filtro_categoria.set("Tutte")
        self.filtro_tags      = tk.Entry(container, width=20)
        self.filtro_testo     = tk.Entry(container, width=30)
        tk.Label(container, text="Filtro Categoria:").grid(row=7, column=0, sticky="e")
        self.filtro_categoria.grid(row=7, column=1, sticky="w")
        tk.Label(container, text="Filtro Tag:").grid(row=8, column=0, sticky="e")
        self.filtro_tags.grid(row=8, column=1, sticky="w")
        tk.Label(container, text="Contiene testo:").grid(row=9, column=0, sticky="e")
        self.filtro_testo.grid(row=9, column=1, sticky="w")
        tk.Button(container, text="Filtra", command=self.filtra_note).grid(row=10, column=1, sticky="e")

        # anteprima
        if anteprima_frame:
            self.anteprima = tk.Text(anteprima_frame, height=15, width=40, state="disabled")
            self.anteprima.pack(fill="both", expand=True)
            self.lista_note.bind("<<ListboxSelect>>", self.mostra_anteprima)

        self.aggiorna_lista()

    def salva_nota(self):
        titolo    = self.titolo_entry.get()
        testo     = self.testo_text.get("1.0", tk.END).strip()
        categoria = self.categoria_combo.get()
        tags      = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        if not titolo:
            return
        nota = {"titolo": titolo, "testo": testo, "categoria": categoria, "tags": tags}
        if self.editing_index is not None:
            self.note[self.editing_index] = nota
        else:
            self.note.append(nota)
        self.salva_su_file()
        self.aggiorna_lista()
        self.pulisci_campi()

    def modifica_selezione(self):
        sel = self.lista_note.curselection()
        if not sel:
            return
        i = sel[0]
        self.editing_index = i
        nota = self.note[i]
        self.titolo_entry.delete(0, tk.END)
        self.titolo_entry.insert(0, nota["titolo"])
        self.testo_text.delete("1.0", tk.END)
        self.testo_text.insert("1.0", nota["testo"])
        self.categoria_combo.set(nota["categoria"])
        self.tags_entry.delete(0, tk.END)
        self.tags_entry.insert(0, ", ".join(nota["tags"]))

    def elimina_nota(self):
        sel = self.lista_note.curselection()
        if not sel:
            return
        if messagebox.askyesno("Elimina", "Eliminare la nota selezionata?"):
            del self.note[sel[0]]
            self.salva_su_file()
            self.aggiorna_lista()

    def filtra_note(self):
        filtro_cat = self.filtro_categoria.get()
        filtro_tag = self.filtro_tags.get().strip().lower()
        filtro_txt = self.filtro_testo.get().strip().lower()
        self.lista_note.delete(0, tk.END)
        for i, nota in enumerate(self.note):
            if filtro_cat != "Tutte" and nota["categoria"] != filtro_cat:
                continue
            if filtro_tag and filtro_tag not in ",".join(nota["tags"]).lower():
                continue
            if filtro_txt and filtro_txt not in nota["testo"].lower():
                continue
            tags = ", ".join(nota["tags"])
            self.lista_note.insert(tk.END,
                f"{i+1}. {nota['titolo']} [{nota['categoria']}] ({tags})"
            )

    def aggiorna_lista(self):
        self.lista_note.delete(0, tk.END)
        for i, nota in enumerate(self.note):
            tags = ", ".join(nota["tags"])
            self.lista_note.insert(tk.END,
                f"{i+1}. {nota['titolo']} [{nota['categoria']}] ({tags})"
            )

    def pulisci_campi(self):
        self.titolo_entry.delete(0, tk.END)
        self.testo_text.delete("1.0", tk.END)
        self.categoria_combo.set("Generale")
        self.tags_entry.delete(0, tk.END)
        self.filtro_tags.delete(0, tk.END)
        self.filtro_testo.delete(0, tk.END)
        self.editing_index = None
        if hasattr(self, "anteprima"):
            self.anteprima.configure(state="normal")
            self.anteprima.delete("1.0", tk.END)
            self.anteprima.configure(state="disabled")

    def mostra_anteprima(self, event):
        sel = self.lista_note.curselection()
        if not sel:
            return
        nota = self.note[sel[0]]
        self.anteprima.configure(state="normal")
        self.anteprima.delete("1.0", tk.END)
        self.anteprima.insert(tk.END, "TITOLO: " + nota["titolo"]+"\n")
        self.anteprima.insert(tk.END, "TESTO: " + nota["testo"])
        self.anteprima.configure(state="disabled")
