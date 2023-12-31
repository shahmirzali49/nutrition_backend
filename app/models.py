from sqlalchemy import Column, Integer, Float, String, ForeignKey, Numeric, Boolean
from .database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    weekly_menus = relationship("WeeklyMenu")


class WeeklyMenu(Base):
    __tablename__ = "weekly_menus"

    id = Column(Integer, primary_key=True, nullable=False)
    week = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    daily_menus = relationship("DailyMenu")


class DailyMenu(Base):
    __tablename__ = "daily_menus"
    
    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    day = Column(Integer, nullable=False)
    weekly_menu_id = Column(Integer, ForeignKey('weekly_menus.id'))
    meals = relationship("Meal",secondary="daily_menu_meals") 

    # total nutrient values of daily menu
    total_energy = Column(Float, nullable=False)
    total_carbohydrate = Column(Float, nullable=False)
    total_protein = Column(Float, nullable=False)
    total_fat = Column(Float, nullable=False)
    total_fiber = Column(Float, nullable=False)

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, nullable=False)
    food = Column(String, nullable=False)
    price = Column(Numeric(precision=8,scale=2), nullable=False)
    color = Column(String, nullable=False)
    portion_weight = Column(Integer, nullable=False)
    consistency = Column(String, nullable=False)
    energy = Column(Float, nullable=False)
    carbohydrate = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    fiber = Column(Float, nullable=False)
    # daily_menu_id = Column(Integer, ForeignKey('daily_menus.id'))


class MealPreference(Base):
    __tablename__ = "meal_preferences"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    meal_id = Column(Integer, ForeignKey('meals.id'))
    like = Column(Boolean, nullable=True)  # True için beğeni, False için beğenmeme

    user = relationship("User")
    meal = relationship("Meal")


class DailyMenuMeal(Base):
    __tablename__ = "daily_menu_meals"

    id = Column(Integer, primary_key=True,nullable=False, index=True, autoincrement=True)
    daily_menu_id = Column(Integer, ForeignKey('daily_menus.id'), primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'), primary_key=True)


# -------------------------- Questions --------------------------------

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String, nullable=False)
    # Soru tipi, örneğin 'multiple_choice', 'boolean' vb.
    type = Column(String, nullable=False)
    choices = relationship("Choice")

class Choice(Base):
    __tablename__ = "choices"
    id = Column(Integer, primary_key=True,nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    text = Column(String, nullable=False)

class UserResponse(Base):
    __tablename__ = "user_responses"
    id = Column(Integer, primary_key=True,nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer = Column(String, nullable=False)

    user = relationship("User")
    question = relationship("Question")