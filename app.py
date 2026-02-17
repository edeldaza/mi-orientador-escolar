import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components 

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

# --- 6. CONEXIÓN INTELIGENTE ---
def obtener_modelo_disponible():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        lista_modelos = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    lista_modelos.append(m.name)
        except:
            return genai.GenerativeModel('gemini-pro')

        modelo_a_usar = ""
        
        for m in lista_modelos:
            if 'flash' in m:
                modelo_a_usar = m
                break
        
        if not modelo_a_usar:
            for m in lista_modelos:
                if 'pro' in m:
                    modelo_a_usar = m
                    break
                    
        if not modelo_a_usar and lista_modelos:
            modelo_a_usar = lista_modelos[0]

        if modelo_a_usar:
            return genai.GenerativeModel(modelo_a_usar)
        else:
            return None

    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

model = obtener_modelo_disponible()

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
                        components.html(html_avatar, height=320)
                        
            except Exception as e:
                st.error(f"Ocurrió un error técnico: {e}")
    else:
        st.error("⚠️ No se encontró ningún modelo de IA disponible. Verifica tu API Key o intenta más tarde.")


# --- 9. BOTÓN FLOTANTE DE WHATSAPP (CORREGIDO) ---
def boton_whatsapp():
    # ⚠️ CAMBIA ESTE NÚMERO POR EL TUYO ⚠️
    numero_telefono = "573000000000" 
    
    mensaje = "Hola, necesito orientación escolar."
    url_wa = f"https://wa.me/{numero_telefono}?text={mensaje.replace(' ', '%20')}"
    
    # CSS CORREGIDO: bottom: 90px (para subirlo) y right: 20px (para alinearlo)
    st.markdown(f"""
    <style>
        .boton-flotante {{
            position: fixed;
            width: 55px;
            height: 55px;
            bottom: 90px; /* ANTES 40px, AHORA 90px (Sube para no tapar el chat) */
            right: 20px;  /* ANTES 40px, AHORA 20px (Más pegado a la derecha) */
            background-color: #25d366;
            color: #FFF;
            border-radius: 50px;
            text-align: center;
            box-shadow: 2px 2px 3px #999;
            z-index: 9999; /* Asegura que esté siempre encima */
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        .boton-flotante:hover {{
            background-color: #128c7e;
            transform: scale(1.1);
        }}
    </style>
    <a href="{url_wa}" class="boton-flotante" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="30px" style="filter: brightness(0) invert(1);">
    </a>
    """, unsafe_allow_html=True)

boton_whatsapp()
