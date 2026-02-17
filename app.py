import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual 3D", page_icon="🤖", layout="wide")

# --- URLs DE LOS AVATARES (PUEDES CAMBIARLAS) ---
# Busca una imagen quieta y un GIF que parezca el mismo robot hablando
AVATAR_QUIETO = "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
# Este es un GIF de ejemplo de un robot con luces parpadeando
AVATAR_HABLANDO = "https://i.pinimg.com/originals/a1/46/36/a146364e0ea9cd972fb60989a8dd8296.gif"

# --- GESTIÓN DE ESTADO DEL AVATAR ---
# Inicializamos una variable para saber si el robot debe moverse o no
if "esta_hablando" not in st.session_state:
    st.session_state.esta_hablando = False

# --- BARRA LATERAL (AVATAR DINÁMICO) ---
with st.sidebar:
    st.title("Tu Consejero Virtual")
    
    # AQUÍ ESTÁ EL TRUCO VISUAL:
    # Si el estado dice que está hablando, mostramos el GIF. Si no, la imagen quieta.
    if st.session_state.esta_hablando:
        st.image(AVATAR_HABLANDO, width=180, caption="Respondiendo... 🗣️")
    else:
        st.image(AVATAR_QUIETO, width=180, caption="Escuchando... 👂")
    
    st.divider()
    
    # SELECTOR DE MODO
    modo = st.radio("Opciones de respuesta:", ["Solo Texto 📝", "Voz Automática 🔊"], index=1)
    
    st.info("ℹ️ El modo 'Voz Automática' leerá la respuesta y animará al avatar.")

# --- TÍTULO PRINCIPAL ---
st.title("🤖 Espacio de Escucha Interactivo")
st.markdown("---")

# --- CONEXIÓN ---
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
1. Respuestas MUY CORTAS (máximo 3 frases) para que el audio no sea eterno.
2. Tono cálido y comprensivo.
3. SI DETECTAS PELIGRO (suicidio, abuso, armas):
   RESPONDE: "🚨 Siento mucho esto. Es muy delicado. Busca AHORA MISMO a un profesor o llama a la línea 123. No estás solo."
"""

# --- FUNCIÓN PARA GENERAR AUDIO ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0) # Rebobinar el buffer antes de leerlo
        return audio_buffer
    except Exception as e:
        st.error(f"No pude generar el audio: {e}")
        return None

# --- TRUCO HTML PARA AUTOPLAY (Reproducción automática) ---
def reproducir_autoplay(audio_bytes):
    # Convertimos el audio a una cadena de texto base64 para meterlo en HTML
    b64 = base64.b64encode(audio_bytes.read()).decode()
    # Creamos un reproductor de audio oculto que se activa solo
    md = f"""
        <audio controls autoplay style="width: 100%;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.querySelector('audio');
            audio.play().catch(function(error) {{
                console.log("El navegador bloqueó el autoplay hasta que el usuario interactúe.");
            }});
        </script>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INTERACCIÓN PRINCIPAL ---
if texto := st.chat_input("Escribe aquí lo que sientes..."):
    # 1. Usuario envía mensaje
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # 2. ACTIVAMOS EL MODO "HABLANDO" antes de generar
    st.session_state.esta_hablando = True
    st.rerun() # Recargamos la página para que el avatar cambie a GIF

# Esta parte se ejecuta después de que la página se recarga y 'esta_hablando' es True
if st.session_state.esta_hablando and st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    try:
        with st.spinner("Procesando respuesta..."):
            # Recuperamos el último mensaje del usuario
            ultimo_texto = st.session_state.mensajes[-1]["content"]
            
            chat = model.start_chat(history=[])
            prompt_final = f"{instrucciones_seguridad}\n\nMensaje del alumno: {ultimo_texto}"
            
            respuesta = chat.send_message(prompt_final)
            texto_respuesta = respuesta.text
            
            # Guardar respuesta
            st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})
        
        # Mostrar respuesta
        with st.chat_message("assistant"):
            st.markdown(texto_respuesta)
            
            # LÓGICA DE AUDIO AUTOPLAY
            if "Voz" in modo:
                audio_data = texto_a_audio(texto_respuesta)
                if audio_data:
                    # Usamos el truco de HTML para autoplay
                    reproducir_autoplay(audio_data)
        
        # 3. FINALIZAMOS EL MODO "HABLANDO"
        st.session_state.esta_hablando = False
        # No hacemos rerun aquí para dejar que el audio termine de cargar en el navegador

    except Exception as e:
        st.error(f"❌ Ocurrió un error: {e}")
        st.session_state.esta_hablando = False
        st.rerun()
