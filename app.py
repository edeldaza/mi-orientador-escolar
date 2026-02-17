import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. DISEÑO ---
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 20px;
            border-bottom: 5px solid #003366;
        }
        .school-title {
            color: #003366;
            font-size: 28px;
            font-weight: bold;
            text-transform: uppercase;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="main-header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="school-title">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p>🎓 Portal de Orientación Escolar 🎓</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL (CON DIAGNÓSTICO) ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    
    st.divider()
    st.write("🔧 **Datos Técnicos (Solo para ti):**")
    try:
        st.info(f"Versión Librería Google: {genai.__version__}")
    except:
        st.error("No se pudo leer la versión.")

# --- 5. FUNCIÓN AVATAR ---
def mostrar_avatar(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html = f"""
    <div style="background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center;">
        <div style="position: relative; width: 180px; height: 240px; margin: 0 auto;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;">
            </div>
            <div id="mouth" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;">
            </div>
        </div>
        <audio id="player" autoplay style="display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    </div>
    <script>
        var player = document.getElementById("player");
        var mouth = document.getElementById("mouth");
        var interval;
        player.onplay = function() {{
            interval = setInterval(function() {{
                mouth.style.opacity = (mouth.style.opacity == "0" ? "1" : "0");
            }}, 200);
        }};
        player.onended = function() {{ clearInterval(interval); mouth.style.opacity = "0"; }};
        player.play(); 
    </script>
    """
    return html

# --- 6. CONEXIÓN INTELIGENTE ---
def conectar_ia():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return genai # Retornamos la librería configurada
    except Exception as e:
        st.error(f"Error de API Key: {e}")
        return None

lib_genai = conectar_ia()

# --- 7. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 8. PROCESAR RESPUESTA (CON REPORTE DE ERROR REAL) ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("Pensando..."):
        try:
            # INTENTO 1: Modelo Rápido (Flash)
            try:
                model = lib_genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Actúa como orientador escolar empático. Mensaje: {st.session_state.mensajes[-1]['content']}")
            except Exception as e_flash:
                # Si falla Flash, intentamos Pro
                st.sidebar.warning(f"Flash falló: {e_flash}") # Diagnóstico visual
                model = lib_genai.GenerativeModel('gemini-pro')
                response = model.generate_content(f"Actúa como orientador escolar empático. Mensaje: {st.session_state.mensajes[-1]['content']}")
            
            texto_resp = response.text
            
            # Guardar y mostrar
            st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
            with st.chat_message("assistant"):
                st.markdown(texto_resp)
            
            if modo_voz:
                tts = gTTS(text=texto_resp, lang='es')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                with st.sidebar:
                    st.components.v1.html(html_avatar, height=320)

        except Exception as e_final:
            # AQUÍ VEREMOS EL ERROR REAL
            st.error(f"❌ ERROR TÉCNICO: {e_final}")
            st.info("Por favor, copia este error y envíamelo para decirte la solución exacta.")
