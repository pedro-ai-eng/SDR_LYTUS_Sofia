
import requests
import time
import base64
import json
import os
import subprocess
import sys

# --- CONFIGURAÇÕES ---
API_URL = "http://localhost:8080"
API_KEY = "lytus_secret_key_123"
INSTANCE_NAME = "Sofia"
HEADERS = {"apikey": API_KEY, "Content-Type": "application/json"}
WEBHOOK_SCRIPT = "webhook_sofia.py"

def verificar_servidor():
    """Verifica se o servidor da Evolution API está rodando"""
    try:
        requests.get(f"{API_URL}", timeout=3)
        return True
    except:
        return False

def salvar_qrcode(base64_img):
    """Salva a imagem do QR Code e exibe instruções"""
    try:
        if ',' in base64_img:
            base64_img = base64_img.split(',')[1]
        
        img_data = base64.b64decode(base64_img)
        with open("qrcode_sofia.png", "wb") as f:
            f.write(img_data)
        
        print("\n" + "="*50)
        print("📸  QR CODE GERADO!")
        print("👉  Abra 'qrcode_sofia.png' e escaneie AGORA.")
        print("="*50 + "\n")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar QR: {e}")
        return False

def garantir_conexao():
    """Gerencia todo o fluxo de conexão (Check -> Create -> QR -> Connect)"""
    print(f"📡 Verificando conexão de '{INSTANCE_NAME}'...")

    # 1. Busca instâncias existentes
    try:
        resp = requests.get(f"{API_URL}/instance/fetchInstances", headers=HEADERS)
        instancias = resp.json() if resp.status_code == 200 else []
        instancia_existe = any(i.get('name') == INSTANCE_NAME or i.get('instanceName') == INSTANCE_NAME for i in instancias)
    except Exception as e:
        print(f"❌ Erro ao conectar na API: {e}")
        return False

    # 2. Se não existe, cria
    if not instancia_existe:
        print(f"🔨 Criando nova instância...")
        payload = {
            "instanceName": INSTANCE_NAME,
            "token": "token_da_sofia_123",
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        res = requests.post(f"{API_URL}/instance/create", json=payload, headers=HEADERS)
        if res.status_code in [200, 201]:
            data = res.json()
            qr = data.get('qrcode', {}).get('base64') or data.get('base64')
            if qr: salvar_qrcode(qr)
        else:
            print(f"❌ Erro ao criar: {res.text}")
            return False

    # 3. Monitora status e QR Code
    print("⏳ Monitorando conexão (Ctrl+C para cancelar)...")
    try:
        while True:
            res = requests.get(f"{API_URL}/instance/connect/{INSTANCE_NAME}", headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                state = data.get('instance', {}).get('state') or data.get('state')
                
                # Exibe QR se aparecer
                qr = data.get('base64') or data.get('qrcode', {}).get('base64')
                if qr and state != 'open':
                    salvar_qrcode(qr)
                    print("📲 Aguardando leitura do QR Code...")
                    time.sleep(5) # Pausa para dar tempo de ler
                    continue

                if state == 'open':
                    print("✅ WHATSAPP CONECTADO COM SUCESSO!")
                    return True
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Cancelado pelo usuário.")
        return False

def iniciar_servidor_sofia():
    """Inicia o servidor Flask em subprocesso"""
    print("\n🚀 INICIANDO O CÉREBRO DA SOFIA...")
    print(f"📂 Executando: {WEBHOOK_SCRIPT}\n")
    
    # Executa o script python e conecta o output ao terminal atual
    try:
        subprocess.run([sys.executable, WEBHOOK_SCRIPT], check=True)
    except KeyboardInterrupt:
        print("\n👋 Sofia desligada.")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    print("🤖 --- STARTUP SOFIA SYSTEM --- 🤖")
    
    # 0. Check API
    if not verificar_servidor():
        print("⚠️  Evolution API não detectada na porta 8080.")
        print("    Certifique-se de que o Docker está rodando (docker-compose up -d)")
        # Opção: os.system("docker-compose up -d") ? Melhor alertar.
        sys.exit(1)

    # 1. Garante Conexão WhatsApp
    if garantir_conexao():
        time.sleep(2)
        # 2. Inicia o Bot
        iniciar_servidor_sofia()