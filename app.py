import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual 3D", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES ACTUALIZADAS ---
# ima1 = Boca Cerrada (Quieto)
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
# ima2 = Boca Abierta (Hablando) - ENLACE ACTUALIZADO
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- COMPONENTE DE AVATAR AVANZADO (HTML + JS + CSS) ---
def mostrar_avatar_avanzado(texto_para_audio=None):
    # Generamos el audio aquí mismo si hay texto
    audio_b64 = ""
    autoplay_attr = ""
    
    if texto_para_audio:
        try:
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            autoplay_attr = "autoplay"
        except Exception as e:
            st.error(f"Error generando audio: {e}")

    # CÓDIGO HTML/CSS/JS (La Magia de la Animación)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* 1. EFECTO DE RESPIRACIÓN (IDLE) */
        @keyframes respirar {{
            0% {{ transform: scale(1) translateY(0px); }}
            50% {{ transform: scale(1.02) translateY(-5px); }}
            100% {{ transform: scale(1) translateY(0px); }}
        }}

        /* 2. EFECTO DE HABLAR (Alterna imágenes rápido) */
        @keyframes hablar {{
            0% {{ background-image: url('{URL_CERRADA}'); transform: scale(1); }}
            25% {{ background-image: url('{URL_ABIERTA}'); transform: scale(1.05); }}
            50% {{ background-image: url('{URL_CERRADA}'); transform: scale(1); }}
            75% {{ background-image: url('{URL_ABIERTA}'); transform: scale(1.05); }}
            100% {{ background-image: url('{URL_CERRADA}'); transform: scale(1); }}
        }}

        body {{
            background-color: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            overflow: hidden;
        }}

        .avatar-container {{
            width: 100%;
            height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .robot {{
            width: 300px;
            height: 400px;
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            
            /* Por defecto: RESPIRA */
            animation: respirar 3s infinite ease-in-out;
            transition: all 0.2s ease;
        }}

        /* Clase que activa el habla */
        .hablando {{
            animation: hablar 0.2s infinite !important;
        }}
        
        audio {{
            display: none;
        }}
    </style>
    </head>
    <body>

        <div class="avatar-container">
            <div id="robot-personaje" class="robot"></div>
        </div>

        <audio id="player" controls {autoplay_attr}>
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const robot = document.getElementById('robot-personaje');

            // CUANDO SUENA EL AUDIO -> ACTIVA ANIMACIÓN
            player.onplay = function() {{
                robot.classList.add('hablando');
            }};

            // CUANDO TERMINA O PAUSA -> VUELVE A RESPIRAR
            player.onpause = function() {{
                robot.classList.remove('hablando');
            }};
            player.onended = function() {{
                robot.classList.remove('hablando');
            }};
            
            // Intentar reproducir automáticamente
            if ("{autoplay_attr}" === "autoplay") {{
                player.play().catch(e => console.log("Esperando interacción del usuario..."));
            }}
        </script>
    </body>
    </html>
    """
    # Renderizamos el componente con altura suficiente
    components.html(html_code, height=420)

# --- TÍTULO PRINCIPAL ---
st.title("🤖 Espacio de Escucha Escolar")

# --- CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- INSTRUCCIONES ---
instrucciones_seguridad = """
Actúa como un orientador escolar empático y juvenil.
1. Respuestas MUY CORTAS (máximo 2 oraciones) para que el audio sea rápido.
2. Tono cálido.
3. SI HAY PELIGRO: "🚨 Busca ayuda urgente con un profesor o llama al 123."
"""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    st.info("ℹ️ Sube el volumen. El robot moverá la boca cuando hable.")

# --- HISTORIAL ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- LÓGICA DE CHAT ---
# 1. Entrada
if texto := st.chat_input("Escribe aquí lo que sientes..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# 2. Procesar respuesta
texto_para_reproducir = None

# Si el último mensaje es del usuario, generamos respuesta
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("Pensando..."):
        try:
            ultimo_texto = st.session_state.mensajes[-1]["content"]
            chat = model.start_chat(history=[])
            prompt = f"{instrucciones_seguridad}\n\nMensaje: {ultimo_texto}"
            respuesta = chat.send_message(prompt)
            
            # Guardamos respuesta
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
            
            # Preparamos el texto para que el Avatar lo hable
            texto_para_reproducir = respuesta.text
            
        except Exception as e:
            st.error("Error al conectar.")

# --- DISEÑO DE COLUMNAS (Avatar Izq - Chat Der) ---
col1, col2 = st.columns([1, 2])

with col1:
    # AQUÍ ESTÁ LA MAGIA:
    # Pasamos el texto al componente HTML. El componente genera el audio internamente
    # y coordina la animación de las imágenes.
    mostrar_avatar_avanzado(texto_para_reproducir)

with col2:
    container_chat = st.container(height=400)
    for m in st.session_state.mensajes:
        with container_chat.chat_message(m["role"]):
            st.markdown(m["content"])
