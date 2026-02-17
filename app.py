import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Orientador Virtual 3D", page_icon="🤖", layout="wide")

# --- TUS IMÁGENES ---
URL_CERRADA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima1.png?raw=true"
URL_ABIERTA = "https://github.com/edeldaza/mi-orientador-escolar/blob/main/ima2.png?raw=true"

# --- COMPONENTE DE AVATAR AVANZADO (HTML + JS + CSS) ---
def mostrar_avatar_avanzado(texto_para_audio=None):
    # Generamos el audio aquí mismo si hay texto
    audio_b64 = ""
    autoplay_attr = ""
    
    if texto_para_audio:
        try:
            tts = gTTS(text=texto_para_audio, lang='es')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            b64 = base64.b64encode(audio_buffer.read()).decode()
            audio_b64 = f"data:audio/mp3;base64,{b64}"
            autoplay_attr = "autoplay"
        except Exception as e:
            st.error(f"Error generando audio: {e}")

    # CÓDIGO HTML/CSS/JS (Corregido: Solo mueve la boca)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* 1. EFECTO DE RESPIRACIÓN SUAVE (Cuando está callado) */
        @keyframes respirar {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-3px); }} /* Movimiento muy sutil hacia arriba */
            100% {{ transform: translateY(0px); }}
        }}

        /* 2. EFECTO DE HABLAR (CORREGIDO: Solo cambia la imagen, no rebota) */
        @keyframes hablar {{
            0% {{ background-image: url('{URL_CERRADA}'); }}
            25% {{ background-image: url('{URL_ABIERTA}'); }}
            50% {{ background-image: url('{URL_CERRADA}'); }}
            75% {{ background-image: url('{URL_ABIERTA}'); }}
            100% {{ background-image: url('{URL_CERRADA}'); }}
        }}

        body {{
            background-color: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            overflow: hidden;
        }}

        .avatar-container {{
            width: 100%;
            height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .robot {{
            width: 300px;
            height: 400px;
            background-image: url('{URL_CERRADA}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            
            /* Por defecto: RESPIRA SUAVEMENTE */
            animation: respirar 4s infinite ease-in-out;
            transition: all 0.1s ease; /* Transición rápida para la boca */
        }}

        /* Clase que activa el habla */
        .hablando {{
            /* Se quita la respiración y se activa solo el cambio de boca */
            animation: hablar 0.2s infinite !important;
        }}
        
        audio {{
            display: none;
        }}
    </style>
    </head>
    <body>

        <div class="avatar-container">
            <div id="robot-personaje" class="robot"></div>
        </div>

        <audio id="player" controls {autoplay_attr}>
            <source src="{audio_b64}" type="audio/mp3">
        </audio>

        <script>
            const player = document.getElementById('player');
            const robot = document.getElementById('robot-personaje');

            // CUANDO SUENA EL AUDIO -> ACTIVA SOLO B
