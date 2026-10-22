# code/classifieur.py
"""
Classifieur de tickets par LLM via l'API Groq.
Conforme au cahier des charges du TP Atelier 2 — 3e année DSI.
- response_format JSON obligatoire
- Fonction classer(texte, modele, consigne, temperature)
- Aucun rattrapage manuel : si le modèle renvoie du JSON cassé
  ou une catégorie hors-liste, on enregistre "invalide".
"""
import csv
import json
import os
from pathlib import Path
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY", "")
if not API_KEY:
    raise EnvironmentError(
        "La variable d'environnement GROQ_API_KEY n'est pas définie.\n"
        "Définissez-la avec : set GROQ_API_KEY=gsk_votre_cle_ici"
    )

CATEGORIES = ["facturation", "technique", "compte", "commercial"]

# ──────────────────────────────────────────────
# Consignes (prompts système)
# ──────────────────────────────────────────────

CONSIGNE = """Tu es un classificateur de tickets de support client.
Tu dois classer chaque ticket dans exactement UNE des categories suivantes :
- facturation : tout ce qui concerne les factures, paiements, remboursements, prelevements, tarifs factures, montants contestes
- technique : bugs, pannes, erreurs d'affichage, problemes de connexion au service, lenteurs, crashs, mises a jour cassees
- compte : gestion du compte utilisateur, mot de passe, adresse, identifiants, acces bloque, donnees personnelles, RGPD
- commercial : offres, abonnements, resiliation, engagement, comparaison de formules, promotions, depart chez un concurrent

Reponds UNIQUEMENT avec un objet JSON de la forme :
{"categorie": "<une des quatre categories>"}
Pas d'explication, pas de texte autour. Juste le JSON."""

CONSIGNE_EXEMPLES = """Tu es un classificateur de tickets de support client.
Tu dois classer chaque ticket dans exactement UNE des categories suivantes :
- facturation : tout ce qui concerne les factures, paiements, remboursements, prelevements, tarifs factures, montants contestes
- technique : bugs, pannes, erreurs d'affichage, problemes de connexion au service, lenteurs, crashs, mises a jour cassees
- compte : gestion du compte utilisateur, mot de passe, adresse, identifiants, acces bloque, donnees personnelles, RGPD
- commercial : offres, abonnements, resiliation, engagement, comparaison de formules, promotions, depart chez un concurrent

Voici des exemples de classification correcte :
- Ticket : "Le geste commercial promis n'est pas sur mon releve." -> facturation
- Ticket : "Je paie chaque mois et rien ne marche depuis jeudi." -> technique
- Ticket : "Mon associe doit consulter les memes documents." -> compte
- Ticket : "Je demenage a l'etranger en septembre." -> commercial

Reponds UNIQUEMENT avec un objet JSON de la forme :
{"categorie": "<une des quatre categories>"}
Pas d'explication, pas de texte autour. Juste le JSON."""


# ──────────────────────────────────────────────
# Fonctions
# ──────────────────────────────────────────────

def charger_tickets(chemin_csv):
    """Charge les tickets depuis le CSV et renvoie une liste de dicts."""
    with open(chemin_csv, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classer(texte, modele, consigne=CONSIGNE, temperature=0.0):
    """
    Envoie un ticket au LLM et renvoie la catégorie prédite.

    Utilise response_format={"type": "json_object"} pour forcer le modèle
    à renvoyer du JSON valide.

    Si le JSON est cassé ou si la catégorie n'est pas dans la liste,
    renvoie "invalide" sans rattrapage.
    """
    client = Groq(api_key=API_KEY)

    reponse = client.chat.completions.create(
        model=modele,
        messages=[
            {"role": "system", "content": consigne},
            {"role": "user", "content": texte}
        ],
        temperature=temperature,
        max_tokens=50,
        response_format={"type": "json_object"}
    )

    reponse_brute = reponse.choices[0].message.content or ""

    # Tentative de parsing JSON — aucun rattrapage manuel
    try:
        obj = json.loads(reponse_brute)
        categorie = obj.get("categorie", "").strip().lower()
    except (json.JSONDecodeError, AttributeError):
        return "invalide"

    if categorie in CATEGORIES:
        return categorie

    return "invalide"
