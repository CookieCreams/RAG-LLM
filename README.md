# 🤖 Local RAG Assistant

Un assistant conversationnel **100% local** basé sur une architecture RAG (Retrieval-Augmented Generation), capable de répondre à des questions sur vos documents PDF sans envoyer de données à un service externe.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Utilisateur                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ Question
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Interface Streamlit                         │
│              (upload PDF + chat multi-tour)                 │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐      ┌───────────────────────────────┐
│   ChromaDB (locale)  │      │        Ollama (local)         │
│                      │      │                               │
│  Embeddings stockés  │◄────►│  LLM  : mistral / llama3     │
│  sur disque          │      │  Embed: mxbai-embed-large     │
│  (persistance)       │      │                               │
└──────────────────────┘      └───────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pipeline RAG                              │
│                                                             │
│  PDF → Chunks → Embeddings → Similarity Search → Contexte  │
│                                                             │
│  Contexte + Historique + Question → LLM → Réponse streamée │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Fonctionnalités

- 📄 **Indexation de PDFs** — Upload et indexation permanente dans ChromaDB
- 💬 **Chat multi-tour** — L'assistant se souvient des échanges précédents
- ⚡ **Streaming** — Les réponses s'affichent mot par mot
- 📚 **Sources citées** — Chaque réponse indique le document et la page utilisés
- 🔒 **100% local** — Aucune donnée ne quitte votre machine
- 🐳 **Dockerisé** — Déploiement en une commande
- 📊 **Évaluation RAGAS** — Mesure objective de la qualité du pipeline

---

## 🚀 Installation & Lancement

### Prérequis
- [Docker](https://docs.docker.com/get-docker/) installé
- 8 Go de RAM minimum (16 Go recommandés)

### 1. Cloner le projet
```bash
git clone https://github.com/votre-user/local-rag-assistant.git
cd local-rag-assistant
```

### 2. Lancer les services
```bash
docker compose up --build
```

### 3. Télécharger les modèles (première fois uniquement)
```bash
# Dans un second terminal, pendant que les containers tournent
docker exec -it rag_ollama ollama pull mistral
docker exec -it rag_ollama ollama pull mxbai-embed-large
```

### 4. Ouvrir l'application
```
http://localhost:8501
```

---

## ⚙️ Configuration

Tous les paramètres se changent dans `docker-compose.yml`, **sans modifier le code** :

```yaml
environment:
  - LLM_MODEL=mistral          # mistral | llama3 | gemma3 | phi3 | deepseek-r1
  - EMBED_MODEL=mxbai-embed-large
```

Après modification :
```bash
docker compose down && docker compose up
```

### Modèles disponibles

| Modèle | Taille | Points forts |
|--------|--------|--------------|
| `mistral` | 4 GB | Rapide, bon en français |
| `llama3` | 5 GB | Qualité générale élevée |
| `gemma3` | 3 GB | Léger et efficace |
| `phi3` | 2 GB | Très léger, faible RAM |
| `deepseek-r1` | 4 GB | Raisonnement complexe |

---

## 🔧 Choix techniques

### Chunking : `chunk_size=800`, `chunk_overlap=80`
Un chunk de 800 caractères représente environ 2-3 paragraphes — suffisant pour contenir une idée complète sans dépasser la fenêtre de contexte du LLM. Le chevauchement de 80 caractères (~10%) évite de couper une phrase clé à la frontière entre deux chunks.

### Retrieval : `k=3`
Récupérer 3 chunks représente environ 2 400 caractères de contexte. C'est un compromis délibéré : en dessous, on manque d'informations ; au-dessus, on risque de saturer la VRAM sur du matériel grand public et de diluer le signal pertinent (problème dit de "lost in the middle").

### Embeddings : `mxbai-embed-large`
Modèle open-source classé dans le top 5 du [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) pour la recherche sémantique en anglais et en français. Meilleur rapport qualité/performance pour un usage local comparé à `nomic-embed-text`.

### LLM : Ollama (local)
Ollama expose une API compatible OpenAI, ce qui rend le swap de modèle trivial. Le choix d'un LLM local garantit la confidentialité des données — essentiel pour des documents d'entreprise.

### Persistance : ChromaDB sur disque
La base vectorielle est montée comme volume Docker (`./ma_base`). Les documents indexés survivent aux redémarrages et rebuilds du container.

---

## 📊 Évaluation de la qualité (RAGAS)

Le projet inclut un script d'évaluation qui mesure objectivement la qualité du pipeline sur 4 métriques :

| Métrique | Description | Cible |
|----------|-------------|-------|
| `faithfulness` | Le LLM répond-il sans halluciner ? | ≥ 0.70 |
| `answer_relevancy` | La réponse est-elle pertinente ? | ≥ 0.70 |
| `context_precision` | Les chunks récupérés sont-ils utiles ? | ≥ 0.70 |
| `context_recall` | Toutes les infos nécessaires sont-elles récupérées ? | ≥ 0.70 |

### Lancer l'évaluation
```bash
# 1. Adapter les cas de test dans evaluate.py
# 2. Lancer
python evaluate.py

# Les résultats sont sauvegardés dans eval_results.csv
```

---

## 📁 Structure du projet

```
local-rag-assistant/
├── main.py               # Application Streamlit principale
├── evaluate.py           # Script d'évaluation RAGAS
├── requirements.txt      # Dépendances Python
├── Dockerfile            # Image Docker de l'app
├── docker-compose.yml    # Orchestration des services
├── data/                 # PDFs uploadés (gitignored)
├── ma_base/              # Base ChromaDB (gitignored)
└── eval_results.csv      # Historique des évaluations
```

---

## 🗂️ Commandes utiles

```bash
docker compose up -d                        # Lancer en arrière-plan
docker compose down                         # Arrêter
docker compose logs -f app                  # Logs en temps réel
docker exec -it rag_ollama ollama list      # Voir les modèles installés
docker exec -it rag_ollama ollama pull phi3 # Ajouter un modèle
```

---

## 🛣️ Améliorations futures

- [ ] Reranking des chunks avec `cross-encoder`
- [ ] Support de fichiers `.docx` et `.txt`
- [ ] Interface de gestion des documents indexés
- [ ] Export de la conversation en PDF
- [ ] Support multi-utilisateurs

---

## 🧰 Stack technique

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)
![Ollama](https://img.shields.io/badge/Ollama-local-purple)
![Docker](https://img.shields.io/badge/Docker-compose-blue)
![RAGAS](https://img.shields.io/badge/RAGAS-eval-yellow)