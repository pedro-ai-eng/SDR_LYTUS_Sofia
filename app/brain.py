import os
import time
import random
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÕES ---
EVOLUTION_API_URL = "http://localhost:8080"  # Ajuste se estiver em container diferente
API_KEY_EVOLUTION = os.getenv("EVOLUTION_API_KEY", "global-api-key") # Defina no .env se mudou
INSTANCE_NAME = "Sofia" # Nome da instância na Evolution

# Configuração Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configuração Supabase (Base de Conhecimento)
url_supabase = os.getenv("SUPABASE_URL")
key_supabase = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, key_supabase)

class SofiaSDR:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp') # Ou modelo de sua preferência
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
        # 1. Tempo de Leitura (Simulado)
        # Humanos leem aprox 200 palavras/min. Vamos ser mais rápidos, mas não instantâneos.
        palavras_recebidas = len(texto_recebido.split())
        tempo_leitura = random.uniform(1.5, 4.0) + (palavras_recebidas * 0.1)
        print(f"👀 Sofia Lendo por {tempo_leitura:.2f}s...")
        time.sleep(tempo_leitura)

        # 2. Enviar 'Digitando...' (Presence)
        url_presence = f"{EVOLUTION_API_URL}/chat/sendPresence/{INSTANCE_NAME}"
        payload_presence = {"number": remote_jid.split('@')[0], "presence": "composing", "delay": 0}
        try:
            requests.post(url_presence, json=payload_presence, headers=self._get_headers())
        except Exception as e:
            print(f"Erro ao enviar presence: {e}")

        # 3. Tempo de Digitação (Simulado)
        # Baseado no tamanho da resposta gerada
        caracteres_resposta = len(texto_resposta)
        # Média de digitação no celular + pausas para pensar
        tempo_digitacao = random.uniform(2.0, 5.0) + (caracteres_resposta * 0.05) 
        
        # Teto máximo para não demorar demais
        tempo_digitacao = min(tempo_digitacao, 15.0) 
        
        print(f"✍️ Sofia Digitando por {tempo_digitacao:.2f}s...")
        time.sleep(tempo_digitacao)

    def _consultar_base_conhecimento(self, query):
        """
        Busca vetorial no Supabase (Placeholder funcional)
        """
        try:
            # Gera embedding da query
            embedding = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )["embedding"]

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

    def processar_mensagem(self, remote_jid, mensagem_usuario, nome_usuario="Cliente"):
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
        payload_send = {
            "number": remote_jid.split('@')[0],
            "text": texto_final
        }
        
        try:
            res = requests.post(url_send, json=payload_send, headers=self._get_headers())
            print(f"✅ Resposta enviada: {res.status_code}")
            return res.json()
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")
            return None

# Instância Global para ser importada pelo servidor HTTP
sofia = SofiaSDR()