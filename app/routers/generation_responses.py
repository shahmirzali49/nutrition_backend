import json
import random

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from ..database import get_db
from ..models import UserResponses
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy import inspect


router = APIRouter(
    prefix="/generate",
    tags=['Generation']
)

class Distribution(BaseModel):
    question_id: int
    weights: Optional[List[int]]

class UserResponseDistributions(BaseModel):
    count: int
    distributions: List[Distribution]

# JSON dosyasından soruları okuyan fonksiyon
def read_questions_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    

# Cevapları sayısal değerlere dönüştürecek fonksiyon
def convert_answers_to_numeric(questions, answer):
    for i, option in enumerate(questions['answers']):
        if answer == option:
            return i
    # Yaş aralığı için özel durum
    if questions['type'] == 'range':
        return answer 

# Kullanıcı verisini rastgele oluşturacak fonksiyon
def generate_user_responses(questions, distributions_dict):
    user_responses = []
    for question in questions:
        dist = distributions_dict.get(question['id'])
        if question['type'] == 'range':
            age_range = question['answers']
            answer = random.randint(int(age_range[0]), int(age_range[1]))
        else:
            if dist:
                answer = random.choices(question['answers'], weights=dist, k=1)[0]
            else:
                answer = random.choice(question['answers'])
        numeric_answer = convert_answers_to_numeric(question, answer)
        user_responses.append(numeric_answer)
    return user_responses

# @router.post("/responses")
# def generate_and_add_responses_to_db(response_distributions: UserResponseDistributions, db: Session = Depends(get_db)):
#     questions = read_questions_from_json('questions.json')
#     distributions_dict = {dist.question_id: dist.weights for dist in response_distributions.distributions if dist.weights}

#     all_user_responses = []
#     for _ in range(response_distributions.count):  # 300 kullanıcı için cevaplar üret
#         user_responses = generate_user_responses(questions, distributions_dict)
#         all_user_responses.append(user_responses)

#     max_company_id = db.query(func.max(UserResponses.company_id)).scalar() or 0
#     new_company_id = max_company_id + 1

#     mapper = inspect(UserResponses)
#     attribute_names = [column.key for column in mapper.columns if column.key != 'id' and column.key != 'company_id']

#     try:
#         for user_responses in all_user_responses:
#             user_response_data = dict(zip(attribute_names, user_responses))
#             user_response_data['company_id'] = new_company_id
#             user_response = UserResponses(**user_response_data)
                                  
#             db.add(user_response)
#         db.commit()
#         return {"message": f"{len(all_user_responses)} user responses successfully added to the database"}
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))







@router.post("/responses")
def generate_and_add_responses_to_db(response_distributions: UserResponseDistributions, db: Session = Depends(get_db)):
    questions = read_questions_from_json('questions_eng.json')
    distributions_dict = {dist.question_id: dist.weights for dist in response_distributions.distributions if dist.weights}

    all_user_responses = []
    response_statistics = []  # Liste içinde sözlükler şeklinde sınıf dağılımını saklamak için güncellendi

    for _ in range(response_distributions.count):
        user_responses = generate_user_responses(questions, distributions_dict)
        all_user_responses.append(user_responses)

        # Her yanıt için sınıf dağılımını güncelle
        for question, response in zip(questions, user_responses):
            question_id = question["id"]  # Sorunun ID'sini al
            question_text = question["question"]  # Sorunun metnini al
            found = False
            for stat in response_statistics:
                if stat['question_id'] == question_id:
                    if response in stat['dagilim']:
                        stat['dagilim'][response] += 1
                    else:
                        stat['dagilim'][response] = 1
                    found = True
                    break
            if not found:
                response_statistics.append({
                    "question": question_text,
                    "question_id": question_id,
                    "dagilim": {response: 1}
                })

    max_company_id = db.query(func.max(UserResponses.company_id)).scalar() or 0
    new_company_id = max_company_id + 1

    mapper = inspect(UserResponses)
    attribute_names = [column.key for column in mapper.columns if column.key != 'id' and column.key != 'company_id']

    try:
        for user_responses in all_user_responses:
            user_response_data = dict(zip(attribute_names, user_responses))
            user_response_data['company_id'] = new_company_id
            user_response = UserResponses(**user_response_data)
                                  
            db.add(user_response)
        db.commit()

        # Yanıt istatistiklerini döndür
        return response_statistics
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


class UserResponseModel(BaseModel):
    age: int
    gender: int
    activity_status: int
    marital_status: int
    prefers_kofte: int
    prefers_kebab_guvec: int
    prefers_et_kizartma: int
    prefers_tavuk: int
    prefers_balik: int
    prefers_sebze: int
    prefers_zeytinyagli: int
    prefers_etli_sebze: int
    prefers_corba: int
    prefers_pilav: int
    prefers_borek: int
    prefers_makarna_eriste: int
    prefers_salata_soguk: int
    prefers_tatli: int
    prefers_icecek: int
    prefers_meyve: int
    company_id: int  # Eğer otomatik artış değilse, kullanıcı tarafından sağlanmalıdır.

@router.post("/user")
def create_user_response(response: UserResponseModel, db: Session = Depends(get_db)):
    db_response = UserResponses(**response.model_dump())
    db.add(db_response)
    try:
        db.commit()
        db.refresh(db_response)
        return {"message": "Response successfully saved.", "id": db_response.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))






# -------------------------------------------------------------------------------------------------------------------------------------------------------------


# # Kullanıcı verisini rastgele oluşturacak fonksiyon
# def generate_user_responses(questions):
#     user_responses = []
#     for question in questions:
#         if question['type'] == 'range':
#             # Yaş aralığı için rastgele bir değer üret
#             age_range = question['answers'].split('-')
#             answer = random.randint(int(age_range[0]), int(age_range[1]))
#         else:
#             # Radyo tipi sorular için rastgele bir seçenek seç
#             answer = random.choice(question['answers'])
#         # Cevabı sayısal değere dönüştür
#         numeric_answer = convert_answers_to_numeric(question, answer)
#         user_responses.append(numeric_answer)
#     return user_responses

# def generate_user_responses_bulk(questions, num_users=200):
#     # Tüm kullanıcılar için cevapları içeren bir liste
#     all_user_responses = []
#     for _ in range(num_users):
#         user_responses = generate_user_responses(questions)
#         all_user_responses.append(user_responses)
#     return all_user_responses



# @router.post("/responses")
# def generate_and_add_responses_to_db(db: Session = Depends(get_db)):

#     questions = read_questions_from_json('questions.json')

#     all_user_responses = generate_user_responses_bulk(questions, num_users=300)

#     # Mevcut en yüksek company_id değerini bul
#     max_company_id = db.query(func.max(UserResponses.company_id)).scalar() or 0
#     new_company_id = max_company_id + 1  # Yeni company_id

#     try:
#         # Her bir kullanıcı için cevapları oluştur ve veritabanına ekle
#         for i, user_responses in enumerate(all_user_responses):
#             # UserResponses modelini kullanarak yeni bir kayıt oluştur
           
#             user_response = UserResponses(
#                 company_id = new_company_id,
#                 age=user_responses[0],
#                 gender=user_responses[1],
#                 activity_status=user_responses[2],
#                 marital_status=user_responses[3],
#                 prefers_kofte=user_responses[4],
#                 prefers_kebab_guvec=user_responses[5],
#                 prefers_et_kizartma=user_responses[6],
#                 prefers_tavuk=user_responses[7],
#                 prefers_balik=user_responses[8],
#                 prefers_sebze=user_responses[9],
#                 prefers_zeytinyagli=user_responses[10],
#                 prefers_etli_sebze=user_responses[11],
#                 prefers_corba=user_responses[12],
#                 prefers_pilav=user_responses[13],
#                 prefers_borek=user_responses[14],
#                 prefers_makarna_eriste=user_responses[15],
#                 prefers_salata_soguk=user_responses[16],
#                 prefers_tatli=user_responses[17],
#                 prefers_icecek=user_responses[18],
#                 prefers_meyve=user_responses[19],
#             )
#             # Oturuma yeni objeyi ekle
#             db.add(user_response)
        
#         # Tüm yeni objeleri veritabanına kaydet
#         db.commit()
#         print(f"{len(all_user_responses)} kullanıcı yanıtları veritabanına başarıyla eklendi.")
        
#     except Exception as e:
#         # Bir hata oluşursa, değişiklikleri geri al
#         db.rollback()
#         raise e
#     finally:
#         return {"message": "All meals added successfully"}