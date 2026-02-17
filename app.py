import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components 

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. RECURSOS (IMÁGENES) ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. ESTILOS CSS ---
st.markdown("""
    <style>
        .header {
            text-align: center;
            padding: 20px;
            background-color: #f4f6f9;
            border-radius: 15px;
            border-bottom: 5px solid #003366;
            margin-bottom: 20px;
        }
        .title-text {
            color: #003366;
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
        }
        /* Botón Flotante de WhatsApp */
        .boton-flotante {
            position: fixed;
            bottom: 100px;
            right: 20px;
            background-color: #25d366;
            color: white !important;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: sans-serif;
            font-weight: bold;
            transition: transform 0.3s;
        }
        .boton-flotante:hover {
            background-color: #128c7e;
            transform: scale(1.05);
        }
        @media (max-width: 600px) {
            .title-text { font-size: 18px; }
            .boton-flotante { bottom: 80px; right: 10px; padding: 10px 20px; }
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado visible
st.markdown(f"""
    <div class="header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="title-text">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p>🎓 Portal de Orientación Escolar</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.info("Sistema exclusivo para estudiantes.\nPotenciado por Gemini AI.")

# --- 5. LÓGICA DEL AVATAR (HTML/JS) ---
def mostrar_avatar(texto, audio_bytes):
    b64_audio = ""
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html = f"""
    <div style="background: white; padding: 10px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="position: relative; width: 180px; height: 240px; margin: 0 auto;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;"></div>
            <div id="mouth" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.1s;"></div>
        </div>
        <audio id="player" autoplay style="display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    </div>
    <script>
        var p = document.getElementById("player");
        var m = document.getElementById("mouth");
        var i;
        p.onplay = () => {{ i = setInterval(() => {{ m.style.opacity = (m.style.opacity == "0" ? "1" : "0"); }}, 200); }};
        p.onended = () => {{ clearInterval(i); m.style.opacity = "0"; }};
        p.play();
    </script>
    """
    return html

# --- 6. CONEXIÓN INTELIGENTE A GEMINI (SOLUCIÓN AL ERROR 404) ---
@st.cache_resource
def configurar_modelo():
    """Configura y devuelve el mejor modelo disponible."""
    try:
        # 1. Autenticación
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 2. Buscar modelos disponibles
        modelos_disponibles = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponibles.append(m.name)
        except Exception as e:
            st.error(f"Error al listar modelos: {e}")
            return None

        # 3. Selección de prioridad (1.5 Pro > Pro > Flash)
        modelo_seleccionado = None
        
        # Prioridad 1: Gemini 1.5 Pro
        for m in modelos_disponibles:
            if "gemini-1.5-pro" in m:
                modelo_seleccionado = m
                break
        
        # Prioridad 2: Gemini 1.5 Flash (Muy bueno y rápido)
        if not modelo_seleccionado:
            for m in modelos_disponibles:
                if "gemini-1.5-flash" in m:
                    modelo_seleccionado = m
                    break

        # Prioridad 3: Gemini Pro Clásico
        if not modelo_seleccionado:
            for m in modelos_disponibles:
                if "gemini-pro" in m:
                    modelo_seleccionado = m
                    break
        
        # Fallback final
        if not modelo_seleccionado and modelos_disponibles:
            modelo_seleccionado = modelos_disponibles[0]

        if modelo_seleccionado:
            # Configuración de generación
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            # Instrucción del sistema
            system_instruction = (
                "Eres el Orientador Escolar de la Institución Educativa Rural Hugues Manuel Lacouture. "
                "Tu nombre es Orientador Virtual. "
                "Tu misión es escuchar y apoyar a los estudiantes con empatía, respeto y claridad. "
                "Tus respuestas deben ser cortas, cálidas y directas (máximo 3 oraciones). "
                "Si el tema es grave (suicidio, abuso, violencia), sugiere contactar a un adulto de confianza inmediatamente."
            )

            # Intentamos crear el modelo con system_instruction
            try:
                model = genai.GenerativeModel(
                    model_name=modelo_seleccionado,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            except:
                # Si falla (versión vieja de librería), lo creamos sin system_instruction
                model = genai.GenerativeModel(
                    model_name=modelo_seleccionado,
                    generation_config=generation_config
                )
            
            return model
        else:
            st.error("No se encontraron modelos disponibles.")
            return None

    except Exception as e:
        st.error(f"Error crítico en la conexión: {e}")
        return None

# Inicializar modelo
model = configurar_modelo()

# --- 7. INTERFAZ DE CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 8. PROCESAMIENTO ---
if texto := st.chat_input("Escribe aquí lo que sientes o necesitas..."):
    # 1. Guardar mensaje usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    # 2. Generar respuesta
    if model:
        with st.chat_message("assistant"):
            with st.spinner("Escuchando..."):
                try:
                    # Crear chat (sin historial largo para ahorrar tokens, o podrías pasarlo)
                    chat = model.start_chat(history=[])
                    
                    # Si el modelo no soportó system_instruction al crearse, lo inyectamos aquí
                    prompt_final = texto
                    # (Opcional: puedes descomentar la siguiente línea si sientes que olvida quién es)
                    # prompt_final = f"Actúa como Orientador Escolar breve y empático. Responde a esto: {texto}"

                    response = chat.send_message(prompt_final)
                    texto_resp = response.text
                    
                    st.markdown(texto_resp)
                    st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})

                    # 3. Voz y Avatar
                    if modo_voz:
                        tts = gTTS(text=texto_resp, lang='es')
                        audio_buffer = BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)
                        
                        html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                        with st.sidebar:
                            components.html(html_avatar, height=320)

                except Exception as e:
                    st.error(f"Lo siento, tuve un problema de conexión. Intenta de nuevo. ({e})")
    else:
        st.error("El sistema no está disponible en este momento.")

# --- 9. BOTÓN WHATSAPP ---
def render_whatsapp_button():
    # ⚠️ CAMBIA ESTE NÚMERO POR EL TUYO REAL (Ej: 573001234567)
    numero_telefono = "573000000000" 
    
    mensaje = "Hola, necesito orientación escolar."
    url_wa = f"https://wa.me/{numero_telefono}?text={mensaje.replace(' ', '%20')}"
    
    st.markdown(f"""
    <a href="{url_wa}" class="boton-flotante" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="25px" style="filter: brightness(0) invert(1);">
        <span style="font-size: 16px;">Ayuda WhatsApp</span>
    </a>
    """, unsafe_allow_html=True)

render_whatsapp_button()
