import csv
from collections import Counter
from pathlib import Path

# Chemin vers tickets.csv (fonctionne depuis code/ ou la racine)
chemin = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"
if not chemin.exists():
    chemin = Path("../data/tickets.csv")

with open(chemin, encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

print(f"Total tickets : {len(lignes)}\n")
for cat, n in Counter(l["categorie"] for l in lignes).most_common():
    print(f"{cat:<13}{n:>3} {100*n/len(lignes):>5.1f} % {'#' * n}")

# Question de l'énoncé :
# Un modèle qui ne prédirait jamais la catégorie commercial perdrait au maximum 19,4 points d'accuracy.
# Est-ce acceptable ? Que dirait l'équipe commerciale ?
#
# Réponse :
# Non, ce n'est absolument pas acceptable !
# L'accuracy globale serait encore de 80.6 % (ce qui paraît élevé en trompe-l'œil), mais l'équipe commerciale
# recevrait 0 ticket : les demandes d'offres, les abonnements et les réclamations de résiliation seraient
# totalement ignorés, causant une perte directe de chiffre d'affaires et de clients.
# C'est pourquoi le macro-F1 est la métrique de décision : il traite chaque catégorie à égalité.
