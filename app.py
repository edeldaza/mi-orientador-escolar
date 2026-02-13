import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🎓")

st.title("🎓 Espacio de Escucha Escolar")
st.markdown("""
    Bienvenido. Soy un asistente virtual diseñado para escucharte y orientarte.
    
    ⚠️ **Importante:** Soy una IA, no un humano. Si estás en peligro, busca a un profesor inmediatamente.
""")

# --- CONEXIÓN CON LA IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Error: No se encontró la API Key. Configúrala en 'Secrets'.")
    st.stop()

# --- SELECCIÓN DEL MODELO (INTELIGENTE) ---
# Intentamos usar el modelo rápido. Si falla, avisamos.
nombre_modelo = 'gemini-1.5-flash'
try:
    model = genai.GenerativeModel(nombre_modelo)
except Exception:
    st.error("Error al cargar el modelo. Verifica requirements.txt")

# --- INSTRUCCIONES DE PERSONALIDAD ---
instrucciones = """
Eres un orientador escolar amable y empático para jóvenes de bajos recursos.
1. Escucha activamente y valida sus emociones.
2. Da consejos cortos y prácticos.
3. IMPORTANTE: Si detectas ideas suicidas, abuso o violencia grave, responde SOLO con:
   "🚨 Esta situación es muy delicada y necesitas ayuda humana urgente. Por favor, habla ya mismo con tu profesor o llama a la línea 123."
"""

# --- GESTIÓN DEL HISTORIAL ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- MOSTRAR CHAT EN PANTALLA ---
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# --- CAPTURAR TEXTO DEL ALUMNO ---
if texto_alumno := st.chat_input("Escribe aquí lo que sientes..."):
    
    # 1. Guardar y mostrar mensaje del alumno
    st.session_state.mensajes.append({"role": "user", "content": texto_alumno})
    with st.chat_message("user"):
        st.markdown(texto_alumno)

    # 2. Generar respuesta
    try:
        chat = model.start_chat(history=[])
        # Enviamos instrucciones + mensaje
        prompt_final = f"Instrucciones del sistema: {instrucciones}\n\nMensaje del usuario: {texto_alumno}"
        
        respuesta = chat.send_message(prompt_final)
        
        # 3. Guardar y mostrar respuesta de la IA
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
            
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.info("💡 Si ves un error 404, necesitas actualizar el archivo 'requirements.txt' en GitHub y Reiniciar la App.")
