# code/evaluation.py
"""
Module d'évaluation pour la classification de tickets (Atelier 2 - 3e année DSI).
Toutes les métriques sont codées à la main sans bibliothèque externe boîte-noire.
"""

CATEGORIES = ["facturation", "technique", "compte", "commercial"]


def accuracy(vrais, predits):
    """Calcule l'exactitude globale (part de prédictions correctes)."""
    if not vrais:
        return 0.0
    return sum(1 for v, p in zip(vrais, predits) if v == p) / len(vrais)


def scores_par_classe(vrais, predits, classes=CATEGORIES):
    """
    Calcule précision, rappel, F1-score et support pour chaque catégorie.
    - precision = VP / (VP + FP)
    - recall    = VP / (VP + FN)
    - f1        = 2 * (P * R) / (P + R)
    """
    resultat = {}
    for c in classes:
        vp = sum(1 for v, p in zip(vrais, predits) if v == c and p == c)
        fp = sum(1 for v, p in zip(vrais, predits) if v != c and p == c)
        fn = sum(1 for v, p in zip(vrais, predits) if v == c and p != c)

        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) else 0.0)

        resultat[c] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": vp + fn
        }
    return resultat


def f1_macro(scores):
    """Calcule la moyenne non pondérée des F1 de chaque classe."""
    if not scores:
        return 0.0
    return sum(d["f1"] for d in scores.values()) / len(scores)


def taux_invalides(predits):
    """Compte la proportion de réponses 'invalide'."""
    if not predits:
        return 0.0
    return sum(1 for p in predits if p == "invalide") / len(predits)


def matrice_confusion(vrais, predits, classes=CATEGORIES):
    """
    Construit la matrice de confusion.
    Lignes = catégories réelles (vérité terrain)
    Colonnes = catégories prédites + colonne 'invalide'
    """
    colonnes = list(classes) + ["invalide"]
    matrice = {c_vrai: {c_pred: 0 for c_pred in colonnes} for c_vrai in classes}

    for v, p in zip(vrais, predits):
        if v in matrice:
            if p in colonnes:
                matrice[v][p] += 1
            else:
                matrice[v]["invalide"] += 1

    return matrice


def afficher_rapport(etiquette, vrais, predits, classes=CATEGORIES):
    """
    Affiche le rapport complet dans le terminal et renvoie un dictionnaire
    résumé prêt à être sérialisé en JSON.
    """
    acc = accuracy(vrais, predits)
    scores = scores_par_classe(vrais, predits, classes)
    macro_f1 = f1_macro(scores)
    invalides = taux_invalides(predits)
    mat = matrice_confusion(vrais, predits, classes)

    print(f"\n=== {etiquette} ===")
    print(f"accuracy   : {acc:.3f}")
    print(f"macro-F1   : {macro_f1:.3f}")
    print(f"invalides  : {invalides:.3f}\n")

    # Tableau par classe
    print(f"{'categorie':<14} {'precision':>9} {'recall':>8} {'F1':>8} {'n':>4}")
    for c in classes:
        s = scores[c]
        print(f"{c:<14} {s['precision']:>9.3f} {s['recall']:>8.3f} {s['f1']:>8.3f} {s['support']:>4}")

    # Matrice de confusion
    print("\nConfusion matrix (lignes = vérité, colonnes = prédiction)")
    headers = ["factur", "techni", "compte", "commer", "invali"]
    col_keys = ["facturation", "technique", "compte", "commercial", "invalide"]

    print(f"{'':<14}" + "".join(f"{h:>7}" for h in headers))
    for c in classes:
        ligne_str = "".join(f"{mat[c][col]:>7}" for col in col_keys)
        print(f"{c:<14}{ligne_str}")
    print()

    # Dictionnaire de retour pour l'enregistrement JSON
    resume = {
        "etiquette": etiquette,
        "accuracy": round(acc, 3),
        "macro_f1": round(macro_f1, 3),
        "invalides": round(invalides, 3),
        "scores_par_classe": {
            c: {k: round(v, 3) if isinstance(v, float) else v for k, v in s.items()}
            for c, s in scores.items()
        },
        "matrice_confusion": mat
    }
    return resume
