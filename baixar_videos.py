import os
import yt_dlp

def baixar_video(url, formato="mp4", somente_audio=False, pasta_destino="videos"):
    """Baixa um vídeo da URL especificada, lidando com sites protegidos."""
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    opcoes = {
        "outtmpl": os.path.join(pasta_destino, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best" if not somente_audio else "bestaudio",
        "postprocessors": [],
        "noprogress": False,
        "quiet": False,
    }

    if somente_audio:
        opcoes["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
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
