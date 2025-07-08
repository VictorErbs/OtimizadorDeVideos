import subprocess
import os
import re
import ffmpeg

def otimizar_video(
    input_path, output_path, crf=28, preset='medium', scale=None, use_gpu=False, gpu_encoder=None,
    progress_callback=None, log_callback=None, bitrate_custom=None, codec='h264', two_pass=False, denoise=False
):
    print(f"[OTIMIZADOR] input_path: {input_path}")
    print(f"[OTIMIZADOR] input_path existe: {os.path.exists(input_path)}")
    print(f"[OTIMIZADOR] output_path (antes): {output_path}")
    
    # Garante que o arquivo de entrada existe
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")
    
    # Garante extensão válida no arquivo de saída
    valid_exts = ['.mp4', '.mkv', '.webm', '.mov', '.avi']
    ext = os.path.splitext(output_path)[-1].lower()
    if ext not in valid_exts:
        output_path += '.mp4'
    
    print(f"[OTIMIZADOR] output_path (depois): {output_path}")
    
    # Seleção de codec e encoder
    codec = codec.lower()
    if codec == 'h265' or codec == 'hevc':
        cpu_codec = 'libx265'
        nvidia_codec = 'hevc_nvenc'
        amd_codec = 'hevc_amf'
        vaapi_codec = 'hevc_vaapi'
    elif codec == 'av1':
        cpu_codec = 'libaom-av1'
        nvidia_codec = 'av1_nvenc'
        amd_codec = 'av1_amf'
        vaapi_codec = 'av1_vaapi'
    else:  # h264 padrão
        cpu_codec = 'libx264'
        nvidia_codec = 'h264_nvenc'
        amd_codec = 'h264_amf'
        vaapi_codec = 'h264_vaapi'

    # Detecta encoder com fallback automático
    def encoder_exists(encoder_name):
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            return encoder_name in result.stdout
        except:
            return False
    
    def test_encoder_real(encoder_name, test_input):
        """Testa encoder com um comando real para garantir que funciona"""
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
    
    if use_gpu:
        # Lista de encoders em ordem de preferência
        gpu_encoders = []
        if gpu_encoder and gpu_encoder.lower() == 'nvidia':
            gpu_encoders = [nvidia_codec]
        elif gpu_encoder and gpu_encoder.lower() == 'amd':
            gpu_encoders = [amd_codec]
        elif gpu_encoder and gpu_encoder.lower() == 'vaapi':
            gpu_encoders = [vaapi_codec]
        else:
            # Auto-detect: tenta todos os encoders de GPU
            gpu_encoders = [nvidia_codec, amd_codec, vaapi_codec]
        
        # Testa encoders de GPU
        vcodec = cpu_codec  # fallback padrão
        for encoder in gpu_encoders:
            print(f"[LOG] Testando encoder: {encoder}")
            if encoder_exists(encoder):
                print(f"[LOG] Encoder {encoder} existe, testando funcionamento...")
                if test_encoder_real(encoder, input_path):
                    vcodec = encoder
                    print(f"[LOG] Encoder GPU selecionado: {encoder}")
                    break
                else:
                    print(f"[LOG] Encoder {encoder} existe mas não funciona, continuando...")
            else:
                print(f"[LOG] Encoder {encoder} não disponível")
        
        if vcodec == cpu_codec:
            print(f"[LOG] Nenhum encoder GPU disponível ou funcionando, usando CPU: {cpu_codec}")
    else:
        vcodec = cpu_codec
        print(f"[LOG] Usando encoder CPU: {cpu_codec}")

    # Ajusta preset conforme encoder
    if vcodec in ['h264_amf', 'h264_nvenc', 'hevc_nvenc', 'hevc_amf', 'av1_nvenc', 'av1_amf']:
        preset = 'balanced'
    elif vcodec in ['h264_vaapi', 'hevc_vaapi', 'av1_vaapi']:
        preset = None
    elif vcodec.startswith('lib'):  # CPU encoders
        if preset not in ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']:
            preset = 'medium'  # fallback para CPU
    
    # Bitrate map
    bitrate_map = {18: '6000k', 23: '3000k', 28: '1500k'}

    # Filtros
    filtros = []
    if denoise:
        filtros.append('hqdn3d')
    if scale:
        filtros.append(f'scale={scale[0]}:{scale[1]}')
    vf = ','.join(filtros) if filtros else None

    # 2-pass
    if two_pass and vcodec in ['libx264', 'libx265', 'libaom-av1']:
        # 1º Passo
        cmd1 = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', input_path,
            '-c:v', vcodec,
            '-preset', preset if preset else 'medium',
            '-b:v', bitrate_custom if bitrate_custom else bitrate_map.get(crf, '3000k'),
            '-pass', '1', '-an', '-f', 'null', '/dev/null'
        ]
        if vf:
            cmd1 += ['-vf', vf]
        print('Comando FFmpeg 1-pass:', ' '.join(cmd1))
        subprocess.run(cmd1, check=True)
        
        # 2º Passo
        cmd2 = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', input_path,
            '-c:v', vcodec,
            '-preset', preset if preset else 'medium',
            '-b:v', bitrate_custom if bitrate_custom else bitrate_map.get(crf, '3000k'),
            '-pass', '2', '-c:a', 'aac', '-movflags', 'faststart', output_path
        ]
        if vf:
            cmd2 += ['-vf', vf]
        print('Comando FFmpeg 2-pass:', ' '.join(cmd2))
        subprocess.run(cmd2, check=True)
        return

    # Validação final do encoder
    if not encoder_exists(vcodec):
        print(f"[WARNING] Encoder {vcodec} não disponível, usando libx264")
        vcodec = 'libx264'
        preset = 'medium'

    # 1-pass normal
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', input_path,
        '-c:v', vcodec,
    ]
    if vcodec.startswith('lib'):
        cmd += ['-crf', str(crf)]
    else:
        bitrate = bitrate_custom if bitrate_custom else bitrate_map.get(crf, '3000k')
        cmd += ['-b:v', bitrate, '-maxrate', bitrate, '-bufsize', str(int(bitrate[:-1])*2)+'k' if bitrate[-1] == 'k' else str(int(float(bitrate[:-1])*2000))+'k']
    if preset:
        cmd += ['-preset', preset]
    if vf:
        cmd += ['-vf', vf]
    cmd += [
        '-c:a', 'aac',
        '-movflags', 'faststart',
        output_path
    ]
    
    print(f"[LOG] Codec selecionado: {codec}")
    print(f"[LOG] Encoder ffmpeg: {vcodec}")
    print(f"[LOG] Preset: {preset}")
    print(f"[LOG] CRF: {crf}")
    print(f"[LOG] Bitrate customizado: {bitrate_custom}")
    print(f"[LOG] Two-pass: {two_pass}")
    print(f"[LOG] Denoise: {denoise}")
    print(f"[LOG] Resize: {scale}")
    print(f"[LOG] Comando FFmpeg: {' '.join(cmd)}")
    
    # Primeira tentativa com encoder selecionado
    try:
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, universal_newlines=True, bufsize=1)
        ffmpeg_stderr = []
        for line in process.stderr:
            ffmpeg_stderr.append(line)
            if log_callback:
                log_callback(line)
        process.wait()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, ''.join(ffmpeg_stderr))
            
    except subprocess.CalledProcessError as e:
        error_output = str(e.stderr) if e.stderr else str(e.output)
        
        # Se falhou com encoder GPU, tenta novamente com CPU
        if vcodec != 'libx264' and ('not available' in error_output.lower() or 'unknown encoder' in error_output.lower() or 'no such file' in error_output.lower()):
            print(f"[WARNING] Encoder {vcodec} falhou, tentando fallback para libx264")
            
            # Reconstroi comando com libx264
            cmd_fallback = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', input_path,
                '-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium'
            ]
            if vf:
                cmd_fallback += ['-vf', vf]
            cmd_fallback += ['-c:a', 'aac', '-movflags', 'faststart', output_path]
            
            print(f"[LOG] Comando FFmpeg (fallback): {' '.join(cmd_fallback)}")
            
            # Segunda tentativa com libx264
            process = subprocess.Popen(cmd_fallback, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, universal_newlines=True, bufsize=1)
            ffmpeg_stderr = []
            for line in process.stderr:
                ffmpeg_stderr.append(line)
                if log_callback:
                    log_callback(line)
            process.wait()
            
            if process.returncode != 0:
                raise RuntimeError('Erro ao rodar ffmpeg com fallback.\n' + ''.join(ffmpeg_stderr))
        else:
            raise RuntimeError('Erro ao rodar ffmpeg.\n' + error_output)
    
    # Verifica se o arquivo de saída foi criado
    if not os.path.exists(output_path):
        raise RuntimeError('Arquivo de saída não foi gerado pelo ffmpeg')

def tamanho_arquivo(path):
    return os.path.getsize(path) / 1024 / 1024  # MB