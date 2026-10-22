# code/test_evaluation.py
"""
Script de vérification des métriques avant appel API (Page 8 du TP).
"""
from evaluation import accuracy, f1_macro, matrice_confusion, scores_par_classe

vrais = ["compte", "technique", "compte", "commercial"]
predits = ["compte", "technique", "commercial", "commercial"]

print("Accuracy :", accuracy(vrais, predits))
print("Scores :", scores_par_classe(vrais, predits))
print("Macro-F1 :", f1_macro(scores_par_classe(vrais, predits)))
print("Matrice :", matrice_confusion(vrais, predits))

# Vérification du point de contrôle avec les 4 classes présentes :
vrais_toutes_classes = ["facturation", "technique", "compte", "commercial"]
scores_parfaits = scores_par_classe(vrais_toutes_classes, vrais_toutes_classes)
print("\n--- Point de contrôle : predits == vrais sur les 4 classes ---")
print("Accuracy attendue (1.0) :", accuracy(vrais_toutes_classes, vrais_toutes_classes))
print("Macro-F1 attendu (1.0)  :", f1_macro(scores_parfaits))

# Vérification robustesse : le modèle ne prédit qu'une seule classe
print("\n--- Point de contrôle : prédiction d'une seule classe (pas de crash) ---")
predits_mono = ["compte"] * len(vrais)
scores_mono = scores_par_classe(vrais, predits_mono)
print("Macro-F1 mono-classe :", round(f1_macro(scores_mono), 3))
print("Matrice mono-classe  :", matrice_confusion(vrais, predits_mono))
