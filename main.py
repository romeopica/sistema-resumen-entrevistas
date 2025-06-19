from nicegui import ui
from pyngrok import ngrok
import asyncio
import nest_asyncio
import time
from pathlib import Path

from transcripcion import transcribe_and_diarize
from resumen import generate_summary
from wordpress import crear_post
from utils import format_to_html
from config import configurar_ambiente

# Aplicar fixes y configuraciones
nest_asyncio.apply()
configurar_ambiente()

# Constantes
PORT = 7860
uploaded_file_path = None
summary_output = None
loading_container = None
generating_summary = False

# Funciones de interfaz
def toggle_lang_visibility(event):
    lang_select.set_visibility(not event.value)

def toggle_speakers_visibility(event):
    speakers_input.set_visibility(not event.value)

def handle_upload(event):
    global uploaded_file_path
    uploaded_file_name = event.name
    uploaded_file_content = event.content.read()

    temp_dir = Path('/content/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)
    uploaded_file_path = temp_dir / uploaded_file_name

    with open(uploaded_file_path, 'wb') as f:
        f.write(uploaded_file_content)

    ui.notify(f'Archivo subido: {uploaded_file_name}')

def download_summary():
    content = summary_output.content
    js_code = f"""
        const blob = new Blob([{content!r}], {{type: 'text/html'}});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'resumen.html';
        a.click();
        URL.revokeObjectURL(a.href);
    """
    ui.run_javascript(js_code)

def open_publish_modal():
    publish_modal.open()

def publish():
    wp_url = wp_url_input.value
    username = wp_username_input.value
    password = wp_password_input.value
    content = summary_output.content
    crear_post(wp_url, username, password, content)

async def transcribe_and_diarize_async(file_path, language):
    return await asyncio.to_thread(transcribe_and_diarize, file_path, language)

async def generate_summary_async(transcription_file, format):
    return await asyncio.to_thread(generate_summary, transcription_file, format)

async def summarize():
    global uploaded_file_path, summary_output, loading_container, generating_summary

    if generating_summary:
        ui.notify('Generación en proceso, por favor espere.', type='warning')
        return

    if not uploaded_file_path:
        ui.notify('Error: Falta subir el archivo de audio', type='negative')
        return

    generating_summary = True
    lang = None if auto_lang.value else lang_select.value

    loading_container.classes(remove='opacity-0 pointer-events-none')
    summary_output.classes('blur-sm')

    start_time = time.time()
    try:
        transcription_file = await transcribe_and_diarize_async(str(uploaded_file_path), language=lang)
        resumen = await generate_summary_async(transcription_file, format_template)
        html = format_to_html(resumen)

        summary_output.set_content(html)
        summary_output.classes(remove='blur-sm')
    finally:
        loading_container.classes('opacity-0 pointer-events-none')
        generating_summary = False
    end_time = time.time()
    print(f"Resumen generado en {(end_time - start_time):.2f} segundos.")

# Formato para el resumen
format_template = """
#Título#
*Introducción general*

##Subtítulo del Tema 1##
&Pregunta 1&
**Respuesta 1**
&Pregunta 2&
**Respuesta 2**

##Subtítulo del Tema 2##
&Pregunta 1&
**Respuesta 1**
&Pregunta 2&
**Respuesta 2**

# %Conclusión general sobre la entrevista%
"""

# UI
with ui.header().classes('bg-blue-500 text-white p-4'):
    ui.label('Generar Resumen de Entrevistas').classes('text-xl')

with ui.row().classes('w-full p-4'):
    with ui.column().classes('w-1/3 p-4 bg-gray-100 rounded-lg').style("min-width: 340px"):
        ui.label('Configuración').classes('text-lg font-bold mt-3')

        with ui.row().classes('items-center w-full'):
            ui.label('Autodetectar idioma')
            auto_lang = ui.switch(value=True, on_change=toggle_lang_visibility)
        lang_select = ui.select(['en', 'es'], value='es').props('label="Idioma"').style('min-width: 200px')
        lang_select.set_visibility(False)

        with ui.row().classes('items-center w-full mt-4'):
            ui.label('Autodetectar Speakers')
            auto_speakers = ui.switch(value=True, on_change=toggle_speakers_visibility)
        speakers_input = ui.input(value='', placeholder='Cantidad de speakers', validation={'Cantidad invalida': lambda value: value.isdigit() and int(value) >= 1})
        speakers_input.set_visibility(False)

        file_upload = ui.upload(label='Subir archivo de audio (.mp3, .wav)', auto_upload=True, on_upload=handle_upload)
        file_upload.props('accept=".mp3,.wav" max-files=1')

        with ui.row().classes('w-full justify-between align-items-end p-4'):
            ui.space()
            ui.button('Generar Resumen', on_click=summarize).classes('bg-green-500 text-white')

    with ui.column().classes('w-1/2 p-4 border rounded-lg relative').style("min-width: 340px"):
        with ui.row().classes('w-full justify-between align-items-end'):
            ui.label('Resumen').classes('text-lg font-bold mt-3')
            ui.space()
            ui.button('', icon='download', on_click=download_summary)
            ui.button('Publicar', icon='wordpress', on_click=open_publish_modal)

        ui.separator()

        summary_output = ui.html("").classes('w-full transition').style("min-height: 400px")

        with ui.row().classes('absolute inset-0 flex justify-center items-center bg-white/50 opacity-0 pointer-events-none transition') as loading_container:
            ui.spinner('dots', size='xl', color='red')

# Modal de publicación
with ui.dialog() as publish_modal, ui.card().classes('w-1/3 p-6 rounded-lg shadow-lg'):
    ui.label('Publicar en WordPress').classes('text-lg font-bold mb-4')
    wp_url_input = ui.input(label='WordPress URL', validation={'URL inválida': lambda value: value.startswith("http")}).classes('w-full')
    wp_username_input = ui.input(label='Usuario', validation={'Requerido': lambda value: value.strip() != ""}).classes('w-full')
    wp_password_input = ui.input(label='Contraseña', validation={'Requerida': lambda value: value.strip() != ""}, password=True, password_toggle_button=True).classes('w-full')
    with ui.row().classes('justify-between align-items-end gap-2 mt-4'):
        ui.button('Cancelar', on_click=publish_modal.close, color="gray").classes('text-black px-4 py-2 rounded-md').props("outline")
        ui.button('Publicar', on_click=publish, color="primary").classes('text-white px-4 py-2 rounded-md')

# Lanzar NiceGUI
public_url = ngrok.connect(PORT).public_url
print(f"La página está disponible en: {public_url}")
asyncio.create_task(ui.run(title="Resumen de Entrevistas", port=PORT, host="0.0.0.0", favicon="🔊"))
