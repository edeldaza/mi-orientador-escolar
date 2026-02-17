import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual 3D", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES (Asegúrate de que sean las mismas URLs de antes) ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- COMPONENTE DE AVATAR AVANZADO (HTML + JS + CSS) ---
def mostrar_avatar_avanzado(audio_bytes=None):
    # Si hay audio, lo convertimos a base64 para el navegador
    audio_b64 = ""
    autoplay_attr = ""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes.read()).decode()
        audio_b64 = f"data:audio/mp3;base64,{b64}"
        autoplay_attr = "autoplay"

    # CÓDIGO HTML/CSS/JS COMPLETO
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* 1. EFECTO DE RESPIRACIÓN (IDLE) - Para que parezca 3D/Vivo */
        @keyframes respirar {{
            0% {{ transform: scale(1) translateY(0px); }}
            50% {{ transform: scale(1.02) translateY(-5px); }} /* Sube un poquito */
            100% {{ transform: scale(1) translateY(0px); }}
        }}

        /* 2. EFECTO DE HABLAR - Abre y cierra la boca rápido */
        @keyframes hablar {{
            0% {{ background-image: url('{URL_CERRADA}'); transform: scale(1); }}
            25% {{ background-image: url('{URL_ABIERTA}'); transform: scale(1.05); }} /* Rebote al hablar */
            50% {{ background-image: url('{URL_CERRADA}'); transform: scale(1); }}
            75% {{ background-image: url('{URL_ABIERTA}'); transform: scale(1.05); }}
            100% {{ background-image: url('{URL_CERRADA}'); transform: scale(1); }}
        }}

        /* CONTENEDOR DEL ROBOT */
        .avatar-container {{
            width: 100%;
            height: 350px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: visible;
        }}

        .robot {{
            width: 280px; /* Tamaño del robot */
            height: 350px;
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            
            /* Por defecto está respirando (vivo) */
            animation: respirar 3s infinite ease-in-out;
            transition: all 0.2s ease;
        }}

        /* CLASE QUE SE ACTIVA SOLO AL HABLAR */
        .hablando {{
            animation: hablar 0.2s infinite !important;
        }}
        
        audio {{
            display: none; /* Ocultamos el reproductor feo */
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

            // EVENTO 1: CUANDO EL AUDIO REALMENTE EMPIEZA A SONAR
            player.onplay = function() {{
                robot.classList.add('hablando'); // Activa la animación rápida
            }};

            // EVENTO 2: CUANDO EL AUDIO TERMINA O SE PAUSA
            player.onpause = function() {{
                robot.classList.remove('hablando'); // Vuelve a respirar suave
            }};
            player.onended = function() {{
                robot.classList.remove('hablando'); // Vuelve a respirar suave
            }};
            
            // Intento de autoplay forzado (a veces los navegadores bloquean)
            player.play().catch(e => console.log("Esperando interacción..."));
        </script>
    </body>
    </html>
    """
    # Renderizamos el componente con altura suficiente
    components.html(html_code, height=400)

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
1. Respuestas MUY CORTAS (máximo 2 oraciones) para que el audio cargue rápido.
2. Tono cálido.
3. SI HAY PELIGRO: "🚨 Busca ayuda urgente con un profesor o llama al 123."
"""

# --- FUNCIÓN DE AUDIO ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        return None

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    st.info("ℹ️ Sube el volumen. El robot se moverá solo cuando hable.")

# --- HISTORIAL ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- LÓGICA DE CHAT ---
# 1. Entrada del usuario
if texto := st.chat_input("Escribe aquí lo que sientes..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# 2. Procesar respuesta (SI el último mensaje es del usuario)
audio_para_reproducir = None

if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("Pensando..."):
        try:
            ultimo_texto = st.session_state.mensajes[-1]["content"]
            chat = model.start_chat(history=[])
            prompt = f"{instrucciones_seguridad}\n\nMensaje: {ultimo_texto}"
            respuesta = chat.send_message(prompt)
            
            # Guardamos respuesta
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
            
            # Generamos audio INMEDIATAMENTE para pasarlo al avatar
            audio_para_reproducir = texto_a_audio(respuesta.text)
            
        except Exception as e:
            st.error("Error al conectar.")

# --- MOSTRAR INTERFAZ ---

# A) COLUMNA IZQUIERDA: EL AVATAR (SIEMPRE VISIBLE)
col1, col2 = st.columns([1, 2])

with col1:
    # Aquí llamamos a nuestra función mágica.
    # Si hay "audio_para_reproducir", el robot hablará.
    # Si no (es None), el robot estará en modo "respirar" (vivo).
    mostrar_avatar_avanzado(audio_para_reproducir)

# B) COLUMNA DERECHA: EL CHAT
with col2:
    container_chat = st.container(height=400)
    for m in st.session_state.mensajes:
        with container_chat.chat_message(m["role"]):
            st.markdown(m["content"])
