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
            border-bottom: 5px solid #1E3A8A; /* Línea azul institucional */
        }
        .titulo-colegio {
            color: #1E3A8A;
            font-family: sans-serif;
            font-weight: 900;
            font-size: 2rem;
            text-transform: uppercase;
            margin-top: 10px;
        }
        .subtitulo {
            color: #555;
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOSTRAR ENCABEZADO ---
st.markdown(f"""
    <div class="encabezado">
        <img src="{URL_ESCUDO}" width="120">
        <div class="titulo-colegio">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <div class="subtitulo">🎓 Orientación Escolar Virtual 🎓</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz y Animación", value=True)
    st.info("ℹ️ Sistema exclusivo para estudiantes de la I.E.R. Hugues Manuel Lacouture.")

# --- 6. FUNCIÓN AVATAR (AUDIO + ANIMACIÓN) ---
def mostrar_avatar_con_audio(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        
        <div style="position: relative; width: 200px; height: 260px;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;">
            </div>
            <div id="boca" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;">
            </div>
        </div>

        <audio id="player" controls autoplay style="width: 200px; margin-top: 10px; display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>

        <button id="btn" onclick="document.getElementById('player').play()" 
                style="display: none; margin-top: 10px; padding: 10px 20px; background: #1E3A8A; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
            🔊 ESCUCHAR RESPUESTA
        </button>
    </div>

    <script>
        var player = document.getElementById("player");
        var boca = document.getElementById("boca");
        var btn = document.getElementById("btn");
        var intervalo;

        player.onplay = function() {{
            btn.style.display = "none";
            intervalo = setInterval(() => {{ boca.style.opacity = (boca.style.opacity == "0" ? "1" : "0"); }}, 200);
        }};
        
        player.onpause = function() {{ clearInterval(intervalo); boca.style.opacity = "0"; }};
        player.onended = function() {{ clearInterval(intervalo); boca.style.opacity = "0"; }};

        // Autoplay seguro
        player.play().catch(e => {{ btn.style.display = "block"; }});
    </script>
    """
    return html

# --- 7. CONEXIÓN IA (AQUÍ ESTÁ EL ARREGLO) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # --- CAMBIO IMPORTANTE: MODELO ESTABLE ---
    # Usamos 'gemini-1.5-flash' que tiene mejor capa gratuita y es más rápido
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error("Error de conexión. Verifica tu API Key.")
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
            Tu tono es empático, profesional y cercano.
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
                
                html_avatar = mostrar_avatar_con_audio(texto_resp, audio_buffer)
                
                # Mostrar en barra lateral
                with st.sidebar:
                    st.components.v1.html(html_avatar, height=350)
            
        except Exception as e:
            # Si vuelve a salir error de cuota, mostramos un mensaje amable
            if "429" in str(e):
                st.error("⚠️ El sistema está recibiendo muchas consultas. Por favor espera 1 minuto.")
            else:
                st.error(f"Error: {e}")
