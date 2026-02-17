import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES (Boca Cerrada y Abierta) ---
# Asegúrate de que ambas imágenes tengan EL MISMO tamaño y encuadre
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- COMPONENTE DE AVATAR (SOLO BOCA) ---
def mostrar_avatar_avanzado(texto_para_audio=None):
    # Generar Audio
    audio_b64 = ""
    autoplay_attr = ""
    
    if texto_para_audio:
        try:
            # Generamos el audio
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            autoplay_attr = "autoplay"
        except Exception as e:
            st.error(f"Error audio: {e}")

    # CÓDIGO HTML/CSS/JS LIMPIO
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* 1. ANIMACIÓN DE HABLAR (SOLO CAMBIO DE IMAGEN) */
        /* Eliminé todos los 'transform: scale' para que no rebote */
        @keyframes hablar {{
            0% {{ background-image: url('{URL_CERRADA}'); }}
            50% {{ background-image: url('{URL_ABIERTA}'); }}
            100% {{ background-image: url('{URL_CERRADA}'); }}
        }}

        body {{
            background-color: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }}

        .robot {{
            width: 300px;  /* Ajusta el tamaño si lo quieres más grande/pequeño */
            height: 400px;
            
            /* Imagen por defecto: QUIETA */
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center bottom;
            
            /* Transiciones suaves por si acaso, pero sin movimiento */
            transition: background-image 0.1s;
        }}

        /* CLASE QUE ACTIVA EL MOVIMIENTO DE BOCA */
        .hablando {{
            /* 0.2s es la velocidad de abrir/cerrar la boca */
            animation: hablar 0.2s infinite; 
        }}
        
        audio {{ display: none; }}
    </style>
    </head>
    <body>

        <div id="robot-personaje" class="robot"></div>

        <audio id="player" controls {autoplay_attr}>
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const robot = document.getElementById('robot-personaje');

            // CUANDO SUENA EL AUDIO -> Activa la clase .hablando
            player.onplay = function() {{
                robot.classList.add('hablando');
            }};

            // CUANDO TERMINA O PAUSA -> Quita la clase .hablando
            player.onpause = function() {{
                robot.classList.remove('hablando');
            }};
            player.onended = function() {{
                robot.classList.remove('hablando');
            }};
            
            // Intento de autoplay
            if ("{autoplay_attr}" === "autoplay") {{
                player.play().catch(e => console.log("Esperando clic del usuario..."));
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)

# --- TÍTULO ---
st.title("🤖 Espacio de Escucha Escolar")

# --- CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error("Verifica tu API Key.")
    st.stop()

# --- INSTRUCCIONES ---
instrucciones = """
Actúa como un orientador escolar empático.
1. Respuestas CORTAS (máximo 2 frases) para que el audio sea rápido.
2. Tono amable.
3. SI HAY PELIGRO: "🚨 Busca ayuda urgente con un profesor o llama al 123."
"""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    st.info("🔊 Sube el volumen.")

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# --- PROCESAR RESPUESTA ---
texto_para_reproducir = None

if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("Pensando..."):
        try:
            ultimo = st.session_state.mensajes[-1]["content"]
            chat = model.start_chat(history=[])
            prompt = f"{instrucciones}\n\nMensaje: {ultimo}"
            respuesta = chat.send_message(prompt)
            
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
            texto_para_reproducir = respuesta.text # Guardamos para el audio
            
        except Exception as e:
            st.error("Error de conexión.")

# --- MOSTRAR EN COLUMNAS ---
col1, col2 = st.columns([1, 2])

with col1:
    # El avatar recibe el texto, genera el audio y mueve la boca
    mostrar_avatar_avanzado(texto_para_reproducir)

with col2:
    container = st.container(height=450)
    for m in st.session_state.mensajes:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])
