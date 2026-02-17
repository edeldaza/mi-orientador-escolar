import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Orientador Escolar", page_icon="🤖", layout="wide")

# --- IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    modo_voz = st.checkbox("Activar Voz y Animación", value=True)
    st.info("Si el audio no suena automático, aparecerá un botón debajo del avatar.")

# --- LA MAGIA: AUDIO + AVATAR EN UNO SOLO ---
def mostrar_avatar_con_audio(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    # Este HTML contiene TODO: El dibujo, el audio y la lógica
    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
        
        <div id="avatar_container" style="position: relative; width: 200px; height: 260px;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;">
            </div>
            <div id="avatar_boca" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;">
            </div>
        </div>

        <audio id="audio_player" controls autoplay style="width: 250px; margin-top: 10px; display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>

        <button id="btn_manual" onclick="forzarPlay()" style="display: none; margin-top: 10px; padding: 10px 20px; background: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🔊 Reproducir Respuesta
        </button>

    </div>

    <script>
        var player = document.getElementById("audio_player");
        var boca = document.getElementById("avatar_boca");
        var btn = document.getElementById("btn_manual");

        // --- ANIMACIÓN ---
        // Abrir y cerrar la boca en bucle mientras suena
        var intervalo;
        
        player.onplay = function() {{
            btn.style.display = "none"; // Ocultar botón si suena
            player.style.display = "block"; // Mostrar controles por si acaso
            
            intervalo = setInterval(function() {{
                boca.style.opacity = (boca.style.opacity == "0" ? "1" : "0");
            }}, 200); // Velocidad del habla
        }};

        player.onpause = function() {{
            clearInterval(intervalo);
            boca.style.opacity = "0"; // Cerrar boca
        }};

        player.onended = function() {{
            clearInterval(intervalo);
            boca.style.opacity = "0"; // Cerrar boca
        }};

        // --- INTENTO DE AUTOPLAY ---
        var promise = player.play();
        if (promise !== undefined) {{
            promise.catch(error => {{
                console.log("Autoplay bloqueado. Mostrando botón manual.");
                btn.style.display = "block"; // Mostrar botón para que el usuario haga clic
                player.style.display = "none";
            }});
        }}

        // Función para el botón manual
        function forzarPlay() {{
            player.play();
        }}
    </script>
    """
    return html

# --- CONEXIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error API: {e}")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Espacio de Escucha Escolar")

# Inicializar historial
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Input del usuario
if texto := st.chat_input("Cuéntame algo..."):
    # Guardar mensaje
    st.session_state.mensajes.append({"role": "user", "content": texto})

# Mostrar historial CHAT
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- GENERAR RESPUESTA ---
# Solo si el último mensaje es del usuario (para evitar repeticiones al recargar)
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    with st.spinner("Pensando..."):
        try:
            # 1. Obtener texto de IA
            chat = model.start_chat(history=[])
            prompt = f"Actúa como un orientador escolar empático. Responde corto (máx 2 frases). Mensaje: {st.session_state.mensajes[-1]['content']}"
            respuesta = chat.send_message(prompt)
            texto_resp = respuesta.text
            
            # 2. Guardar en historial
            st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
            
            # 3. Mostrar respuesta en texto
            with st.chat_message("assistant"):
                st.markdown(texto_resp)

            # 4. GENERAR AUDIO Y AVATAR (Aquí está la clave)
            if modo_voz:
                tts = gTTS(text=texto_resp, lang='es')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                # Renderizamos el componente "Todo en Uno" en la barra lateral o arriba
                html_avatar = mostrar_avatar_con_audio(texto_resp, audio_buffer)
                
                # Lo mostramos en la barra lateral para que se vea siempre
                with st.sidebar:
                    st.components.v1.html(html_avatar, height=350)
            
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
