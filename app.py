import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

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

# --- 6. CONEXIÓN INTELIGENTE (EL SALVAVIDAS) ---
def obtener_modelo_seguro():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # INTENTO 1: Usar el modelo moderno (Flash)
        try:
            modelo = genai.GenerativeModel('gemini-1.5-flash')
            # Hacemos una prueba muda. Si falla, saltará al 'except'
            modelo.generate_content("test", generation_config={"max_output_tokens": 1})
            return modelo
        except:
            # INTENTO 2: Si falla el Flash (404), usamos el CLÁSICO (Pro)
            # Este SIEMPRE existe, incluso en versiones viejas
            return genai.GenerativeModel('gemini-pro')

    except Exception as e:
        st.error(f"Error de conexión con Google: {e}")
        return None

model = obtener_modelo_seguro()

# --- 7. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 8. RESPUESTA ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    if model:
        with st.spinner("El orientador está pensando..."):
            try:
                chat = model.start_chat(history=[])
                prompt = f"""
                Eres el Orientador Escolar de la Institución Educativa Rural Hugues Manuel Lacouture.
                Responde breve y amablemente (máx 2 frases).
                Si el alumno menciona peligro, deriva a un adulto.
                Mensaje: {st.session_state.mensajes[-1]['content']}
                """
                response = chat.send_message(prompt)
                texto_resp = response.text
                
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
                        
            except Exception as e:
                # Si es un error de cuota (429), lo decimos claro
                if "429" in str(e):
                    st.warning("⏳ El sistema está ocupado. Espera 1 minuto.")
                else:
                    st.error(f"Error técnico: {e}")
    else:
        st.error("⚠️ No se pudo conectar. Verifica tu API Key.")
