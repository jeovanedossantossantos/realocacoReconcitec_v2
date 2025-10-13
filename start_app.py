import os
import webbrowser

# Caminho completo para o seu app
app_path = os.path.abspath("app.py")

# Abrir o navegador (opcional)
webbrowser.open("http://localhost:8501")

# Rodar o streamlit
os.system(f"streamlit run {app_path}")