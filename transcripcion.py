def transcribe_and_diarize(audio_file_path, language=None, device="cuda", batch_size=20, compute_type="float16", model_type="large-v2"):
    import whisperx
    import torch
    import os
    import gc

    model = whisperx.load_model(model_type, device, compute_type=compute_type)
    audio = whisperx.load_audio(audio_file_path)
    result = model.transcribe(audio, batch_size=batch_size, language=language)

    idioma_detectado = result["language"]
    model_a, metadata = whisperx.load_align_model(language_code=idioma_detectado, device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    diarize_model = whisperx.DiarizationPipeline(use_auth_token="INSERTAR TOKEN", device=device)
    diarize_segments = diarize_model(audio)
    final_result = whisperx.assign_word_speakers(diarize_segments, result)

    output_directory = "/content/transcriptions"
    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, os.path.basename(audio_file_path).replace(".mp3", ".txt").replace(".raw", ".txt"))
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("Transcripción con etiquetas de hablantes:\n\n")
        for segment in final_result["segments"]:
            speaker = segment.get("speaker", "Unknown")
            file.write(f"[{speaker}] {segment['text']}\n")

    del model, diarize_model, diarize_segments, final_result, model_a, metadata, audio, result
    gc.collect()
    torch.cuda.empty_cache()

    return output_file
