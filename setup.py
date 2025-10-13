from cx_Freeze import setup, Executable
import sys

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'


executables = [Executable("app.py", base=base)]

packages = [
  "pandas","re","numpy","unidecode","io","streamlit","plotly"
]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = "Realocação de Avaliadores",
    options = options,
    version = "1.0",
    description = 'Sistema de alocação de trablahos para professores avaliarem.',
    executables = executables
)