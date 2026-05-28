# 🌐 ACESSO REMOTO À IA MAMUTE

## 📍 Situação Atual

Sua IA está configurada perfeitamente para **acesso remoto**! O servidor já roda em `host="0.0.0.0"`, permitindo conexões externas.

## 🏠 1. Acesso na Rede Local (LAN)

**✅ PRONTO PARA USO!**

- **URL**: `http://192.168.1.70:8000`
- **Chat**: `http://192.168.1.70:8000/chat` 
- **Funciona em**: Celular, tablet, outros PCs na mesma rede WiFi

### Como usar:
1. Execute: `python web_app.py` 
2. No celular/outro PC: Digite `http://192.168.1.70:8000`

---

## 🌍 2. Acesso Global (Internet)

### Opção A: 🚀 Ngrok (Recomendado)
**GRATUITO e INSTANTÂNEO**

```bash
# Execute o configurador
python setup_acesso_remoto.py
```

Isso vai:
- ✅ Instalar ngrok automaticamente
- ✅ Criar túnel público HTTPS
- ✅ Gerar URL global (ex: https://abc123.ngrok.io)
- ✅ Abrir no navegador automaticamente

### Opção B: 🔧 Port Forwarding
**Para uso permanente no seu IP**

1. **Roteador**: Abra porta 8000 → 192.168.1.70:8000
2. **IP Público**: Descubra em https://whatismyipaddress.com
3. **Acesso**: `http://[SEU_IP]:8000`

### Opção C: ☁️ Deploy na Nuvem
**Para uso profissional 24/7**

- **Heroku**: Deploy gratuito
- **Railway**: Deploy com 1 clique  
- **DigitalOcean**: VPS por $5/mês

---

## 🛡️ Segurança

Para acesso público, adicione autenticação:

```python
# No web_app.py, adicione:
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.middleware("http")
async def add_auth(request: Request, call_next):
    if request.url.path.startswith("/admin"):
        credentials = await security(request)
        # Validar credenciais
    return await call_next(request)
```

---

## 🚀 Início Rápido

**Para acesso imediato de qualquer lugar:**

```bash
python setup_acesso_remoto.py
```

Escolha opção **2** (Internet Global) e em 30 segundos sua IA estará online mundialmente! 🌎

---

## 📱 URLs de Acesso

| Tipo | URL | Descrição |
|------|-----|-----------|
| **Local** | http://localhost:8000 | Só neste PC |
| **Rede** | http://192.168.1.70:8000 | Qualquer dispositivo na mesma rede |
| **Global** | Via ngrok/port forward | De qualquer lugar do mundo |

---

## ⚡ Testando Agora

1. **Execute**: `python web_app.py`
2. **Teste local**: http://localhost:8000
3. **Teste rede**: http://192.168.1.70:8000 (do celular)
4. **Global**: Execute `python setup_acesso_remoto.py`