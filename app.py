import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Pro 3D", page_icon="🤖", layout="wide")

# --- TU ÚNICA IMAGEN (Boca Cerrada) ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"

# --- COMPONENTE DE MARIONETA AVANZADA ---
def mostrar_marioneta_avanzada(texto_para_audio=None):
    audio_b64 = ""
    start_script = ""
    
    if texto_para_audio:
        try:
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            start_script = "iniciarAudio();" 
        except Exception as e:
            st.error(f"Error audio: {e}")

    # --- HTML/CSS/JS (Técnica de Marioneta) ---
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; }}
        
        .container {{
            position: relative;
            width: 300px; /* Ajuste fino para que coincida con la imagen */
            height: 400px;
        }}

        /* EL CUERPO DEL ROBOT (Imagen base) */
        .robot-cuerpo {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center bottom;
            z-index: 1;
            /* Animación de respiración por defecto */
            animation: respirar 4s infinite ease-in-out;
            transform-origin: bottom center;
        }}

        /* LOS PÁRPADOS (Capas blancas semitransparentes sobre los ojos) */
        .parpado {{
            position: absolute;
            background-color: #ffffff; /* Color del párpado */
            opacity: 0.7; /* Un poco transparentes para que se vea la luz azul debajo */
            height: 0%; /* Empiezan abiertos (altura 0) */
            z-index: 5;
            transition: height 0.1s;
        }}

        /* Posición exacta de los ojos en TU imagen ima1.png */
        .ojo-izq {{
            top: 27%;
            left: 24%;
            width: 18%;
            height: 15%;
            border-top-left-radius: 50%;
            border-top-right-radius: 50%;
        }}
        .ojo-der {{
            top: 27%;
            right: 24%;
            width: 18%;
            height: 15%;
            border-top-left-radius: 50%;
            border-top-right-radius: 50%;
        }}
        
        /* CLASE PARA PARPADEAR */
        .cerrar-ojos {{
             height: 15% !important; /* Cierra el párpado */
        }}

        /* ANIMACIONES */
        @keyframes respirar {{
            0% {{ transform: scale(1) translateY(0px); }}
            50% {{ transform: scale(1.02) translateY(-4px); }}
            100% {{ transform: scale(1) translateY(0px); }}
        }}

        /* Esta animación hace que el robot vibre rápido al hablar */
        @keyframes vibrar-hablando {{
            0% {{ transform: translateY(0px) scale(1.01); }}
            25% {{ transform: translateY(2px) scale(1.01); }}
            50% {{ transform: translateY(0px) scale(1.01); }}
            75% {{ transform: translateY(3px) scale(1.01); }}
            100% {{ transform: translateY(0px) scale(1.01); }}
        }}

        .hablando-activo {{
            /* Sobreescribe la respiración con la vibración rápida */
            animation: vibrar-hablando 0.15s infinite linear !important;
        }}

        #btn-start {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            z-index: 10; background: #ff4b4b; color: white; border: none;
            padding: 10px 20px; border-radius: 20px; cursor: pointer; font-weight: bold;
            display: none;
        }}
    </style>
    </head>
    <body>

        <div class="container">
            <div id="robot" class="robot-cuerpo">
                 <div id="p-izq" class="parpado ojo-izq"></div>
                <div id="p-der" class="parpado ojo-der"></div>
            </div>
            <button id="btn-start" onclick="iniciarAudio()">🔊 Tocar para escuchar</button>
        </div>

        <audio id="player" crossorigin="anonymous">
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const robot = document.getElementById('robot');
            const pIzq = document.getElementById('p-izq');
            const pDer = document.getElementById('p-der');
            const btn = document.getElementById('btn-start');
            let audioContext, analyser, dataArray, source;
            let hablando = false;

            // --- FUNCIÓN DE PARPADEO ALEATORIO ---
            function parpadear() {{
                // Cierra los ojos
                pIzq.classList.add('cerrar-ojos');
                pDer.classList.add('cerrar-ojos');
                
                // Los abre después de 150ms
                setTimeout(() => {{
                    pIzq.classList.remove('cerrar-ojos');
                    pDer.classList.remove('cerrar-ojos');
                }}, 150);

                // Programa el próximo parpadeo entre 2 y 6 segundos
                const proximoParpadeo = Math.random() * 4000 + 2000;
                setTimeout(parpadear, proximoParpadeo);
            }}
            // Iniciar ciclo de parpadeo
            setTimeout(parpadear, 3000);


            // --- LÓGICA DE AUDIO (VIBRACIÓN) ---
            function iniciarAudio() {{
                if (!player.src || player.src === window.location.href) return;
                if (!audioContext) {{
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioContext.createAnalyser();
                    source = audioContext.createMediaElementSource(player);
                    source.connect(analyser);
                    analyser.connect(audioContext.destination);
                    analyser.fftSize = 64; 
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                }}
                if (audioContext.state === 'suspended') audioContext.resume();

                player.play().then(() => {{
                    btn.style.display = 'none';
                    hablando = true;
                    detectarVoz();
                }}).catch(e => {{ btn.style.display = 'block'; }});
            }}

            function detectarVoz() {{
                if (player.paused || !hablando) {{
                    robot.classList.remove('hablando-activo');
                    return;
                }}
                requestAnimationFrame(detectarVoz);
                analyser.getByteFrequencyData(dataArray);

                // Calcular volumen promedio
                let suma = 0;
                for(let i = 0; i < dataArray.length; i++) suma += dataArray[i];
                let promedio = suma / dataArray.length;

                // UMBRAL: Si el volumen supera 30, activa la vibración
                if (promedio > 30) {{
                    robot.classList.add('hablando-activo');
                }} else {{
                    robot.classList.remove('hablando-activo');
                }}
            }}
            
            player.onended = () => {{ hablando = false; robot.classList.remove('hablando-activo'); }};
            {start_script}
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
    st.error("Revisa tu API Key.")
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
            st.error("Error conexión.")

# --- MOSTRAR ---
col1, col2 = st.columns([1, 2])

with col1:
    # Usamos la nueva marioneta
    mostrar_marioneta_avanzada(texto_para_reproducir)

with col2:
    container = st.container(height=450)
    for m in st.session_state.mensajes:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])
