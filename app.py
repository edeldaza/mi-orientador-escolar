import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Orientador Escolar",
    page_icon="🎓",
    layout="centered"
)

# --- TÍTULO ---
st.title("🎓 Espacio de Escucha Escolar")
st.markdown("""
    Bienvenido. Soy un asistente virtual diseñado para escucharte y apoyarte.
    
    ⚠️ **Recordatorio:** Soy una Inteligencia Artificial. 
    **Si estás en peligro, busca a un profesor o adulto inmediatamente.**
""")

# --- CONEXIÓN CON LA IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # VOLVEMOS AL MODELO ESTÁNDAR (Ahora sí funcionará con tu actualización)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error("⚠️ Error de conexión con Google.")
    st.stop()

# --- CEREBRO DEL ORIENTADOR ---
instrucciones = """
ROL: Eres un consejero escolar empático para estudiantes.
TONO: Amable, cercano y motivador.

REGLAS DE ORO:
1. Si el alumno habla de suicidio, autolesiones, violencia o abuso:
   RESPONDE EXACTAMENTE: "🚨 Lo que me cuentas es muy serio y delicado. Por favor, no te guardes esto. Busca AHORA MISMO a tu profesor titular o llama a la línea de ayuda 123. No estás solo/a."
2. Para otros temas (estudio, amigos, estrés): Escucha y da un consejo breve.
"""

# --- CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

if texto_alumno := st.chat_input("Cuéntame, ¿cómo te sientes?"):
    
    st.session_state.mensajes.append({"role": "user", "content": texto_alumno})
    with st.chat_message("user"):
        st.markdown(texto_alumno)

    try:
        chat = model.start_chat(history=[])
        prompt = f"Instrucciones: {instrucciones}\n\nMensaje alumno: {texto_alumno}"
        
        respuesta = chat.send_message(prompt)
        
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
            
    except Exception as e:
        # Si falla el 1.5, intentamos con el modelo "Pro" automáticamente
        try:
            model_backup = genai.GenerativeModel('gemini-pro')
            respuesta = model_backup.generate_content(f"Instrucciones: {instrucciones}\n\nMensaje: {texto_alumno}")
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
            with st.chat_message("assistant"):
                st.markdown(respuesta.text)
        except:
            st.error("El sistema está saturado en este momento. Intenta en 1 minuto.")
