import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components 

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide"
)

# --- 2. IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. DISEÑO ---
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
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header">
        <img src="{URL_ESCUDO}" width="100">
        <div class="title-text">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
        <p>🎓 Portal de Orientación Escolar 🎓</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image(URL_ESCUDO, width=80)
    st.write("---")
    modo_voz = st.checkbox("🔊 Activar Voz", value=True)
    st.info("Sistema exclusivo para estudiantes.")

# --- 5. FUNCIÓN AVATAR ---
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

# --- 6. CONEXIÓN INTELIGENTE ---
def obtener_modelo_disponible():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        lista_modelos = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    lista_modelos.append(m.name)
        except:
            return genai.GenerativeModel('gemini-pro')

        modelo_a_usar = ""
        for m in lista_modelos:
            if 'flash' in m:
                modelo_a_usar = m
                break
        if not modelo_a_usar:
            for m in lista_modelos:
                if 'pro' in m:
                    modelo_a_usar = m
                    break
        if not modelo_a_usar and lista_modelos:
            modelo_a_usar = lista_modelos[0]

        if modelo_a_usar:
            return genai.GenerativeModel(modelo_a_usar)
        else:
            return None

    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

model = obtener_modelo_disponible()

# --- 7. CHAT ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if texto := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 8. RESPUESTA (AHORA CON MEMORIA Y REGLAS ESTRICTAS) ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    if model:
        with st.spinner("El orientador está pensando..."):
            try:
                # 1. PREPARAMOS LAS REGLAS DEL COLEGIO
                reglas_sistema = """
                INSTRUCCIONES ESTRICTAS PARA TI:
                1. IDENTIDAD: Si te preguntan tu nombre, quién eres, cómo te llamas o qué haces, responde siempre que eres el "Orientador Virtual de la Institución Educativa Rural Hugues Manuel Lacouture".
                2. TONO: Sé extremadamente amable, cálido, empático y comprensivo. Haz que el estudiante se sienta escuchado, seguro y sin ser juzgado.
                3. BREVEDAD: Tus respuestas deben ser cortas y directas (máximo 2 o 3 frases).
                4. 🚨 EMERGENCIA VITAL: Si detectas que el estudiante menciona o insinúa ideación suicida, autolesiones, abuso, depresión severa o cualquier situación de peligro grave, DETÉN el consejo regular y dile de forma muy empática que no está solo, y que DEBE pedir ayuda urgente comunicándose con la profesional a cargo: ELIANYS PLATA al número 3002431343.
                5. Cada vez que encuentres la palabra Hugues, la vas a pronunciar a la fransesa.
                -----------------
                """

                # 2. CONSTRUIMOS LA MEMORIA (HISTORIAL) PARA LA IA
                historial_gemini = []
                for i, msg in enumerate(st.session_state.mensajes[:-1]): # Tomamos todos menos el último
                    # Convertimos los roles de Streamlit a los roles que entiende Google
                    rol_ia = "user" if msg["role"] == "user" else "model"
                    contenido = msg["content"]
                    
                    # Le inyectamos las reglas ocultas solo al primerísimo mensaje para que no las olvide
                    if i == 0 and rol_ia == "user":
                        contenido = reglas_sistema + "\nMENSAJE DEL ESTUDIANTE: " + contenido
                        
                    historial_gemini.append({"role": rol_ia, "parts": [contenido]})

                # 3. INICIAMOS EL CHAT PASÁNDOLE LA MEMORIA
                chat = model.start_chat(history=historial_gemini)
                
                # 4. PREPARAMOS EL MENSAJE ACTUAL
                mensaje_actual = st.session_state.mensajes[-1]['content']
                
                # Si es el primer mensaje de toda la charla, le pegamos las reglas aquí
                if len(st.session_state.mensajes) == 1:
                    mensaje_actual = reglas_sistema + "\nMENSAJE DEL ESTUDIANTE: " + mensaje_actual
                
                # 5. ENVIAMOS Y RECIBIMOS RESPUESTA
                response = chat.send_message(mensaje_actual)
                texto_resp = response.text
                
                # Guardamos y mostramos en pantalla
                st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})
                with st.chat_message("assistant"):
                    st.markdown(texto_resp)
                
                # Generamos la voz y animación
                if modo_voz:
                    tts = gTTS(text=texto_resp, lang='es')
                    audio_buffer = BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    html_avatar = mostrar_avatar(texto_resp, audio_buffer)
                    with st.sidebar:
                        components.html(html_avatar, height=320)
                        
            except Exception as e:
                st.error(f"Ocurrió un error técnico: {e}")
    else:
        st.error("⚠️ No se encontró ningún modelo de IA disponible. Verifica tu API Key.")

# --- 9. BOTÓN WHATSAPP MEJORADO (CON TEXTO Y MÁS ARRIBA) ---
def boton_whatsapp():
    # ⚠️ CAMBIA ESTE NÚMERO POR EL TUYO ⚠️
    numero_telefono = "57300243134" 
    
    mensaje = "Hola, necesito orientación escolar."
    url_wa = f"https://wa.me/{numero_telefono}?text={mensaje.replace(' ', '%20')}"
    
    st.markdown(f"""
    <style>
        .boton-flotante {{
            position: fixed;
            bottom: 150px;
            right: 20px;
            background-color: #25d366;
            color: white !important;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: sans-serif;
            font-weight: bold;
            transition: transform 0.3s;
        }}
        .boton-flotante:hover {{
            background-color: #128c7e;
            transform: scale(1.05);
        }}
        .texto-boton {{
            font-size: 16px;
        }}
    </style>
    
    <a href="{url_wa}" class="boton-flotante" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="25px" style="filter: brightness(0) invert(1);">
        <span class="texto-boton">Ayuda WhatsApp</span>
    </a>
    """, unsafe_allow_html=True)

boton_whatsapp()
