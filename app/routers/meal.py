from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import joinedload

from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
from ..models import UserResponse, MealPreference
from ..diet_planning import get_diet_menu
from ..database import engine
from ..db_changes import add_all_meals_from_csv


router = APIRouter(
    prefix="/meals",
    tags=['Meals']
)

 
# @router.get("/diet_menu", response_model=List[schemas.WeeklyMenu])
# def api_get_diet_menu(
#     db: Session = Depends(get_db),
#     current_user: schemas.UserOut = Depends(oauth2.get_current_user)
# ):
    # # Kullanıcının yaşını ve cinsiyetini çekmek için `user_responses` sorgulayın
    # age_response = db.query(UserResponse).filter(
    #     UserResponse.user_id == current_user.id,
    #     UserResponse.question_id == 1  # Burada 1, yaş sorusunun ID'sini temsil ediyor
    # ).first()

    # gender_response = db.query(UserResponse).filter(
    #     UserResponse.user_id == current_user.id,
    #     UserResponse.question_id == 2  # Burada 2, cinsiyet sorusunun ID'sini temsil ediyor
    # ).first()

    # # Cevapları kontrol edin
    # if not age_response or not gender_response:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User age or gender responses not found."
    #     )
    
    # user_age = int(age_response.answer)  # 'answer' sütununu uygun bir tipe dönüştürün
    # user_gender = gender_response.answer
    
    # user_preferences = db.query(MealPreference).filter(
    # MealPreference.user_id == current_user.id
    #     ).options(joinedload(MealPreference.meal)).all()
    
    # user_pref_dict = {pref.meal_id: pref.like for pref in user_preferences}

    # print("user_pref_dict: ", user_pref_dict)

#     # Şimdi bu bilgileri kullanarak diyet menüsünü alın

#     print("user_age: ", user_age , "user_gender: ", user_gender)

#     # return get_diet_menu(user_age, user_gender, 1, db)

#     return get_diet_menu(41, "Kadın", 1, user_pref_dict, db)

# Generate weekly menu for the user

@router.post("/generate_diet_menu")
def generate_diet_menu(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    # Kullanıcının yaşını ve cinsiyetini çekmek için `user_responses` sorgulayın
    age_response = db.query(models.UserResponse).filter(
        models.UserResponse.user_id == current_user.id,
        models.UserResponse.question_id == 1  # Yaş sorusu
    ).first()
    gender_response = db.query(models.UserResponse).filter(
        models.UserResponse.user_id == current_user.id,
        models.UserResponse.question_id == 2  # Cinsiyet sorusu
    ).first()

    if not age_response or not gender_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User age or gender responses not found."
        )

    user_age = int(age_response.answer)
    user_gender = gender_response.answer

    # Kullanıcının tercihlerini alın
    user_preferences = db.query(models.MealPreference).filter(
        models.MealPreference.user_id == current_user.id
    ).all()
    user_pref_dict = {pref.meal_id: pref.like for pref in user_preferences}

    # Haftalık menüyü oluşturun
    pydantic_weekly_menus: List[schemas.WeeklyMenu] = get_diet_menu(user_age, user_gender, 1, user_pref_dict, db)

    # En yüksek hafta numarasını bulun
    max_week = db.query(func.max(models.WeeklyMenu.week)).filter(
        models.WeeklyMenu.user_id == current_user.id
    ).scalar() or 0




    for pydantic_weekly_menu in pydantic_weekly_menus:
        new_week = max_week + 1
        sqlalchemy_weekly_menu = models.WeeklyMenu(
            week=new_week,
            user_id=current_user.id
        )
        db.add(sqlalchemy_weekly_menu)
        db.flush()  # Haftalık menünün ID'sini almak için

        for pydantic_daily_menu in pydantic_weekly_menu.menus:
            meal_ids = [meal.id for meal in pydantic_daily_menu.menu]  # Pydantic modelden meal ID'lerini al
            sqlalchemy_meals = db.query(models.Meal).filter(models.Meal.id.in_(meal_ids)).all()

            sqlalchemy_daily_menu = models.DailyMenu(
                weekly_menu_id=sqlalchemy_weekly_menu.id,
                day=pydantic_daily_menu.day,
                status=pydantic_daily_menu.status,
                total_energy=pydantic_daily_menu.total_nutrient_values.energy,
                total_carbohydrate=pydantic_daily_menu.total_nutrient_values.carbohydrate,
                total_protein=pydantic_daily_menu.total_nutrient_values.protein,
                total_fat=pydantic_daily_menu.total_nutrient_values.fat,
                total_fiber=pydantic_daily_menu.total_nutrient_values.fiber,
                meals=sqlalchemy_meals
            )
            db.add(sqlalchemy_daily_menu)

        max_week += 1

    db.commit()


    return {"message": "New diet menu generated for week {}".format(new_week)}
    

# Get list of weekly menus for the user

@router.get("/list_diet_menus")
def list_diet_menus(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    weekly_menus = db.query(models.WeeklyMenu).filter(
        models.WeeklyMenu.user_id == current_user.id
    ).options(
        joinedload(models.WeeklyMenu.daily_menus).joinedload(models.DailyMenu.meals)
    ).all()

    for weekly_menu in weekly_menus:
        weekly_menu.daily_menus.sort(key=lambda x: x.day)


    user_preferences = db.query(models.MealPreference).filter(
        models.MealPreference.user_id == current_user.id
    ).all()
    user_pref_dict = {pref.meal_id: pref.like for pref in user_preferences}

    result = []
    for weekly_menu in weekly_menus:
        weekly_menu_data = schemas.WeeklyMenu(
            week=weekly_menu.week,
            menus=[
                schemas.DayMenu(
                    status=daily_menu.status,
                    day=daily_menu.day,
                    menu=[
                        schemas.Meal(
                            id=meal.id,
                            food=meal.food,
                            price=meal.price,
                            color=meal.color,
                            consistency=meal.consistency,
                            is_liked=user_pref_dict.get(meal.id, None)
                        ) for meal in daily_menu.meals
                    ],
                    total_nutrient_values=schemas.NutrientValues(
                        energy=daily_menu.total_energy,
                        carbohydrate=daily_menu.total_carbohydrate,
                        protein=daily_menu.total_protein,
                        fat=daily_menu.total_fat,
                        fiber=daily_menu.total_fiber
                    )
                ) for daily_menu in weekly_menu.daily_menus
            ]
        )
        result.append(weekly_menu_data)

    return result


@router.post("/preferences")
def set_meal_preference(meal_id: int, like: bool, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    # MealPreference tablosunda kullanıcının bu yemek için önceden bir tercihi olup olmadığını kontrol edin
    existing_preference = db.query(MealPreference).filter(
        MealPreference.user_id == current_user.id,
        MealPreference.meal_id == meal_id
    ).first()

    if existing_preference:
        # Eğer varsa, mevcut tercihi güncelleyin
        existing_preference.like = like
    else:
        # Eğer yoksa, yeni bir tercih oluşturun
        new_preference = MealPreference(user_id=current_user.id, meal_id=meal_id, like=like)
        db.add(new_preference)
    
    db.commit()
    return {"message": "Meal preference set successfully"}


@router.post("/add_all_meals")
def add_all_meals(
    db: Session = Depends(get_db)
):
    add_all_meals_from_csv(db)
    return {"message": "All meals added successfully"}