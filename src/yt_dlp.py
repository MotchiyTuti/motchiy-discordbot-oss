import os
import subprocess
from .util import select_option, random_path, send


FIREFOX_COOKIE_PATH = 'cookies.txt'


async def download(args):
    options, url = select_option(args)
    dir_name = random_path()
    out_dir = output_dir(dir_name)

    def _download(mode_type, text, output):
        if mode_type == "audio":
            download_youtube_audio_as_wav(text, output)
        elif mode_type == "audio_lite":
            download_youtube_audio_as_mp3(text, output)
        elif mode_type == "video":
            download_youtube_video_as_avi(text, output)
        elif mode_type == "audio_video":
            download_youtube_as_mp4(text, output)

    # optionsの内容で分岐
    if 'audio' in options:
        mode = "audio_lite" if 'lite' in options else "audio"
    elif 'video' in options:
        mode = "video"
    else:
        mode = "audio_video"

    for line in url:
        _download(mode, line.strip(), out_dir)

    # ダウンロードURLをチャットへ送信
    download_url = dl_url(dir_name)
    await send.message(f"Download URL: {download_url}", None)
    

def output_dir(dir_name):
    dir = f"/var/www/html/yt-dlp/{dir_name}/"
    os.makedirs(dir, exist_ok=True)
    return dir


def dl_url(dir_name):
    url = f'https://motchiy.f5.si/yt-dlp/{dir_name}/'
    return url


def download_youtube_audio_as_wav(url, output):
    # wav download
    cmd = [
        "yt-dlp",
        "--cookies", FIREFOX_COOKIE_PATH,
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", os.path.join(output, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(cmd)

def download_youtube_video_as_avi(url, output):
    # avi download
    cmd = [
        "yt-dlp",
        "--cookies", FIREFOX_COOKIE_PATH,
        "-f", "bestvideo[height<=1080]",
        "-o", os.path.join(output, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(cmd)

def download_youtube_audio_as_mp3(url, output):
    # mp3 download
    cmd = [
        "yt-dlp",
        "--cookies", FIREFOX_COOKIE_PATH,
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "5",
        "-o", os.path.join(output, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(cmd)

def download_youtube_as_mp4(url, output):
    # mp4 download
    cmd = [
        "yt-dlp",
        "--cookies", FIREFOX_COOKIE_PATH,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "--merge-output-format", "mp4",
        "-o", os.path.join(output, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(cmd)