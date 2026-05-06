from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil

app = FastAPI()

BASE_DIR = "uploads"
os.makedirs(BASE_DIR, exist_ok=True)

# ✅ CORS（雲端必備）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌐 前端直接上線
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# 📤 上傳檔案 / 資料夾
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):

    for f in files:
        save_path = os.path.join(BASE_DIR, f.filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)

    return {"ok": True}


# 📁 檔案列表
@app.get("/list")
def list_dir(path: str = ""):

    target = os.path.join(BASE_DIR, path)

    result = {"folders": [], "files": []}

    if not os.path.exists(target):
        return result

    for name in os.listdir(target):
        full = os.path.join(target, name)

        if os.path.isdir(full):
            result["folders"].append(name)
        else:
            result["files"].append(name)

    return result


# 📥 下載
@app.get("/download")
def download(path: str):
    return FileResponse(os.path.join(BASE_DIR, path))


# ❌ 刪除（檔案 + 資料夾）
@app.delete("/delete")
def delete(path: str):

    full = os.path.join(BASE_DIR, path)

    if os.path.isdir(full):
        shutil.rmtree(full)
        return {"ok": True, "type": "folder"}

    if os.path.exists(full):
        os.remove(full)
        return {"ok": True, "type": "file"}

    return {"ok": False}
