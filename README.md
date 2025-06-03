## Endpoints

1. /ask

Maneja preguntas por texto. Recibe un texto y devuelve la respuesta del bot en texto. Útil para pruebas o para cuando el usuario prefiere escribir

2. /transcribe

Endpoint principal para interacción por voz.
- Recibe un archivo de audio del usuario
- Transcribe el audio a texto usando el modelo Whisper
- Obtiene la respuesta del bot usando GPT
- Convierte la respuesta del bot usando TTS-1
- Devuelve tanto el texto como la ruta del audio generado

3. /audio/{filename}

Endpoint sirve los archivos de audio generados. permite reproducir la respuesta de voz del bot.

## Flujo para bot de asistencia

1. El usuario graba su voz
2. Se envía el audio al endpoint /transcribe
3. El bot transcribe lo que ha dicho el usuario, genera una respuesta y convierte esa respuesta a voz
4. La aplicación puede mostrar el texto de la conversación y también reproducir la respuesta de voz usando el endpoint /audio