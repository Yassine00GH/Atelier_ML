# Guichet ML — Atelier 01 : Appeler un modèle et l'exposer derrière une API

API d'inférence pour la détection automatique de la langue des requêtes étudiantes (français, anglais, arabe), conçue selon les bonnes pratiques de découplage, de résilience et de sécurité.

---

## 1. Prérequis & Installation

- **Python** 3.10 ou 3.11+
- **Environnement virtuel (recommandé)**

### Sous Windows (PowerShell) :
```powershell
# Cloner ou se placer dans le projet
cd guichet-ml

# Créer et activer l'environnement virtuel
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Mettre à niveau pip et installer les dépendances
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Sous Linux / macOS / WSL :
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Configuration (`.env`)

Copiez le fichier d'exemple pour initialiser la configuration locale :
```powershell
Copy-Item .env.example .env
```

Contenu par défaut de `.env` :
```env
INFERENCE_MODE=mock
HF_TOKEN=
MODEL_ID=papluca/xlm-roberta-base-language-detection
REVIEW_THRESHOLD=0.60
```

> **Sécurité** : Le fichier `.env` est exclu du contrôle de version via `.gitignore`. Ne partagez jamais vos jetons d'accès API.

---

## 3. Lancer l'API

```powershell
uvicorn app.main:app --reload
```

- **Documentation interactive Swagger** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Vérification de santé (Healthcheck)** : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 4. Tester l'API

### Requête de test (PowerShell) :
```powershell
$body = @{ text = "Je souhaite réinitialiser mon mot de passe." } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/detect-language" -ContentType "application/json; charset=utf-8" -Body $body
```

### Requête de test (cURL / Bash) :
```bash
curl -X POST http://127.0.0.1:8000/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "Je souhaite réinitialiser mon mot de passe."}'
```

---

## 5. Exécuter les tests unitaires

Les tests s'exécutent entièrement hors ligne en mode `mock` :
```powershell
pytest -q
```
