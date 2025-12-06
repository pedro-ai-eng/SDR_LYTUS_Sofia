import asyncio
from app.brain import generate_response

async def teste_sofia():
    print("\n" + "="*50)
    print("🤖 SOFIA (LYTUS) - AMBIENTE DE TESTE")
    print("="*50)
    print("🧠 Carregando inteligência híbrida (Gemini 2.0 + Local)...")
    
    while True:
        print("\n" + "-"*50)
        # Solicita a pergunta ao usuário no terminal
        pergunta = input("Digite sua pergunta (ou 'sair' para encerrar): ")
        
        if pergunta.lower() in ['sair', 'exit', 'parar']:
            print("👋 Encerrando teste.")
            break
            
        if not pergunta.strip():
            continue

        print(f"\n⏳ Sofia está pensando...")
        
        try:
            # Chama a função principal do cérebro
            resposta = await generate_response(
                user_message=pergunta,
                user_name="Admin Lytus"
            )
            
            print(f"\n💬 SOFIA RESPONDEU:\n")
            print(resposta)
            
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(teste_sofia())