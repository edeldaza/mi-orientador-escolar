import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🎓")
st.title("🎓 Espacio de Escucha Escolar")
st.markdown("Bienvenido. Soy una IA diseñada para escucharte y orientarte.")
st.warning("⚠️ Recuerda: No soy humano. Si estás en peligro, busca a un profesor.")

# --- CONEXIÓN ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # CORRECCIÓN AQUÍ: Usamos el nombre que SÍ aparece en tu lista
    model = genai.GenerativeModel('gemini-flash-latest')
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if texto := st.chat_input("Cuéntame, ¿cómo te sientes?"):
    # Guardar mensaje usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # Respuesta IA
    try:
        chat = model.start_chat(history=[])
        prompt = f"Actúa como un orientador escolar empático. Mensaje del alumno: {texto}"
        
        respuesta = chat.send_message(prompt)
        
        # Guardar respuesta IA
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
            
    except Exception as e:
        st.error(f"❌ Error: {e}")
