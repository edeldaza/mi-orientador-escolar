import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. IMÁGENES INSTITUCIONALES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. ESTILOS VISUALES (IDENTIDAD DEL COLEGIO) ---
st.markdown("""
    <style>
        .encabezado {
            text-align: center;
            padding: 20px;
            background-color: #f0f2f6;
            border-radius: 15px;
            margin-bottom: 25px;
            border-bottom: 5px solid #1E3A8A;
        }
        .titulo-colegio {
            color: #1E3A8A;
            font-family: sans-serif;
            font-weight: 900;
            font-size: 1.8rem; /* Ajustado para móviles */
            text-transform: uppercase;
            margin-top: 10px;
        }
        .subtitulo {
            color: #555;
            font-size: 1.1rem;
            margin-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOSTRAR ENCABEZADO ---
st.markdown(f"""
    <div class="encabezado">
        <img src="{URL_ESCUDO}" width="100">
        <div class="titulo-colegio">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <div class="subtitulo">🎓 Orientación Escolar Virtual 🎓</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz y Animación", value=True)
    st.info("ℹ️ Sistema exclusivo para estudiantes.")

# --- 6. FUNCIÓN DE AVATAR (ESTABLE) ---
def mostrar_avatar(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    # Este HTML incluye el reproductor y la lógica de animación
    html = f"""
    <div style="background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;">
        
        <div style="position: relative; width: 200px; height: 260px; margin: 0 auto;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;">
            </div>
            <div id="boca" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;">
            </div>
        </div>

        <audio id="player" controls autoplay style="width: 100%; margin-top: 10px; display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>

        <button id="btn" onclick="document.getElementById('player').play()" 
                style="display: none; margin-top: 10px; padding: 10px 20px; background: #1E3A8A; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">
            🔊 ESCUCHAR
        </button>
    </div>

    <script>
        var player = document.getElementById("player");
        var boca = document.getElementById("boca");
        var btn = document.getElementById("btn");
        var intervalo;

        // CUANDO SUENA -> ANIMAR
        player.onplay = function() {{
            btn.style.display = "none";
            intervalo = setInterval(() => {{
                boca.style.opacity = (boca.style.opacity == "0" ? "1" : "0");
            }}, 200);
        }};

        // CUANDO PARA -> DETENER
        player.onpause = function() {{ clearInterval(intervalo); boca.style.opacity = "0"; }};
        player.onended = function() {{ clearInterval(intervalo); boca.style.opacity = "0"; }};

        // INTENTO DE AUTOPLAY
        var promise = player.play();
        if (promise !== undefined) {{
            promise.catch(error => {{
                // Si falla (bloqueo navegador), mostramos botón
                btn.style.display = "block";
            }});
        }}
    </script>
    """
    return html

# --- 7. CONEXIÓN IA (CORREGIDA) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # INTENTO 1: Usar el modelo Flash (Rápido y Gratis)
    # IMPORTANTE: Esto requiere google-generativeai>=0.7.2
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- 8. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Hola, ¿cómo te sientes?"):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 9. RESPUESTA IA ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("El orientador está pensando..."):
        try:
            chat = model.start_chat(history=[])
            prompt = f"""
            Eres el Orientador Escolar de la Institución Educativa Rural Hugues Manuel Lacouture.
            Tu tono es empático, profesional y cercano con los estudiantes.
            Responde brevemente (máximo 2 frases).
            Si hay peligro (suicidio/abuso), deriva urgentemente a un adulto.
            Mensaje: {st.session_state.mensajes[-1]['content']}
            """
            
            respuesta = chat.send_message(prompt)
            texto_resp = respuesta.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
            
            with st.chat_message("assistant"):
                st.markdown(texto_resp)

            # AUDIO Y AVATAR
            if modo_voz:
                tts = gTTS(text=texto_resp, lang='es')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                # Renderizar Avatar
                html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                
                # Mostrar en barra lateral
                with st.sidebar:
                    st.components.v1.html(html_avatar, height=320)
            
        except Exception as e:
            # Manejo de errores amigable
            if "404" in str(e):
                st.error("⚠️ Error de versión: Por favor actualiza el archivo requirements.txt como te indiqué.")
            elif "429" in str(e):
                st.warning("⏳ El sistema está ocupado. Intenta de nuevo en 1 minuto.")
            else:
                st.error(f"Ocurrió un error: {e}")
