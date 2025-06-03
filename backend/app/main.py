from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from app.api.openai_client import chat_with_gpt, transcribe_audio, text_to_speech
#from app.api.rag import load_and_index_documents, query_rag
import os
from pydantic import BaseModel

app = FastAPI()
# vectorstore = load_and_index_documents()  # Carga los documentos al iniciar

# Modelo Pydantic para validar el input
# para el endpoint de /ask con texto
class QuestionRequest(BaseModel):
    text: str  # Campo debe llamarse "text"

# para el endpoint de /transcribe con audio
class AudioRequest(BaseModel):
    file_name: str  # Campo obligatorio llamado "file_name"

@app.post("/ask")
# TODO 
async def ask_question(request: QuestionRequest):  # Usa el modelo aquí
    response = chat_with_gpt(request.text)
    return {"response": response}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Obtener la ruta base del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Construir las rutas usando os.path.join
        audios_dir = os.path.join(base_dir, "test_audios", "audios")
        
        # Asegurar que el directorio existe
        os.makedirs(audios_dir, exist_ok=True)
        
        # Guardar el archivo temporalmente
        temp_path = os.path.join(audios_dir, file.filename)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="El archivo está vacío")
            buffer.write(content)
        
        # Transcribir el audio
        try:
            # Obtener la transcripción
            transcription = transcribe_audio(file.filename)
            
            # Obtener la respuesta del bot
            bot_response = chat_with_gpt(transcription)
            
            # Convertir la respuesta a voz
            audio_response_path = text_to_speech(bot_response)
            
            # Devolver tanto el texto como el archivo de audio
            return {
                "text": {
                    "user_input": transcription,
                    "bot_response": bot_response
                },
                "audio": FileResponse(
                    audio_response_path,
                    media_type="audio/mpeg",
                    filename=f"response_{os.path.basename(audio_response_path)}"
                )
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al procesar el audio: {str(e)}")
        finally:
            # Limpiar el archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")