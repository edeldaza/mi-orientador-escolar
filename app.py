import streamlit as st
import google.generativeai as genai
import sys

st.title("🕵️ Diagnóstico de Conexión")

# 1. VERIFICAR VERSIÓN DE LIBRERÍA
st.subheader("1. Versión del Sistema")
try:
    version = genai.__version__
    st.info(f"Librería google-generativeai instalada: {version}")
    if version < "0.7.2":
        st.error("⚠️ TU LIBRERÍA ES MUY VIEJA. Streamlit no actualizó el requirements.txt.")
    else:
        st.success("✅ La versión de la librería es correcta.")
except:
    st.error("❌ No se pudo leer la versión. Instalación corrupta.")

# 2. VERIFICAR LA LLAVE (SECRET)
st.subheader("2. Verificación de API Key")
try:
    if "GOOGLE_API_KEY" in st.secrets:
        key = st.secrets["GOOGLE_API_KEY"]
        st.write(f"La llave existe y tiene {len(key)} caracteres.")
        
        # Verificar si tiene comillas extra por error
        if key.startswith('"') or key.startswith("'"):
            st.error("❌ ERROR CRÍTICO: La llave tiene comillas dentro del texto. En 'Secrets' debe ir sin comillas si usas el formato TOML mal, o con comillas si es TOML estricto. Revisa que no sea '\"AIza...\"'")
        elif " " in key:
            st.error("❌ ERROR CRÍTICO: Hay espacios en blanco en tu llave. Bórralos.")
        else:
            st.success("✅ Formato de llave parece correcto (sin espacios ni comillas extra).")
            
            # 3. PRUEBA DE FUEGO CON GOOGLE
            st.subheader("3. Prueba de Conexión Real")
            genai.configure(api_key=key)
            
            try:
                st.write("Intentando conectar con 'gemini-1.5-flash'...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Di 'Hola'")
                st.success(f"✅ ¡ÉXITO! Google respondió: {response.text}")
                st.balloons()
            except Exception as e1:
                st.error(f"❌ Falló 1.5 Flash. Error: {e1}")
                
                try:
                    st.write("Intentando conectar con 'gemini-pro'...")
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content("Di 'Hola'")
                    st.success(f"✅ ¡ÉXITO! Google respondió con PRO: {response.text}")
                except Exception as e2:
                    st.error(f"❌ Falló Gemini Pro. Error: {e2}")
                    st.warning("CONCLUSIÓN: Si ambos fallaron con '404', tu librería sigue vieja. Si sale '400/403 Invalid API Key', tu llave está mal.")

    else:
        st.error("❌ NO se encontró 'GOOGLE_API_KEY' en los Secrets.")
except Exception as e:
    st.error(f"Error leyendo secrets: {e}")
