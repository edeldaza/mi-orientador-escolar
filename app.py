import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import re
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. RECURSOS VISUALES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. ESTILOS MODERNOS (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* Encabezado con degradado institucional moderno */
        .hero-header {
            background: linear-gradient(135deg, #002855 0%, #004e92 100%);
            color: white;
            padding: 22px 30px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 22px;
            box-shadow: 0 10px 25px rgba(0, 40, 85, 0.15);
            margin-bottom: 25px;
            border-bottom: 4px solid #FFC72C;
        }
        .hero-header img {
            width: 85px;
            height: 85px;
            object-fit: contain;
            background: white;
            padding: 6px;
            border-radius: 50%;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .hero-title {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin: 0;
            line-height: 1.2;
            text-transform: uppercase;
        }
        .hero-subtitle {
            font-size: 14px;
            color: #e0ecff;
            margin-top: 5px;
            margin-bottom: 0;
            font-weight: 400;
        }

        /* Estilizar botones rompehielos */
        div.stButton > button {
            border-radius: 12px;
            border: 1px solid #d0d7de;
            background-color: #ffffff;
            color: #002855;
            font-weight: 500;
            padding: 10px 14px;
            transition: all 0.2s ease;
            width: 100%;
            text-align: left;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        div.stButton > button:hover {
            border-color: #004e92;
            background-color: #f0f7ff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 78, 146, 0.12);
        }

        /* Tarjeta de emergencia en barra lateral */
        .emergency-card {
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            padding: 12px 15px;
            border-radius: 10px;
            font-size: 13px;
            color: #742a2a;
            margin-top: 15px;
        }
        .whatsapp-btn {
            display: block;
            text-align: center;
            background-color: #25D366;
            color: white !important;
            text-decoration: none;
            font-weight: 600;
            padding: 8px 12px;
            border-radius: 8px;
            margin-top: 8px;
            font-size: 13px;
        }
        .whatsapp-btn:hover {
            background-color: #1ebe57;
        }

        /* Adaptación para celulares */
        @media (max-width: 768px) {
            .hero-header {
                flex-direction: column;
                text-align: center;
                padding: 18px;
            }
            .hero-title {
                font-size: 18px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. ENCABEZADO PRINCIPAL ---
st.markdown(f"""
    <div class="hero-header">
        <img src="{URL_ESCUDO}" alt="Escudo IER">
        <div>
            <div class="hero-title">Institución Educativa Rural<br>Hugues Manuel Lacouture</div>
            <p class="hero-subtitle">🌱 Espacio Seguro de Orientación Escolar • Confidencial y Gratuito</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 5. ESTADO DE LA SESIÓN ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "ultimo_audio" not in st.session_state:
    st.session_state.ultimo_audio = None

# --- 6. BARRA LATERAL INTERACTIVA ---
with st.sidebar:
    st.markdown("### 👋 ¡Hola, estudiante!")
    st.caption("Este es un espacio seguro para conversar sobre cómo te sientes, tus estudios o tu futuro.")
    
    # Termómetro emocional
    estado_animo = st.selectbox(
        "¿Cómo te sientes en este momento?",
        [
            "😊 Tranquilo / Bien",
            "😐 Normal, con algunas dudas",
            "😟 Estresado o preocupado",
            "😔 Triste o desanimado",
            "😡 Molesto o frustrado"
        ]
    )
    
    st.write("---")
    modo_voz = st.toggle("🔊 Escuchar voz del orientador", value=True)
    
    # Botón de privacidad para computadores compartidos
    if st.button("🗑️ Borrar conversación (Privacidad)"):
        st.session_state.mensajes = []
        st.session_state.ultimo_audio = None
        st.rerun()

    st.markdown("""
        <div class="emergency-card">
            <strong>🚨 ¿Necesitas ayuda urgente?</strong><br>
            No estás solo/a. Puedes hablar directamente con nuestra profesional:<br>
            👩‍⚕️ <b>Elianys Plata</b><br>
            📞 300-243-1343
            <a class="whatsapp-btn" href="https://wa.me/573002431343?text=Hola%20se%C3%B1o%20Elianys,%20soy%20estudiante%20de%20la%20I.E.R.%20Hugues%20Manuel%20Lacouture%20y%20necesito%20orientaci%C3%B3n." target="_blank">
                💬 Escribir por WhatsApp
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 7. FUNCIÓN DEL AVATAR CON ANIMACIÓN ---
def mostrar_avatar(audio_bytes=None):
    b64_audio = ""
    estado_texto = "Escuchándote atentamente..."
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes).decode()
        estado_texto = "Hablando contigo..."

    html = f"""
    <style>
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-5px); }}
            100% {{ transform: translateY(0px); }}
        }}
        .avatar-card {{
            background: linear-gradient(180deg, #ffffff 0%, #f4f8fb 100%);
            padding: 15px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0, 40, 85, 0.08);
            border: 1px solid #e1e8ed;
            font-family: sans-serif;
        }}
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #e6f4ea;
            color: #137333;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 10px;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            background-color: #34a853;
            border-radius: 50%;
            display: inline-block;
        }}
        .avatar-container {{
            position: relative;
            width: 190px;
            height: 230px;
            margin: 0 auto;
            animation: float 4s ease-in-out infinite;
        }}
    </style>
    <div class="avatar-card">
        <div class="status-badge"><span class="dot"></span> <span id="status-text">{estado_texto}</span></div>
        <div class="avatar-container">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_CERRADA}'); background-size: contain; background-repeat: no-repeat; background-position: center;"></div>
            <div id="mouth" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: url('{URL_ABIERTA}'); background-size: contain; background-repeat: no-repeat; background-position: center;
                        opacity: 0; transition: opacity 0.08s;"></div>
        </div>
        <div style="font-size: 13px; color: #002855; font-weight: bold; margin-top: 8px;">Orientador Virtual</div>
        <audio id="player" autoplay style="display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    </div>
    <script>
        var p = document.getElementById("player");
        var m = document.getElementById("mouth");
        var st = document.getElementById("status-text");
        var i;
        if ("{b64_audio}" !== "") {{
            p.onplay = () => {{
                st.innerText = "Hablando contigo...";
                i = setInterval(() => {{
                    m.style.opacity = (m.style.opacity == "0" ? "1" : "0");
                }}, 180);
            }};
            p.onended = () => {{
                clearInterval(i);
                m.style.opacity = "0";
                st.innerText = "Escuchándote atentamente...";
            }};
            p.play().catch(e => {{
                console.log("Autoplay prevenido por el navegador:", e);
                st.innerText = "En línea para ayudarte";
            }});
        }}
    </script>
    """
    return html

# --- 8. FUNCIÓN DE RESPIRACIÓN GUIADA INTERACTIVA ---
def mostrar_ejercicio_respiracion():
    html_respiracion = """
    <style>
        .calm-card {
            background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 100%);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            font-family: sans-serif;
            box-shadow: 0 8px 20px rgba(0, 78, 146, 0.08);
            border: 1px solid #b2ebf2;
        }
        .circle-wrap {
            position: relative;
            width: 220px;
            height: 220px;
            margin: 25px auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .breathing-circle {
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, #4dd0e1 0%, #0097a7 100%);
            border-radius: 50%;
            transition: transform 4s ease-in-out, background 4s ease;
            box-shadow: 0 0 30px rgba(0, 151, 167, 0.4);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 15px;
        }
        .phase-text {
            font-size: 15px;
            font-weight: 600;
            line-height: 1.2;
        }
        .timer-text {
            font-size: 26px;
            font-weight: 700;
            margin-top: 4px;
        }
        .btn-calm {
            background-color: #006064;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 10px rgba(0, 96, 100, 0.2);
        }
        .btn-calm:hover {
            background-color: #00838f;
            transform: translateY(-2px);
        }
    </style>

    <div class="calm-card">
        <h3 style="color: #004d40; margin-top: 0; margin-bottom: 5px;">🌿 Respira conmigo (Técnica 4-4-4)</h3>
        <p style="color: #00695c; font-size: 13px; margin-top: 0;">Sigue el movimiento del círculo para calmar tu mente y bajar el ritmo cardíaco.</p>
        
        <div class="circle-wrap">
            <div id="circle" class="breathing-circle">
                <div id="instruction" class="phase-text">¿Listo/a?</div>
                <div id="counter" class="timer-text"></div>
            </div>
        </div>

        <button id="toggleBtn" class="btn-calm" onclick="toggleBreathing()">▶️ Iniciar ejercicio</button>
    </div>

    <script>
        let running = false;
        let phaseTimer;
        let secondTimer;
        const circle = document.getElementById("circle");
        const instruction = document.getElementById("instruction");
        const counter = document.getElementById("counter");
        const btn = document.getElementById("toggleBtn");

        const phases = [
            { text: "Inhala suave...", scale: 1.65, color: "radial-gradient(circle, #4dd0e1 0%, #00838f 100%)" },
            { text: "Mantén el aire", scale: 1.65, color: "radial-gradient(circle, #81c784 0%, #2e7d32 100%)" },
            { text: "Exhala lento...", scale: 1.0,  color: "radial-gradient(circle, #90caf9 0%, #1565c0 100%)" }
        ];
        let currentPhase = 0;

        function runPhase() {
            if (!running) return;
            const p = phases[currentPhase];
            instruction.innerText = p.text;
            circle.style.transform = `scale(${p.scale})`;
            circle.style.background = p.color;

            let sec = 4;
            counter.innerText = sec;
            clearInterval(secondTimer);
            secondTimer = setInterval(() => {
                sec--;
                if (sec > 0) counter.innerText = sec;
            }, 1000);

            currentPhase = (currentPhase + 1) % phases.length;
        }

        function toggleBreathing() {
            if (!running) {
                running = true;
                btn.innerText = "⏸️ Pausar ejercicio";
                currentPhase = 0;
                runPhase();
                phaseTimer = setInterval(runPhase, 4000);
            } else {
                running = false;
                clearInterval(phaseTimer);
                clearInterval(secondTimer);
                circle.style.transform = "scale(1)";
                instruction.innerText = "En pausa";
                counter.innerText = "";
                btn.innerText = "▶️ Continuar";
            }
        }
    </script>
    """
    return html_respiracion

# --- 9. LIMPIEZA DE TEXTO Y FONÉTICA FRANCESA PARA EL AUDIO ---
def preparar_texto_para_voz(texto):
    # Reemplazamos "Hugues" por su pronunciación francesa aproximada ("Iug") solo para el audio
    texto_limpio = re.sub(r'\bHugues\b', 'Iug', texto, flags=re.IGNORECASE)
    # Quitamos símbolos de formato Markdown
    texto_limpio = re.sub(r'[\*\#\_\~]', '', texto_limpio)
    # Quitamos emojis para que el lector de voz no los lea en voz alta
    texto_limpio = re.sub(r'[^\w\s,.;:¿?¡!áéíóúÁÉÍÓÚñÑüÜ()-]', '', texto_limpio)
    return texto_limpio

# --- 10. CONEXIÓN INTELIGENTE CON GEMINI ---
@st.cache_resource
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
            return genai.GenerativeModel('gemini-1.5-flash')

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

        return genai.GenerativeModel(modelo_a_usar) if modelo_a_usar else None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

model = obtener_modelo_disponible()

# --- 11. DISEÑO DE PANTALLA DIVIDIDA (AVATAR + PESTAÑAS) ---
col_avatar, col_chat = st.columns([1, 2.3], gap="large")

with col_chat:
    tab_chat, tab_calma = st.tabs(["💬 Conversar con el Orientador", "🧘 Zona de Calma (Ansiedad y Estrés)"])

    # --- PESTAÑA 1: CHAT ---
    with tab_chat:
        if not st.session_state.mensajes:
            st.markdown("#### 💬 ¿Sobre qué te gustaría conversar hoy?")
            st.caption("Puedes tocar una de estas opciones rápidas o escribir directamente abajo:")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📚 Me siento estresado con las tareas y exámenes"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola, últimamente me siento muy estresado con las tareas y el estudio."})
                    st.rerun()
                if st.button("🧭 No sé qué quiero hacer cuando termine el colegio"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola, tengo dudas sobre mi futuro y no sé qué estudiar o hacer al salir del colegio."})
                    st.rerun()
            with c2:
                if st.button("🤝 Tuve un problema con un compañero de clase"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola, tuve un inconveniente con un compañero y no sé cómo manejarlo."})
                    st.rerun()
                if st.button("💭 Solo necesito desahogarme con alguien"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola, hoy no me siento muy bien y quisiera desahogarme un rato."})
                    st.rerun()

        contenedor_mensajes = st.container()
        with contenedor_mensajes:
            for m in st.session_state.mensajes:
                icono = "🧑‍🎓" if m["role"] == "user" else "🎓"
                with st.chat_message(m["role"], avatar=icono):
                    st.markdown(m["content"])

    # --- PESTAÑA 2: ZONA DE CALMA ---
    with tab_calma:
        components.html(mostrar_ejercicio_respiracion(), height=410)
        
        with st.expander("🖐️ ¿Sigues sintiendo mucha ansiedad? Prueba la técnica 5-4-3-2-1"):
            st.markdown("""
            Mira a tu alrededor en el salón o en tu casa y nombra mentalmente:
            * 👀 **5 cosas** que puedas ver en este momento.
            * ✋ **4 cosas** que puedas tocar o sentir (como tus pies en el suelo o la textura de tu ropa).
            * 👂 **3 sonidos** que puedas escuchar a lo lejos o cerca.
            * 👃 **2 olores** que puedas percibir en el ambiente.
            * ❤️ **1 cualidad positiva** sobre ti mismo/a.
            """)

# Entrada de texto fija abajo
if texto_usuario := st.chat_input("Escribe aquí tu mensaje con total confianza..."):
    st.session_state.mensajes.append({"role": "user", "content": texto_usuario})
    st.rerun()

# --- 12. GENERACIÓN DE RESPUESTA ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    if model:
        with col_chat:
            with st.spinner("El orientador te está escuchando..."):
                try:
                    reglas_sistema = f"""
                    INSTRUCCIONES ESTRICTAS PARA TI:
                    1. IDENTIDAD: Si te preguntan tu nombre, quién eres, cómo te llamas o qué haces, responde siempre que eres el "Orientador Virtual de la Institución Educativa Rural Hugues Manuel Lacouture".
                    2. CONTEXTO EMOCIONAL: El estudiante indicó en el termómetro emocional que hoy se siente: "{estado_animo}". Tenlo muy en cuenta para adaptar tu calidez.
                    3. TONO: Sé extremadamente amable, cálido, empático y comprensivo. Haz que el estudiante se sienta escuchado, seguro y sin ser juzgado. Termina con una pregunta suave que invite a seguir conversando si aplica.
                    4. BREVEDAD: Tus respuestas deben ser cortas y directas (máximo 2 o 3 frases).
                    5. 🚨 EMERGENCIA VITAL: Si detectas que el estudiante menciona o insinúa ideación suicida, autolesiones, abuso, depresión severa o cualquier situación de peligro grave, DETÉN el consejo regular y dile de forma muy empática que no está solo, y que DEBE pedir ayuda urgente comunicándose con la profesional a cargo: Elianys Plata al número 300-2431-343.
                    -----------------
                    """

                    historial_gemini = []
                    for i, msg in enumerate(st.session_state.mensajes[:-1]):
                        rol_ia = "user" if msg["role"] == "user" else "model"
                        contenido = msg["content"]
                        if i == 0 and rol_ia == "user":
                            contenido = reglas_sistema + "\nMENSAJE DEL ESTUDIANTE: " + contenido
                        historial_gemini.append({"role": rol_ia, "parts": [contenido]})

                    chat = model.start_chat(history=historial_gemini)
                    mensaje_actual = st.session_state.mensajes[-1]['content']
                    
                    if len(st.session_state.mensajes) == 1:
                        mensaje_actual = reglas_sistema + "\nMENSAJE DEL ESTUDIANTE: " + mensaje_actual

                    response = chat.send_message(mensaje_actual)
                    texto_resp = response.text

                    st.session_state.mensajes.append({"role": "assistant", "content": texto_resp})

                    # Generar audio limpio y con pronunciación francesa de "Hugues"
                    if modo_voz:
                        texto_para_voz = preparar_texto_para_voz(texto_resp)
                        tts = gTTS(text=texto_para_voz, lang='es')
                        audio_buffer = BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)
                        st.session_state.ultimo_audio = audio_buffer.read()
                    else:
                        st.session_state.ultimo_audio = None

                    st.rerun()

                except Exception as e:
                    st.error(f"Ocurrió un error técnico: {e}")
    else:
        st.error("⚠️ No se encontró ningún modelo de IA disponible. Verifica tu API Key.")

# Renderizamos el avatar siempre visible en la columna izquierda
with col_avatar:
    components.html(mostrar_avatar(st.session_state.ultimo_audio), height=340)
    st.session_state.ultimo_audio = None
