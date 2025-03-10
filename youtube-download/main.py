from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import yt_dlp
import asyncio
import os
from pathlib import Path
import browser_cookie3

app = FastAPI()

# 配置模板和静态文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 创建临时下载目录
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# 获取 Chrome 浏览器的 YouTube cookies
def get_youtube_cookies():
    try:
        # 根据操作系统获取 Chrome cookie 路径
        if os.name == 'nt':  # Windows
            cookie_path = os.path.expanduser('~') + '/AppData/Local/Google/Chrome/User Data/Default/Cookies'
        elif os.name == 'posix':  # macOS
            cookie_path = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')
        else:  # Linux
            cookie_path = os.path.expanduser('~/.config/google-chrome/Default/Cookies')
            
        return browser_cookie3.chrome(cookie_file=cookie_path, domain_name='.youtube.com')
    except Exception as e:
        print(f"Error accessing cookies: {e}")
        return None

# 配置 yt-dlp 选项
def get_ydl_opts():
    cookies = get_youtube_cookies()
    return {
        'format': 'best',
        'cookiesfrombrowser': ('chrome',),  # 使用 Chrome 浏览器的 cookies
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/info/{video_id}")
async def get_video_info(video_id: str):
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # 处理视频格式
            formats = []
            for f in info['formats']:
                if 'filesize' in f and f['filesize'] and 'resolution' in f:
                    formats.append({
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'resolution': f['resolution'],
                        'filesize': f['filesize']
                    })
            
            return {
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'formats': formats
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/{video_id}/{format_id}")
async def download_video(video_id: str, format_id: str):
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_template = str(DOWNLOAD_DIR / f"{video_id}.%(ext)s")

        # 下载配置
        ydl_opts = {
            'format': format_id if format_id != 'best' else 'bestvideo+bestaudio/best',
            'cookiesfrombrowser': ('chrome',),
            'quiet': True,
            'no_warnings': True,
            'outtmpl': output_template,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            },
            # 更新 extractor 参数
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],  # 同时使用 android 和 web 客户端
                    'player_skip': [],
                    'formats': 'all',
                }
            },
            # 下载设置
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keepvideo': False,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        # 尝试下载视频
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
        except Exception as e:
            if "Requested format is not available" in str(e):
                # 如果请求的格式不可用，回退到最佳质量
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    filename = ydl.prepare_filename(info)
            else:
                raise e

        # 如果文件名不是以 .mp4 结尾，寻找转换后的文件
        if not filename.endswith('.mp4'):
            base_path = Path(filename).with_suffix('')
            mp4_path = str(base_path) + '.mp4'
            if os.path.exists(mp4_path):
                filename = mp4_path

        if not os.path.exists(filename):
            raise Exception("Download failed - file not found")

        # 创建文件流
        def iterfile():
            try:
                with open(filename, 'rb') as f:
                    yield from f
            finally:
                # 清理文件
                if os.path.exists(filename):
                    os.unlink(filename)

        headers = {
            'Content-Disposition': f'attachment; filename="{os.path.basename(filename)}"',
            'Access-Control-Allow-Origin': '*'
        }

        return StreamingResponse(iterfile(), headers=headers, media_type='application/octet-stream')

    except Exception as e:
        # 清理任何临时文件
        for file in DOWNLOAD_DIR.glob(f"{video_id}.*"):
            try:
                os.unlink(file)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 