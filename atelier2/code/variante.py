# code/variante.py
"""
Évalue la variante de consigne enrichie (CONSIGNE_EXEMPLES) sur le meilleur modèle (Page 10 du TP).

Usage :
    python variante.py <nom_du_modele>
    python variante.py qwen/qwen3.8-27b
"""
import json
import sys
import time
from pathlib import Path

from classifieur import charger_tickets, classer, CONSIGNE_EXEMPLES
from evaluation import afficher_rapport

CHEMIN_DATA = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"
CHEMIN_RESULTATS = Path(__file__).resolve().parent.parent / "resultats"


def evaluer_variante(tickets, modele):
    """
    Classe tous les tickets avec CONSIGNE_EXEMPLES (few-shot avec 4 exemples du TP).
    Renvoie (vrais, predits, details).
    """
    vrais = []
    predits = []
    details = []

    for i, t in enumerate(tickets):
        texte = t["texte"]
        vrai = t["categorie"]

        try:
            prediction = classer(texte, modele=modele, consigne=CONSIGNE_EXEMPLES)
        except Exception as e:
            print(f"  [ERREUR API] {t['id']} : {e}", flush=True)
            time.sleep(5)
            try:
                prediction = classer(texte, modele=modele, consigne=CONSIGNE_EXEMPLES)
            except Exception:
                prediction = "invalide"

        vrais.append(vrai)
        predits.append(prediction)
        details.append({
            "id": t["id"],
            "texte": texte,
            "vrai": vrai,
            "predit": prediction,
            "correct": vrai == prediction
        })

        symbole = "OK" if vrai == prediction else "XX"
        print(
            f"  [{i+1:02d}/{len(tickets)}] {symbole} {t['id']} "
            f"| vrai={vrai:<13} predit={prediction:<13} "
            f"| {texte[:50]}",
            flush=True
        )

        time.sleep(0.5)

    return vrais, predits, details


def main():
    if len(sys.argv) < 2:
        print("Usage : python variante.py <nom_du_modele>")
        print("Exemple : python variante.py qwen/qwen3.8-27b")
        sys.exit(1)

    modele = sys.argv[1]
    nom_fichier = modele.replace("/", "_") + "_variante.json"

    tickets = charger_tickets(CHEMIN_DATA)
    print(f"Chargé {len(tickets)} tickets.\n")
    print(f"Modèle : {modele} — Consigne : CONSIGNE_EXEMPLES (few-shot 4 exemples)")
    print("=" * 60)

    vrais, predits, details = evaluer_variante(tickets, modele)
    etiquette = f"{modele} + CONSIGNE_EXEMPLES"
    rapport = afficher_rapport(etiquette, vrais, predits)

    resultats = {
        "modele": modele,
        "consigne": "CONSIGNE_EXEMPLES",
        "rapport": rapport,
        "details": details
    }

    CHEMIN_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_sortie = CHEMIN_RESULTATS / nom_fichier
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)
    print(f"\n  → Résultats sauvegardés dans {chemin_sortie}")


if __name__ == "__main__":
    main()
