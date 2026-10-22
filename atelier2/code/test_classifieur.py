# code/test_classifieur.py
"""
Test rapide du classifieur sur 5 phrases connues (Page 6 du TP).
Vérifie que l'appel API + parsing JSON fonctionne correctement.
"""
import time
from classifieur import classer

MODELE = "qwen/qwen3.8-27b"

PHRASES_TEST = [
    ("J'ai ete preleve deux fois ce mois-ci.", "facturation"),
    ("L'application plante au demarrage depuis la mise a jour.", "technique"),
    ("Je n'arrive plus a me connecter, mon mot de passe ne marche plus.", "compte"),
    ("Je voudrais resilier mon abonnement a la fin du mois.", "commercial"),
    ("Ma facture indique 89 euros au lieu de 39 euros.", "facturation"),
]

print(f"Test du classifieur avec le modèle : {MODELE}\n")
print(f"{'#':<3} {'Attendu':<14} {'Prédit':<14} {'OK?':<5} Texte")
print("-" * 80)

corrects = 0
for i, (texte, attendu) in enumerate(PHRASES_TEST, 1):
    prediction = classer(texte, modele=MODELE)
    ok = prediction == attendu
    corrects += ok
    symbole = "OK" if ok else "XX"
    print(f"{i:<3} {attendu:<14} {prediction:<14} {symbole:<5} {texte[:55]}")
    time.sleep(0.5)  # respect du rate limit

print(f"\nRésultat : {corrects}/{len(PHRASES_TEST)} corrects")
