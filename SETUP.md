# 🤖 JARVIS - Guía de Instalación

## Requisitos
- Python 3.10+
- Cuenta en Telegram
- API Key de Anthropic (anthropic.com)

---

## Paso 1: Crear el bot en Telegram

1. Abre Telegram y busca **@BotFather**
2. Escribe `/newbot`
3. Dale un nombre: ej. `Mi JARVIS`
4. Dale un username: ej. `mi_jarvis_bot`
5. **Copia el token** que te da (parece: `123456789:ABCdef...`)

---

## Paso 2: Obtener tu API Key de Anthropic

1. Ve a https://console.anthropic.com
2. Ve a **API Keys** → **Create Key**
3. **Copia la key** (solo se muestra una vez)

---

## Paso 3: Instalar y configurar

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tu editor favorito y pega tus claves
```

---

## Paso 4: Ejecutar

```bash
python jarvis_bot.py
```

¡Listo! Abre Telegram, busca tu bot y escríbele `/start`

---

## Comandos disponibles

| Comando | Función |
|---------|---------|
| `/start` | Inicia JARVIS y nueva sesión |
| `/reset` | Borra la memoria de la conversación |
| `/status` | Estado del sistema |

---

## Mantenerlo corriendo 24/7

### Opción A: En tu PC mientras está encendida
```bash
python jarvis_bot.py
```

### Opción B: En un servidor VPS (Railway, Render, DigitalOcean)

**Railway.app (gratis):**
1. Crea cuenta en railway.app
2. New Project → Deploy from GitHub
3. Sube el código a GitHub
4. Agrega las variables de entorno en Railway
5. Deploy ✅

### Opción C: Como servicio en Linux (systemd)
```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/jarvis.service

# Contenido:
[Unit]
Description=JARVIS Telegram Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/al/bot
ExecStart=/usr/bin/python3 jarvis_bot.py
Restart=always

[Install]
WantedBy=multi-user.target

# Activar
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

---

## Personalizar la personalidad

Edita `JARVIS_PERSONALITY` en `jarvis_bot.py` para cambiar:
- El nombre del asistente
- El tono (formal, casual, técnico)
- El idioma base
- Las capacidades específicas

---

## Próximas mejoras posibles

- 🎙️ Transcripción de voz con Whisper API
- 📸 Análisis de imágenes con Claude Vision
- 🔍 Búsqueda web en tiempo real
- 📅 Integración con Google Calendar
- 💾 Base de datos para memoria permanente (SQLite)
- 🏠 Integración con Home Assistant (domótica)
