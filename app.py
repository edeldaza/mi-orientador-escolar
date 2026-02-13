import streamlit as st
import google.generativeai as genai
import os

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Orientador Escolar", page_icon="🎓")

st.title("🎓 Espacio de Escucha Escolar")
st.write("Bienvenido. Soy un asistente virtual diseñado para escucharte y orientarte.")
st.info("⚠️ Recuerda: Soy una IA, no un humano. Si estás en peligro, busca a un profesor inmediatamente.")

# CONEXIÓN CON LA IA (SECRETA)
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# INSTRUCCIONES DE PERSONALIDAD (PROMPT)
instrucciones = """
Eres un orientador escolar amable y empático para jóvenes de bajos recursos.
1. Escucha activamente y valida sus emociones.
2. Da consejos cortos y prácticos.
3. IMPORTANTE: Si detectas ideas suicidas, abuso o violencia grave, responde SOLO con:
   "🚨 Esta situación es muy delicada y necesitas ayuda humana urgente. Por favor, habla ya mismo con tu profesor o llama a la línea 123."
"""

# CHAT
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# MOSTRAR CHAT EN PANTALLA
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# CAPTURAR TEXTO DEL ALUMNO
if texto_alumno := st.chat_input("Escribe aquí lo que sientes..."):
    # Guardar mensaje del alumno
    st.session_state.mensajes.append({"role": "user", "content": texto_alumno})
    with st.chat_message("user"):
        st.markdown(texto_alumno)

    # Generar respuesta
    try:
        chat = model.start_chat(history=[])
        respuesta = chat.send_message(f"Instrucciones del sistema: {instrucciones}. Mensaje alumno: {texto_alumno}")
        
        # Mostrar respuesta
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
    except Exception as e:
        st.error("Hubo un error de conexión. Intenta de nuevo.")
