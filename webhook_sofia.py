from flask import Flask, request, jsonify
from app.brain import sofia  # O import funciona perfeitamente estando na raiz
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SofiaWebhook")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    try:
        data = request.json
        
        # Validações básicas
        if not data or 'data' not in data:
            return jsonify({"status": "ignored", "reason": "no_data"}), 200

        event_type = data.get('event')
        payload = data.get('data')

        # Filtro: Apenas novas mensagens
        if event_type != "messages.upsert":
            return jsonify({"status": "ignored"}), 200

        # Identificação
        key = payload.get('key', {})
        remote_jid = key.get('remoteJid')
        from_me = key.get('fromMe', False)

        # Ignora mensagens próprias ou de status
        if from_me or "status@broadcast" in remote_jid:
            return jsonify({"status": "ignored"}), 200

        # Extração do texto
        message_content = payload.get('message', {})
        texto_usuario = (
            message_content.get('conversation') or 
            message_content.get('extendedTextMessage', {}).get('text')
        )
        
        if not texto_usuario:
            return jsonify({"status": "ignored", "reason": "no_text"}), 200

        push_name = payload.get('pushName', 'Cliente')

        # --- ACIONA A SOFIA ---
        logger.info(f"🔔 Webhook acionado por {push_name}: {texto_usuario}")
        sofia.processar_mensagem(remote_jid, texto_usuario, push_name)

        return jsonify({"status": "processed"}), 200

    except Exception as e:
        logger.error(f"❌ Erro no Webhook: {e}", exc_info=True)
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Roda na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)