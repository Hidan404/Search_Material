import os
import yt_dlp
import psutil

# 🔹 Reduzir prioridade do processo para evitar travamentos
# 🔹  realizei testes de performance estava travando antes deu trablaho mas deu certo
if os.name == "nt":  # Windows
    p = psutil.Process(os.getpid())
    p.nice(psutil.IDLE_PRIORITY_CLASS)
else:  # Linux
    os.nice(10)

def baixar_video(url, formato="mp4", somente_audio=False, pasta_destino="videos"):
    """Baixa um vídeo da URL especificada, minimizando o uso de CPU e RAM."""
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    opcoes = {
        "outtmpl": os.path.join(pasta_destino, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best" if not somente_audio else "bestaudio",
        "postprocessors": [],
        "noprogress": True,  # Desativa barra de progresso para reduzir consumo de CPU
        "quiet": True,  # Modo silencioso para evitar logs excessivos
        "concurrent_fragment_downloads": 1,  # Reduz uso de RAM
    }

    if somente_audio:
        opcoes["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128"  # Qualidade reduzida para menos processamento
        })

    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            ydl.download([url])
            
        print("\n[✅] Download concluído!")
    except Exception as e:
        print(f"\n[❌] Erro ao baixar vídeo: {e}")

if __name__ == "__main__":
    url = input("Digite a URL do vídeo: ").strip()
    escolha = input("Deseja baixar [1] Vídeo ou [2] Somente Áudio? (1/2): ").strip()

    baixar_video(url, somente_audio=(escolha == "2"))

