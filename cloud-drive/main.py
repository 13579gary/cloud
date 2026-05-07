from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
import uuid

app = FastAPI()

# =========================
# Supabase 設定（改這裡）
# =========================
SUPABASE_URL = "https://zvtdnfkargsvbvxxhhzh.supabase.co"
SUPABASE_KEY = "sb_secret_Zv699AugyAhx85g38psVWg_X3sEg7hH"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = "files"

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 📁 列出檔案 + 模擬資料夾
# =========================
@app.get("/list")
def list_files(path: str = ""):

    res = supabase.storage.from_(BUCKET).list()

    folders = set()
    files = []

    if res:
        for f in res:
            name = f["name"]

            # 模擬資料夾
            if "/" in name:
                folder = name.split("/")[0]
                folders.add(folder)
            else:
                files.append(name)

    return {
        "folders": list(folders),
        "files": files
    }

# =========================
# 📤 上傳
# =========================
@app.post("/upload")
async def upload(
    files: list[UploadFile] = File(...),
    path: str = Form("")
):

    for file in files:

        data = await file.read()

        file_name = file.filename

        if path:
            file_path = f"{path}/{file_name}"
        else:
            file_path = file_name

        # 避免重複名稱
        file_path = f"{uuid.uuid4()}_{file_path}"

        supabase.storage.from_(BUCKET).upload(
            file_path,
            data,
            {
                "content-type": file.content_type
            }
        )

    return {"ok": True}

# =========================
# 📥 下載
# =========================
@app.get("/download")
def download(path: str):

    url = supabase.storage.from_(BUCKET).get_public_url(path)

    return JSONResponse({"url": url})

# =========================
# 📦 資料夾下載（簡化）
# =========================
@app.get("/download-folder")
def download_folder(path: str):

    return {"error": "Supabase 不支援直接 ZIP（需進階處理）"}

# =========================
# ❌ 刪除
# =========================
@app.delete("/delete")
def delete(path: str):

    supabase.storage.from_(BUCKET).remove([path])

    return {"ok": True}

# =========================
# 🌐 前端
# =========================
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
