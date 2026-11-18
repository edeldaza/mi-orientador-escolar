import os
import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import base64
import re
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="ArmonIA • Orientación I.E.R. Hugues Manuel Lacouture",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. RECURSOS VISUALES ---
URL_ESCUDO = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima3.png?raw=true"

# --- 3. ESTILOS JUVENILES Y MODERNOS (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Poppins:wght@500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
        }

        /* Fondo juvenil suave con degradado alegre */
        .stApp {
            background: linear-gradient(135deg, #e0f2fe 0%, #f3e8ff 50%, #fef9c3 100%);
            background-attachment: fixed;
        }

        /* Aprovechar mejor el espacio superior de la pantalla */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 1.5rem !important;
            max-width: 1220px;
        }

        /* Barra lateral con degradado suave */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #eff6ff 100%);
            border-right: 2px solid #bae6fd;
        }

        /* Encabezado institucional vibrante */
        .hero-header {
            background: linear-gradient(135deg, #002855 0%, #0284c7 65%, #0ea5e9 100%);
            color: white;
            padding: 18px 28px;
            border-radius: 24px;
            display: flex;
            align-items: center;
            gap: 20px;
            box-shadow: 0 10px 28px rgba(2, 132, 199, 0.22);
            margin-bottom: 20px;
            border-bottom: 5px solid #FFC72C;
            position: relative;
            overflow: hidden;
        }
        .hero-header img {
            width: 80px;
            height: 80px;
            object-fit: contain;
            background: white;
            padding: 6px;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            border: 3px solid #FFC72C;
        }
        .hero-title {
            font-family: 'Poppins', sans-serif;
            font-size: 21px;
            font-weight: 700;
            letter-spacing: 0.4px;
            margin: 0;
            line-height: 1.2;
            text-transform: uppercase;
        }
        .hero-subtitle {
            font-size: 14.5px;
            color: #fef08a;
            margin-top: 5px;
            margin-bottom: 0;
            font-weight: 700;
        }

        /* Pestañas estilo cápsula moderna (elimina el rojo por defecto) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(255, 255, 255, 0.85);
            padding: 6px;
            border-radius: 18px;
            border: 2px solid #bae6fd;
            box-shadow: 0 4px 12px rgba(0, 40, 85, 0.05);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 14px;
            padding: 8px 18px;
            font-weight: 700;
            font-size: 14px;
            color: #0369a1;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0284c7 0%, #002855 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
        }
        .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* Tarjeta de bienvenida dentro del chat */
        .welcome-box {
            background: rgba(255, 255, 255, 0.92);
            border-radius: 22px;
            padding: 18px 22px;
            border: 2px solid #bae6fd;
            box-shadow: 0 6px 18px rgba(2, 132, 199, 0.08);
            margin-bottom: 14px;
        }
        .welcome-box h4 {
            color: #002855;
            margin: 0 0 4px 0;
            font-family: 'Poppins', sans-serif;
            font-size: 18px;
        }
        .welcome-box p {
            color: #475569;
            margin: 0;
            font-size: 14px;
        }

        /* Botones rompehielos coloridos e interactivos */
        div.stButton > button {
            border-radius: 16px;
            border: 2px solid #7dd3fc;
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            color: #002855;
            font-weight: 700;
            font-size: 14px;
            padding: 12px 16px;
            transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
            width: 100%;
            text-align: left;
            box-shadow: 0 4px 10px rgba(2, 132, 199, 0.08);
        }
        div.stButton > button:hover {
            border-color: #0284c7;
            background: linear-gradient(135deg, #e0f2fe 0%, #fef9c3 100%);
            color: #002855;
            transform: translateY(-3px) scale(1.01);
            box-shadow: 0 8px 18px rgba(2, 132, 199, 0.18);
        }

        /* Burbujas de chat estilo app juvenil */
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 22px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(0, 40, 85, 0.07);
            border: 1.5px solid #bae6fd;
            font-size: 15px;
        }

        /* Caja de escribir mensaje (elimina el borde rojo) */
        [data-testid="stChatInput"] > div {
            border: 2.5px solid #0284c7 !important;
            border-radius: 22px !important;
            background-color: #ffffff !important;
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.15) !important;
        }

        /* Tarjeta de emergencia en barra lateral */
        .emergency-card {
            background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
            border: 1.5px solid #fda4af;
            border-left: 5px solid #e11d48;
            padding: 14px 15px;
            border-radius: 16px;
            font-size: 13.5px;
            color: #881337;
            margin-top: 15px;
            box-shadow: 0 4px 12px rgba(225, 29, 72, 0.08);
        }
        .whatsapp-btn {
            display: block;
            text-align: center;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white !important;
            text-decoration: none;
            font-weight: 800;
            padding: 9px 12px;
            border-radius: 12px;
            margin-top: 10px;
            font-size: 13.5px;
            box-shadow: 0 4px 10px rgba(34, 197, 94, 0.25);
        }
        .whatsapp-btn:hover {
            filter: brightness(1.06);
        }

        /* Adaptación para celulares */
        @media (max-width: 768px) {
            .hero-header {
                flex-direction: column;
                text-align: center;
                padding: 16px;
            }
            .hero-title {
                font-size: 17px;
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
            <p class="hero-subtitle">✨ ArmonIA • Tu Espacio Seguro de Orientación Escolar • 100% Confidencial</p>
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
    st.caption("Soy **ArmonIA**, tu compañero virtual para escucharte y apoyarte en el colegio o en casa.")
    
    # Termómetro emocional
    estado_animo = st.selectbox(
        "🎭 ¿Cómo te sientes hoy?",
        [
            "😊 Tranquilo / Feliz",
            "😐 Normal, con algunas dudas",
            "😟 Estresado o preocupado",
            "😔 Triste o desanimado",
            "😡 Molesto o frustrado"
        ]
    )
    
    st.write("---")
    modo_voz = st.toggle("🔊 Escuchar voz de ArmonIA", value=True)
    
    # Selector de voz neuronal colombiana
    opciones_voz = {
        "👩‍🏫 Salomé (Voz Femenina)": "es-CO-SalomeNeural",
        "👨‍🏫 Gonzalo (Voz Masculina)": "es-CO-GonzaloNeural"
    }
    voz_elegida_label = st.selectbox("🎙️ Elige la voz que prefieras:", list(opciones_voz.keys()), disabled=not modo_voz)
    voz_codigo = opciones_voz[voz_elegida_label]
    
    # Botón de privacidad para computadores compartidos
    if st.button("🧹 Limpiar chat (Privacidad)"):
        st.session_state.mensajes = []
        st.session_state.ultimo_audio = None
        st.rerun()

    st.markdown("""
        <div class="emergency-card">
            <strong>🚨 ¿Necesitas hablar con alguien ya?</strong><br>
            No estás solo/a. Nuestra orientadora está para apoyarte:<br>
            👩‍⚕️ <b>Elianys Plata</b><br>
            📞 300-243-1343
            <a class="whatsapp-btn" href="https://wa.me/573002431343?text=Hola%20se%C3%B1o%20Elianys,%20soy%20estudiante%20de%20la%20I.E.R.%20Hugues%20Manuel%20Lacouture%20y%20necesito%20orientaci%C3%B3n." target="_blank">
                💬 Escribir por WhatsApp
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 7. FUNCIÓN DEL ROBOT AMIGABLE CON SINCRONIZACIÓN DE VOZ REAL ---
def mostrar_avatar(audio_bytes=None):
    b64_audio = ""
    estado_texto = "Escuchándote con atención..."
    if audio_bytes:
        b64_audio = base64.b64encode(audio_bytes).decode()
        estado_texto = "Hablando contigo..."

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&display=swap');
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-7px) rotate(1.2deg); }}
        }}
        @keyframes blink {{
            0%, 92%, 100% {{ transform: scaleY(1); }}
            96% {{ transform: scaleY(0.08); }}
        }}
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 0 12px #FFC72C; }}
            50% {{ box-shadow: 0 0 22px #fde047; }}
        }}
        .avatar-card {{
            background: linear-gradient(160deg, #002855 0%, #0369a1 65%, #0284c7 100%);
            padding: 16px 14px 18px 14px;
            border-radius: 26px;
            text-align: center;
            box-shadow: 0 12px 28px rgba(0, 40, 85, 0.22);
            border: 3px solid #38bdf8;
            font-family: 'Nunito', sans-serif;
            position: relative;
            overflow: hidden;
            box-sizing: border-box;
        }}
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(4px);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.3);
            font-size: 12px;
            font-weight: 700;
            padding: 5px 14px;
            border-radius: 20px;
            margin-bottom: 8px;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            background-color: #4ade80;
            box-shadow: 0 0 8px #4ade80;
            border-radius: 50%;
            display: inline-block;
        }}
        .robot-stage {{
            position: relative;
            width: 190px;
            height: 190px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        #voice-aura {{
            position: absolute;
            width: 155px;
            height: 155px;
            background: radial-gradient(circle, #38bdf8 0%, rgba(56,189,248,0) 70%);
            border-radius: 50%;
            opacity: 0.35;
            transition: transform 0.05s ease-out, opacity 0.05s ease-out;
        }}
        .robot-wrapper {{
            position: relative;
            z-index: 2;
            animation: float 3.8s ease-in-out infinite;
        }}
        .robot-head {{
            width: 138px;
            height: 112px;
            background: linear-gradient(145deg, #ffffff, #e0f2fe);
            border: 4px solid #FFC72C;
            border-radius: 40px;
            position: relative;
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.25), inset 0 -5px 10px rgba(2, 132, 199, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .antenna {{
            width: 6px;
            height: 18px;
            background: #FFC72C;
            margin: 0 auto;
            position: relative;
        }}
        .antenna-ball {{
            width: 16px;
            height: 16px;
            background: #fde047;
            border: 3px solid #002855;
            border-radius: 50%;
            position: absolute;
            top: -12px;
            left: -8px;
            animation: pulseGlow 2s infinite;
        }}
        .ear {{
            position: absolute;
            width: 14px;
            height: 42px;
            background: #FFC72C;
            border: 3px solid #002855;
            border-radius: 10px;
            top: 32px;
        }}
        .ear.left {{ left: -16px; }}
        .ear.right {{ right: -16px; }}
        .face-screen {{
            width: 110px;
            height: 82px;
            background: #091526;
            border-radius: 28px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 6px;
            box-shadow: inset 0 3px 8px rgba(0,0,0,0.6);
            position: relative;
        }}
        .eyes-row {{
            display: flex;
            gap: 26px;
            margin-bottom: 8px;
        }}
        .eye {{
            width: 19px;
            height: 23px;
            background: #38bdf8;
            border-radius: 50%;
            box-shadow: 0 0 14px #38bdf8;
            animation: blink 4.2s infinite;
            position: relative;
        }}
        .eye::after {{
            content: '';
            width: 7px;
            height: 7px;
            background: white;
            border-radius: 50%;
            position: absolute;
            top: 4px;
            right: 4px;
        }}
        .cheeks-row {{
            position: absolute;
            width: 86px;
            display: flex;
            justify-content: space-between;
            top: 44px;
            pointer-events: none;
        }}
        .cheek {{
            width: 14px;
            height: 7px;
            background: #fb7185;
            border-radius: 50%;
            opacity: 0.75;
            filter: blur(1px);
        }}
        #robot-mouth {{
            width: 34px;
            height: 7px;
            background: #38bdf8;
            border-radius: 10px;
            box-shadow: 0 0 12px #38bdf8;
            transition: height 0.04s ease-out, width 0.04s ease-out, border-radius 0.04s;
        }}
        .eq-container {{
            display: flex;
            justify-content: center;
            align-items: flex-end;
            gap: 4px;
            height: 20px;
            margin-top: 4px;
        }}
        .eq-bar {{
            width: 4px;
            height: 4px;
            background: #FFC72C;
            border-radius: 2px;
            transition: height 0.05s ease;
        }}
        .name-pill {{
            display: inline-block;
            background: #FFC72C;
            color: #002855;
            font-size: 13.5px;
            font-weight: 800;
            padding: 4px 14px;
            border-radius: 14px;
            margin-top: 8px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        }}
        #replay-btn {{
            display: none;
            margin: 8px auto 0;
            background: #ffffff;
            color: #002855;
            border: none;
            padding: 5px 14px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        }}
    </style>

    <div class="avatar-card">
        <div class="status-badge"><span class="dot"></span> <span id="status-text">{estado_texto}</span></div>
        
        <div class="robot-stage">
            <div id="voice-aura"></div>
            <div class="robot-wrapper">
                <div class="antenna"><div class="antenna-ball"></div></div>
                <div class="robot-head">
                    <div class="ear left"></div>
                    <div class="ear right"></div>
                    <div class="face-screen">
                        <div class="eyes-row">
                            <div class="eye"></div>
                            <div class="eye"></div>
                        </div>
                        <div class="cheeks-row">
                            <div class="cheek"></div>
                            <div class="cheek"></div>
                        </div>
                        <div id="robot-mouth"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="eq-container">
            <div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div>
            <div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div>
            <div class="eq-bar"></div>
        </div>
        <div><span class="name-pill">✨ ArmonIA • Tu Guía I.E.R.</span></div>
        <button id="replay-btn" onclick="iniciarAudioManual()">🔊 Escuchar de nuevo</button>

        <audio id="player" style="display: none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    </div>

    <script>
        const b64Audio = "{b64_audio}";
        const audio = document.getElementById("player");
        const mouth = document.getElementById("robot-mouth");
        const aura = document.getElementById("voice-aura");
        const statusText = document.getElementById("status-text");
        const replayBtn = document.getElementById("replay-btn");
        const bars = document.querySelectorAll(".eq-bar");

        let audioCtx;
        let analyser;
        let dataArray;
        let animId;
        let isInitialized = false;

        function inicializarAnalizador() {{
            if (isInitialized) return;
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioCtx = new AudioContext();
            const source = audioCtx.createMediaElementSource(audio);
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 64;
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            isInitialized = true;
        }}

        function animarHabla() {{
            analyser.getByteFrequencyData(dataArray);
            
            let sum = 0;
            for (let i = 2; i < 15; i++) {{
                sum += dataArray[i];
            }}
            let avg = sum / 13;

            let mouthHeight = Math.max(6, Math.min(28, (avg / 145) * 28));
            let mouthWidth = 34 - (mouthHeight * 0.25);
            mouth.style.height = mouthHeight + "px";
            mouth.style.width = mouthWidth + "px";
            mouth.style.borderRadius = mouthHeight > 12 ? "50%" : "10px";

            let scaleAura = 1 + (avg / 255) * 0.5;
            aura.style.transform = "scale(" + scaleAura + ")";
            aura.style.opacity = Math.min(0.9, 0.35 + (avg / 255));

            bars.forEach((bar, idx) => {{
                let val = dataArray[idx + 2] || 0;
                let h = Math.max(4, (val / 255) * 20);
                bar.style.height = h + "px";
            }});

            animId = requestAnimationFrame(animarHabla);
        }}

        function iniciarAudioManual() {{
            replayBtn.style.display = "none";
            inicializarAnalizador();
            if (audioCtx && audioCtx.state === "suspended") {{
                audioCtx.resume();
            }}
            audio.play();
        }}

        if (b64Audio !== "") {{
            audio.onplay = () => {{
                inicializarAnalizador();
                if (audioCtx && audioCtx.state === "suspended") {{
                    audioCtx.resume();
                }}
                statusText.innerText = "Hablando contigo...";
                animarHabla();
            }};

            audio.onended = () => {{
                cancelAnimationFrame(animId);
                mouth.style.height = "7px";
                mouth.style.width = "34px";
                mouth.style.borderRadius = "10px";
                aura.style.transform = "scale(1)";
                aura.style.opacity = "0.35";
                bars.forEach(bar => bar.style.height = "4px");
                statusText.innerText = "Escuchándote con atención...";
                replayBtn.style.display = "inline-block";
            }};

            inicializarAnalizador();
            audio.play().catch(e => {{
                statusText.innerText = "Respuesta lista";
                replayBtn.style.display = "inline-block";
            }});
        }}
    </script>
    """
    return html

# --- 8. FUNCIÓN DE RESPIRACIÓN GUIADA INTERACTIVA ---
def mostrar_ejercicio_respiracion():
    html_respiracion = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800&display=swap');
        .calm-card {
            background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%);
            border-radius: 24px;
            padding: 22px;
            text-align: center;
            font-family: 'Nunito', sans-serif;
            box-shadow: 0 8px 22px rgba(2, 132, 199, 0.1);
            border: 2px solid #7dd3fc;
        }
        .circle-wrap {
            position: relative;
            width: 215px;
            height: 215px;
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .breathing-circle {
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, #38bdf8 0%, #0284c7 100%);
            border-radius: 50%;
            transition: transform 4s ease-in-out, background 4s ease;
            box-shadow: 0 0 32px rgba(2, 132, 199, 0.45);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 15px;
        }
        .phase-text {
            font-size: 15px;
            font-weight: 800;
            line-height: 1.2;
        }
        .timer-text {
            font-size: 28px;
            font-weight: 800;
            margin-top: 4px;
        }
        .btn-calm {
            background: linear-gradient(135deg, #0284c7 0%, #002855 100%);
            color: white;
            border: none;
            padding: 11px 26px;
            border-radius: 25px;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(0, 40, 85, 0.25);
        }
        .btn-calm:hover {
            transform: translateY(-2px) scale(1.03);
        }
    </style>

    <div class="calm-card">
        <h3 style="color: #002855; margin-top: 0; margin-bottom: 4px; font-weight: 800;">🌿 Respira con ArmonIA (Técnica 4-4-4)</h3>
        <p style="color: #0369a1; font-size: 14px; margin-top: 0; font-weight: 600;">Sigue el círculo mágico para relajar tu mente antes de un examen o cuando sientas nervios.</p>
        
        <div class="circle-wrap">
            <div id="circle" class="breathing-circle">
                <div id="instruction" class="phase-text">¿Listo/a?</div>
                <div id="counter" class="timer-text"></div>
            </div>
        </div>

        <button id="toggleBtn" class="btn-calm" onclick="toggleBreathing()">▶️ Comenzar a respirar</button>
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
            { text: "Inhala suave...", scale: 1.65, color: "radial-gradient(circle, #38bdf8 0%, #0284c7 100%)" },
            { text: "Sostén el aire", scale: 1.65, color: "radial-gradient(circle, #4ade80 0%, #16a34a 100%)" },
            { text: "Exhala lento...", scale: 1.0,  color: "radial-gradient(circle, #a78bfa 0%, #6d28d9 100%)" }
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

# --- 9. MOTOR DE VOZ NEURONAL COLOMBIANA (EDGE-TTS) ---
def preparar_texto_para_voz(texto):
    texto_limpio = re.sub(r'\bHugues\b', 'Iug', texto, flags=re.IGNORECASE)
    texto_limpio = re.sub(r'\bArmonIA\b', 'Armonía', texto_limpio, flags=re.IGNORECASE)
    texto_limpio = re.sub(r'[\*\#\_\~]', '', texto_limpio)
    texto_limpio = re.sub(r'[^\w\s,.;:¿?¡!áéíóúÁÉÍÓÚñÑüÜ()-]', '', texto_limpio)
    return texto_limpio.strip()

async def _generar_audio_async(texto, voz):
    communicate = edge_tts.Communicate(text=texto, voice=voz, rate="+0%", pitch="+0Hz")
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes

def generar_voz_colombiana(texto, voz):
    texto_limpio = preparar_texto_para_voz(texto)
    if not texto_limpio:
        return None
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generar_audio_async(texto_limpio, voz))
    finally:
        loop.close()

# --- 10. CONEXIÓN INTELIGENTE CON GEMINI ---
@st.cache_resource
def obtener_modelo_disponible():
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            st.error("⚠️ No se encontró la variable GOOGLE_API_KEY en el apartado Environment de Northflank.")
            return None

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
    tab_chat, tab_calma = st.tabs(["💬 Hablar con ArmonIA", "🧘 Zona de Calma y Relajación"])

    # --- PESTAÑA 1: CHAT ---
    with tab_chat:
        if not st.session_state.mensajes:
            st.markdown("""
                <div class="welcome-box">
                    <h4>🌟 ¡Qué alegría verte por aquí!</h4>
                    <p>Elige una tarjeta para empezar o escríbeme lo que quieras abajo. Nadie te va a juzgar:</p>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📚 Estrés con tareas o exámenes"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola ArmonIA, últimamente me siento muy estresado con las tareas y el estudio."})
                    st.rerun()
                if st.button("🚀 Dudas sobre mi futuro al graduarme"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola ArmonIA, tengo dudas sobre mi futuro y no sé qué estudiar o hacer al salir del colegio."})
                    st.rerun()
            with c2:
                if st.button("🤝 Problema con un compañero o amigo"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola ArmonIA, tuve un inconveniente con un compañero y no sé cómo manejarlo."})
                    st.rerun()
                if st.button("💭 Solo quiero desahogarme un rato"):
                    st.session_state.mensajes.append({"role": "user", "content": "Hola ArmonIA, hoy no me siento muy bien y quisiera desahogarme un rato."})
                    st.rerun()

        contenedor_mensajes = st.container()
        with contenedor_mensajes:
            for m in st.session_state.mensajes:
                icono = "🧑‍🎓" if m["role"] == "user" else "🤖"
                with st.chat_message(m["role"], avatar=icono):
                    st.markdown(m["content"])

    # --- PESTAÑA 2: ZONA DE CALMA ---
    with tab_calma:
        components.html(mostrar_ejercicio_respiracion(), height=400)
        
        with st.expander("🖐️ Reto interactivo 5-4-3-2-1 para calmar los nervios", expanded=True):
            st.caption("Marca cada casilla a medida que vayas completando el reto en tu salón o en tu casa:")
            st.checkbox("👀 **5 cosas** que puedas ver ahora mismo a tu alrededor.")
            st.checkbox("✋ **4 cosas** que puedas tocar (tu cuaderno, tus pies en el suelo, tu ropa).")
            st.checkbox("👂 **3 sonidos** que logres escuchar cerca o a lo lejos.")
            st.checkbox("👃 **2 olores** que puedas percibir en el ambiente.")
            st.checkbox("💛 **1 cosa buena** que te guste de ti mismo/a.")

# Entrada de texto fija abajo
if texto_usuario := st.chat_input("Escribe aquí tu mensaje para ArmonIA con total confianza..."):
    st.session_state.mensajes.append({"role": "user", "content": texto_usuario})
    st.rerun()

# --- 12. GENERACIÓN DE RESPUESTA ---
if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "user":
    if model:
        with col_chat:
            with st.spinner("✨ ArmonIA te está escuchando..."):
                try:
                    reglas_sistema = f"""
                    INSTRUCCIONES ESTRICTAS PARA TI:
                    1. IDENTIDAD: Si te preguntan tu nombre, quién eres, cómo te llamas o qué haces, responde siempre que te llamas "ArmonIA", el Orientador Virtual de la Institución Educativa Rural Hugues Manuel Lacouture.
                    2. CONTEXTO EMOCIONAL: El estudiante indicó en el termómetro emocional que hoy se siente: "{estado_animo}". Tenlo muy en cuenta para adaptar tu calidez.
                    3. TONO: Sé extremadamente amable, cálido, empático y comprensivo. Usa un español colombiano natural, cercano y respetuoso adaptado a niños y jóvenes. Haz que el estudiante se sienta escuchado, seguro y sin ser juzgado. Termina con una pregunta suave que invite a seguir conversando si aplica.
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

                    if modo_voz:
                        st.session_state.ultimo_audio = generar_voz_colombiana(texto_resp, voz_codigo)
                    else:
                        st.session_state.ultimo_audio = None

                    st.rerun()

                except Exception as e:
                    st.error(f"Ocurrió un error técnico: {e}")
    else:
        st.error("⚠️ No se encontró ningún modelo de IA disponible. Verifica tu API Key.")

# Renderizamos el robot siempre visible en la columna izquierda (altura ampliada para que no se corte)
with col_avatar:
    components.html(mostrar_avatar(st.session_state.ultimo_audio), height=380)
    st.session_state.ultimo_audio = None
