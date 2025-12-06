import requests
import time
import base64
import json
import os

API_URL = "http://localhost:8080"
API_KEY = "lytus_secret_key_123"
INSTANCE_NAME = "Sofia"
HEADERS = {"apikey": API_KEY, "Content-Type": "application/json"}

def save_qr(base64_img, origem):
    if "," in base64_img:
        base64_img = base64_img.split(",")[1]
    with open("qrcode_sofia.png", "wb") as f:
        f.write(base64.b64decode(base64_img))
    print(f"\n📸 SUCESSO! QR Code capturado via {origem}!")
    print("👉 Abra 'qrcode_sofia.png' e escaneie AGORA.")
    return True

def clean_and_create():
    print(f"🧹 Limpando '{INSTANCE_NAME}'...")
    try:
        requests.delete(f"{API_URL}/instance/logout/{INSTANCE_NAME}", headers=HEADERS)
        requests.delete(f"{API_URL}/instance/delete/{INSTANCE_NAME}", headers=HEADERS)
    except: pass
    
    print(f"🔨 Criando '{INSTANCE_NAME}'...")
    payload = {
        "instanceName": INSTANCE_NAME,
        "token": "token_final_123",
        "qrcode": True, # Pede o QR Code JÁ na criação
        "integration": "WHATSAPP-BAILEYS"
    }
    
    try:
        res = requests.post(f"{API_URL}/instance/create", json=payload, headers=HEADERS)
        print(f"   Status: {res.status_code}")
        
        if res.status_code == 201:
            data = res.json()
            # Tenta pegar o QR code IMEDIATAMENTE na resposta da criação
            if 'qrcode' in data and 'base64' in data['qrcode']:
                return save_qr(data['qrcode']['base64'], "RESPOSTA DE CRIAÇÃO")
            if 'base64' in data:
                return save_qr(data['base64'], "RESPOSTA DE CRIAÇÃO")
                
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def monitor():
    print("📡 Monitorando (caso não tenha vindo na criação)...")
    for i in range(10):
        try:
            res = requests.get(f"{API_URL}/instance/connect/{INSTANCE_NAME}", headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                # Verifica QR
                qr = data.get('base64') or data.get('qrcode', {}).get('base64')
                if qr: return save_qr(qr, "MONITORAMENTO")
                
                # Verifica Conexão
                if data.get('instance', {}).get('state') == 'open':
                    print("🎉 JÁ CONECTADO!")
                    return True
            time.sleep(1)
        except: pass
    print("❌ Tempo esgotado.")

if __name__ == "__main__":
    # Reseta tudo para garantir que o shm_size faça efeito
    os.system("docker-compose down -v") 
    os.system("docker-compose up -d")
    print("⏳ Aguardando 15s para boot do banco...")
    time.sleep(15)
    
    if not clean_and_create():
        monitor()