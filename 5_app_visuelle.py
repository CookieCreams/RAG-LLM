import streamlit as st
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Mon IA Perso", page_icon="🤖")
st.title("🤖 Assistant Personnel Local")

# --- INITIALISATION DES MOTEURS ---
@st.cache_resource 
def init_models():
    # On initialise les outils une seule fois
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    llm = ChatOllama(model="llama3", temperature=0.3)
    # On charge la base existante sur le disque
    db = Chroma(persist_directory="./ma_base", embedding_function=embeddings)
    return llm, embeddings, db

llm, embeddings, db = init_models()

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.header("📁 Administration")
    
    # Section Upload
    uploaded_file = st.file_uploader("Ajouter un PDF à la base", type="pdf")
    
    if uploaded_file is not None:
        if st.button("🚀 Indexer définitivement"):
            with st.status("Analyse et stockage..."):
                # 1. Sauvegarde physique dans le dossier /data
                if not os.path.exists("./data"): os.makedirs("./data")
                path = os.path.join("./data", uploaded_file.name)
                with open(path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 2. Découpage en petits morceaux (Chunks)
                loader = PyPDFLoader(path)
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
                chunks = text_splitter.split_documents(loader.load())
                
                # 3. Ajout à la base ChromaDB (Ecriture sur disque)
                db.add_documents(chunks)
                
            st.success(f"'{uploaded_file.name}' ajouté à la base !")
            st.info("L'IA peut maintenant répondre sur ce document.")

    st.write("---")
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# --- GESTION DE LA MÉMOIRE (SESSION) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AFFICHAGE DE L'HISTORIQUE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ZONE DE CHAT ---
if prompt := st.chat_input("Posez-moi une question..."):
    # 1. Message Utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Réponse de l'Assistant
    with st.chat_message("assistant"):
        # On cherche dans la base (permanente)
        # On limite k=3 pour éviter de saturer la VRAM du GPU
        docs = db.similarity_search(prompt, k=3)
        context = "\n\n".join([d.page_content for d in docs])
        
        full_prompt = f"""Tu es un assistant personnel. 
        Utilise ce contexte pour répondre : {context}
        
        Si l'info n'est pas là, utilise tes connaissances générales.
        Question : {prompt}"""
        
        response = llm.invoke(full_prompt)
        st.markdown(response.content)
        
    # 3. Sauvegarde
    st.session_state.messages.append({"role": "assistant", "content": response.content})