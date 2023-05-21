import uuid

from fastapi import UploadFile, HTTPException, FastAPI
from pydantic import BaseModel
import ffmpeg
from fastapi.responses import FileResponse

from models import User, AudioRecord

SessionLocal = 1
app = FastAPI()


class CreateUserRequest(BaseModel):
    name: str


class CreateUserResponse(BaseModel):
    id: int
    access_token: str


class AddAudioRequest(BaseModel):
    user_id: int
    access_token: str
    audio: UploadFile


class AddAudioResponse(BaseModel):
    url: str


class GetAudioResponse(BaseModel):
    url: str


def convert_to_mp3(input_filename, output_filename):
    ffmpeg.input(input_filename).output(output_filename, audio_bitrate='128k').run()


@app.post('/users', response_model=CreateUserResponse)
def create_user(user_request: CreateUserRequest):
    session = SessionLocal()
    user = User(name=user_request.name, access_token=str(uuid.uuid4()))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {'id': user.id, 'access_token': user.access_token}


@app.post('/audio', response_model=AddAudioResponse)
def add_audio(audio_request: AddAudioRequest):
    session = SessionLocal()
    user = session.query(User).filter(User.id == audio_request.user_id,
                                      User.access_token == audio_request.access_token).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    audio = audio_request.audio
    audio_id = str(uuid.uuid4())

    # Save the WAV file
    wav_filename = f'recordings/{audio_id}.wav'
    with open(wav_filename, 'wb') as f:
        f.write(audio.file.read())

    # Convert to MP3
    mp3_filename = f'recordings/{audio_id}.mp3'
    convert_to_mp3(wav_filename, mp3_filename)

    # Save the record in the database
    record = AudioRecord(user_id=user.id, filename=wav_filename, mp3_filename=mp3_filename)
    session.add(record)
    session.commit()
    session.refresh(record)

    # Return the download URL
    download_url = f'http://localhost:8000/audio/{record.id}'
    return {'url': download_url}


@app.get('/audio/{record_id}', response_model=GetAudioResponse)
def get_audio(record_id: int):
    session = SessionLocal()
    record = session.query(AudioRecord).filter(AudioRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail='Audio record not found')

    return {'url': record.mp3_filename}


@app.get('/audio/download/{record_id}')
def download_audio(record_id: int):
    session = SessionLocal()
    record = session.query(AudioRecord).filter(AudioRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail='Audio record not found')

    return FileResponse(record.mp3_filename, media_type='audio/mpeg')
