#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as sd
from tabulate import tabulate
from datetime import datetime
from tkinter import messagebox
import random
from tkinter import filedialog
from tkcalendar import Calendar



app = tk.Tk()
app.title("Gestion de Factures")
app.geometry("1280x720")
app.resizable(height=False,width=False)
app.config(bg="#12486B")

label_client = tk.Label(app, text="Client:",font=("Helvetica", 18),bg="#12486B",fg="#E9B824")
label_client.place(x=150,y=110)
entry_client = tk.Entry(app,font=("Helvetica", 18),bg="#12486B",fg="#E9B824",insertbackground="white")
entry_client.place(x=250,y=110)
                   
# Liste pour stocker les numéros de facture existants
numeros_de_facture_existant = []

prix = 0

label_date = tk.Label(app, text="Date:",font=("Helvetica", 18),bg="#12486B",fg="#E9B824")
label_date.place(x=590,y=110)

style = ttk.Style()
style.configure("MonStyle.TCombobox", 
                fieldbackground="#2E4374", 
                arrowsize=20, 
                borderwidth=4, 
                foreground="#E9B824")        
date_combobox = ttk.Combobox(app, width=30, style="MonStyle.TCombobox")

# Créez un Combobox pour la sélection de la date
date_combobox['values'] = [" ","Sélectionnez une date"]
date_combobox.set(" ")
date_combobox.place(x=675,y=110)

# Fonction pour afficher le calendrier
def afficher_calendrier():
    cal_window = tk.Toplevel(app)  # Créez une fenêtre fille
    cal = Calendar(cal_window)
    cal.pack()

    def selectionner_date():
        selected_date = cal.get_date()
        date_combobox.set(selected_date)
        cal_window.destroy()

    bouton_selectionner = tk.Button(cal_window, text="Sélectionner la date", command=selectionner_date)
    bouton_selectionner.pack()

def selection_combobox(event):
    client = entry_client.get().title()  # Obtenez le contenu du champ client
    entry_client.delete(0,"end")
    entry_client.insert(0,client)

    date_combobox.focus()
    selected_item = date_combobox.get()
    if selected_item == "Sélectionnez une date":
        # Afficher le calendrier lorsque "Sélectionnez une date" est sélectionné
        afficher_calendrier()

date_combobox.bind("<<ComboboxSelected>>", selection_combobox)
entry_client.bind("<Return>", selection_combobox)
entry_client.bind("<Tab>", selection_combobox)


columns = ("Article", "Quantité", "Prix $")
table = ttk.Treeview(app, columns=columns, show="headings")

# Définissez une police personnalisée en utilisant tag_configure
table.tag_configure("custom_font", font=("Helvetica", 14),background="#0B666A",foreground="#E9B824")  # Spécifiez la police et la taille de police souhaitées

for col in columns:
    table.heading(col, text=col,anchor="w")

table.place(x=150,y=200,width=800,height=400)

add_bouton = tk.Button(app, text="Ajouter Article",width=13,bg="#12486B",fg="yellow",font=("Helvetica", 16))
total_bouton = tk.Button(app, text="Calculer Total",width=13,bg="#12486B",fg="yellow",font=("Helvetica", 16))
modifier_bouton = tk.Button(app, text="Modifier Article",width=13,bg="#12486B",fg="yellow",font=("Helvetica", 16))
supprimer_bouton = tk.Button(app,text="Supprimer Article",width=13,bg="#12486B",fg="yellow",font=("Helvetica", 16))
afficher_bouton = tk.Button(app,text="Afficher Factures",width=13,bg="#12486B",fg="yellow",font=("Helvetica", 16))

add_bouton.place(x=150,y=620)
modifier_bouton.place(x=455,y=620)
supprimer_bouton.place(x=765,y=620)
total_bouton.place(x=1000,y=225)
afficher_bouton.place(x=1000,y=325)

entry_client.focus()

def ajouter_article():
    client = entry_client.get().title()  # Obtenez le contenu du champ client
    date = date_combobox.get()
    if not client:
        # Le champ client est vide, affichez une erreur ou effectuez une action appropriée
        messagebox.showerror("Erreur", "Veuillez saisir le nom du client.")
        return  # Quittez la fonction
    if date == " ":
        messagebox.showerror("Erreur", "Veuillez saisir la date.")
        return
    article = sd.askstring("Nouvel Article", "Entrez l'article :").title()
    quantite = sd.askinteger("Quantité", "Entrez le nombre :")
    prix = sd.askfloat("Prix", "Entrez le prix :")
    if article and quantite is not None and prix is not None:
        # Insérez des données avec la police personnalisée
        table.insert("", "end", values=(article, quantite, prix), tags=("custom_font"))
    else:
        messagebox.showerror("Erreur", "Entrer tout les champs")
        return
    
def calculer_total():
    if len(table.get_children()) == 0:
        messagebox.showerror("Erreur", "Aucuns articles entrée")
        return

    total = 0
    montant_total_tps = 0
    montant_total_tvq = 0

    total_sans_taxes = 0  # Pour le montant total avant taxes
    taux_tps = 0.05  # Taux de la TPS (5 %)
    taux_tvq = 0.09975  # Taux de la TVQ (9,975 %)

    for item in table.get_children():
        quantite = int(table.item(item, "values")[1])
        prix = float(table.item(item, "values")[2])
        montant_sans_taxes = quantite * prix  # Montant avant taxes pour cet article

        # Ajoutez le montant sans taxes au total avant taxes
        total_sans_taxes += montant_sans_taxes

        # Calculez la TPS et la TVQ pour cet article
        tps = montant_sans_taxes * taux_tps
        tvq = montant_sans_taxes * taux_tvq

        montant_total_tps = montant_total_tps + tps
        montant_total_tvq = montant_total_tvq + tvq

        # Ajoutez la TPS et la TVQ au montant total
        total += montant_sans_taxes + tps + tvq

    if numeros_de_facture_existant == []:
        global numero_facture
        numero_facture = generer_numero_facture()


    afficher_formulaire_facture(montant_total_tvq, montant_total_tps)

def generer_numero_facture():
    while True:
        numero_facture = random.randint(1000, 9999)  # Par exemple, un numéro aléatoire de 4 chiffres
        if numero_facture not in numeros_de_facture_existant:
            numeros_de_facture_existant.append(numero_facture)
            return numero_facture

def afficher_formulaire_facture(tvq, tps):
    global facture_text 
    formulaire_facture = tk.Toplevel(app)
    formulaire_facture.title("Facture")
    formulaire_facture.geometry("800x500")

    client = entry_client.get().title()
    date = date_combobox.get()

    total = 0

    facture_text = f"#:{numero_facture}\nClient : {client}\nDate : {date}\n"

    facture_data = []  # Stockage des données pour le tableau

    for item in table.get_children():
        nom_article = table.item(item, "values")[0]
        quantite = int(table.item(item, "values")[1])
        prix = float(table.item(item, "values")[2])
        total_article = quantite * prix

        facture_data.append([nom_article, quantite, f"{prix:.2f}$", f"{total_article:.2f}$"])

        total += total_article

    total_taxes = total + tps + tvq

    facture_text += tabulate(facture_data, headers=["Article", "Quantité", "Prix unitaire", "Montant total"], tablefmt="pretty")
    facture_text += f"\nAvant Taxes : {round(total,2)}$"  
    facture_text += f"\ntps : {round(tps,2)}$"
    facture_text += f"\ntvq : {round(tvq,2)}$"
    facture_text += f"\nTotal : {round(total_taxes,2)}$"  # Ajoutez la ligne du total ici

    facture_text_widget = tk.Text(formulaire_facture)
    facture_text_widget.insert(tk.END, facture_text)
    facture_text_widget.pack()
    
    facture_text_widget.config(state=tk.DISABLED)  # Empêche la modification du texte
    
    def sauvegarder():
            date = datetime.now().strftime("%Y-%m-%d")

            if messagebox.askyesno("Confirmation", "Sauvegarder?"):
                with open(f"facture_{numero_facture}_{date}.txt", "w") as fichier:
                    fichier.write(facture_text)
                    for item in table.get_children():
                        table.delete(item)


                entry_client.delete(0, "end")
                formulaire_facture.destroy()
                entry_client.focus()
        
    sauvegarder_bouton = tk.Button(formulaire_facture,text="Sauvegrader",command=sauvegarder)
    sauvegarder_bouton.pack()
    
    formulaire_facture.mainloop()


def supprimer_article():
    global selected_item  # Utilisez la variable globale pour suivre la ligne sélectionnée
    selected_item = table.selection()  # Mise à jour de la ligne sélectionnée

    if not selected_item:
        messagebox.showerror("Erreur", "Aucune ligne sélectionnée.")
        return
    if selected_item:
        if messagebox.askyesno("Confirmation", "Supprimer Article?"):
            # Récupérer les valeurs actuelles de la ligne sélectionnée
            ligne_selectionnee = table.delete(selected_item)


def modifier_article():
    global selected_item  # Utilisez la variable globale pour suivre la ligne sélectionnée
    selected_item = table.selection()  # Mise à jour de la ligne sélectionnée

    if not selected_item:
        messagebox.showerror("Erreur", "Aucune ligne sélectionnée.")
        return

    # Récupérer les valeurs actuelles de la ligne sélectionnée
    ligne_selectionnee = table.item(selected_item)
    article_actuel = ligne_selectionnee['values'][0]
    quantite_actuelle = ligne_selectionnee['values'][1]
    prix_actuel = ligne_selectionnee['values'][2]

    # Afficher les valeurs actuelles dans les boîtes de dialogue pour modification
    nouvel_article = sd.askstring("Modifier l'article", "Nouvel article :", initialvalue=article_actuel).title()
    nouvelle_quantite = sd.askinteger("Modifier la quantité", "Nouvelle quantité :", initialvalue=quantite_actuelle)
    nouveau_prix = sd.askfloat("Modifier le prix", "Nouveau prix :", initialvalue=prix_actuel)
    prix_signe = nouveau_prix
    prix_signe = f"{prix_signe}$"

    if nouvel_article is not None and nouvelle_quantite is not None and nouveau_prix is not None:
        # Mettre à jour la ligne sélectionnée avec les nouvelles valeurs
        table.item(selected_item, values=(nouvel_article, nouvelle_quantite, nouveau_prix))
    else:
        messagebox.showerror("Erreur", "Entrez toutes les valeurs.")

def afficher_facture():
    # Fonction pour sélectionner un fichier à décrypter
    nom_fichier = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Facture", "*.txt")])
    if nom_fichier:
        with open(nom_fichier, "r") as fichier_facture:
            contenu_texte = fichier_facture.read()

            # Créer une nouvelle fenêtre
            affichage_window = tk.Toplevel(app)
            affichage_window.title("Facture")

            # Définir la géométrie pour centrer la fenêtre
            affichage_window.geometry("800x500")

            # Créer un widget Text pour afficher le contenu du fichier texte
            text_widget = tk.Text(affichage_window)
            text_widget.pack()

            # Insérer le contenu du fichier dans le widget Text
            text_widget.insert(tk.END, contenu_texte)

            # Ajouter un bouton pour fermer la fenêtre
            fermer_button = tk.Button(affichage_window,text="Fermer",command=affichage_window.destroy)
            fermer_button.pack()
            
def quitter():
    if messagebox.askyesno("Confirmation", "Êtes-vous sûr de\n vouloir quitter ? "):
        app.destroy()

app.protocol("WM_DELETE_WINDOW", quitter)

add_bouton.config(command=ajouter_article)
modifier_bouton.config(command=modifier_article)
supprimer_bouton.config(command=supprimer_article)
total_bouton.config(command=calculer_total)
afficher_bouton.config(command=afficher_facture)


app.mainloop()
