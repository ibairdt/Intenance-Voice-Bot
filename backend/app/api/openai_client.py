from openai import OpenAI, APIError
from app.config import settings
import os
from datetime import datetime

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def chat_with_gpt(prompt: str, stream: bool = False):
    """
    Envía un mensaje a GPT y devuelve la respuesta
    
    Argumentos:
        prompt (string): contenido del mensaje que se le pasa al modelo
        stream (bool): parametro para hacerlo en tiempo real

    Retorna:
        string del contenido de la respuesta
    
    """
    response = client.chat.completions.create(
        model = settings.MODEL_VOICE,
        messages = [
            # le pasamos un diccionario con ciertos parámetros para cada rol (usuario y bot)
            {"role": "user", 
            "content": prompt},
            {"role": "system",
            "content": "Eres un asistente de mantenimiento industrial para ayudar a los empleados a hacer su trabajo de manera más eficiente"}
            ],
            # Debes proporcionar respuestas claras y concisas basándote en la documentación que tienes disponible. Si no conoces la respuesta en base a la documentación debes decir que tus funciones son exclusivamente de mantenimiento
        stream = stream
    )
    return response.choices[0].message.content

def text_to_speech(text: str) -> str:
    """
    Convierte texto a voz usando el modelo TTS-1 de OpenAI
    
    Argumentos:
        text (string): texto a convertir en voz
        
    Retorna:
        string con la ruta del archivo de audio generado
    """
    try:
        # Obtener la ruta base del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(base_dir, "test_audios", "responses")
        
        # Asegurar que el directorio existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"response_{timestamp}.mp3")
        
        # Convertir texto a voz
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Opciones: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        # Guardar el archivo de audio usando streaming
        with open(output_file, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Error en la conversión de texto a voz: {str(e)}")

def transcribe_audio(audio_file_name: str) -> str:
    """Transcribe un audio desde la carpeta /audios y guarda el resultado en /transcriptions."""
    
    try:
        # Obtener la ruta base del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Construir las rutas usando os.path.join
        input_dir = os.path.join(base_dir, "test_audios", "audios")
        output_dir = os.path.join(base_dir, "test_audios", "transcriptions")
        
        # Asegurar que las carpetas existen
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        input_path = os.path.join(input_dir, audio_file_name)
        
        # Verificar que el archivo existe
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"No se encontró el archivo de audio: {audio_file_name}")
            
        # el archivo de salida se llamará transcripted_{nombre archivo audio}
        output_file_name = f"transcripted_{audio_file_name.split('.')[0]}.txt"
        output_path = os.path.join(output_dir, output_file_name)

        # Transcribir con el modelo Whisper
        with open(input_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="text"
            )
        
        # Guardar transcripción
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        return transcription
        
    except Exception as e:
        raise Exception(f"Error en la transcripción: {str(e)}")