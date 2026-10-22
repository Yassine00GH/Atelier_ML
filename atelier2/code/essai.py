# code/essai.py
import os
from groq import Groq

# Récupération de la clé API depuis l'environnement
api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    raise EnvironmentError("Variable GROQ_API_KEY non définie. Utilisez : set GROQ_API_KEY=gsk_votre_cle_ici")

client = Groq(api_key=api_key)

reponse = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Réponds : OK"}]
)

print(reponse.choices[0].message.content)
