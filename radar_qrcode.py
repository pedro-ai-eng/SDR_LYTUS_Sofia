import requests
import time
import json

API_URL = "http://localhost:8080"
API_KEY = "lytus_secret_key_123"
INSTANCE_NAME = "Sofia"
HEADERS = {"apikey": API_KEY}

print(f"📡 Iniciando Radar para: {INSTANCE_NAME}")
print("Pressione CTRL+C para parar.\n")

for i in range(1, 21): # Tenta por 40 segundos
    try:
        url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
        response = requests.get(url, headers=HEADERS)
        
        print(f"--- Tentativa {i} ---")
        if response.status_code == 200:
            data = response.json()
            # Mostra o estado atual da instância
            state = data.get('instance', {}).get('state', 'Desconhecido')
            print(f"Estado: {state}")
            
            # Verifica se veio QR Code (sem imprimir o base64 gigante)
            if 'base64' in data or ('qrcode' in data and 'base64' in data['qrcode']):
                print("✅ QR CODE DETECTADO NO JSON!")
                print("O sistema está funcionando, o erro era apenas no salvamento.")
                break
            else:
                print("⚠️ JSON recebido, mas SEM QR Code.")
                # Imprime chaves para ver o que veio
                print(f"Chaves recebidas: {list(data.keys())}")
        else:
            print(f"Erro HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
    
    time.sleep(2)