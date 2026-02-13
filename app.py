import streamlit as st
import os
import subprocess
import sys

# --- TRUCO DE REPARACIÓN AUTOMÁTICA ---
# Esto obliga al servidor a actualizar la librería SI O SI
try:
    import google.generativeai as genai
    version_actual = genai.__version__
except ImportError:
    version_actual = "0.0.0"

# Si la versión es vieja (menor a 0.8.0), forzamos la instalación
if version_actual < "0.8.0":
    print(f"⚠️ Versión vieja detectada ({version_actual}). Actualizando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai"])
    # Reiniciamos la app para que tome el cambio
    st.rerun()

# --- AHORA SÍ, EL CÓDIGO NORMAL ---
import google.generativeai as genai

# Configuración de página
st.set_page_config(page_title="Orientador Escolar", page_icon="🎓")

st.title("🎓 Espacio de Escucha Escolar")
st.caption(f"Estado del sistema: Conectado (v{genai.__version__})") # Esto nos confirmará que se arregló

st.markdown("""
    Bienvenido. Soy un asistente virtual diseñado para escucharte y orientarte.
    ⚠️ **Importante:** Soy una IA, no un humano. Si estás en peligro, busca a un profesor inmediatamente.
""")

# Conexión con la IA
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Usamos el modelo Flash que es rápido y gratuito
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# Instrucciones
instrucciones = """
Eres un orientador escolar amable y empático.
1. Escucha activamente.
2. Da consejos cortos y prácticos.
3. SEGURIDAD: Si mencionan suicidio, abuso o violencia, responde:
   "🚨 Esta situación requiere ayuda humana urgente. Habla con tu profesor o llama a la línea 123."
"""

# Chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

if texto_alumno := st.chat_input("Cuéntame, ¿cómo te sientes hoy?"):
    st.session_state.mensajes.append({"role": "user", "content": texto_alumno})
    with st.chat_message("user"):
        st.markdown(texto_alumno)

    try:
        chat = model.start_chat(history=[])
        prompt = f"Instrucciones: {instrucciones}\n\nMensaje: {texto_alumno}"
        respuesta = chat.send_message(prompt)
        
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
    except Exception as e:
        st.error(f"Error al responder: {e}")
