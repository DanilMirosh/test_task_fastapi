from datetime import datetime
from typing import List

import requests
from fastapi import FastAPI
from pydantic import BaseModel

from database import engine, Base, SessionLocal
from models import QuizQuestion

app = FastAPI()

Base.metadata.create_all(bind=engine)


class QuestionRequest(BaseModel):
    questions_num: int


class QuizQuestionResponse(BaseModel):
    question_text: str
    answer_text: str
    created_date: datetime


@app.post('/quiz', response_model=List[QuizQuestionResponse])
def get_quiz_questions(request: QuestionRequest) -> List[QuizQuestionResponse]:
    db = SessionLocal()
    questions = []
    while len(questions) < request.questions_num:
        response = requests.get(f'https://jservice.io/api/random?count={request.questions_num}')
        response.raise_for_status()
        quiz_data = response.json()
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
            questions.append(QuizQuestionResponse(
                question_text=new_question.question_text,
                answer_text=new_question.answer_text,
                created_date=new_question.created_date
            ))
    db.close()
    return questions[-request.questions_num:]
