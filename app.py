import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual", page_icon="🎓", layout="wide")

# --- TUS IMÁGENES DE GITHUB ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- TÍTULO PRINCIPAL ---
st.title("🤖 Espacio de Escucha Escolar")
st.markdown("---")

# --- CONEXIÓN IA ---
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
1. Respuestas MUY CORTAS (máximo 2 párrafos).
2. Tono cálido.
3. SI HAY PELIGRO (suicidio, abuso): "🚨 Siento mucho esto. Busca ayuda urgente con un profesor o llama al 123."
"""

# --- FUNCIÓN DE AUDIO ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        return None

# --- EL CEREBRO DEL AVATAR (JavaScript) ---
# Esta función crea un mini-programa web que sincroniza tu audio con las fotos
def mostrar_avatar_sincronizado(audio_bytes=None):
    if audio_bytes is None:
        # Si no hay audio, solo mostramos la foto quieta
        st.image(URL_CERRADA, use_container_width=True)
    else:
        # Si hay audio, inyectamos el reproductor inteligente
        b64 = base64.b64encode(audio_bytes.read()).decode()
        html_code = f"""
        <div style="display: flex; justify-content: center; width: 100%;">
            <img id="avatar-img" src="{URL_CERRADA}" style="width: 100%; max-width: 300px; border-radius: 10px;">
        </div>
        <audio id="voz" autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>

        <script>
            const audio = document.getElementById("voz");
            const avatar = document.getElementById("avatar-img");
            let intervalo;

            // CUANDO EL AUDIO EMPIEZA A SONAR
            audio.onplay = function() {{
                let bocaAbierta = false;
                // Cambiar la imagen cada 0.2 segundos (200 milisegundos)
                intervalo = setInterval(function() {{
                    if (bocaAbierta) {{
                        avatar.src = "{URL_CERRADA}";
                    }} else {{
                        avatar.src = "{URL_ABIERTA}";
                    }}
                    bocaAbierta = !bocaAbierta;
                }}, 200); 
            }};

            // CUANDO EL AUDIO TERMINA
            audio.onended = function() {{
                clearInterval(intervalo); // Detiene la animación
                avatar.src = "{URL_CERRADA}"; // Cierra la boca
            }};
            
            // Forzar el play por si el navegador lo bloquea
            audio.play().catch(e => console.log("Esperando interacción del usuario para reproducir audio."));
        </script>
        """
        # Renderizamos este bloque de código en la pantalla
        components.html(html_code, height=350)

# --- ESPACIO PARA EL AVATAR EN LA BARRA LATERAL ---
# Usamos un "placeholder" (espacio vacío reservado) para poder actualizarlo después
with st.sidebar:
    st.title("Tu Consejero Virtual")
    espacio_avatar = st.empty() 
    
    st.divider()
    modo = st.radio("Configuración:", ["Solo Texto 📝", "Voz Automática 🗣️"], index=1)
    st.info("ℹ️ Sube el volumen para escuchar al orientador.")

# --- HISTORIAL DE CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- LÓGICA PRINCIPAL ---
# 1. Por defecto, ponemos la imagen quieta en la barra lateral
with espacio_avatar:
    mostrar_avatar_sincronizado(None)

if texto := st.chat_input("Escribe aquí lo que sientes..."):
    # Guardar usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # Respuesta IA
    try:
        with st.spinner("Pensando... 💭"):
            chat = model.start_chat(history=[])
            prompt_final = f"{instrucciones_seguridad}\n\nMensaje del alumno: {texto}"
            
            respuesta = chat.send_message(prompt_final)
            texto_respuesta = respuesta.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})
        
        with st.chat_message("assistant"):
            st.markdown(texto_respuesta)
            
            # 2. Si el usuario eligió Voz, generamos el audio y actualizamos el avatar
            if "Voz" in modo:
                audio_data = texto_a_audio(texto_respuesta)
                if audio_data:
                    # Borramos la foto quieta y ponemos el avatar animado sincronizado
                    espacio_avatar.empty()
                    with espacio_avatar:
                        mostrar_avatar_sincronizado(audio_data)

    except Exception as e:
        st.error(f"❌ Error: {e}")
