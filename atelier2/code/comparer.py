# code/comparer.py
"""
Compare les résultats de tous les modèles évalués (Pages 9-10 du TP).
Lit les fichiers JSON du dossier resultats/ et affiche :
  - Le tableau comparatif (accuracy, macro-F1, invalides)
  - Les tickets de désaccord entre modèles
  - Le delta en nombre de tickets
"""
import json
from pathlib import Path

CHEMIN_RESULTATS = Path(__file__).resolve().parent.parent / "resultats"
NB_TICKETS = 72  # nombre total de tickets dans le jeu de test


def charger_resultats():
    """
    Charge tous les fichiers JSON de résultats.
    Renvoie une liste de dicts triés par macro_f1 décroissant.
    """
    resultats = []
    for fichier in sorted(CHEMIN_RESULTATS.glob("*.json")):
        # On ignore les anciens fichiers (details_*.json, comparaison.json)
        if fichier.name.startswith("details_") or fichier.name == "comparaison.json":
            continue
        with open(fichier, encoding="utf-8") as f:
            data = json.load(f)

        # Le fichier doit contenir un "rapport" avec les métriques
        if "rapport" not in data:
            continue

        rapport = data["rapport"]
        resultats.append({
            "fichier": fichier.name,
            "modele": data.get("modele", "?"),
            "consigne": data.get("consigne", "CONSIGNE"),
            "accuracy": rapport["accuracy"],
            "macro_f1": rapport["macro_f1"],
            "invalides": rapport["invalides"],
            "details": data.get("details", []),
            "scores_par_classe": rapport.get("scores_par_classe", {}),
            "matrice_confusion": rapport.get("matrice_confusion", {})
        })

    # Tri par macro_f1 décroissant
    resultats.sort(key=lambda r: r["macro_f1"], reverse=True)
    return resultats


def afficher_tableau(resultats):
    """Affiche le tableau comparatif."""
    print("\n" + "=" * 80)
    print("  TABLEAU COMPARATIF DES MODÈLES")
    print("=" * 80)

    print(f"\n{'Candidat':<45} {'Accuracy':>9} {'Macro-F1':>9} {'Invalides':>10}")
    print("-" * 75)
    for r in resultats:
        nom = r["modele"]
        if r["consigne"] != "CONSIGNE":
            nom += " + exemples"
        print(f"{nom:<45} {r['accuracy']:>9.3f} {r['macro_f1']:>9.3f} {r['invalides']:>10.3f}")


def afficher_ecarts(resultats):
    """Affiche l'écart entre le 1er et le 2e en points de macro-F1 et en nb de tickets."""
    if len(resultats) < 2:
        print("\n  Pas assez de modèles pour calculer un écart.")
        return

    premier = resultats[0]
    deuxieme = resultats[1]
    delta_f1 = premier["macro_f1"] - deuxieme["macro_f1"]
    delta_tickets = delta_f1 * NB_TICKETS / 100  # approximation

    # Calcul exact : nb de tickets corrects en plus
    corrects_1 = sum(1 for d in premier["details"] if d["correct"])
    corrects_2 = sum(1 for d in deuxieme["details"] if d["correct"])
    delta_tickets_exact = corrects_1 - corrects_2

    print(f"\n--- Écart entre 1er et 2e ---")
    nom1 = premier["modele"] + (" + exemples" if premier["consigne"] != "CONSIGNE" else "")
    nom2 = deuxieme["modele"] + (" + exemples" if deuxieme["consigne"] != "CONSIGNE" else "")
    print(f"  1er : {nom1} (macro-F1 = {premier['macro_f1']:.3f})")
    print(f"  2e  : {nom2} (macro-F1 = {deuxieme['macro_f1']:.3f})")
    print(f"  Δ macro-F1  : {delta_f1:+.3f} points")
    print(f"  Δ tickets   : {delta_tickets_exact:+d} tickets bien classés en plus")
    print(f"  (rappel : 1 ticket ≈ {100/NB_TICKETS:.1f} points d'accuracy)")


def afficher_desaccords(resultats):
    """Affiche les tickets où les modèles ne sont pas d'accord entre eux."""
    if len(resultats) < 2:
        return

    print(f"\n--- Tickets de désaccord entre modèles ---")

    # On construit un dictionnaire {id_ticket: {modele: prediction}}
    tickets_par_id = {}
    for r in resultats:
        nom = r["modele"] + (" + exemples" if r["consigne"] != "CONSIGNE" else "")
        for d in r["details"]:
            tid = d["id"]
            if tid not in tickets_par_id:
                tickets_par_id[tid] = {"texte": d["texte"][:55], "vrai": d["vrai"], "predictions": {}}
            tickets_par_id[tid]["predictions"][nom] = d["predit"]

    desaccords = []
    for tid, info in sorted(tickets_par_id.items()):
        preds = list(info["predictions"].values())
        if len(set(preds)) > 1:  # au moins une prédiction différente
            desaccords.append((tid, info))

    if not desaccords:
        print("  Aucun désaccord entre les modèles !")
        return

    print(f"  {len(desaccords)} tickets en désaccord :\n")
    for tid, info in desaccords:
        print(f"  {tid} | vrai={info['vrai']:<13} | {info['texte']}")
        for nom, pred in info["predictions"].items():
            ok = "OK" if pred == info["vrai"] else "XX"
            print(f"    {ok} {nom:<40} -> {pred}")
        print()


def afficher_categorie_faible(resultats):
    """Identifie la catégorie la plus faible du meilleur modèle."""
    if not resultats:
        return

    meilleur = resultats[0]
    scores = meilleur.get("scores_par_classe", {})
    if not scores:
        return

    cat_min = min(scores, key=lambda c: scores[c]["f1"])
    nom = meilleur["modele"] + (" + exemples" if meilleur["consigne"] != "CONSIGNE" else "")
    print(f"\n--- Catégorie la plus faible ({nom}) ---")
    s = scores[cat_min]
    print(f"  {cat_min} : F1={s['f1']:.3f}, precision={s['precision']:.3f}, recall={s['recall']:.3f}, support={s['support']}")


def main():
    resultats = charger_resultats()

    if not resultats:
        print("Aucun résultat trouvé dans resultats/.")
        print("Lancez d'abord : python evaluer.py <modele> pour chaque modèle.")
        return

    print(f"Chargé {len(resultats)} fichier(s) de résultats.")

    afficher_tableau(resultats)
    afficher_ecarts(resultats)
    afficher_desaccords(resultats)
    afficher_categorie_faible(resultats)

    # Sauvegarde du résumé comparatif
    comparaison = {
        "classement": [
            {
                "modele": r["modele"],
                "consigne": r["consigne"],
                "accuracy": r["accuracy"],
                "macro_f1": r["macro_f1"],
                "invalides": r["invalides"]
            }
            for r in resultats
        ]
    }

    chemin_sortie = CHEMIN_RESULTATS / "comparaison.json"
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        json.dump(comparaison, f, ensure_ascii=False, indent=2)
    print(f"\n  → Comparaison sauvegardée dans {chemin_sortie}")


if __name__ == "__main__":
    main()
