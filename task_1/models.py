from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String)
    answer_text = Column(String)
    created_date = Column(DateTime)
