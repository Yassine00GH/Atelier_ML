# code/evaluer.py
"""
Évalue un modèle sur les 72 tickets et sauvegarde les résultats (Pages 8-9 du TP).

Usage :
    python evaluer.py openai/gpt-oss-20b
    python evaluer.py openai/gpt-oss-120b
    python evaluer.py qwen/qwen3.8-27b
"""
import json
import sys
import time
from pathlib import Path

from classifieur import charger_tickets, classer, CONSIGNE
from evaluation import afficher_rapport

CHEMIN_DATA = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"
CHEMIN_RESULTATS = Path(__file__).resolve().parent.parent / "resultats"


def evaluer_modele(tickets, modele, consigne=CONSIGNE):
    """
    Classe tous les tickets avec le modèle donné.
    Renvoie (vrais, predits, details).
    """
    vrais = []
    predits = []
    details = []

    for i, t in enumerate(tickets):
        texte = t["texte"]
        vrai = t["categorie"]

        # Appel API avec gestion d'erreur (rate limit, timeout)
        try:
            prediction = classer(texte, modele=modele, consigne=consigne)
        except Exception as e:
            print(f"  [ERREUR API] {t['id']} : {e}", flush=True)
            time.sleep(5)
            try:
                prediction = classer(texte, modele=modele, consigne=consigne)
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

        # Pause pour ne pas dépasser le rate limit
        time.sleep(0.5)

    return vrais, predits, details


def main():
    if len(sys.argv) < 2:
        print("Usage : python evaluer.py <nom_du_modele>")
        print("Exemple : python evaluer.py qwen/qwen3.8-27b")
        sys.exit(1)

    modele = sys.argv[1]

    # Nom de fichier propre pour les résultats (/ -> _)
    nom_fichier = modele.replace("/", "_") + ".json"

    tickets = charger_tickets(CHEMIN_DATA)
    print(f"Chargé {len(tickets)} tickets.\n")
    print(f"Modèle : {modele}")
    print("=" * 60)

    vrais, predits, details = evaluer_modele(tickets, modele)
    rapport = afficher_rapport(modele, vrais, predits)

    # Sauvegarde des résultats détaillés
    resultats = {
        "modele": modele,
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
