import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
# Layout "wide" ayuda en PC, pero en móviles se adapta solo.
st.set_page_config(page_title="Orientador Virtual", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES DE GITHUB ---
AVATAR_QUIETO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
AVATAR_HABLANDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- GESTIÓN DE ESTADO ---
if "esta_hablando" not in st.session_state:
    st.session_state.esta_hablando = False

# --- BARRA LATERAL (AVATAR RESPONSIVO) ---
with st.sidebar:
    st.title("Tu Consejero Virtual")
    
    # LÓGICA DEL AVATAR:
    # 'use_container_width=True' hace que la imagen se adapte al ancho del dispositivo
    if st.session_state.esta_hablando:
        st.image(AVATAR_HABLANDO, caption="Respondiendo...", use_container_width=True)
    else:
        st.image(AVATAR_QUIETO, caption="Escuchando...", use_container_width=True)
    
    st.divider()
    
    # SELECTOR DE MODO
    # Le puse iconos para que sea más amigable en móviles
    modo = st.radio("Configuración:", ["Solo Texto 📝", "Voz Automática 🗣️"], index=1)
    
    st.info("ℹ️ En celulares, asegúrate de no tener el teléfono en 'Silencio' para escuchar.")

# --- TÍTULO PRINCIPAL ---
st.title("🤖 Espacio de Escucha Escolar")
st.markdown("---")

# --- CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- INSTRUCCIONES DE SEGURIDAD ---
instrucciones_seguridad = """
Actúa como un orientador escolar empático y juvenil.
1. Respuestas MUY CORTAS (máximo 2 párrafos) para que el audio sea rápido.
2. Tono cálido y comprensivo.
3. SI DETECTAS PELIGRO (suicidio, abuso, armas):
   RESPONDE: "🚨 Siento mucho esto. Es muy delicado. Busca AHORA MISMO a un profesor o llama a la línea 123. No estás solo."
"""

# --- FUNCIÓN DE AUDIO ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        st.error(f"Error de audio: {e}")
        return None

# --- REPRODUCTOR AUTOPLAY (INVISIBLE) ---
def reproducir_autoplay(audio_bytes):
    b64 = base64.b64encode(audio_bytes.read()).decode()
    md = f"""
        <audio controls autoplay style="display:none">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.querySelector('audio');
            audio.play().catch(error => {{
                console.log("Autoplay bloqueado por el navegador.");
            }});
        </script>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- HISTORIAL DE CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INTERACCIÓN ---
if texto := st.chat_input("Escribe aquí lo que sientes..."):
    # 1. Guardar usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # 2. Activar animación (Recarga rápida)
    st.session_state.esta_hablando = True
    st.rerun()

# --- RESPUESTA IA (Tras recarga) ---
if st.session_state.esta_hablando and st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    try:
        with st.spinner("Pensando... 💭"):
            ultimo_texto = st.session_state.mensajes[-1]["content"]
            
            chat = model.start_chat(history=[])
            prompt_final = f"{instrucciones_seguridad}\n\nMensaje del alumno: {ultimo_texto}"
            
            respuesta = chat.send_message(prompt_final)
            texto_respuesta = respuesta.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})
        
        with st.chat_message("assistant"):
            st.markdown(texto_respuesta)
            
            # AUDIO
            if "Voz" in modo:
                audio_data = texto_a_audio(texto_respuesta)
                if audio_data:
                    reproducir_autoplay(audio_data)
        
        # Desactivar animación
        st.session_state.esta_hablando = False

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.session_state.esta_hablando = False
        st.rerun()
