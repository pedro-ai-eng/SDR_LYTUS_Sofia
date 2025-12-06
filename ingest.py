import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# 1. Carregar configurações
load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 2. Carregar a IA Local
print("📥 Carregando modelo de IA local...")
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

async def process_pdf(file_path):
    print(f"📖 Lendo arquivo: {file_path}...")
    
    try:
        reader = PdfReader(file_path)
        text = ""
        # DICA DE OURO: Pular cabeçalhos/rodapés repetitivos seria o ideal,
        # mas como varia muito, vamos focar em chunks menores.
        for page in reader.pages:
            content = page.extract_text() or ""
            text += content + "\n" # Adiciona quebra de linha entre páginas
    except Exception as e:
        print(f"❌ Erro ao ler PDF: {e}")
        return

    # MUDANÇA CRUCIAL AQUI: ALTA PRECISÃO
    # Diminuímos de 1000 para 400. Agora cada parágrafo é um "fato" isolado.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,     # Pedaços menores = Busca mais precisa
        chunk_overlap=100,  # Garante que frases não sejam cortadas no meio
        separators=["\n\n", "\n", ".", " ", ""] # Prioriza quebrar em parágrafos
    )
    chunks = splitter.split_text(text)
    
    print(f"✂️  Texto dividido em {len(chunks)} pedaços de Alta Precisão...")

    for i, chunk in enumerate(chunks):
        try:
            # Gera vetor
            vector = embedding_model.encode(chunk).tolist()

            data = {
                "content": chunk,
                "metadata": {"source": file_path, "chunk_index": i},
                "embedding": vector
            }
            supabase.table("documents").insert(data).execute()
            
            # Print apenas a cada 10 para não poluir o terminal
            if i % 10 == 0:
                print(f"✅ Processando pedaço {i+1}/{len(chunks)}...")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar pedaço {i}: {e}")

async def main():
    folder = "knowledge_base"
    if not os.path.exists(folder):
        print(f"❌ Pasta '{folder}' não encontrada!")
        return

    files = [f for f in os.listdir(folder) if f.endswith('.pdf')]
    if not files:
        print("📭 Nenhum PDF encontrado.")
        return

    print(f"🚀 Iniciando processamento de Alta Precisão...")
    for filename in files:
        path = os.path.join(folder, filename)
        await process_pdf(path)
    print("\n🎉 Memória atualizada com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())