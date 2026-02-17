import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components 

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. RECURSOS (IMÁGENES) ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. ESTILOS CSS ---
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
        /* Botón Flotante de WhatsApp */
        .boton-flotante {
            position: fixed;
            bottom: 100px;
            right: 20px;
            background-color: #25d366;
            color: white !important;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: sans-serif;
            font-weight: bold;
            transition: transform 0.3s;
        }
        .boton-flotante:hover {
            background-color: #128c7e;
            transform: scale(1.05);
        }
        @media (max-width: 600px) {
            .title-text { font-size: 18px; }
            .boton-flotante { bottom: 80px; right: 10px; padding: 10px 20px; }
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado visible
st.markdown(f"""
    <div class="header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="title-text">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p>🎓 Portal de Orientación Escolar</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.info("Sistema exclusivo para estudiantes.\nPotenciado por Gemini AI.")

# --- 5. LÓGICA DEL AVATAR (HTML/JS) ---
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

# --- 6. CONEXIÓN INTELIGENTE A GEMINI (SOLUCIÓN AL ERROR 404) ---
@st.cache_resource
def configurar_modelo():
    """Configura y devuelve el mejor modelo disponible."""
    try:
        # 1. Autenticación
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 2. Buscar modelos disponibles
        modelos_disponibles = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponibles.append(m.name)
        except Exception as e:
            st.error(f"Error al listar modelos: {e}")
            return None

        # 3. Selección de prioridad (1.5 Pro > Pro > Flash)
        modelo_seleccionado = None
        
        # Prioridad 1: Gemini 1.5 Pro
        for m in modelos_disponibles:
            if "gemini-1.5-pro" in m:
                modelo_seleccionado = m
                break
        
        # Prioridad 2: Gemini 1.5 Flash (Muy bueno y rápido)
        if not modelo_seleccionado:
            for m in modelos_disponibles:
                if "gemini-1.5-flash" in m:
                    modelo_seleccionado = m
                    break

        # Prioridad 3: Gemini Pro Clásico
        if not modelo_seleccionado:
            for m in modelos_disponibles:
                if "gemini-pro" in m:
                    modelo_seleccionado = m
                    break
        
        # Fallback final
        if not modelo_seleccionado and modelos_dis
