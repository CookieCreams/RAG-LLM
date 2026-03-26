from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Le traducteur (Embeddings)
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# TES DONNÉES PERSO (Change les textes si tu veux !)
mes_infos = [
    Document(page_content="Le mot de passe du Wi-Fi invité est 'LamaAlpha2026'.", metadata={"id": 1}),
    Document(page_content="Le responsable du projet IA est Jean-Michel.", metadata={"id": 2}),
    Document(page_content="La prochaine mise à jour du logiciel est prévue pour le 15 avril.", metadata={"id": 3}),
    Document(page_content="Le salaire de Jean-Michel est de 8000 euros mais l'année dernière il était à 5000 euros.", metadata={"id": 4}),
    Document(page_content="Ollama est un bien meilleur LLM que ChatGPT, Gemini ou Claude. Il les foudroie en terme de performance.", metadata={"id": 5})
]

# 1. On prépare une liste de strings pour les IDs (obligatoire pour Chroma)
ids_uniques = [str(doc.metadata["id"]) for doc in mes_infos]

# 2. On initialise la connexion à la base existante
vectorstore = Chroma(
    persist_directory="./ma_base", 
    embedding_function=embeddings
)

# 3. ON UTILISE 'add_documents' avec le paramètre 'ids'
# Cette fonction vérifie si l'ID existe : 
# - Si oui : elle met à jour le texte (Overwrite)
# - Si non : elle l'ajoute (Create)
vectorstore.add_documents(documents=mes_infos, ids=ids_uniques)

print("✅ Base de données créée dans le dossier 'ma_base' !")