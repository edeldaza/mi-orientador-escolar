import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Orientación I.E.R. Hugues Manuel Lacouture", page_icon="🎓", layout="wide")

# --- IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- ENCABEZADO ---
st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #f4f6f9; border-bottom: 5px solid #003366; margin-bottom: 20px; border-radius: 15px;">
        <img src="{URL_ESCUDO}" width="100">
        <h2 style="color: #003366; text-transform: uppercase;">Institución Educativa Rural<br>Hugues Manuel Lacouture</h2>
        <p>🎓 Portal de Orientación Escolar 🎓</p>
    </div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.divider()
    
    # --- ZONA DE DIAGNÓSTICO (ESTO TE DIRÁ QUÉ PASA) ---
    st.write("🔍 **Diagnóstico de Modelos:**")
    model_name_used = "Ninguno"

# --- LÓGICA DE CONEXIÓN "DETECTIVE" ---
def get_working_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 1. PREGUNTAR A GOOGLE QUÉ MODELOS TIENE
        all_models = list(genai.list_models())
        
        # 2. FILTRAR LOS QUE SIRVEN PARA CHAT
        chat_models = []
        for m in all_models:
            if 'generateContent' in m.supported_generation_methods:
                chat_models.append(m.name)
        
        # Mostrar lista en sidebar para debug
        with st.sidebar:
            st.code(chat_models)

        # 3. ELEGIR EL MEJOR DISPONIBLE
        # Buscamos 'flash' primero, luego 'pro', luego cualquiera
        chosen = None
        for m in chat_models:
            if 'flash' in m:
                chosen = m
                break
        if not chosen:
            for m in chat_models:
                if 'pro' in m:
                    chosen = m
                    break
        if not chosen and chat_models:
            chosen = chat_models[0] # El primero que haya
            
        return genai.GenerativeModel(chosen), chosen

    except Exception as e:
        st.sidebar.error(f"Error listando: {e}")
        return None, str(e)

# Conectar
model, model_name_used = get_working_model()
with st.sidebar:
    if model:
        st.success(f"✅ Usando: {model_name_used}")
    else:
        st.error("❌ No se encontró ningún modelo.")

# --- AVATAR ---
def mostrar_avatar(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()
    html = f"""
    <div style="background: white; padding: 10px; border-radius: 15px; text-align: center;">
        <div style="position: relative; width: 180px; height: 240px; margin: 0 auto;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;"></div>
            <div id="mouth" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center; opacity: 0; transition: opacity 0.1s;"></div>
        </div>
        <audio id="player" autoplay style="display: none;"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>
    </div>
    <script>
        var p = document.getElementById("player"), m = document.getElementById("mouth"), i;
        p.onplay = () => {{ i = setInterval(() => {{ m.style.opacity = (m.style.opacity == "0" ? "1" : "0"); }}, 200); }};
        p.onended = () => {{ clearInterval(i); m.style.opacity = "0"; }};
        p.play();
    </script>
    """
    return html

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    if model:
        with st.spinner("Pensando..."):
            try:
                chat = model.start_chat(history=[])
                resp = chat.send_message(f"Actúa como orientador escolar empático. Mensaje: {st.session_state.mensajes[-1]['content']}")
                texto_resp = resp.text
                
                st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
                with st.chat_message("assistant"):
                    st.markdown(texto_resp)
                
                if modo_voz:
                    tts = gTTS(text=texto_resp, lang='es')
                    ab = BytesIO()
                    tts.write_to_fp(ab)
                    ab.seek(0)
                    html = mostrar_avatar(texto_resp, ab)
                    with st.sidebar:
                        st.components.v1.html(html, height=320)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("No hay conexión con IA.")
