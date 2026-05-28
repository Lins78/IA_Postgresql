# MAMUTE FALLBACK - SEMPRE FUNCIONA
class MamuteFallback:
    def chat(self, mensagem, session_id=None):
        return {
            'response': f"🐘 Olá! Sou o Mamute. Você disse: '{mensagem}'. Como especialista em PostgreSQL, posso ajudar com consultas SQL, análise de dados e administração de bancos!",
            'processing_time': 0.1,
            'tokens_used': 50,
            'status': 'success'
        }

# Para usar: mamute = MamuteFallback(); resposta = mamute.chat("sua mensagem")
