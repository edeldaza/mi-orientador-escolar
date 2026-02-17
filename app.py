import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- FUNCIÓN DE AVATAR ROBUSTO ---
def mostrar_avatar_seguro(texto_para_audio=None):
    audio_b64 = ""
    js_autoplay = ""
    
    # 1. Generar Audio
    if texto_para_audio:
        try:
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            js_autoplay = "intentarReproducir();"
        except Exception as e:
            st.error(f"Error generando audio: {e}")

    # 2. HTML/CSS/JS SIMPLIFICADO Y SEGURO
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
        }}

        /* EL ROBOT */
        .robot {{
            width: 100%;
            height: 100%;
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center bottom;
            /* Respiración suave siempre activa */
            animation: respirar 3s infinite ease-in-out;
            transition: transform 0.2s;
        }}

        /* CLASE PARA CUANDO HABLA */
        .hablando {{
            /* Alterna entre abierta y cerrada rápidamente */
            animation: moverBoca 0.2s infinite !important;
        }}

        /* ANIMACIONES */
        @keyframes respirar {{
            0% {{ transform: scale(1) translateY(0px); }}
            50% {{ transform: scale(1.02) translateY(-5px); }}
            100% {{ transform: scale(1) translateY(0px); }}
        }}

        @keyframes moverBoca {{
            0% {{ background-image: url('{URL_CERRADA}'); }}
            50% {{ background-image: url('{URL_ABIERTA}'); }}
            100% {{ background-image: url('{URL_CERRADA}'); }}
        }}

        /* BOTÓN DE AUDIO MANUAL (Por si falla el automático) */
        #btn-audio {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            background: #ff4b4b; color: white;
            border: none; padding: 15px 25px;
            border-radius: 50px; font-weight: bold; cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: none; /* Oculto por defecto */
            z-index: 100;
        }}
        #btn-audio:hover {{ background: #ff2b2b; transform: translate(-50%, -55%); }}

    </style>
    </head>
    <body>

        <div class="contenedor">
            <div id="personaje" class="robot"></div>
            <button id="btn-audio" onclick="forzarReproduccion()">🔊 ESCUCHAR RESPUESTA</button>
        </div>

        <audio id="player" preload="auto">
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const personaje = document.getElementById('personaje');
            const btn = document.getElementById('btn-audio');

            // --- LÓGICA DE SINCRONIZACIÓN (SIMPLE Y EFECTIVA) ---
            
            // 1. Cuando el audio empieza a sonar -> Mover boca
            player.onplay = function() {{
                personaje.classList.add('hablando');
                btn.style.display = 'none'; // Ocultar botón si suena
            }};

            // 2. Cuando el audio termina o se pausa -> Cerrar boca
            player.onended = function() {{
                personaje.classList.remove('hablando');
            }};
            player.onpause = function() {{
                personaje.classList.remove('hablando');
            }};

            // 3. Función para intentar reproducir
            function intentarReproducir() {{
                if (!player.src || player.src.includes('null')) return;
                
                var promise = player.play();
                
                if (promise !== undefined) {{
                    promise.catch(error => {{
                        console.log("Autoplay bloqueado. Mostrando botón manual.");
                        btn.style.display = 'block'; // Mostrar botón si falla
                    }});
                }}
            }}

            function forzarReproduccion() {{
                player.play();
                btn.style.display = 'none';
            }}

            // Ejecutar al cargar
            {js_autoplay}

        </script>
    </body>
    </html>
    """
    components.html(html_code, height=420)

# --- TÍTULO ---
st.title("🤖 Espacio de Escucha Escolar")

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
1. Respuestas MUY CORTAS (máximo 2 oraciones).
2. Tono amable.
3. PELIGRO: "🚨 Busca ayuda urgente con un profesor."
"""

# --- BARRA LATERAL ---
with st.sidebar:
    st.info("🔊 Si no escuchas automáticamente, pulsa el botón rojo sobre el robot.")

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# --- PROCESAMIENTO ---
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

# --- INTERFAZ ---
col1, col2 = st.columns([1, 2])

with col1:
    # Componente de Avatar
    mostrar_avatar_seguro(texto_final)

with col2:
    container = st.container(height=450)
    for m in st.session_state.mensajes:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])
