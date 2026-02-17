import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.image(URL_CERRADA, width=100)
    st.title("Configuración")
    
    # 1. AQUÍ ESTÁ LA OPCIÓN QUE FALTABA
    modo_audio = st.radio(
        "¿Cómo quieres las respuestas?",
        ["Solo Texto 📝", "Audio y Animación 🗣️"],
        index=1
    )
    
    st.info("ℹ️ Si el audio no arranca solo, aparecerá un botón de 'Play' sobre el robot.")

# --- COMPONENTE DE AVATAR ROBUSTO ---
def mostrar_avatar(texto_para_audio=None):
    # Solo generamos audio si el usuario eligió esa opción y hay texto
    audio_b64 = ""
    display_style = "none" # Por defecto el botón de play está oculto
    autoplay_js = ""

    if texto_para_audio and "Audio" in modo_audio:
        try:
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            autoplay_js = "intentarAutoplay();" # Intentamos reproducir al cargar
        except Exception as e:
            st.error(f"Error generando audio: {e}")

    # CÓDIGO HTML/CSS/JS
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; background: transparent; display: flex; justify-content: center; font-family: sans-serif; }}
        
        .contenedor {{
            position: relative;
            width: 300px;
            height: 400px;
            cursor: pointer;
        }}

        /* CAPAS DE IMAGEN */
        .robot-base {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{URL_CERRADA}');
            background-size: contain; background-repeat: no-repeat; background-position: center bottom;
            z-index: 1;
            transition: transform 0.1s;
        }}
        
        .robot-boca {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{URL_ABIERTA}');
            background-size: contain; background-repeat: no-repeat; background-position: center bottom;
            z-index: 2;
            opacity: 0; /* Invisible por defecto */
        }}

        /* CLASE PARA ANIMAR LA BOCA */
        .hablando {{
            animation: moverBoca 0.2s infinite;
        }}

        @keyframes moverBoca {{
            0% {{ opacity: 0; transform: scale(1); }}
            50% {{ opacity: 1; transform: scale(1.02); }} /* Abre boca */
            100% {{ opacity: 0; transform: scale(1); }}
        }}

        /* BOTÓN DE PLAY GIGANTE (OVERLAY) */
        #overlay-play {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.4);
            z-index: 10;
            display: flex; justify-content: center; align-items: center;
            border-radius: 20px;
            display: none; /* Oculto inicialmente */
        }}
        .btn-icon {{
            font-size: 50px;
            background: white;
            border-radius: 50%;
            width: 80px; height: 80px;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            cursor: pointer;
        }}
        .btn-icon:hover {{ transform: scale(1.1); }}

    </style>
    </head>
    <body>

        <div class="contenedor" onclick="forzarPlay()">
            <div id="base" class="robot-base"></div>
            <div id="boca" class="robot-boca"></div>
            
            <div id="overlay-play">
                <div class="btn-icon">▶️</div>
            </div>
        </div>

        <audio id="player">
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const boca = document.getElementById('boca');
            const overlay = document.getElementById('overlay-play');

            // 1. SINCRONIZACIÓN: Solo mover boca si suena el audio
            player.onplay = function() {{
                boca.classList.add('hablando');
                overlay.style.display = 'none'; // Quitar botón play
            }};
            
            player.onpause = function() {{ boca.classList.remove('hablando'); }};
            player.onended = function() {{ boca.classList.remove('hablando'); }};

            // 2. INTENTO DE AUTOPLAY
            function intentarAutoplay() {{
                if (!player.src || player.src.includes('null')) return;

                var promise = player.play();
                if (promise !== undefined) {{
                    promise.catch(error => {{
                        console.log("Autoplay bloqueado. Mostrando botón.");
                        overlay.style.display = 'flex'; // MOSTRAR BOTÓN GIGANTE
                    }});
                }}
            }}

            // 3. PLAY MANUAL (Al hacer clic en el robot)
            function forzarPlay() {{
                if (player.paused && player.src) {{
                    player.play();
                }} else {{
                    player.pause();
                }}
            }}

            // Ejecutar al inicio
            {autoplay_js}

        </script>
    </body>
    </html>
    """
    components.html(html_code, height=420)

# --- TÍTULO PRINCIPAL ---
st.title("🎓 Espacio de Escucha Escolar")

# --- CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error("Error de conexión.")
    st.stop()

# --- INSTRUCCIONES ---
instrucciones = """
Actúa como un orientador escolar empático.
1. Respuestas CORTAS (máximo 2 párrafos).
2. Tono amable.
3. SI HAY PELIGRO: "🚨 Busca ayuda urgente con un profesor."
"""

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe aquí lo que sientes..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# --- PROCESAR ---
texto_final = None

if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("Pensando..."):
        try:
            ultimo = st.session_state.mensajes[-1]["content"]
            chat = model.start_chat(history=[])
            prompt = f"{instrucciones}\n\nMensaje: {ultimo}"
            respuesta = chat.send_message(prompt)
            
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
            texto_final = respuesta.text
            
        except Exception as e:
            st.error("Error al conectar.")

# --- INTERFAZ (COLUMNAS) ---
col1, col2 = st.columns([1, 2])

with col1:
    # Mostramos el avatar (el componente decide si poner audio o no según el modo)
    mostrar_avatar(texto_final)

with col2:
    container = st.container(height=450)
    for m in st.session_state.mensajes:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])
