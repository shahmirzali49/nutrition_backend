from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import isnot
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut) 
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

#     # hash the password - user.password
#     hashed_password = utils.hash(user.password)
#     user.password = hashed_password

#     is_user_exist = db.query(models.User).filter(
#                         models.User.email == user.email).first()
#     if is_user_exist is not None:
#         # if not post:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f"{is_user_exist.email} is already exist")
#     # new_user = models.User(**user.dict())
#     new_user = models.User(**user.model_dump())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user


@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), ):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user

