from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict


from pydantic.types import conint


#response model
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    access_token: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None

class ChoiceResponse(BaseModel):
    text: str

class QuestionResponse(BaseModel):
    id: int
    text: str
    type: str
    choices: list[ChoiceResponse]

    class Config:
        from_attributes = True

class UserResponseCreate(BaseModel):
    question_id: int
    answer: str

# class Vote(BaseModel):
#     post_id: int
#     dir: conint(le=1)



# -------------------------- diet planning schemas --------------------------------

class Meal(BaseModel):
    id: int
    food: str
    price: int
    color: str
    consistency: str
    is_liked: Optional[bool] = None

class NutrientValues(BaseModel):
    energy: float
    carbohydrate: float
    protein: float
    fat: float
    fiber: float

class DayMenu(BaseModel):
    status: str
    day: int
    menu: List[Meal]
    total_nutrient_values: NutrientValues

class WeeklyMenu(BaseModel):
    week: int 
    created_at: Optional[datetime] = None
    menus: List[DayMenu]