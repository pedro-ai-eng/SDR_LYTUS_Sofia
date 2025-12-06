import requests
import time
import base64

# CONFIGURAÇÕES
API_URL = "http://localhost:8080"
API_KEY = "lytus_secret_key_123"
INSTANCE_NAME = "Sofia"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def reset_sofia():
    print("🔥 INICIANDO PROTOCOLO DE RESET DA SOFIA...")
    print("-" * 40)

    # 1. DELETAR a instância velha (se existir)
    print(f"1. Deletando instância '{INSTANCE_NAME}' travada...")
    try:
        requests.delete(f"{API_URL}/instance/delete/{INSTANCE_NAME}", headers=headers)
        print("   ✅ Comando de delete enviado.")
    except Exception as e:
        print(f"   ⚠️ Erro ao deletar (pode ser que não existisse): {e}")

    time.sleep(3) # Espera a API limpar o banco

    # 2. CRIAR a instância nova
    print("\n2. Criando instância nova...")
    payload = {
        "instanceName": INSTANCE_NAME,
        "token": "token_da_sofia_123",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS" # Importante para V2
    }
    
    try:
        resp = requests.post(f"{API_URL}/instance/create", json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            print("   ✅ Instância criada com sucesso!")
        else:
            print(f"   ❌ Erro ao criar: {resp.text}")
            return
    except Exception as e:
        print(f"   ❌ Erro fatal: {e}")
        return

    print("\n⏳ Aguardando 5 segundos para gerar o QR Code...")
    time.sleep(5)

    # 3. PEGAR O QR CODE
    print("\n3. Buscando o QR Code...")
    try:
        resp = requests.get(f"{API_URL}/instance/connect/{INSTANCE_NAME}", headers=headers)
        data = resp.json()
        
        base64_img = None
        # Tenta achar o base64 em vários lugares possíveis do JSON
        if 'base64' in data:
            base64_img = data['base64']
        elif 'qrcode' in data and 'base64' in data['qrcode']:
            base64_img = data['qrcode']['base64']
            
        if base64_img:
            # Salva a imagem
            img_data = base64.b64decode(base64_img.split(',')[1])
            with open("qrcode.png", "wb") as f:
                f.write(img_data)
            print("\n" + "="*50)
            print("📸  QR CODE NOVO GERADO COM SUCESSO!  📸")
            print("👉  Abra o arquivo 'qrcode.png' na pasta e escaneie AGORA.")
            print("="*50 + "\n")
        else:
            print("⚠️ A API ainda não mandou a imagem. Tente rodar este script novamente.")
            print(f"Debug: {data}")

    except Exception as e:
        print(f"❌ Erro ao baixar QR: {e}")

if __name__ == "__main__":
    reset_sofia()