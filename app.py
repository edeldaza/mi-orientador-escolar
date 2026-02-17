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
        /* Ajuste para móviles */
        @media (max-width: 600px) {
            .title-text { font-size: 18px; }
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="title-text">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p>🎓 Portal de Orientación Escolar - IA Pro 🎓</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.info("Sistema exclusivo para estudiantes.\nPotenciado por Gemini 1.5 Pro.")

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

# --- 6. CONFIGURACIÓN DEL MODELO PRO ---
def configurar_modelo():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # Configuración avanzada para el modelo Pro
        generation_config = {
            "temperature": 0.7,        # Balance entre creatividad y precisión
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192, # Permite respuestas detalladas si es necesario
        }

        # Instrucción del sistema (Define la personalidad de raíz)
        system_instruction = (
            "Eres el Orientador Escolar de la Institución Educativa Rural Hugues Manuel Lacouture. "
            "Tu misión es apoyar a los estudiantes con empatía y claridad. "
            "Responde de manera breve, cálida y útil (máximo 2 o 3 frases)."
        )

        # Inicialización explícita de Gemini 1.5 Pro
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction=system_instruction
        )
        return model

    except Exception as e:
        st.error(f"Error al configurar la IA: {e}")
        return None

model = configurar_modelo()

# --- 7. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Historial visual (UI)
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 8. LÓGICA DE RESPUESTA ---
if texto := st.chat_input("Escribe tu inquietud aquí..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # Generar respuesta
    if model:
        with st.chat_message("assistant"):
            with st.spinner("El orientador está analizando tu caso..."):
                try:
                    # Crear sesión de chat (podrías pasar historial aquí si quisieras memoria continua)
                    # Por ahora lo mantenemos simple (stateless) por petición, pero usando el config Pro
                    chat_session = model.start_chat(history=[])
                    
                    # Ya no necesitamos inyectar el prompt de personalidad aquí, 
                    # porque está en 'system_instruction' arriba.
                    response = chat_session.send_message(texto)
                    texto_resp = response.text
                    
                    st.markdown(texto_resp)
                    st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
                    
                    # Generación de voz
                    if modo_voz:
                        tts = gTTS(text=texto_resp, lang='es')
                        audio_buffer = BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)
                        html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                        with st.sidebar:
                            components.html(html_avatar, height=320)
                            
                except Exception as e:
                    st.error(f"Lo siento, hubo un error de conexión: {e}")
    else:
        st.error("⚠️ El sistema de IA no está disponible en este momento.")


# --- 9. BOTÓN WHATSAPP ---
def boton_whatsapp():
    # ⚠️ RECUERDA: CAMBIA ESTE NÚMERO POR EL TUYO REAL
    numero_telefono = "573000000000" 
    
    mensaje = "Hola, necesito orientación escolar."
    url_wa = f"https://wa.me/{numero_telefono}?text={mensaje.replace(' ', '%20')}"
    
    st.markdown(f"""
    <style>
        .boton-flotante {{
            position: fixed;
            bottom: 120px;
            right: 20px;
            background-color: #25d366;
            color: white !important;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: sans-serif;
            font-weight: bold;
            transition: transform 0.3s;
        }}
        .boton-flotante:hover {{
            background-color: #128c7e;
            transform: scale(1.05);
        }}
        .texto-boton {{ font-size: 16px; }}
    </style>
    
    <a href="{url_wa}" class="boton-flotante" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="25px" style="filter: brightness(0) invert(1);">
        <span class="texto-boton">Ayuda WhatsApp</span>
    </a>
    """, unsafe_allow_html=True)

boton_whatsapp()
