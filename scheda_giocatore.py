import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class SchedaPersonaggio:
    def __init__(self):
        self.entries = {}
        self.mods = {}
        self.equipaggiamento = []
        self.abilita = []
        self.incantesimi = []
        self.filename = None

        self.attributes = ["forza", "destrezza", "costituzione",
                           "intelligenza", "saggezza", "carisma"]
        self.numeric_fields = ["livello", "ca", "iniziativa",
                               "velocita", "pf_massimi",
                               "pf_attuali", "pf_temporanei"] + self.attributes

    def calc_mod(self, val):
        try:
            return (int(val) - 10) // 2
        except:
            return 0

    def update_modifiers(self, *args):
        for attr in self.attributes:
            v = self.entries[attr].get()
            self.mods[attr].set(f"{self.calc_mod(v):+}")

    def modifica_pf(self, delta):
        try:
            temp    = int(self.entries["pf_temporanei"].get())
            attuali = int(self.entries["pf_attuali"].get())
            if delta < 0 and temp > 0:
                da_sot = min(abs(delta), temp)
                temp -= da_sot
                delta += da_sot
            nuovi = attuali + delta
            max_pf = int(self.entries["pf_massimi"].get())
            nuovi = max(0, min(nuovi, max_pf))
            self.entries["pf_attuali"].delete(0, tk.END)
            self.entries["pf_attuali"].insert(0, str(nuovi))
            self.entries["pf_temporanei"].delete(0, tk.END)
            self.entries["pf_temporanei"].insert(0, str(temp))
        except:
            pass

    def reset_pf(self):
        try:
            max_pf = int(self.entries["pf_massimi"].get())
            self.entries["pf_attuali"].delete(0, tk.END)
            self.entries["pf_attuali"].insert(0, str(max_pf))
            self.entries["pf_temporanei"].delete(0, tk.END)
            self.entries["pf_temporanei"].insert(0, "0")
        except:
            pass

    def salva_tutto(self):
        data = {k: e.get() for k, e in self.entries.items()}
        for k in self.numeric_fields:
            try:
                data[k] = int(data[k])
            except:
                data[k] = 0
        data["equipaggiamento"] = self.equipaggiamento
        data["abilita"]         = self.abilita
        data["incantesimi"]     = self.incantesimi

        if not self.filename:
            self.filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Salva Scheda con Nome"
            )
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Salvato", "Scheda salvata correttamente.")

    def carica_tutto(self):
        fname = filedialog.askopenfilename(
            filetypes=[("JSON","*.json")], title="Carica Scheda")
        if not fname: return
        with open(fname,"r",encoding="utf-8") as f:
            data = json.load(f)
        self.filename = fname

        # per ogni entry, salva lo stato, la setti normal, popoli, e ripristini
        for key, entry in self.entries.items():
            prev = entry.cget("state")
            entry.config(state="normal")
            entry.delete(0,tk.END)
            entry.insert(0,str(data.get(key,"")))
            entry.config(state=prev)

        self.update_modifiers()
        self.equipaggiamento = data.get("equipaggiamento",[])
        self.abilita         = data.get("abilita",[])
        self.incantesimi     = data.get("incantesimi",[])
        self.aggiorna_liste()
        messagebox.showinfo("Caricato","Scheda caricata con successo.")
    
    
    def aggiorna_liste(self):
        self.aggiorna_lista_eq()
        self.aggiorna_lista_ab()
        self.aggiorna_lista_inc()

    def reset_scheda(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        for v in self.mods.values():
            v.set("+0")
        self.equipaggiamento.clear()
        self.abilita.clear()
        self.incantesimi.clear()
        try:
            self.aggiorna_liste()
        except:
            pass

    def crea_scheda(self, container):
        # Campo ID Diario readonly
        fields = [
            ("ID Diario",      "id_diario"),
            ("Nome",           "nome"),
            ("Classe",         "classe"),
            ("Razza",          "razza"),
            ("Livello",        "livello"),
            ("CA",             "ca"),
            ("Iniziativa",     "iniziativa"),
            ("Velocità",       "velocita"),
            ("PF Max",         "pf_massimi"),
            ("PF Attuali",     "pf_attuali"),
            ("PF Temporanei",  "pf_temporanei")
        ]
        for i, (lbl, key) in enumerate(fields):
            tk.Label(container, text=lbl + ":").grid(row=i, column=0, sticky="e")
            ent = tk.Entry(container, width=20)
            ent.grid(row=i, column=1, pady=2)
            if key == "id_diario":
                ent.config(state="readonly")
            self.entries[key] = ent

        # PF modifier buttons
        pff = tk.Frame(container)
        pff.grid(row=9, column=2, columnspan=3, pady=5)
        tk.Label(pff, text="Modifica PF: ").pack(side=tk.LEFT)
        tk.Button(pff, text="-1", command=lambda: self.modifica_pf(-1)).pack(side=tk.LEFT)
        tk.Button(pff, text="+1", command=lambda: self.modifica_pf(1)).pack(side=tk.LEFT)
        tk.Button(pff, text="Reset", command=self.reset_pf).pack(side=tk.LEFT)

        # Attributi + mod
        tk.Label(container, text="Attributi:").grid(row=0, column=2, padx=20)
        for idx, attr in enumerate(self.attributes):
            tk.Label(container, text=attr.capitalize()).grid(row=idx+1, column=2)
            e = tk.Entry(container, width=5)
            e.grid(row=idx+1, column=3)
            e.bind("<KeyRelease>", self.update_modifiers)
            self.entries[attr] = e
            self.mods[attr]    = tk.StringVar(value="+0")
            tk.Label(container, textvariable=self.mods[attr]).grid(row=idx+1, column=4)

    # Equipaggiamento, Abilità e Incantesimi: copia qui i metodi già esistenti
    # (crea_equipaggiamento, aggiungi_oggetto, ..., crea_abilita, crea_incantesimi, etc.)


    def crea_equipaggiamento(self, container):
        self.nome_eq       = tk.Entry(container, width=30)
        self.categoria_eq  = ttk.Combobox(container,
                                          values=["Arma", "Armatura", "Pozione", "Magico", "Generico"],
                                          state="readonly")
        self.categoria_eq.set("Generico")
        self.descrizione_eq = tk.Text(container, height=3, width=40)
        self.bonus_eq       = tk.Entry(container, width=30)
        self.bonus_var      = tk.BooleanVar()

        tk.Label(container, text="Nome:").grid(row=0, column=0, sticky="e")
        self.nome_eq.grid(row=0, column=1)
        tk.Label(container, text="Categoria:").grid(row=1, column=0, sticky="e")
        self.categoria_eq.grid(row=1, column=1)
        tk.Label(container, text="Descrizione:").grid(row=2, column=0, sticky="ne")
        self.descrizione_eq.grid(row=2, column=1)
        tk.Label(container, text="Bonus:").grid(row=3, column=0, sticky="e")
        self.bonus_eq.grid(row=3, column=1)
        tk.Checkbutton(container, text="Bonus attivo",
                       variable=self.bonus_var).grid(row=4, column=1, sticky="w")
        tk.Button(container, text="Aggiungi",
                  command=self.aggiungi_oggetto).grid(row=5, column=1, sticky="e")
        self.lista_eq = tk.Listbox(container, width=60)
        self.lista_eq.grid(row=6, column=0, columnspan=2)
        tk.Button(container, text="Rimuovi",
                  command=self.rimuovi_oggetto).grid(row=7, column=1, sticky="e")

    def aggiungi_oggetto(self):
        obj = {
            "nome": self.nome_eq.get(),
            "categoria": self.categoria_eq.get(),
            "descrizione": self.descrizione_eq.get("1.0", tk.END).strip(),
            "bonus": self.bonus_eq.get(),
            "bonus_attivo": self.bonus_var.get()
        }
        if not obj["nome"]:
            return
        self.equipaggiamento.append(obj)
        self.aggiorna_lista_eq()
        self.nome_eq.delete(0, tk.END)
        self.categoria_eq.set("Generico")
        self.descrizione_eq.delete("1.0", tk.END)
        self.bonus_eq.delete(0, tk.END)
        self.bonus_var.set(False)

    def rimuovi_oggetto(self):
        sel = self.lista_eq.curselection()
        if sel:
            del self.equipaggiamento[sel[0]]
            self.aggiorna_lista_eq()

    def aggiorna_lista_eq(self):
        self.lista_eq.delete(0, tk.END)
        for o in self.equipaggiamento:
            stato = "[ON]" if o.get("bonus_attivo") else "[OFF]"
            bonus = f" → {o['bonus']}" if o.get("bonus") else ""
            self.lista_eq.insert(tk.END,
                f"{o['nome']} ({o['categoria']}) {stato}{bonus}"
            )

    def crea_abilita(self, container):
        self.nome_ab        = tk.Entry(container, width=30)
        self.tipo_ab        = ttk.Combobox(
            container,
            values=["Classe", "Talento", "Raziale", "Incantesimo", "Generico"],
            state="readonly"
        )
        self.tipo_ab.set("Generico")
        self.descrizione_ab = tk.Text(container, height=3, width=40)

        tk.Label(container, text="Nome:").grid(row=0, column=0, sticky="e")
        self.nome_ab.grid(row=0, column=1)
        tk.Label(container, text="Tipo:").grid(row=1, column=0, sticky="e")
        self.tipo_ab.grid(row=1, column=1)
        tk.Label(container, text="Descrizione:").grid(row=2, column=0, sticky="ne")
        self.descrizione_ab.grid(row=2, column=1)
        tk.Button(container, text="Aggiungi",
                  command=self.aggiungi_abilita).grid(row=3, column=1, sticky="e")
        self.lista_ab = tk.Listbox(container, width=60)
        self.lista_ab.grid(row=4, column=0, columnspan=2)
        tk.Button(container, text="Rimuovi",
                  command=self.rimuovi_abilita).grid(row=5, column=1, sticky="e")
        self.lista_ab.bind("<<ListboxSelect>>", self.mostra_descrizione_abilita)

        self.descrizione_abilita_output = tk.Text(container, height=5, width=60)
        self.descrizione_abilita_output.grid(row=6, column=0, columnspan=2)

    def aggiungi_abilita(self):
        ab = {
            "nome": self.nome_ab.get(),
            "tipo": self.tipo_ab.get(),
            "descrizione": self.descrizione_ab.get("1.0", tk.END).strip()
        }
        if not ab["nome"]:
            return
        self.abilita.append(ab)
        self.aggiorna_lista_ab()
        self.nome_ab.delete(0, tk.END)
        self.tipo_ab.set("Generico")
        self.descrizione_ab.delete("1.0", tk.END)
        self.salva_tutto()

    def rimuovi_abilita(self):
        sel = self.lista_ab.curselection()
        if sel:
            del self.abilita[sel[0]]
            self.aggiorna_lista_ab()
            self.salva_tutto()

    def aggiorna_lista_ab(self):
        self.lista_ab.delete(0, tk.END)
        for a in self.abilita:
            self.lista_ab.insert(tk.END, f"{a['nome']} ({a['tipo']})")

    def mostra_descrizione_abilita(self, event):
        sel = self.lista_ab.curselection()
        if sel:
            ab = self.abilita[sel[0]]
            self.descrizione_abilita_output.delete("1.0", tk.END)
            self.descrizione_abilita_output.insert(tk.END, ab.get("descrizione", ""))

    def crea_incantesimi(self, container):
        self.nome_inc        = tk.Entry(container, width=30)
        self.livello_inc     = ttk.Combobox(container, values=[str(i) for i in range(10)], state="readonly")
        self.livello_inc.set("0")
        self.scuola_inc      = ttk.Combobox(container, values=[
            "Evocazione", "Abiurazione", "Illusione",
            "Necromanzia", "Trasmutazione", "Generica"
        ], state="readonly")
        self.scuola_inc.set("Generica")
        self.descrizione_inc = tk.Text(container, height=3, width=40)
        self.lanci_inc       = tk.Entry(container, width=5)

        tk.Label(container, text="Nome:").grid(row=0, column=0, sticky="e")
        self.nome_inc.grid(row=0, column=1)
        tk.Label(container, text="Livello:").grid(row=1, column=0, sticky="e")
        self.livello_inc.grid(row=1, column=1)
        tk.Label(container, text="Scuola:").grid(row=2, column=0, sticky="e")
        self.scuola_inc.grid(row=2, column=1)
        tk.Label(container, text="Descrizione:").grid(row=3, column=0, sticky="ne")
        self.descrizione_inc.grid(row=3, column=1)
        tk.Label(container, text="Lanci disponibili:").grid(row=4, column=0, sticky="e")
        self.lanci_inc.grid(row=4, column=1)
        tk.Button(container, text="Aggiungi",
                  command=self.aggiungi_incantesimo).grid(row=5, column=1, sticky="e")
        self.lista_inc = tk.Listbox(container, width=60)
        self.lista_inc.grid(row=6, column=0, columnspan=2)
        self.lista_inc.bind("<<ListboxSelect>>", self.mostra_descrizione_incantesimo)

        self.descrizione_output = tk.Text(container, height=5, width=60)
        self.descrizione_output.grid(row=7, column=0, columnspan=2)
        tk.Button(container, text="Rimuovi",
                  command=self.rimuovi_incantesimo).grid(row=8, column=1, sticky="e")

    def aggiungi_incantesimo(self):
        inc = {
            "nome": self.nome_inc.get(),
            "livello": self.livello_inc.get(),
            "scuola": self.scuola_inc.get(),
            "descrizione": self.descrizione_inc.get("1.0", tk.END).strip(),
            "lanci_disponibili": int(self.lanci_inc.get() or 0)
        }
        if not inc["nome"]:
            return
        self.incantesimi.append(inc)
        self.aggiorna_lista_inc()
        self.salva_tutto()

        self.nome_inc.delete(0, tk.END)
        self.livello_inc.set("0")
        self.scuola_inc.set("Generica")
        self.descrizione_inc.delete("1.0", tk.END)
        self.lanci_inc.delete(0, tk.END)

    def rimuovi_incantesimo(self):
        sel = self.lista_inc.curselection()
        if sel:
            del self.incantesimi[sel[0]]
            self.aggiorna_lista_inc()
            self.salva_tutto()

    def mostra_descrizione_incantesimo(self, event):
        sel = self.lista_inc.curselection()
        if sel:
            inc = self.incantesimi[sel[0]]
            self.descrizione_output.delete("1.0", tk.END)
            self.descrizione_output.insert(tk.END, inc.get("descrizione", ""))

    def aggiorna_lista_inc(self):
        self.lista_inc.delete(0, tk.END)
        ordinati = sorted(self.incantesimi, key=lambda x: int(x.get("livello", 0)))
        for i in ordinati:
            self.lista_inc.insert(tk.END,
                f"{i['nome']} (Lv {i['livello']}) [{i['scuola']}]"
            )
