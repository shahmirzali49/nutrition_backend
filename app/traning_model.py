# import pandas as pd

# from sqlalchemy.orm import Session
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_squared_error
# import models
# from database import get_db
# from fastapi import Depends

# def train_model(db: Session = Depends(get_db)):

#     # df = pd.read_sql_query(sorgu, engine)
#     query_meals = db.query(models.UserResponses).statement
#     data = pd.read_sql_query(query_meals, db.bind)

#     # data = pd.read_csv('user_responses_numeric.csv')

#     # print(data.head())

#     # Girdi (X) ve Hedef (Y) Değişkenlerini Belirleme
#     X = data[['age','gender','activity_status','marital_status']]
#     Y = data.drop(['id', 'age','gender','activity_status','marital_status', 'company_id'],axis=1)

#     # print(Y.shape)


#     X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X_train, Y_train)

#     Y_pred = model.predict(X_test)
    
#     accuracy = model.score(X_test, Y_test)
#     mse = mean_squared_error(Y_test, Y_pred)
#     print('Mean Squared Error:', mse)
#     print('Accuracy:', accuracy)