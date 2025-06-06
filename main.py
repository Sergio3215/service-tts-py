import base64
from flask import Flask, request, send_file, jsonify
from TTS.api import TTS
from TTS.utils.manage import ModelManager
import tempfile
import os

app = Flask(__name__)


# Cambia esto al modelo que quieras, pero este funciona y es liviano
MODEL_NAME = "tts_models/es/mai/tacotron2-DDC"

MODEL_MULTISPEAKER = "tts_models/multilingual/multi-dataset/_v2"

# Inicializa una única vez el modelo
tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

xtts2 = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)


VOICE_DIR = "voices"
os.makedirs(VOICE_DIR, exist_ok=True)

@app.route('/api/tts', methods=['POST'])
def tts_api():
    data = request.json
    text = data.get("text", "")
    voice_id = data.get("voice_id", None)
    if not text:
        return jsonify({"error": "Falta el texto"}), 400
    speaker_wav = None
    if voice_id:
        voice_path = os.path.join(VOICE_DIR, f"{voice_id}.wav")
        if not os.path.exists(voice_path):
            return jsonify({"error": f"voice_id inválido o archivo no existe: {voice_path}"}), 400
        speaker_wav = voice_path

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        print(f"Address: {fp.name}")
        xtts2.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            file_path=fp.name,
        )
        fp.flush()
        return send_file(fp.name, mimetype="audio/wav")

@app.route('/api/tts', methods=['GET'])
def get_api():
    return jsonify({
        "message": "API de TTS Coqui funcionando correctamente",
        "status": "ok"
    })



@app.route('/api/clone', methods=['POST'])
def clone_voice():
    # Espera que subas el archivo como "audio"
    if 'audio' not in request.files:
        return jsonify({"error": "Falta archivo de audio"}), 400
    audio = request.files['audio']

    # Creamos un id random para este sample
    voice_id = base64.urlsafe_b64encode(os.urandom(9)).decode("ascii")
    voice_path = os.path.join(VOICE_DIR, f"{voice_id}.wav")

    audio.save(voice_path)
    return jsonify({"voice_id": voice_id})



if __name__ == '__main__':
    app.run(port=5000, debug=True)
# Para ejecutar el servidor, usa el comando:
# python main.py
# Asegúrate de tener Flask y TTS instalados:
# pip install Flask TTS
# Puedes probar la API enviando una solicitud POST a http://localhost:5000/api/tts