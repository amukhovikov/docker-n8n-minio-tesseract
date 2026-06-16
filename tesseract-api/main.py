import io
import httpx
from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.responses import RedirectResponse
from PIL import Image
import pytesseract


app = FastAPI()

# Укажите путь к Tesseract, если он отличается в вашем контейнере, например:
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


@app.get("/")
async def root():
    return RedirectResponse(url="/docs", status_code=302)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # Распознавание текста (можно добавить lang="rus+eng")
    text = pytesseract.image_to_string(image, lang="rus+eng")
    return {"filename": file.filename, "text": text}


# Вызов через http://ваш-fastapi-хост/ocr-by-url?url={{ $json.minio_url }}
@app.get("/ocr-by-url")
async def extract_text_by_url(url: str = Query(..., description="Прямая или Presigned URL ссылка на файл")):
    try:
        # Скачиваем файл по ссылке в память
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Не удалось скачать файл по ссылке")
        
        # Передаем байты в PIL
        image = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(image, lang="rus+eng")
        
        return {"url": url, "text": text.strip()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))