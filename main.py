import uuid
from typing import Dict, List
from uuid import UUID

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from app import shemas
from db import models, crud
from db.database import SessionLocal, engine
from app.file_storage import save_file_to_disk, delete_file_from_disk

app = FastAPI()


def get_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.put("/frame/", status_code=201)
async def save_images(images: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> Dict:
    if len(images) > 15:
        raise HTTPException(status_code=403, detail='No more than 15 images can be sent')
    request_code = uuid.uuid4()
    for image in images:
        if image.content_type != 'image/jpeg':
            raise HTTPException(status_code=403, detail='All images should have jpeg format')
        db_image = crud.create_file_data(request_code, db)
        await save_file_to_disk(image, db_image)
    return {'request_code': request_code}


@app.get("/frame/{request_code}", response_model=List[shemas.Image])
async def get_images(request_code: UUID, db: Session = Depends(get_db)) -> List:
    db_images = crud.read_files_data(request_code, db)
    if not db_images:
        raise HTTPException(status_code=404, detail="Images not found")
    return db_images


@app.delete("/frame/{request_code}")
async def delete_images(request_code: UUID, db: Session = Depends(get_db)) -> Dict:
    db_images = crud.read_files_data(request_code, db)
    if not db_images:
        raise HTTPException(status_code=404, detail="Images not found")
    for image in db_images:
        print(type(image))
        delete_file_from_disk(image)
        crud.delete_file_data(db, image)
    return {'deleted': request_code}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
