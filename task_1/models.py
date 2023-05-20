from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'

    id: int = Column(Integer, primary_key=True, index=True)
    question_text: str = Column(String)
    answer_text: str = Column(String)
    created_date: datetime = Column(DateTime)
