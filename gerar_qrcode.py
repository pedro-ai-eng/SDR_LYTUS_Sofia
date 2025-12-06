"""
Script para conectar a Sofia ao WhatsApp via Evolution API
Gera QR Code e salva como imagem para escaneamento
"""
import requests
import time
import base64

# Configurações
API_URL = "http://localhost:8080"
API_KEY = "lytus_secret_key_123"
INSTANCE_NAME = "Sofia"
HEADERS = {"apikey": API_KEY, "Content-Type": "application/json"}

def verificar_status():
    """Verifica o status atual da instância"""
    try:
        resp = requests.get(f"{API_URL}/instance/fetchInstances", headers=HEADERS)
        if resp.status_code == 200:
            instancias = resp.json()
            for inst in instancias:
                if inst.get('name') == INSTANCE_NAME or inst.get('instanceName') == INSTANCE_NAME:
                    print(f"📊 Instância encontrada: {inst}")
                    return inst
        return None
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return None

def criar_instancia():
    """Cria a instância Sofia"""
    print(f"🔨 Criando instância '{INSTANCE_NAME}'...")
    payload = {
        "instanceName": INSTANCE_NAME,
        "token": "token_da_sofia_123",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    try:
        resp = requests.post(f"{API_URL}/instance/create", json=payload, headers=HEADERS)
        print(f"   Status: {resp.status_code}")
        print(f"   Resposta: {resp.text[:500]}")
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            # Tenta capturar QR Code da resposta de criação
            qr = data.get('qrcode', {}).get('base64') or data.get('base64')
            if qr:
                salvar_qrcode(qr)
                return True
            print("   ✅ Instância criada, buscando QR Code...")
            return True
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def buscar_qrcode():
    """Busca o QR Code da instância"""
    print("🔍 Buscando QR Code...")
    
    for tentativa in range(15):
        try:
            # Tenta endpoint /connect
            resp = requests.get(f"{API_URL}/instance/connect/{INSTANCE_NAME}", headers=HEADERS)
            if resp.status_code == 200:
                data = resp.json()
                print(f"   Tentativa {tentativa+1}: {list(data.keys())}")
                
                # Procura QR Code em vários lugares possíveis
                qr = None
                if 'base64' in data:
                    qr = data['base64']
                elif 'qrcode' in data:
                    if isinstance(data['qrcode'], dict) and 'base64' in data['qrcode']:
                        qr = data['qrcode']['base64']
                    elif isinstance(data['qrcode'], str):
                        qr = data['qrcode']
                
                if qr:
                    salvar_qrcode(qr)
                    return True
                
                # Verifica se já está conectado
                state = data.get('instance', {}).get('state') or data.get('state')
                if state == 'open':
                    print("🎉 WhatsApp já está conectado!")
                    return True
                    
        except Exception as e:
            print(f"   Erro na tentativa {tentativa+1}: {e}")
        
        time.sleep(2)
    
    print("❌ Não foi possível obter o QR Code após várias tentativas")
    return False

def salvar_qrcode(base64_img):
    """Salva a imagem do QR Code"""
    try:
        # Remove prefixo data:image se existir
        if ',' in base64_img:
            base64_img = base64_img.split(',')[1]
        
        img_data = base64.b64decode(base64_img)
        with open("qrcode_sofia.png", "wb") as f:
            f.write(img_data)
        
        print("\n" + "="*50)
        print("📸  QR CODE GERADO COM SUCESSO!")
        print("👉  Abra o arquivo 'qrcode_sofia.png' e escaneie com o celular")
        print("📱  No WhatsApp: Menu > Aparelhos conectados > Conectar aparelho")
        print("="*50 + "\n")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar QR Code: {e}")
        return False

def deletar_instancia():
    """Deleta a instância existente"""
    print(f"🧹 Deletando instância '{INSTANCE_NAME}' se existir...")
    try:
        requests.delete(f"{API_URL}/instance/logout/{INSTANCE_NAME}", headers=HEADERS)
        requests.delete(f"{API_URL}/instance/delete/{INSTANCE_NAME}", headers=HEADERS)
        time.sleep(2)
    except:
        pass

if __name__ == "__main__":
    print("🤖 CONEXÃO SOFIA - WHATSAPP")
    print("-" * 40)
    
    # 1. Verifica status atual
    status = verificar_status()
    
    if status:
        state = status.get('connectionStatus') or status.get('state')
        if state == 'open':
            print("✅ Sofia já está conectada ao WhatsApp!")
            exit(0)
        else:
            deletar_instancia()
    
    # 2. Cria instância nova
    if criar_instancia():
        time.sleep(3)
        buscar_qrcode()
    else:
        print("❌ Falha ao criar instância")
