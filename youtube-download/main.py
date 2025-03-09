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
        # Manually specify the path to the Chrome cookie database
        cookie_path = os.path.expanduser('~') + '/AppData/Local/Google/Chrome/User Data/Default/Cookies'
        return browser_cookie3.chrome(cookie_file=cookie_path)
    except Exception as e:
        print(f"Error accessing cookies: {e}")
        return None

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/info/{video_id}")
async def get_video_info(video_id: str):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'cookies': COOKIES_FILE,
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo+bestaudio/best',  # 修改格式选择逻辑
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            # 过滤和处理格式
            for f in info['formats']:
                # 只添加有视频流的格式
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    formats.append({
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'quality': f.get('quality', 0),
                        'filesize': f.get('filesize', 0),
                        'resolution': f.get('resolution', 'N/A'),
                        'format_note': f.get('format_note', ''),
                    })
            
            # 按质量排序
            formats.sort(key=lambda x: x['quality'], reverse=True)
            
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
        url = f"https://www.youtube.com/watch?v={video_id}"
        output_path = DOWNLOAD_DIR / f"{video_id}.%(ext)s"
        
        ydl_opts = {
            'format': format_id,
            'outtmpl': str(output_path),
            'cookies': COOKIES_FILE,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            # 添加更多选项以提高稳定性
            'ignoreerrors': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'prefer_ffmpeg': True,
            'quiet': True,
            'no_warnings': True,
            # 如果下载速度慢，可以取消注释下面的选项
            # 'external_downloader': 'aria2c',
            # 'external_downloader_args': ['--min-split-size=1M', '--max-connection-per-server=16'],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # 确保文件存在
            if not os.path.exists(filename):
                raise HTTPException(status_code=404, detail="Download failed")
                
            # 创建流式响应
            def iterfile():
                with open(filename, mode="rb") as file_like:
                    yield from file_like
                # 下载完成后删除文件
                try:
                    os.remove(filename)
                except:
                    pass

            # 获取文件名（不包含路径）
            final_filename = os.path.basename(filename)
            
            return StreamingResponse(
                iterfile(),
                media_type="video/mp4",
                headers={
                    "Content-Disposition": f'attachment; filename="{final_filename}"'
                }
            )
            
    except Exception as e:
        # 确保出错时也能清理文件
        try:
            if 'filename' in locals():
                os.remove(filename)
        except:
            pass
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 