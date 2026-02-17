import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA (TÍTULO DE PESTAÑA) ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. TUS IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. ESTILOS VISUALES (CSS PERSONALIZADO) ---
st.markdown("""
    <style>
        /* Centrar todo el encabezado */
        .encabezado {
            text-align: center;
            padding: 20px;
            background-color: #f0f2f6;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        /* Estilo del nombre del colegio */
        .titulo-colegio {
            color: #1E3A8A; /* Azul institucional oscuro */
            font-family: 'Helvetica', sans-serif;
            font-weight: 900;
            font-size: 2.2rem; /* Grande */
            line-height: 1.2;
            margin-top: 10px;
            margin-bottom: 5px;
            text-transform: uppercase; /* Todo mayúsculas */
        }
        /* Subtítulo */
        .subtitulo {
            color: #555;
            font-size: 1.2rem;
            font-weight: 400;
        }
        /* Ajuste para móviles */
        @media (max-width: 600px) {
            .titulo-colegio { font-size: 1.5rem; }
            .subtitulo { font-size: 1rem; }
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. ENCABEZADO (ESCUDO Y NOMBRE) ---
# Usamos HTML para que quede perfecto y centrado
st.markdown(f"""
    <div class="encabezado">
        <img src="{URL_ESCUDO}" width="150" style="margin-bottom: 10px;">
        <div class="titulo-colegio">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <div class="subtitulo">🎓 Espacio de Escucha y Orientación Escolar 🎓</div>
    </div>
""", unsafe_allow_html=True)


# --- 5. BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80) # Escudo pequeño en la barra
    st.write("**Panel de Control**")
    modo_voz = st.checkbox("🔊 Activar Voz y Animación", value=True)
    st.info("ℹ️ Este asistente virtual está diseñado para apoyar a los estudiantes de la institución.")


# --- 6. FUNCIÓN DE AVATAR (LA QUE FUNCIONA) ---
def mostrar_avatar_con_audio(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        
        <div id="avatar_container" style="position: relative; width: 180px; height: 240px;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;">
            </div>
            <div id="avatar_boca" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;">
            </div>
        </div>

        <audio id="audio_player" controls autoplay style="width: 200px; margin-top: 10px; display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>

        <button id="btn_manual" onclick="forzarPlay()" style="display: none; margin-top: 10px; padding: 10px 20px; background: #c0392b; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
            🔊 ESCUCHAR AL ORIENTADOR
        </button>

    </div>

    <script>
        var player = document.getElementById("audio_player");
        var boca = document.getElementById("avatar_boca");
        var btn = document.getElementById("btn_manual");
        var intervalo;
        
        // CUANDO SUENA EL AUDIO
        player.onplay = function() {{
            btn.style.display = "none"; 
            intervalo = setInterval(function() {{
                boca.style.opacity = (boca.style.opacity == "0" ? "1" : "0");
            }}, 200);
        }};

        // CUANDO TERMINA O PAUSA
        player.onpause = function() {{ clearInterval(intervalo); boca.style.opacity = "0"; }};
        player.onended = function() {{ clearInterval(intervalo); boca.style.opacity = "0"; }};

        // INTENTO DE AUTOPLAY
        var promise = player.play();
        if (promise !== undefined) {{
            promise.catch(error => {{
                btn.style.display = "block"; // Mostrar botón si falla
            }});
        }}

        function forzarPlay() {{ player.play(); }}
    </script>
    """
    return html

# --- 7. CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error("Error de conexión. Verifica la API Key.")
    st.stop()

# --- 8. HISTORIAL DE CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Input del alumno
if texto := st.chat_input("Hola, ¿cómo te sientes hoy?"):
    st.session_state.mensajes.append({"role": "user", "content": texto})

# Mostrar mensajes anteriores
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 9. GENERAR RESPUESTA ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("El orientador está pensando..."):
        try:
            chat = model.start_chat(history=[])
            
            # PROMPT PERSONALIZADO PARA EL COLEGIO
            prompt = f"""
            Actúa como el Orientador Escolar de la Institución Educativa Rural Hugues Manuel Lacouture.
            Tu misión es apoyar a los alumnos con empatía y calidez.
            Responde de forma breve (máximo 2 párrafos).
            IMPORTANTE: Si el alumno menciona peligro (suicidio, abuso, armas), diles que busquen a un profesor o coordinador inmediatamente.
            Mensaje del alumno: {st.session_state.mensajes[-1]['content']}
            """
            
            respuesta = chat.send_message(prompt)
            texto_resp = respuesta.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
            
            with st.chat_message("assistant"):
                st.markdown(texto_resp)

            # GENERAR AUDIO Y MOSTRARLO EN BARRA LATERAL
            if modo_voz:
                tts = gTTS(text=texto_resp, lang='es')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                # Renderizar Avatar
                html_avatar = mostrar_avatar_con_audio(texto_resp, audio_buffer)
                
                # Ubicamos el avatar en la barra lateral, ARRIBA de todo
                with st.sidebar:
                    # Usamos un contenedor vacío al principio para asegurarnos de que se actualice
                    placeholder = st.empty() 
                    placeholder.components.v1.html(html_avatar, height=320)
            
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
