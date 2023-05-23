import os
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, Depends, File
from fastapi.responses import FileResponse
from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, AudioRecord

DATABASE_URL = 'postgresql://postgres:postgres@db/postgres'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/users')
def create_user(user_data: dict, db=Depends(get_db)):
    name = user_data.get('name')
    if not name:
        raise HTTPException(status_code=400, detail='Name is required')

    access_token = str(uuid.uuid4())
    user = User(name=name, access_token=access_token)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'id': user.id, 'access_token': user.access_token}


@app.post('/records')
def upload_record(user_id: int, access_token: str, record: UploadFile = File(...), db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.access_token == access_token).first()
    if not user:
        raise HTTPException(status_code=401, detail='Invalid user credentials')

    record_id = str(uuid.uuid4())
    record_path = f'{record_id}.wav'
    mp3_path = f'{record_id}.mp3'

    # Save the uploaded record as a WAV file
    with open(record_path, 'wb') as f:
        f.write(record.file.read())

    # Convert the WAV file to MP3 format
    audio = AudioSegment.from_wav(record_path)
    audio.export(mp3_path, format='mp3')

    # Save the record details in the database
    download_url = f'http://localhost:8000/record?id={record_id}&user={user_id}'
    audio_record = AudioRecord(user_id=user_id, record_id=record_id, download_url=download_url)
    db.add(audio_record)
    db.commit()

    return {'download_url': download_url}


@app.get('/record')
def download_record(id: str, user: int, db=Depends(get_db)):
    audio_record = db.query(AudioRecord).filter(AudioRecord.record_id == id, AudioRecord.user_id == user).first()
    if not audio_record:
        raise HTTPException(status_code=404, detail='Record not found')

    file_path = f'{id}.mp3'
    file_name = os.path.basename(file_path)

    headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"'
    }

    return FileResponse(file_path, headers=headers)
