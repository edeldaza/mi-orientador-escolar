import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Orientador Escolar",
    page_icon="🎓",
    layout="centered"
)

# --- TÍTULO Y ADVERTENCIA ---
st.title("🎓 Espacio de Escucha Escolar")
st.markdown("""
    Bienvenido. Soy un asistente virtual diseñado para escucharte, apoyarte y orientarte.
    
    ⚠️ **Importante:** Soy una Inteligencia Artificial, no un humano. 
    **Si estás en peligro, busca a un profesor o adulto de confianza inmediatamente.**
""")

# --- CONEXIÓN CON LA IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # ¡AQUÍ ESTÁ EL CAMBIO! Usamos el modelo que sí tienes en tu lista
    model = genai.GenerativeModel('gemini-2.0-flash')
    
except Exception as e:
    st.error("⚠️ Error de conexión. Verifica tu API Key en los 'Secrets' de Streamlit.")
    st.stop()

# --- CEREBRO DEL ORIENTADOR (Instrucciones) ---
instrucciones_sistema = """
ROL: Eres un consejero escolar empático, amable y cercano para estudiantes de un colegio de bajos recursos.
TONO: Cálido, comprensivo, juvenil pero respetuoso. No uses palabras complicadas.

REGLAS DE SEGURIDAD (OBLIGATORIAS):
1. TU PRIORIDAD ES LA SEGURIDAD DEL ESTUDIANTE.
2. Si el estudiante menciona: SUICIDIO, AUTOLESIONES (cortarse), ABUSO SEXUAL, VIOLENCIA FÍSICA GRAVE o ARMAS:
   - DEBES DEJAR DE DAR CONSEJOS.
   - Responde EXACTAMENTE con esto: 
     "🚨 Siento mucho que estés pasando por esto. Es una situación muy delicada y NO debes enfrentarla solo/a. Por favor, acércate AHORA MISMO a un profesor de confianza o llama a la línea de ayuda 123. Yo soy una IA y no puedo protegerte físicamente, pero un humano sí."

3. Para problemas normales (exámenes, peleas con amigos, tristeza):
   - Escucha primero.
   - Valida sus sentimientos ("Entiendo que te sientas así...").
   - Da un consejo pequeño y práctico.
"""

# --- GESTIÓN DEL CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# --- INTERACCIÓN ---
if texto_alumno := st.chat_input("Cuéntame, ¿qué te preocupa hoy?"):
    
    # 1. Mostrar mensaje del alumno
    st.session_state.mensajes.append({"role": "user", "content": texto_alumno})
    with st.chat_message("user"):
        st.markdown(texto_alumno)

    # 2. Generar respuesta
    try:
        # Preparamos el chat
        chat = model.start_chat(history=[])
        
        # Enviamos instrucciones + mensaje
        prompt_completo = f"INSTRUCCIONES DEL SISTEMA: {instrucciones_sistema}\n\nMENSAJE DEL ALUMNO: {texto_alumno}"
        
        respuesta = chat.send_message(prompt_completo)
        
        # 3. Mostrar respuesta de la IA
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
            
    except Exception as e:
        st.error(f"Lo siento, hubo un error de conexión. Intenta de nuevo. (Error: {e})")
