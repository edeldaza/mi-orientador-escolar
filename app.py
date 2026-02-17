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

# --- 3. ENCABEZADO INSTITUCIONAL ---
st.markdown("""
    <style>
        .header {
            text-align: center;
            padding: 20px;
            background-color: #f4f6f9;
            border-radius: 15px;
            border-bottom: 5px solid #003366;
            margin-bottom: 20px;
        }
        .title-text {
            color: #003366;
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="title-text">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p>🎓 Portal de Orientación Escolar 🎓</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.info("Sistema exclusivo para estudiantes.")

# --- 5. FUNCIÓN AVATAR ---
def mostrar_avatar(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html = f"""
    <div style="background: white; padding: 10px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="position: relative; width: 180px; height: 240px; margin: 0 auto;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;"></div>
            <div id="mouth" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;"></div>
        </div>
        <audio id="player" autoplay style="display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    </div>
    <script>
        var p = document.getElementById("player");
        var m = document.getElementById("mouth");
        var i;
        p.onplay = () => {{ i = setInterval(() => {{ m.style.opacity = (m.style.opacity == "0" ? "1" : "0"); }}, 200); }};
        p.onended = () => {{ clearInterval(i); m.style.opacity = "0"; }};
        p.play();
    </script>
    """
    return html

# --- 6. CONFIGURACIÓN DE MODELOS (SIN GASTAR CUOTA) ---
def obtener_respuesta_ia(mensaje_usuario):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # Intentamos primero con el modelo RÁPIDO (Flash)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Eres el Orientador Escolar de la I.E.R. Hugues Manuel Lacouture. Responde breve y amablemente (máx 2 frases). Mensaje: {mensaje_usuario}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            # Si el error es 404 (Librería vieja) o 429 (Cuota), intentamos con PRO
            if "404" in error_msg or "429" in error_msg:
                # Fallback al modelo PRO
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"Eres el Orientador Escolar de la I.E.R. Hugues Manuel Lacouture. Responde breve y amablemente (máx 2 frases). Mensaje: {mensaje_usuario}"
                response = model.generate_content(prompt)
                return response.text
            else:
                raise e # Si es otro error, lo lanzamos

    except Exception as e_final:
        if "429" in str(e_final):
            return "⏳ El sistema está recibiendo muchas consultas. Por favor, espera 1 minuto y vuelve a intentarlo."
        else:
            return f"❌ Error técnico: {e_final}"

# --- 7. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 8. PROCESAR ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("El orientador está pensando..."):
        # Llamamos a la función optimizada
        texto_resp = obtener_respuesta_ia(st.session_state.mensajes[-1]['content'])
        
        st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
        with st.chat_message("assistant"):
            st.markdown(texto_resp)
        
        # Audio (Solo si no es un mensaje de error)
        if modo_voz and "Error" not in texto_resp and "consulta" not in texto_resp:
            try:
                tts = gTTS(text=texto_resp, lang='es')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                with st.sidebar:
                    st.components.v1.html(html_avatar, height=320)
            except:
                pass # Si falla el audio, no bloqueamos el chat
