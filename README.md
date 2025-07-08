# Otimizador de Vídeos Web

Uma aplicação web moderna para otimizar vídeos direto do navegador, com suporte a Docker, aceleração por GPU (NVIDIA) e fallback automático para CPU.

---

## Como usar (Passo a Passo)

1. **Tenha o [Docker](https://www.docker.com/) instalado**
2. (Opcional) Para usar GPU NVIDIA, instale o [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
3. **Abra o terminal na pasta do projeto**
4. Rode o comando abaixo para criar a imagem:
   ```sh
   docker build -t otimizador-video .
   ```
5. Para rodar só com CPU (funciona em qualquer PC):
   ```sh
   docker run -it --rm -p 5000:5000 otimizador-video
   ```
6. Para rodar com GPU NVIDIA (se disponível):
   ```sh
   docker run -it --rm --gpus all -p 5000:5000 otimizador-video
   ```
7. **Acesse no navegador:** [http://localhost:5000](http://localhost:5000)
8. Faça upload do vídeo, escolha as opções e clique em Otimizar. O download inicia automaticamente.

---

## Possíveis problemas e soluções

- **Porta 5000 já está em uso**
  - Feche o programa que está usando a porta ou troque para outra porta (ex: `-p 8080:5000`)
- **Erro de permissão no Docker**
  - No Linux, use `sudo` antes do comando docker
- **Erro: "Unknown encoder 'h264_nvenc'"**
  - Sua máquina não tem GPU NVIDIA ou o driver/NVIDIA Container Toolkit não está instalado
  - Solução: Rode só com CPU (veja passo 5)
- **Erro: "Arquivo não foi gerado"**
  - O vídeo de entrada pode estar corrompido ou o formato não é suportado
- **Interface não muda de idioma**
  - Atualize a página, selecione o idioma novamente
- **Demora para processar**
  - Em máquinas sem GPU, a compressão pode ser lenta (especialmente em vídeos grandes)

---

## Recursos

- Upload/download de vídeos via navegador
- Compressão, resize, denoise, 2-pass (CPU)
- Fallback automático: usa GPU NVIDIA se disponível, senão CPU
- Interface em português e inglês
- Docker-ready

---

## Estrutura do Projeto

```
Otimizador_Video/
├── Dockerfile
├── README.md
├── otimizador.py         # Lógica de otimização (ffmpeg)
├── webserver.py          # Backend Flask
├── requeriments.txt      # Dependências Python
├── .dockerignore
├── web/
│   ├── index.html        # Frontend
│   ├── app.js
│   ├── style.css
│   ├── lang_pt.json
│   └── lang_en.json
└── temp/                 # (gerado em runtime)
```

---

## Observações

- 2-pass só funciona com CPU
- Denoise funciona sempre
- O sistema detecta automaticamente os encoders disponíveis
- O backend faz fallback automático para CPU se GPU não estiver disponível

---

## Licença

MIT

---

## Créditos

Desenvolvido por Victor. Baseado em Flask, ffmpeg-python e ffmpeg.
