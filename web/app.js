let tempPath = null;
let lang = 'pt';
let textos = {};
let availableEncoders = null;

function carregarTextos() {
    fetch('/web/lang_' + lang + '.json')
        .then(r => r.json())
        .then(t => {
            textos = t;
            document.getElementById('label_otimizacao').textContent = textos.optimization || 'Otimização';
            document.getElementById('label_gpu').textContent = textos.accelerator || 'Acelerador';
            document.getElementById('btn_otimizar').textContent = textos.optimize_selected || 'Otimizar';
            document.getElementById('lang_select').options[0].text = '🌐 Language / Idioma';
            document.getElementById('label_codec').textContent = textos.codec || 'Codec';
            document.getElementById('label_preset').textContent = textos.preset || 'Preset';
            document.getElementById('label_resize').textContent = textos.resize || 'Resize:';
            atualizarOpcoesOtimizacao();
            atualizarOpcoesGPU();
            atualizarTextosFixos();
        })
        .catch(() => {
            // Se não conseguir carregar textos, usa valores padrão
            atualizarOpcoesOtimizacao();
            atualizarOpcoesGPU();
            atualizarTextosFixos();
        });
}

function carregarEncodersDisponiveis() {
    fetch('/encoders')
        .then(r => r.json())
        .then(encoders => {
            availableEncoders = encoders;
            console.log('Encoders disponíveis:', encoders);
            atualizarOpcoesGPU();
        })
        .catch(err => {
            console.error('Erro ao carregar encoders:', err);
            // Assume que apenas CPU está disponível
            availableEncoders = { nvidia: false, amd: false, vaapi: false };
            atualizarOpcoesGPU();
        });
}

function atualizarOpcoesGPU() {
    const select = document.getElementById('gpu');
    if (!select || !availableEncoders) return;
    
    // Limpa opções atuais
    select.innerHTML = '';
    
    // Sempre adiciona CPU
    select.appendChild(new Option('CPU', 'cpu'));
    // Adiciona NVIDIA se disponível
    if (availableEncoders.nvidia) {
        select.appendChild(new Option('NVIDIA', 'nvidia'));
    }
    
    // Se nenhum encoder GPU disponível, mostra aviso
    if (!availableEncoders.nvidia && !availableEncoders.amd && !availableEncoders.vaapi) {
        console.log('Nenhum encoder GPU disponível, apenas CPU será usado');
    }
}

function selecionarIdioma(sel) {
    lang = sel.value;
    carregarTextos();
}

function atualizarTextosFixos() {
    if (!textos) return;
    if (document.getElementById('main_title')) document.getElementById('main_title').textContent = textos.main_title || '';
    if (document.getElementById('main_title_span')) document.getElementById('main_title_span').textContent = textos.main_title || '';
    if (document.getElementById('upload_title')) document.getElementById('upload_title').textContent = textos.upload_title || '';
    if (document.getElementById('upload_desc')) document.getElementById('upload_desc').textContent = textos.upload_desc || '';
    if (document.getElementById('how_title')) document.getElementById('how_title').textContent = textos.how_title || '';
    if (document.getElementById('how_codec')) document.getElementById('how_codec').innerHTML = '<b>Codec:</b> ' + (textos.how_codec || '');
    if (document.getElementById('how_quality')) document.getElementById('how_quality').innerHTML = '<b>Qualidade (CRF):</b> ' + (textos.how_quality || '');
    if (document.getElementById('how_preset')) document.getElementById('how_preset').innerHTML = '<b>Preset:</b> ' + (textos.how_preset || '');
    if (document.getElementById('how_accelerator')) document.getElementById('how_accelerator').innerHTML = '<b>Acelerador:</b> ' + (textos.how_accelerator || '');
    if (document.getElementById('how_2pass')) document.getElementById('how_2pass').innerHTML = '<b>Two-pass:</b> ' + (textos.how_2pass || '');
    if (document.getElementById('how_denoise')) document.getElementById('how_denoise').innerHTML = '<b>Denoise:</b> ' + (textos.how_denoise || '');
    if (document.getElementById('how_resize')) document.getElementById('how_resize').innerHTML = '<b>Resize:</b> ' + (textos.how_resize || '');
    if (document.getElementById('upload_button')) document.getElementById('upload_button').textContent = textos.upload_button || 'Upload';
    if (document.getElementById('btn_otimizar')) document.getElementById('btn_otimizar').textContent = textos.optimize_button || 'Otimizar';
    if (document.getElementById('resize_w')) document.getElementById('resize_w').placeholder = textos.resize_placeholder_w || 'Largura';
    if (document.getElementById('resize_h')) document.getElementById('resize_h').placeholder = textos.resize_placeholder_h || 'Altura';
    if (document.getElementById('denoise_label')) document.getElementById('denoise_label').textContent = textos.denoise_label || 'Denoise (reduzir ruído)';
    if (document.getElementById('twopass_label')) document.getElementById('twopass_label').textContent = textos.twopass_label || 'Two-pass (2-pass)';
    if (document.getElementById('footer_text')) document.getElementById('footer_text').textContent = textos.footer || '';
}

function atualizarOpcoesOtimizacao() {
    const select = document.getElementById('crf');
    if (!select) return;
    select.innerHTML = '';
    const opcoes = [
        { value: '18', label: textos.high_quality || 'Alta Qualidade (Grande)' },
        { value: '23', label: textos.medium_quality || 'Qualidade Média (Equilíbrio)' },
        { value: '28', label: textos.low_quality || 'Baixa Qualidade (Pequeno)' },
        { value: 'custom', label: textos.custom_bitrate || 'Bitrate Personalizado' }
    ];
    opcoes.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.label;
        select.appendChild(option);
    });
    
    let customInput = document.getElementById('bitrate_custom');
    if (!customInput) {
        customInput = document.createElement('input');
        customInput.type = 'text';
        customInput.id = 'bitrate_custom';
        customInput.placeholder = 'ex: 3000k';
        customInput.style.display = 'none';
        customInput.style.marginTop = '0.5rem';
        select.parentNode.appendChild(customInput);
    }
    
    select.onchange = function() {
        if (select.value === 'custom') {
            customInput.style.display = '';
        } else {
            customInput.style.display = 'none';
        }
    };
}

function enviarVideo() {
    const fileInput = document.getElementById('upload_video');
    if (!fileInput.files.length) {
        alert('Selecione um vídeo primeiro!');
        return;
    }
    
    const formData = new FormData();
    formData.append('video', fileInput.files[0]);
    
    document.getElementById('relatorio').textContent = 'Enviando vídeo...';
    
    fetch('/upload', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(res => {
            if (res.ok) {
                tempPath = res.temp_path;
                document.getElementById('relatorio').textContent = 'Upload concluído! Agora você pode otimizar o vídeo.';
                document.getElementById('btn_otimizar').disabled = false;
            } else {
                alert('Erro no upload: ' + (res.error || 'Erro desconhecido'));
                document.getElementById('relatorio').textContent = 'Erro no upload.';
            }
        })
        .catch(err => {
            console.error('Erro no upload:', err);
            alert('Erro no upload: ' + err.message);
            document.getElementById('relatorio').textContent = 'Erro no upload.';
        });
}

function otimizarSelecionado() {
    if (!tempPath) {
        alert('Envie um vídeo antes de otimizar!');
        return;
    }
    
    let crf = document.getElementById('crf').value;
    let bitrate_custom = null;
    if (crf === 'custom') {
        bitrate_custom = document.getElementById('bitrate_custom').value;
        if (!bitrate_custom) {
            alert('Digite o bitrate personalizado!');
            return;
        }
        crf = 23;
    }
    
    const gpu = document.getElementById('gpu').value;
    const codec = document.getElementById('codec').value;
    const preset = document.getElementById('preset').value;
    const two_pass = document.getElementById('two_pass').checked;
    const denoise = document.getElementById('denoise').checked;
    
    let resize = null;
    const rw = parseInt(document.getElementById('resize_w').value);
    const rh = parseInt(document.getElementById('resize_h').value);
    if (rw > 0 && rh > 0) resize = [rw, rh];
    
    document.getElementById('relatorio').textContent = 'Otimizando vídeo... Aguarde.';
    document.getElementById('spinner').style.display = 'block';
    document.getElementById('btn_otimizar').disabled = true;
    
    fetch('/otimizar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            temp_path: tempPath,
            crf: parseInt(crf),
            gpu,
            bitrate_custom,
            codec,
            preset,
            two_pass,
            denoise,
            resize
        })
    })
    .then(async response => {
        document.getElementById('spinner').style.display = 'none';
        document.getElementById('btn_otimizar').disabled = false;
        
        if (response.ok && response.headers.get('Content-Disposition')) {
            // Download automático do arquivo otimizado
            const blob = await response.blob();
            const filename = response.headers.get('Content-Disposition')
                .split('filename=')[1]
                .replace(/"/g, '');
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            
            document.getElementById('relatorio').textContent = 'Otimização concluída! Download iniciado.';
            
            // Reset para novo upload
            tempPath = null;
            document.getElementById('upload_video').value = '';
            
        } else {
            const res = await response.json();
            document.getElementById('relatorio').textContent = 'Erro: ' + (res.error || 'Erro na otimização');
            console.error('Erro na otimização:', res);
        }
    })
    .catch(err => {
        document.getElementById('spinner').style.display = 'none';
        document.getElementById('btn_otimizar').disabled = false;
        document.getElementById('relatorio').textContent = 'Erro na otimização: ' + err.message;
        console.error('Erro na otimização:', err);
    });
}

window.onload = () => {
    carregarEncodersDisponiveis();
    carregarTextos();
    document.getElementById('btn_otimizar').disabled = true;
};
