# Video Optimizer Web

A modern web application to optimize videos directly from your browser, with Docker support, GPU acceleration (NVIDIA) and automatic fallback to CPU.

---

## How to use (Step by Step)

1. **Make sure you have [Docker](https://www.docker.com/) installed**
2. (Optional) For NVIDIA GPU support, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
3. **Open a terminal in the project folder**
4. Build the Docker image:
   ```sh
   docker build -t video-optimizer .
   ```
5. To run with CPU only (works on any PC):
   ```sh
   docker run -it --rm -p 5000:5000 video-optimizer
   ```
6. To run with NVIDIA GPU (if available):
   ```sh
   docker run -it --rm --gpus all -p 5000:5000 video-optimizer
   ```
7. **Open your browser and go to:** [http://localhost:5000](http://localhost:5000)

8. Upload your video, choose the options and click Optimize. The download will start automatically.

---
> **Note:** Currently, hardware acceleration is only available for NVIDIA GPUs via NVENC. There is no support for AMD or Intel acceleration due to ffmpeg and Docker ecosystem limitations.
---

## Common issues and solutions

- **Port 5000 already in use**
  - Close the program using the port or use another port (e.g. `-p 8080:5000`)
- **Docker permission error**
  - On Linux, use `sudo` before the docker command
- **Error: "Unknown encoder 'h264_nvenc'"**
  - Your machine does not have an NVIDIA GPU or the driver/NVIDIA Container Toolkit is not installed
  - Solution: Run with CPU only (see step 5)
- **Error: "Output file was not generated"**
  - The input video may be corrupted or the format is not supported
- **Interface does not change language**
  - Refresh the page and select the language again
- **Slow processing**
  - On machines without GPU, compression may be slow (especially for large videos)

---

## Features

- Upload/download videos via browser
- Compression, resize, denoise, 2-pass (CPU)
- Automatic fallback: uses NVIDIA GPU if available, otherwise CPU
- Interface in English and Portuguese
- Docker-ready

---

## Project Structure

```
Otimizador_Video/
├── Dockerfile
├── README.md
├── otimizador.py         # Optimization logic (ffmpeg)
├── webserver.py          # Flask backend
├── requeriments.txt      # Python dependencies
├── .dockerignore
├── web/
│   ├── index.html        # Frontend
│   ├── app.js
│   ├── style.css
│   ├── lang_pt.json
│   └── lang_en.json
└── temp/                 # (generated at runtime)
```

---

## Notes

- 2-pass only works with CPU
- Denoise is optional and can be enabled/disabled during optimization
- The system automatically detects available encoders
- Backend automatically falls back to CPU if GPU is not available

---

## License

MIT

---

## Credits

Developed by Victor. Based on Flask, ffmpeg-python and ffmpeg.
