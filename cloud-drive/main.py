from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import zipfile

app = FastAPI()

BASE_DIR = "uploads"
os.makedirs(BASE_DIR, exist_ok=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 列表
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


# 📤 上傳
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    for f in files:
        path = os.path.join(BASE_DIR, f.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)

    return {"ok": True}


# 📥 下載檔案
@app.get("/download")
def download(path: str):
    return FileResponse(os.path.join(BASE_DIR, path))


# 📦 下載資料夾（ZIP）
@app.get("/download-folder")
def download_folder(path: str):
    folder_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(folder_path):
        return {"error": "not found"}

    zip_name = f"{path.replace('/', '_') or 'root'}.zip"
    zip_path = os.path.join(BASE_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)

    return FileResponse(zip_path, filename=zip_name)


# ❌ 刪除
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


# 🌐 前端（一定要最後）
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
