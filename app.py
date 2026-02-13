import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Orientador Escolar",
    page_icon="🎓",
    layout="centered"
)

# --- TÍTULO Y ADVERTENCIA LEGAL ---
st.title("🎓 Espacio de Escucha Escolar")
st.markdown("""
    *Bienvenido. Este es un espacio seguro para expresarte.*
    
    ⚠️ **Importante:** Soy una Inteligencia Artificial, no un humano. 
    **Si estás en peligro inmediato, por favor busca a un profesor o adulto de confianza.**
""")

# --- CONEXIÓN CON LA IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Usamos el modelo Flash: es el más rápido y eficiente para chat
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error de conexión. Verifica la API Key.")
    st.stop()

# --- PERSONALIDAD DEL ORIENTADOR (SYSTEM PROMPT) ---
instrucciones = """
ROL: Eres un consejero escolar virtual para una institución educativa.
TONO: Empático, paciente, juvenil pero respetuoso. Nunca juzgues.

PROTOCOLOS DE SEGURIDAD (ESTRICTO):
1. Si el alumno menciona SUICIDIO, AUTOLESIONES, ABUSO o VIOLENCIA:
   - DEBES responder con este mensaje exacto: 
     "🚨 Siento mucho que estés pasando por esto. Es una situación muy delicada y necesitas apoyo humano real. Por favor, acércate YA MISMO al profesor titular o llama a la línea de ayuda 123. No estás solo/a."
   - NO intentes solucionar tú la crisis.
   
2. Para problemas académicos o sociales:
   - Escucha primero.
   - Valida la emoción ("Entiendo que te sientas frustrado...").
   - Da un consejo breve y práctico.
"""

# --- GESTIÓN DEL CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# --- INTERACCIÓN ---
if texto_alumno := st.chat_input("Escribe aquí lo que sientes..."):
    
    # 1. Guardar mensaje del alumno
    st.session_state.mensajes.append({"role": "user", "content": texto_alumno})
    with st.chat_message("user"):
        st.markdown(texto_alumno)

    # 2. Generar respuesta
    try:
        chat = model.start_chat(history=[])
        prompt_final = f"Instrucciones del sistema: {instrucciones}\n\nMensaje del alumno: {texto_alumno}"
        
        respuesta = chat.send_message(prompt_final)
        
        # 3. Guardar respuesta de la IA
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
            
    except Exception as e:
        st.error(f"Hubo un error momentáneo. Por favor intenta de nuevo. (Error: {e})")
