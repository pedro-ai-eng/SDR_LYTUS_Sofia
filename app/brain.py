import os
import time
import random
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

# Carrega variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÕES ---
EVOLUTION_API_URL = "http://localhost:8080"  # Ajuste se estiver em container diferente
API_KEY_EVOLUTION = os.getenv("EVOLUTION_API_KEY", "lytus_secret_key_123")
INSTANCE_NAME = "Sofia" # Nome da instância na Evolution

# Configuração Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configuração Supabase (Base de Conhecimento)
url_supabase = os.getenv("SUPABASE_URL")
key_supabase = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, key_supabase)

# Modelo de Embeddings LOCAL (MESMO do ingest.py para compatibilidade)
print("📥 Carregando modelo de embeddings...")
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

class SofiaSDR:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite') # Modelo leve e disponível
        self.consultor_nome = "Pedro"
        self.empresa = "Lytus"

    def _get_headers(self):
        return {
            "apikey": API_KEY_EVOLUTION,
            "Content-Type": "application/json"
        }

    def _simular_comportamento_humano(self, remote_jid, texto_recebido, texto_resposta):
        """
        Gera delays naturais e envia status de 'digitando...'
        """
        # 1. Tempo de Leitura (Otimizado)
        # Rápido: 0.5 a 1.0s
        palavras_recebidas = len(texto_recebido.split())
        tempo_leitura = random.uniform(0.5, 1.0)
        print(f"👀 Sofia Lendo por {tempo_leitura:.2f}s...")
        time.sleep(tempo_leitura)

        # 2. Enviar 'Digitando...' (Presence)
        url_presence = f"{EVOLUTION_API_URL}/chat/sendPresence/{INSTANCE_NAME}"
        
        # Tratamento LID para presence
        number_presence = remote_jid
        if "@lid" not in remote_jid:
            number_presence = remote_jid.split('@')[0].split(':')[0]

        payload_presence = {"number": number_presence, "presence": "composing", "delay": 0}
        try:
            requests.post(url_presence, json=payload_presence, headers=self._get_headers())
        except Exception as e:
            print(f"Erro ao enviar presence: {e}")

        # 3. Tempo de Digitação (Otimizado)
        caracteres_resposta = len(texto_resposta)
        # Acelerado: 1.0 a 2.0s base + 0.02s por caracter
        tempo_digitacao = random.uniform(1.0, 2.0) + (caracteres_resposta * 0.02) 
        
        # Teto maximo de 5s
        tempo_digitacao = min(tempo_digitacao, 5.0) 
        
        print(f"✍️ Sofia Digitando por {tempo_digitacao:.2f}s...")
        time.sleep(tempo_digitacao)

    def _consultar_base_conhecimento(self, query):
        """
        Busca vetorial no Supabase usando modelo LOCAL (mesmo do ingest.py)
        """
        try:
            # Gera embedding da query com modelo LOCAL
            embedding = embedding_model.encode(query).tolist()

            # Chama função RPC no Supabase (match_documents)
            response = supabase.rpc(
                "match_documents",
                {"query_embedding": embedding, "match_threshold": 0.5, "match_count": 3}
            ).execute()
            
            contexto = ""
            if response.data:
                for doc in response.data:
                    contexto += f"{doc['content']}\n---\n"
            return contexto
        except Exception as e:
            print(f"⚠️ Erro no RAG: {e}")
            return "Sem dados específicos na base."

    def processar_mensagem(self, remote_jid, mensagem_usuario, nome_usuario="Cliente", message_id=None):
        print(f"📩 Processando mensagem de {nome_usuario}: {mensagem_usuario}")

        # 1. Recuperar Contexto (RAG)
        contexto_lytus = self._consultar_base_conhecimento(mensagem_usuario)

        # 2. Construir o Prompt do Sistema (A "Alma" da Sofia)
        system_instruction = f"""
        Você é SOFIA, assistente de pré-vendas da empresa {self.empresa}.
        Você trabalha para o Consultor Financeiro {self.consultor_nome}.

        OBJETIVO:
        Seu objetivo NÃO é vender diretamente, mas sim qualificar o interesse e AGENDAR UMA REUNIÃO/CHAMADA com o {self.consultor_nome}.

        BASE DE CONHECIMENTO (Use para responder dúvidas técnicas):
        {contexto_lytus}

        DIRETRIZES DE PERSONALIDADE (HUMANIZAÇÃO EXTREMA):
        1. Responda como uma pessoa no WhatsApp. Use linguagem natural, ocasionalmente coloquial, mas profissional.
        2. SEJA BREVE. Ninguém lê textão no Zap. Máximo 2 ou 3 frases curtas por vez.
        3. JAMAIS use listas com bullet points, negrito excessivo ou formatação de "robô".
        4. Use emojis moderadamente (1 por mensagem no máximo).
        5. Se perguntarem se você é um robô/IA, diga: "Sou a assistente virtual do Pedro, ajudo ele a organizar a agenda e os atendimentos iniciais! 😊" (Não minta descaradamente, mas não quebre a imersão).
        6. TERMINE SEMPRE COM UMA PERGUNTA ABERTA ou uma sugestão de próximo passo.

        ESTRUTURA DE VENDAS:
        - Se for o primeiro contato: Cumprimente, pergunte o nome (se não souber) e qual o objetivo (Investimento, Casa Própria, Carro?).
        - Se for dúvida técnica: Responda usando a Base de Conhecimento de forma resumida e pergunte: "Faz sentido pra você?"
        - Se demonstrou interesse: Tente agendar. "O Pedro tem um horário livre na quinta à tarde para te explicar melhor essa simulação. Pode ser?"
        """

        # 3. Gerar Resposta com Gemini
        chat = self.model.start_chat(history=[])
        response = chat.send_message(f"System: {system_instruction}\nUser ({nome_usuario}): {mensagem_usuario}")
        texto_final = response.text.strip()

        # 4. Simular Comportamento Humano (Delay + Typing)
        self._simular_comportamento_humano(remote_jid, mensagem_usuario, texto_final)

        # 5. Enviar Mensagem Real
        url_send = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
        
        # Correção LID: Se for LID, usa o JID completo. Se não, limpa.
        if "@lid" in remote_jid:
            numero_destino = remote_jid
            print(f"⚠️ Detectado LID. Usando JID completo: {numero_destino}")
        else:
            # Remove sufixo de dispositivo (ex: :2) e domínio
            numero_destino = remote_jid.split('@')[0].split(':')[0]
        
        print(f"🎯 JID Original: {remote_jid} | Número processado: {numero_destino}")

        payload_send = {
            "number": numero_destino,
            "text": texto_final
        }
        
        # Adiciona Quote se tiver message_id
        if message_id:
            payload_send["quoted"] = {"key": {"id": message_id}}
        
        try:
            print(f"📤 Enviando payload para Evolution: {json.dumps(payload_send)}")
            res = requests.post(url_send, json=payload_send, headers=self._get_headers())
            
            if res.status_code == 200 or res.status_code == 201:
                print(f"✅ Resposta enviada: {res.status_code}")
                return res.json()
            else:
                print(f"❌ Erro Evolution API ({res.status_code}): {res.text}")
                return None
        except Exception as e:
            print(f"❌ Erro crítico ao enviar: {e}")
            return None

# Instância Global para ser importada pelo servidor HTTP
sofia = SofiaSDR()