from flask import Flask, request, send_file, jsonify, send_from_directory
from otimizador import otimizar_video
import os, tempfile, uuid, subprocess

app = Flask(__name__, static_folder='web', template_folder='web')

# Cria diretório temporário dentro do container
TEMP_DIR = '/app/temp'
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/web/<path:path>')
def send_static(path):
    return app.send_static_file(path)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return jsonify({'ok': False, 'error': 'Nenhum arquivo enviado'}), 400
    
    f = request.files['video']
    if f.filename == '':
        return jsonify({'ok': False, 'error': 'Nenhum arquivo selecionado'}), 400
    
    # Garante extensão válida
    ext = os.path.splitext(f.filename)[-1].lower()
    if not ext or ext not in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']:
        ext = '.mp4'
    
    temp_filename = str(uuid.uuid4()) + ext
    temp_path = os.path.join(TEMP_DIR, temp_filename)
    f.save(temp_path)
    
    print(f"[UPLOAD] Arquivo salvo: {temp_path}")
    print(f"[UPLOAD] Arquivo existe: {os.path.exists(temp_path)}")
    print(f"[UPLOAD] Tamanho do arquivo: {os.path.getsize(temp_path) if os.path.exists(temp_path) else 'N/A'} bytes")
    
    return jsonify({'ok': True, 'temp_path': temp_filename})

@app.route('/otimizar', methods=['POST'])
def otimizar():
    data = request.json
    
    if not data or 'temp_path' not in data:
        return jsonify({'ok': False, 'error': 'Parâmetros inválidos'}), 400
    
    input_path = os.path.join(TEMP_DIR, data['temp_path'])
    
    if not os.path.exists(input_path):
        print(f"[ERRO] Arquivo não encontrado: {input_path}")
        return jsonify({'ok': False, 'error': 'Arquivo não encontrado'}), 404
    
    output_filename = os.path.splitext(data['temp_path'])[0] + '_otimizado.mp4'
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    print(f"[OTIMIZAR] input_path: {input_path}")
    print(f"[OTIMIZAR] output_path: {output_path}")
    print(f"[OTIMIZAR] Arquivo de entrada existe: {os.path.exists(input_path)}")
    
    try:
        otimizar_video(
            input_path, output_path,
            crf=data.get('crf', 23),
            use_gpu=data.get('gpu', 'cpu').lower() != 'cpu',
            gpu_encoder=data.get('gpu'),
            bitrate_custom=data.get('bitrate_custom'),
            codec=data.get('codec', 'h264'),
            preset=data.get('preset', 'medium'),
            two_pass=data.get('two_pass', False),
            denoise=data.get('denoise', False),
            scale=data.get('resize', None)
        )
        
        if not os.path.exists(output_path):
            raise Exception("Arquivo otimizado não foi gerado")
        
        print(f"[OTIMIZAR] Enviando arquivo: {output_path}")
        
        # Envia o arquivo e remove depois
        def remove_files():
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass
        
        response = send_file(output_path, as_attachment=True, download_name=output_filename)
        
        # Agenda remoção dos arquivos após envio
        import threading
        threading.Timer(5.0, remove_files).start()
        
        return response
        
    except Exception as e:
        print(f"[ERRO OTIMIZAR] {e}")
        # Remove arquivo de entrada em caso de erro
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/encoders', methods=['GET'])
def get_available_encoders():
    """Retorna lista de encoders GPU disponíveis"""
    def encoder_exists(encoder_name):
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            return encoder_name in result.stdout
        except:
            return False
    
    def test_encoder_works(encoder_name):
        """Testa se encoder realmente funciona"""
        try:
            test_cmd = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'panic',
                '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                '-c:v', encoder_name, '-frames:v', '1', '-f', 'null', '-'
            ]
            result = subprocess.run(test_cmd, capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    available = {
        'nvidia': False,
        'amd': False,
        'vaapi': False
    }
    
    # Testa encoders H.264
    nvidia_encoders = ['h264_nvenc']
    amd_encoders = ['h264_amf']
    vaapi_encoders = ['h264_vaapi']
    
    for encoder in nvidia_encoders:
        if encoder_exists(encoder) and test_encoder_works(encoder):
            available['nvidia'] = True
            break
    
    for encoder in amd_encoders:
        if encoder_exists(encoder) and test_encoder_works(encoder):
            available['amd'] = True
            break
    
    for encoder in vaapi_encoders:
        if encoder_exists(encoder) and test_encoder_works(encoder):
            available['vaapi'] = True
            break
    
    print(f"[ENCODERS] Disponíveis: {available}")
    return jsonify(available)

if __name__ == '__main__':
    import sys
    print("\n\033[92mAcesse a interface web em: http://localhost:5000\033[0m\n", flush=True, file=sys.stderr)
    app.run(host='0.0.0.0', port=5000, debug=True)
