from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
import json


router = APIRouter(
    prefix="/questions",
    tags=['Questions']
)

 
@router.get("/", response_model=List[schemas.QuestionResponse])
def get_questions(
        db: Session = Depends(get_db)):

    questions = db.query(models.Question).all()

    return questions


@router.post("/responses", status_code=status.HTTP_201_CREATED)
def create_or_update_response(
    responses: List[schemas.UserResponseCreate],
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    for res in responses:
        obj = db.query(models.UserResponse).filter_by(
            user_id=current_user.id,
            question_id=res.question_id
        ).first()

        if obj:
            obj.answer = res.answer
        else:
            new_response = models.UserResponse(
                user_id=current_user.id,
                question_id=res.question_id,
                answer=res.answer
            )
            db.add(new_response)
    db.commit()
    return {"message": "Responses added or updated successfully"}

@router.get("/survey_completed", response_model=dict)
def check_all_questions_answered(
    db: Session = Depends(get_db),
     current_user: schemas.UserOut = Depends(oauth2.get_current_user),
    ):
    # Toplam soru sayısını alın
    total_questions = db.query(models.Question).count()

    # Kullanıcının cevapladığı farklı soruların sayısını alın
    answered_questions = db.query(models.UserResponse.question_id).filter(
        models.UserResponse.user_id == current_user.id
    ).distinct().count()

    # Tüm soruların cevaplanıp cevaplanmadığını kontrol edin
    all_answered = total_questions == answered_questions

    return {"is_completed": all_answered}

@router.get("/all")
def get_all_questions():
    
    questions = read_questions_from_json('questions.json')
    return questions



def read_questions_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)