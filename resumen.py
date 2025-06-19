def load_transcription(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        transcription = file.read()
    return transcription

def generate_summary_gemini(transcription, format):
    import google.generativeai as genai

    prompt = f"""
    Eres un periodista... (incluir aquí el prompt completo como en el script original)
    Entrevista:
    {transcription}
    {format}
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_summary(transcription_file_path, format):
    transcription = load_transcription(transcription_file_path)
    return generate_summary_gemini(transcription, format)