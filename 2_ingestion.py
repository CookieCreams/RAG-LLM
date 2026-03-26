import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter # <-- LE DÉCOUPEUR
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# --- CONFIG ---
DATA_PATH = "./data"
CHROMA_PATH = "./ma_base"

# 1. Nettoyage de l'ancienne base (pour éviter les doublons)
if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)
    print("🧹 Ancienne base supprimée pour repartir sur du propre.")

# 2. Chargement des documents
print("📂 Lecture des fichiers...")
loader = DirectoryLoader(DATA_PATH, glob="./**/*.*", show_progress=True)
raw_docs = loader.load()

# 3. DÉCOUPAGE (Chunking) : La clé de la précision
# On découpe en morceaux de 1000 caractères avec un petit recouvrement (overlap)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=100,
    add_start_index=True # Pour savoir à quelle page/index se trouve l'info
)
docs = text_splitter.split_documents(raw_docs)
print(f"✂️ Documents découpés en {len(docs)} morceaux.")

# 4. Indexation
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vectorstore = Chroma.from_documents(
    documents=docs, 
    embedding=embeddings, 
    persist_directory=CHROMA_PATH
)

print(f"✅ Terminé ! {len(docs)} vecteurs créés dans '{CHROMA_PATH}'.")