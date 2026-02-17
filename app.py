import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- BARRA LATERAL CON ANIMACIÓN ---
# Esta función reemplaza a st.image y hace la magia visual
def mostrar_avatar_animado(audio_bytes=None):
    
    # 1. Preparar audio si existe
    audio_html = ""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes.read()).decode()
        # El truco: 'autoplay' y eventos de JS para activar la animación
        audio_html = f"""
        <audio id="audio_player" autoplay style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """

    # 2. El código HTML/CSS que hace que se mueva
    html_code = f"""
    <style>
        .contenedor-robot {{
            position: relative;
            width: 100%;
            max-width: 250px; /* Tamaño máximo en sidebar */
            aspect-ratio: 3/4; /* Proporción de la imagen */
            margin: auto;
        }}
        
        /* Imagen Base (Quieto) */
        .robot-base {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{URL_CERRADA}');
            background-size: contain; background-repeat: no-repeat; background-position: center top;
            transition: transform 0.1s;
        }}
        
        /* Imagen Boca Abierta (Animación) */
        .robot-boca {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{URL_ABIERTA}');
            background-size: contain; background-repeat: no-repeat; background-position: center top;
            opacity: 0; /* Oculta por defecto */
        }}

        /* CLASE QUE ACTIVA EL MOVIMIENTO */
        .hablando {{
            animation: hablar 0.2s infinite;
        }}

        @keyframes hablar {{
            0% {{ opacity: 0; }}
            50% {{ opacity: 1; }} /* Abre la boca */
            100% {{ opacity: 0; }} /* Cierra la boca */
        }}
    </style>

    <div class="contenedor-robot">
        <div id="base" class="robot-base"></div>
        <div id="boca" class="robot-boca"></div>
    </div>
    
    {audio_html}

    <script>
        var audio = document.getElementById("audio_player");
        var boca = document.getElementById("boca");

        if (audio) {{
            // CUANDO EL AUDIO ARRANCA -> MOVEMOS LA BOCA
            audio.onplay = function() {{
                boca.classList.add("hablando");
            }};
            
            // CUANDO EL AUDIO TERMINA -> PARAMOS LA BOCA
            audio.onended = function() {{
                boca.classList.remove("hablando");
            }};

            // INTENTO DE AUTOPLAY SEGURO
            audio.play().catch(e => console.log("Autoplay esperando interacción"));
        }}
    </script>
    """
    st.sidebar.markdown(html_code, unsafe_allow_html=True)

# --- BARRA LATERAL (CONTENIDO) ---
with st.sidebar:
    st.title("Tu Consejero Virtual")
    
    # Marcador de posición para el avatar (se llenará más abajo)
    contenedor_avatar = st.empty()
    
    st.divider()
    modo = st.radio("Configuración:", ["Solo Texto 📝", "Voz Automática 🗣️"], index=1)
    st.info("ℹ️ Asegúrate de tener volumen.")

# --- CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- FUNCIONES AUXILIARES ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        st.error(f"Error audio: {e}")
        return None

# --- CHAT UI ---
st.title("🤖 Espacio de Escucha Escolar")
st.markdown("---")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- LÓGICA PRINCIPAL ---
# Inicializamos el avatar quieto por defecto al cargar la página
if "ultimo_audio" not in st.session_state:
    st.session_state.ultimo_audio = None

# Si no hay interacción nueva, mostramos el avatar estático o el último audio
with contenedor_avatar:
    mostrar_avatar_animado(st.session_state.ultimo_audio)
    # Limpiamos el audio después de mostrarlo para que no se repita en loop al recargar
    st.session_state.ultimo_audio = None 

if texto := st.chat_input("Escribe aquí..."):
    # 1. Guardar mensaje usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # 2. Generar respuesta
    try:
        with st.spinner("Pensando..."):
            chat = model.start_chat(history=[])
            prompt = f"Actúa como un orientador escolar empático. Responde corto (máx 2 frases). Mensaje: {texto}"
            respuesta = chat.send_message(prompt)
            texto_res = respuesta.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_res})
            
            # 3. Generar Audio (SI está activado)
            audio_data = None
            if "Voz" in modo:
                audio_data = texto_a_audio(texto_res)
                # Guardamos el audio en session_state para pasarlo al sidebar tras el rerun
                st.session_state.ultimo_audio = audio_data
            
        # 4. Forzar recarga para actualizar el sidebar con el audio nuevo
        st.rerun()
            
    except Exception as e:
        st.error(f"Error: {e}")
