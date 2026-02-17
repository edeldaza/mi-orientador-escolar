import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual", page_icon="🎓", layout="wide")

# --- BARRA LATERAL (AVATAR Y CONFIGURACIÓN) ---
with st.sidebar:
    # Puedes cambiar esta URL por la foto de cualquier avatar que te guste
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=150)
    
    st.title("Tu Consejero Virtual")
    st.write("Hola, estoy aquí para escucharte.")
    
    st.divider()
    
    # SELECTOR DE MODO
    modo = st.radio("¿Cómo prefieres mi respuesta?", ["Solo Texto 📝", "Texto y Audio 🗣️"])
    
    st.info("ℹ️ Recuerda: Todo lo que hablamos es confidencial, pero soy una IA.")

# --- TÍTULO PRINCIPAL ---
st.title("🎓 Espacio de Escucha Escolar")
st.markdown("---")

# --- CONEXIÓN (MANTENIENDO LO QUE FUNCIONA) ---
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
1. Respuestas cortas (máximo 2 párrafos).
2. Tono cálido y comprensivo.
3. SI DETECTAS PELIGRO (suicidio, abuso, armas):
   RESPONDE: "🚨 Siento mucho que pases por esto. Es muy delicado para una IA. Por favor, busca AHORA MISMO a un profesor o llama a la línea 123. No estás solo."
"""

# --- FUNCIÓN PARA GENERAR AUDIO ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es') # 'es' es español
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        return audio_buffer
    except Exception as e:
        st.error(f"No pude generar el audio: {e}")
        return None

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INTERACCIÓN ---
if texto := st.chat_input("Escribe aquí lo que sientes..."):
    # 1. Guardar y mostrar mensaje del alumno
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # 2. Generar respuesta IA
    try:
        chat = model.start_chat(history=[])
        prompt_final = f"{instrucciones_seguridad}\n\nMensaje del alumno: {texto}"
        
        respuesta = chat.send_message(prompt_final)
        texto_respuesta = respuesta.text
        
        # 3. Guardar y mostrar respuesta
        st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})
        with st.chat_message("assistant"):
            st.markdown(texto_respuesta)
            
            # 4. LOGICA DE AUDIO (SI ESTÁ ACTIVADO)
            if "Audio" in modo:
                with st.spinner("Generando voz... 🔊"):
                    audio_data = texto_a_audio(texto_respuesta)
                    if audio_data:
                        st.audio(audio_data, format="audio/mp3")
            
    except Exception as e:
        st.error(f"❌ Ocurrió un error: {e}")
