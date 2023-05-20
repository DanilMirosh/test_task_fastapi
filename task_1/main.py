from datetime import datetime

import requests
from fastapi import FastAPI
from pydantic import BaseModel

from database import engine, Base, SessionLocal
from models import QuizQuestion

app = FastAPI()

Base.metadata.create_all(bind=engine)


class QuestionRequest(BaseModel):
    questions_num: int


@app.post('/quiz')
def get_quiz_questions(request: QuestionRequest) -> list[QuizQuestion]:
    db = SessionLocal()
    questions: list[QuizQuestion] = []
    while len(questions) < request.questions_num:
        response = requests.get(f'https://jservice.io/api/random?count={request.questions_num}')
        response.raise_for_status()
        quiz_data: list[dict] = response.json()
        for data in quiz_data:
            question = db.query(QuizQuestion).filter_by(question_text=data['question']).first()
            if question:
                continue
            new_question = QuizQuestion(
                question_text=data['question'],
                answer_text=data['answer'],
                created_date=datetime.now()
            )
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
            questions.append(new_question)
    db.close()
    return questions[-request.questions_num:]
