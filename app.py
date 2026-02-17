import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual 3D", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES (Mantenemos las que ya funcionan) ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- COMPONENTE AVANZADO CON RITMO ORGÁNICO ---
def mostrar_avatar_avanzado(texto_para_audio=None):
    # Generar Audio
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
            st.error(f"Error audio: {e}")

    # CÓDIGO HTML/CSS/JS (LÓGICA DE HABLA REALISTA)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
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
            width: 300px;
            height: 400px;
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center bottom;
            transition: transform 0.1s ease; /* Suaviza el movimiento */
        }}

        /* Clase para boca abierta */
        .boca-abierta {{
            background-image: url('{URL_ABIERTA}') !important;
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
            
            let intervaloHabla;
            let estaHablando = false;

            // --- FUNCIÓN DE RESPIRACIÓN (Idle) ---
            // Hace que el robot suba y baje suavemente cuando no habla
            function animarRespiracion() {{
                if (!estaHablando) {{
                    const tiempo = Date.now() / 1000;
                    const escala = 1 + Math.sin(tiempo * 2) * 0.01; // Sube y baja 1%
                    robot.style.transform = `scale(${{escala}})`;
                    requestAnimationFrame(animarRespiracion);
                }}
            }}
            animarRespiracion(); // Iniciar respiración

            // --- FUNCIÓN DE HABLA ORGÁNICA ---
            function moverBocaAleatorio() {{
                if (!estaHablando) return;

                // 1. Abrimos la boca
                robot.classList.add('boca-abierta');
                // Efecto de rebote pequeño al hablar (énfasis)
                robot.style.transform = 'scale(1.02)';

                // 2. Calculamos un tiempo aleatorio para mantenerla abierta
                // (Simula vocales cortas y largas: entre 50ms y 200ms)
                const tiempoAbierto = Math.random() * 150 + 50;

                setTimeout(() => {{
                    // 3. Cerramos la boca
                    robot.classList.remove('boca-abierta');
                    robot.style.transform = 'scale(1.0)';

                    // 4. Calculamos tiempo aleatorio para mantenerla cerrada
                    // (Simula pausas entre sílabas: entre 50ms y 150ms)
                    const tiempoCerrado = Math.random() * 100 + 50;

                    if (estaHablando) {{
                        setTimeout(moverBocaAleatorio, tiempoCerrado);
                    }}
                }}, tiempoAbierto);
            }}

            // EVENTOS DE AUDIO
            player.onplay = function() {{
                estaHablando = true;
                moverBocaAleatorio(); // Iniciar ciclo de habla
            }};

            player.onpause = function() {{
                estaHablando = false;
                robot.classList.remove('boca-abierta');
                animarRespiracion(); // Volver a respirar
            }};
            
            player.onended = function() {{
                estaHablando = false;
                robot.classList.remove('boca-abierta');
                animarRespiracion(); // Volver a respirar
            }};

            // Autoplay forzado
            if ("{autoplay_attr}" === "autoplay") {{
                player.play().catch(e => console.log("Esperando clic..."));
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
1. Respuestas CORTAS (máximo 2 frases) para que el audio sea fluido.
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
            texto_para_reproducir = respuesta.text
            
        except Exception as e:
            st.error("Error de conexión.")

# --- MOSTRAR ---
col1, col2 = st.columns([1, 2])

with col1:
    mostrar_avatar_avanzado(texto_para_reproducir)

with col2:
    container = st.container(height=450)
    for m in st.session_state.mensajes:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])
