import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🎓")
st.title("🎓 Espacio de Escucha Escolar")
st.markdown("Bienvenido. Soy una IA diseñada para escucharte y orientarte.")
st.warning("⚠️ Recuerda: No soy humano. Si estás en peligro, busca a un profesor.")

# --- CONEXIÓN (LA QUE FUNCIONA) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # MANTENEMOS TU MODELO GANADOR:
    model = genai.GenerativeModel('gemini-flash-latest')
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- INSTRUCCIONES DE SEGURIDAD (AGREGADAS) ---
# Esto es vital para que la IA sepa qué hacer en casos graves
instrucciones_seguridad = """
Actúa como un orientador escolar empático.
TUS REGLAS:
1. Escucha y da consejos cortos y amables.
2. IMPORTANTE: Si el alumno menciona suicidio, autolesiones, abuso o violencia, 
   TU RESPUESTA DEBE SER: "🚨 Lo siento, pero esta situación es muy delicada para una IA. Por favor, busca AHORA MISMO a un profesor o llama a la línea de emergencias. No estás solo."
"""

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
        
        # Aquí combinamos las instrucciones con el mensaje del alumno
        prompt_final = f"{instrucciones_seguridad}\n\nMensaje del alumno: {texto}"
        
        respuesta = chat.send_message(prompt_final)
        
        # Guardar respuesta IA
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
            
    except Exception as e:
        st.error(f"❌ Error: {e}")
