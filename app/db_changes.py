import pandas as pd
from sqlalchemy.orm import Session


def add_all_meals_from_csv(db: Session):
    df = pd.read_csv("set1.csv")
    with db.connection() as conn:
        df.to_sql('meals', con=conn, if_exists='append', index=False)
        conn.commit()

# df = pd.read_csv("set1.csv")

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:4915054ali@localhost:5432/nutritiondb'

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# df.to_sql('meals', con=engine, if_exists='append', index=False)


     