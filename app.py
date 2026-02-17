import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Pro", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES (Boca Cerrada y Abierta) ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- COMPONENTE DE SINCRONIZACIÓN PROFESIONAL ---
def mostrar_avatar_definitivo(texto_para_audio=None):
    audio_b64 = ""
    # Variable para intentar autoplay desde JS
    trigger_js = "" 
    
    if texto_para_audio:
        try:
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            trigger_js = "iniciarReproduccion();" # Orden de arrancar
        except Exception as e:
            st.error(f"Error generando audio: {e}")

    # --- CÓDIGO HTML/JS ROBUSTO ---
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; font-family: sans-serif; }}
        
        .contenedor-avatar {{
            position: relative;
            width: 300px;
            height: 400px;
        }}

        /* IMAGEN 1: BASE (SIEMPRE VISIBLE) */
        .capa-base {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{URL_CERRADA}');
            background-size: contain; background-repeat: no-repeat; background-position: center bottom;
            z-index: 1;
        }}

        /* IMAGEN 2: BOCA ABIERTA (SE MEZCLA SEGÚN VOLUMEN) */
        .capa-boca {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{URL_ABIERTA}');
            background-size: contain; background-repeat: no-repeat; background-position: center bottom;
            z-index: 2;
            opacity: 0; /* Invisible al inicio */
            transition: opacity 0.08s ease-out; /* Suavizado para realismo */
            will-change: opacity;
        }}

        /* ANIMACIÓN DE RESPIRACIÓN (IDLE) */
        @keyframes respirar {{
            0% {{ transform: translateY(0px) scale(1); }}
            50% {{ transform: translateY(-5px) scale(1.02); }}
            100% {{ transform: translateY(0px) scale(1); }}
        }}
        
        .animado {{
            animation: respirar 4s infinite ease-in-out;
        }}

        /* BOTÓN DE EMERGENCIA (SI EL NAVEGADOR BLOQUEA EL AUDIO) */
        #btn-play {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            z-index: 10;
            background-color: #ff4b4b; color: white; border: none;
            padding: 15px 30px; border-radius: 50px; font-size: 16px; font-weight: bold;
            cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: none; /* Oculto por defecto */
        }}
        #btn-play:hover {{ background-color: #ff2b2b; transform: translate(-50%, -52%); }}

    </style>
    </head>
    <body>

        <div class="contenedor-avatar animado">
            <div class="capa-base"></div>
            <div class="capa-boca" id="boca"></div>
            <button id="btn-play" onclick="iniciarReproduccion()">▶️ ACTIVAR AUDIO</button>
        </div>

        <audio id="player" crossorigin="anonymous">
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const boca = document.getElementById('boca');
            const btn = document.getElementById('btn-play');
            
            let audioContext, analyser, dataArray;
            let animacionActiva = false;

            function iniciarReproduccion() {{
                if (!player.src || player.src === window.location.href) return;

                // 1. Configurar Audio Context (Necesario para analizar volumen)
                if (!audioContext) {{
                    try {{
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = audioContext.createAnalyser();
                        const source = audioContext.createMediaElementSource(player);
                        source.connect(analyser);
                        analyser.connect(audioContext.destination);
                        analyser.fftSize = 64; // Precisión del análisis
                        dataArray = new Uint8Array(analyser.frequencyBinCount);
                    }} catch (e) {{ console.log("Error audio context:", e); }}
                }}

                // 2. Intentar reproducir
                player.play().then(() => {{
                    btn.style.display = 'none'; // Ocultar botón si funciona
                    if (audioContext.state === 'suspended') audioContext.resume();
                    animacionActiva = true;
                    sincronizarLabios();
                }}).catch(error => {{
                    console.log("Autoplay bloqueado. Mostrando botón.");
                    btn.style.display = 'block'; // Mostrar botón si falla
                }});
            }}

            // --- EL CEREBRO DE LA SINCRONIZACIÓN ---
            function sincronizarLabios() {{
                if (!animacionActiva || player.paused) {{
                    boca.style.opacity = 0; // Cerrar boca si no suena
                    return;
                }}
                
                requestAnimationFrame(sincronizarLabios);

                // Leer volumen actual
                if (analyser) {{
                    analyser.getByteFrequencyData(dataArray);
                    
                    let suma = 0;
                    // Promediar frecuencias bajas (donde está la voz humana)
                    for(let i = 0; i < dataArray.length; i++) {{
                        suma += dataArray[i];
                    }}
                    let volumen = suma / dataArray.length; // Valor entre 0 y 255

                    // Convertir volumen a Opacidad (0.0 a 1.0)
                    // Dividimos por 80 para que sea sensible
                    let apertura = volumen / 80; 
                    
                    // Limitar extremos
                    if (apertura > 1) apertura = 1;
                    if (apertura < 0.1) apertura = 0; // Silencio = boca cerrada

                    boca.style.opacity = apertura;
                }}
            }}

            // Eventos
            player.onended = () => {{ animacionActiva = false; boca.style.opacity = 0; }};
            
            // Intentar arranque automático
            {trigger_js}

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
1. Respuestas CORTAS (máximo 2 oraciones).
2. Tono amable.
3. PELIGRO: "🚨 Busca ayuda urgente con un profesor."
"""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    st.info("🔊 Si no escuchas nada, pulsa el botón rojo que aparecerá sobre el robot.")

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
            st.error("Error conexión.")

# --- MOSTRAR ---
col1, col2 = st.columns([1, 2])

with col1:
    # Llamamos al componente
    mostrar_avatar_definitivo(texto_para_reproducir)

with col2:
    container = st.container(height=450)
    for m in st.session_state.mensajes:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])
