import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- 1. CONFIGURACIÓN INSTITUCIONAL ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. RUTAS DE IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. DISEÑO VISUAL ---
st.markdown(f"""
    <style>
        .header-box {{
            text-align: center;
            padding: 1.5rem;
            background-color: #f8fafc;
            border-radius: 20px;
            border-bottom: 6px solid #1e3a8a;
            margin-bottom: 2rem;
        }}
        .school-name {{
            color: #1e3a8a;
            font-size: 1.8rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-top: 10px;
        }}
    </style>
    <div class="header-box">
        <img src="{URL_ESCUDO}" width="120">
        <div class="school-name">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p style="color: #64748b;">Bienvenido al Portal de Orientación Escolar</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("Configuración")
    modo_voz = st.toggle("Activar Voz y Avatar", value=True)
    st.divider()
    st.info("Asistente Virtual para la comunidad estudiantil.")

# --- 5. LÓGICA DEL AVATAR ---
def mostrar_avatar(audio_bytes):
    b64_audio = base64.b64encode(audio_bytes.read()).decode()
    html = f"""
    <div style="text-align: center; background: white; padding: 15px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <div style="position: relative; width: 200px; height: 260px; margin: 0 auto;">
            <div style="position: absolute; width: 100%; height: 100%; background: url('{URL_CERRADA}') center/contain no-repeat;"></div>
            <div id="mouth" style="position: absolute; width: 100%; height: 100%; background: url('{URL_ABIERTA}') center/contain no-repeat; opacity: 0; transition: opacity 0.1s;"></div>
        </div>
        <audio id="aud" autoplay style="display:none"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>
        <button id="btn" onclick="document.getElementById('aud').play()" style="display:none; width: 100%; padding: 10px; background: #1e3a8a; color: white; border: none; border-radius: 10px; margin-top: 10px; cursor: pointer;">🔊 ESCUCHAR</button>
    </div>
    <script>
        var a = document.getElementById("aud"), m = document.getElementById("mouth"), b = document.getElementById("btn"), i;
        a.onplay = () => {{ b.style.display="none"; i = setInterval(() => {{ m.style.opacity = m.style.opacity=="0"?"1":"0" }}, 200); }};
        a.onpause = a.onended = () => {{ clearInterval(i); m.style.opacity="0"; }};
        a.play().catch(() => {{ b.style.display="block"; }});
    </script>
    """
    st.components.v1.html(html, height=350)

# --- 6. CONEXIÓN INTELIGENTE (EL ARREGLO DEL ERROR 404) ---
@st.cache_resource
def conectar_ia():
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Lista de modelos por orden de preferencia
    modelos_a_probar = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-pro']
    
    for nombre in modelos_a_probar:
        try:
            m = genai.GenerativeModel(nombre)
            # Prueba rápida
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = conectar_ia()

if not model:
    st.error("Error crítico: No se pudo conectar con ningún modelo de IA. Revisa tu API Key.")
    st.stop()

# --- 7. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                contexto = "Eres el Orientador de la I.E.R. Hugues Manuel Lacouture. Sé empático y breve (máx 2 frases). "
                r = model.generate_content(contexto + prompt)
                respuesta_texto = r.text
                st.markdown(respuesta_texto)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_texto})
                
                if modo_voz:
                    tts = gTTS(text=respuesta_texto, lang='es')
                    b = BytesIO()
                    tts.write_to_fp(b)
                    b.seek(0)
                    with st.sidebar:
                        mostrar_avatar(b)
            except Exception as e:
                st.error(f"Error: {e}")
