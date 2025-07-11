import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.filedialog import asksaveasfilename, askopenfilename
import json

def distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def saisir_coordonnees_auto(index, axis):
    # Valide et met à jour la coordonnée modifiée, puis rafraîchit le graphique si possible
    try:
        x = float(entries_x[index].get())
        y = float(entries_y[index].get())
        z = float(entries_z[index].get())
        points[index] = [x, y, z]
        afficher_resultat()
    except ValueError:
        # On peut choisir d'ignorer ou d'afficher une erreur ici, mais c'est plus fluide sans popup
        pass

def reset_interface():
    global points, canvas, n_p
    n_p = 0
    clear_all_point_widgets()
    entries_x.clear()
    entries_y.clear()
    entries_z.clear()
    points.clear()
    resultat_text.delete("1.0", tk.END)
    canvas = None
    initialiser_points()

def afficher_resultat():
    if not points or any(p is None for p in points):
        return  # Pas assez de données valides

    points_array = np.array(points)
    x_pos = points_array[:, 0]
    y_pos = points_array[:, 1]
    z_pos = points_array[:, 2]

    resultat_text.delete("1.0", tk.END)
    resultat_text.insert(tk.END, "Résultats des calculs:\n")
    for i in range(len(points) - 1):
        dist = distance(x_pos[i], y_pos[i], x_pos[i + 1], y_pos[i + 1])
        resultat_text.insert(tk.END, f"Distance entre le point {i+1} et {i+2} : {dist:.2f} m\n")

    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

        ax1.tricontourf(x_pos, y_pos, z_pos, levels=14, cmap='terrain')
        ax1.set_title("Carte topographique")
        ax1.set_xlabel("X (m)")
        ax1.set_ylabel("Y (m)")

        for i in range(len(points) - 1):
            ax2.plot((x_pos[i] + x_pos[i + 1]) / 2, (y_pos[i] + y_pos[i + 1]) / 2, 'ro')
        ax2.tricontourf(x_pos, y_pos, z_pos, levels=14, cmap='viridis')
        ax2.set_title("Carte des pentes")
        ax2.set_xlabel("X (m)")
        ax2.set_ylabel("Y (m)")

        global canvas, fig_to_save
        fig_to_save = fig
        if canvas:
            canvas.get_tk_widget().grid_forget()
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=n_p + 5, column=0, columnspan=7)

    except RuntimeError:
        messagebox.showerror("Erreur", "Impossible de générer la carte.")

def enregistrer_pdf():
    if fig_to_save:
        filename = asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            with PdfPages(filename) as pdf:
                pdf.savefig(fig_to_save)
            messagebox.showinfo("Enregistré", f"Graphiques enregistrés : {filename}")
    else:
        messagebox.showerror("Erreur", "Aucun graphique à enregistrer.")

def clear_all_point_widgets():
    for widgets_list in [labels_x, labels_y, labels_z, entries_x, entries_y, entries_z]:
        for w in widgets_list:
            w.grid_forget()
    labels_x.clear()
    labels_y.clear()
    labels_z.clear()
    entries_x.clear()
    entries_y.clear()
    entries_z.clear()

def construire_points():
    clear_all_point_widgets()
    for i in range(n_p):
        row = i
        label_x = tk.Label(root, text=f"Point {i+1} - X :")
        label_x.grid(row=row, column=0)
        labels_x.append(label_x)

        label_y = tk.Label(root, text="Y :")
        label_y.grid(row=row, column=2)
        labels_y.append(label_y)

        label_z = tk.Label(root, text="Z :")
        label_z.grid(row=row, column=4)
        labels_z.append(label_z)

        entry_x = tk.Entry(root)
        entry_x.grid(row=row, column=1)
        entry_x.insert(0, points[i][0] if points[i] is not None else "")
        entry_x.bind("<FocusOut>", lambda e, idx=i: saisir_coordonnees_auto(idx, 'x'))
        entry_x.bind("<Return>", lambda e, idx=i: saisir_coordonnees_auto(idx, 'x'))
        entries_x.append(entry_x)

        entry_y = tk.Entry(root)
        entry_y.grid(row=row, column=3)
        entry_y.insert(0, points[i][1] if points[i] is not None else "")
        entry_y.bind("<FocusOut>", lambda e, idx=i: saisir_coordonnees_auto(idx, 'y'))
        entry_y.bind("<Return>", lambda e, idx=i: saisir_coordonnees_auto(idx, 'y'))
        entries_y.append(entry_y)

        entry_z = tk.Entry(root)
        entry_z.grid(row=row, column=5)
        entry_z.insert(0, points[i][2] if points[i] is not None else "")
        entry_z.bind("<FocusOut>", lambda e, idx=i: saisir_coordonnees_auto(idx, 'z'))
        entry_z.bind("<Return>", lambda e, idx=i: saisir_coordonnees_auto(idx, 'z'))
        entries_z.append(entry_z)

def ajouter_point():
    global n_p
    n_p += 1
    points.append(None)
    construire_points()
    repositionner_widgets()

def supprimer_point():
    global n_p
    if n_p <= 2:
        messagebox.showwarning("Attention", "Il faut au moins deux points.")
        return
    n_p -= 1
    points.pop()
    construire_points()
    repositionner_widgets()
    afficher_resultat()

def repositionner_widgets():
    resultat_text.grid(row=n_p + 1, column=0, columnspan=7)
    button_reset.grid(row=n_p + 2, column=0, columnspan=7)
    button_pdf.grid(row=n_p + 3, column=0, columnspan=7)
    button_ajout.grid(row=n_p + 4, column=0, columnspan=2)
    button_suppression.grid(row=n_p + 4, column=2, columnspan=2)
    button_save_preset.grid(row=n_p + 4, column=4, columnspan=2)
    button_load_preset.grid(row=n_p + 4, column=6, columnspan=1)

def sauvegarder_preset():
    filename = asksaveasfilename(defaultextension=".json", filetypes=[("Fichiers JSON", "*.json")])
    if filename:
        # Sauvegarder les points valides uniquement
        data_to_save = [p if p is not None else [0,0,0] for p in points]
        with open(filename, 'w') as f:
            json.dump(data_to_save, f)
        messagebox.showinfo("Sauvegarde", f"Preset sauvegardé dans {filename}")

def charger_preset():
    global n_p, points
    filename = askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
    if filename:
        with open(filename, 'r') as f:
            data_loaded = json.load(f)
        if len(data_loaded) < 2:
            messagebox.showerror("Erreur", "Le preset doit contenir au moins deux points.")
            return
        n_p = len(data_loaded)
        points = data_loaded
        construire_points()
        repositionner_widgets()
        afficher_resultat()

root = tk.Tk()
root.title("Carte topographique dynamique")

n_p = simpledialog.askinteger("Nombre de points", "Combien de points ?", minvalue=2, initialvalue=4)

labels_x, labels_y, labels_z = [], [], []
entries_x, entries_y, entries_z = [], [], []
points = [None]*n_p

resultat_text = tk.Text(root, height=10, width=50)
button_reset = tk.Button(root, text="Réinitialiser", command=reset_interface)
button_pdf = tk.Button(root, text="Enregistrer en PDF", command=enregistrer_pdf)
button_ajout = tk.Button(root, text="Ajouter un point", command=ajouter_point)
button_suppression = tk.Button(root, text="Supprimer le dernier point", command=supprimer_point)
button_save_preset = tk.Button(root, text="Sauvegarder preset", command=sauvegarder_preset)
button_load_preset = tk.Button(root, text="Charger preset", command=charger_preset)

canvas = None
fig_to_save = None

construire_points()
repositionner_widgets()

root.mainloop()
