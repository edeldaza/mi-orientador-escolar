import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. IMÁGENES DEL COLEGIO ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. DISEÑO INSTITUCIONAL (CSS) ---
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 20px;
            border-bottom: 5px solid #003366; /* Azul Institucional */
        }
        .school-title {
            color: #003366;
            font-size: 28px;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOSTRAR ENCABEZADO ---
st.markdown(f"""
    <div class="main-header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="school-title">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <div class="subtitle">🎓 Portal de Orientación Escolar 🎓</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.info("Espacio seguro para estudiantes.")

# --- 6. FUNCIÓN AVATAR (Audio + Animación) ---
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

        <button id="btn_play" onclick="document.getElementById('player').play()" 
                style="display: none; margin-top: 10px; width: 100%; padding: 8px; background: #003366; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🔊 REPRODUCIR RESPUESTA
        </button>
    </div>

    <script>
        var player = document.getElementById("player");
        var mouth = document.getElementById("mouth");
        var btn = document.getElementById("btn_play");
        var interval;

        // 1. Al reproducir -> Animar boca
        player.onplay = function() {{
            btn.style.display = "none";
            interval = setInterval(function() {{
                mouth.style.opacity = (mouth.style.opacity == "0" ? "1" : "0");
            }}, 200);
        }};

        // 2. Al terminar -> Parar animación
        player.onended = function() {{ clearInterval(interval); mouth.style.opacity = "0"; }};
        player.onpause = function() {{ clearInterval(interval); mouth.style.opacity = "0"; }};

        // 3. Autoplay seguro
        player.play().catch(function(error) {{
            // Si el navegador bloquea el audio, mostramos el botón
            btn.style.display = "block";
        }});
    </script>
    """
    return html

# --- 7. CONEXIÓN INTELIGENTE A GOOGLE AI ---
def conectar_ia():
    try:
        # Recuperamos la llave de los Secrets (¡TU CONFIGURACIÓN!)
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # INTENTO 1: Modelo Flash (Rápido y Gratis)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Prueba silenciosa de conexión
            model.generate_content("test", generation_config={"max_output_tokens": 1})
            return model
        except:
            # INTENTO 2: Modelo Pro (Respaldo compatible)
            return genai.GenerativeModel('gemini-pro')
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

model = conectar_ia()

# --- 8. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Hola, ¿cómo estás?"):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 9. RESPUESTA Y AUDIO ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    if model:
        with st.spinner("El orientador está pensando..."):
            try:
                chat = model.start_chat(history=[])
                prompt_sistema = f"""
                Actúa como el Orientador Escolar de la Institución Educativa Rural Hugues Manuel Lacouture.
                Responde de forma breve, empática y clara (máximo 2 frases).
                Si detectas riesgo (suicidio, abuso, violencia), indica buscar ayuda urgente de un adulto.
                Mensaje del alumno: {st.session_state.mensajes[-1]['content']}
                """
                
                respuesta = chat.send_message(prompt_sistema)
                texto_resp = respuesta.text
                
                st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
                with st.chat_message("assistant"):
                    st.markdown(texto_resp)
                
                # Generar Audio y Avatar
                if modo_voz:
                    tts = gTTS(text=texto_resp, lang='es')
                    audio_buffer = BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    
                    html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                    with st.sidebar:
                        st.components.v1.html(html_avatar, height=320)
                        
            except Exception as e:
                st.error("Lo siento, estoy recibiendo muchas consultas. Intenta de nuevo en un momento.")
