import streamlit as st
import google.generativeai as genai

st.title("🕵️‍♂️ Escáner de Modelos de Google")
st.write("Vamos a ver qué modelos están disponibles para tu clave API.")

try:
    # 1. Conectamos
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 2. Pedimos la lista a Google
    st.write("⏳ Consultando a Google...")
    lista_modelos = []
    for m in genai.list_models():
        # Filtramos solo los que sirven para generar texto
        if 'generateContent' in m.supported_generation_methods:
            lista_modelos.append(m.name)
    
    # 3. Mostramos el resultado
    if lista_modelos:
        st.success(f"¡Éxito! Se encontraron {len(lista_modelos)} modelos disponibles:")
        st.code("\n".join(lista_modelos))
        st.info("👆 Mándame una foto de esta lista para decirte cuál usar.")
    else:
        st.error("Se conectó, pero la lista está vacía. Tu API Key podría no tener permisos.")

except Exception as e:
    st.error(f"Error grave de conexión: {e}")
