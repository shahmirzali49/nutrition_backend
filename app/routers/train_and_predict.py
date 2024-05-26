
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from ..database import get_db
import pandas as pd

from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from .. import models
from fastapi import Depends
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from joblib import dump, load
from fastapi.encoders import jsonable_encoder

import os
import re
import glob
from sqlalchemy import func





router = APIRouter(
    prefix="/ai",
    tags=['AI Model']
)




# @router.get("/traint")
# def train_model(db: Session = Depends(get_db)):

#     # Veritabanından veriyi çek
#     query_meals = db.query(models.UserResponses).statement
#     data = pd.read_sql_query(query_meals, db.bind)

#     # Verinin ilk birkaç satırını kontrol et
#     print("Data Head:\n", data.head())

#     # Girdi (X) ve Hedef (Y) Değişkenlerini Belirleme
#     X = data[['age', 'gender', 'activity_status', 'marital_status']]
#     Y = data.drop(['id', 'age', 'gender', 'activity_status', 'marital_status', 'company_id'], axis=1)

#     # Her bir hedef değişkenin sınıf dağılımını kontrol et
#     for col in Y.columns:
#         print(f"Class distribution for {col}:\n{Y[col].value_counts()}\n")

#     # Eğitim ve test setlerini ayır
#     X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=21)

#     # Eğitim ve test setlerinin boyutlarını kontrol et
#     print(f"X_train shape: {X_train.shape}, Y_train shape: {Y_train.shape}")
#     print(f"X_test shape: {X_test.shape}, Y_test shape: {Y_test.shape}")

#     # MultiOutputClassifier ile RandomForestClassifier modelini sarma
#     model = MultiOutputClassifier(RandomForestClassifier(class_weight='balanced',random_state=21))

#     # Modeli eğitme
#     model.fit(X_train, Y_train)

#     # Tahminleri yapma
#     predictions = model.predict(X_test)
#     print(f"Predictions: {predictions}")

#     # Modelin skoru (genel doğruluk)
#     score = model.score(X_test, Y_test)
#     print(f"Score: {score}")

#     # Her bir hedef değişken için performans metriklerini hesapla
#     performances = {}
#     for i, col in enumerate(Y.columns):
#         acc = accuracy_score(Y_test.iloc[:, i], predictions[:, i])
#         report = classification_report(Y_test.iloc[:, i], predictions[:, i], output_dict=True)
#         performances[col] = {"Accuracy": acc, "Report": report}

#     # Performans metriklerini döndür
#     return {"Overall Score": score, "Performance per Target": performances}










@router.get("/train")
def train_model(db: Session = Depends(get_db)):

    # df = pd.read_sql_query(sorgu, engine)
    query_meals = db.query(models.UserResponses).statement
    data = pd.read_sql_query(query_meals, db.bind)

    # data = pd.read_csv('user_responses_numeric.csv')

    # print(data.head())

    # Girdi (X) ve Hedef (Y) Değişkenlerini Belirleme
    X = data[['age','gender','activity_status','marital_status']]
    Y = data.drop(['id', 'age','gender','activity_status','marital_status', 'company_id'],axis=1)

    # print(Y.shape)


    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, Y_train)

    # model.score(X_test, Y_test)

    Y_pred = model.predict(X_test)
    
    print("Y_pred: ", Y_pred)

    # accuracy = accuracy_score(Y_test, Y_pred)
    # accuracy = model.score(X_test, Y_test)
    # mse = mean_squared_error(Y_test, Y_pred)
    # print('Mean Squared Error:', mse)
    # print('Accuracy:', accuracy)
    # print("Accuracy Score: {}".format(accuracy_score(Y_test, Y_pred)))

    directory = '.'
    # Belirli bir klasördeki tüm dosyaları listele
    files = os.listdir(directory)
    # "model_" ile başlayan ve ".joblib" ile biten dosyaları filtrele
    model_files = [f for f in files if re.match(r'model_\d+\.joblib', f)]

    # Dosya versiyonlarını bul
    versions = [int(re.search(r'model_(\d+)\.joblib', f).group(1)) for f in model_files]
    latest_version = max(versions) + 1 if versions else 1

    # Yeni dosya adı
    new_filename = f"model_{latest_version}.joblib"

    # Eski dosyaları sil
    for file in model_files:
        os.remove(os.path.join(directory, file))

    # Modeli kaydet
    dump(model, os.path.join(directory, new_filename))

    print(f"Model saved as {new_filename}")

    # dump(model, 'model.joblib')

    # Performans metrikleri
    performances = {}
    for col in Y.columns:
        acc = accuracy_score(Y_test[col], Y_pred[:, Y.columns.get_loc(col)])
        report = classification_report(Y_test[col], Y_pred[:, Y.columns.get_loc(col)], output_dict=True)
        performances[col] = {"Accuracy": acc, "Report": report}
    return {"Accuracy": performances}


@router.get("/predict")
def predict( user_method: Optional[int] = None, db: Session = Depends(get_db)):
    model_files = glob.glob('model_*.joblib')
    # Dosyaları sırala (en yeni model dosyasını almak için)
    latest_model_file = max(model_files, key=os.path.getctime)
    # En son model dosyasını yükle
    model = load(latest_model_file)
    # model = load('model.joblib')
    # query_meals = db.query(models.UserResponses).statement
    if user_method == 1:
        max_company_id = db.query(func.max(models.UserResponses.company_id)).scalar() or 0
        query_meals = db.query(models.UserResponses).filter(models.UserResponses.company_id == max_company_id)
    elif user_method == 2:
        query_meals = db.query(models.UserResponses)
    else:
        raise HTTPException(status_code=400, detail="Invalid method provided")
    
    data = pd.read_sql_query(query_meals.statement, db.bind)

    # data = pd.read_csv('user_responses_numeric.csv')

    # print(data.head())

    # Girdi (X) ve Hedef (Y) Değişkenlerini Belirleme
    X = data[['age','gender','activity_status','marital_status']]
    Y = data.drop(['id', 'age','gender','activity_status','marital_status', 'company_id'],axis=1)
    predicted = model.predict(X)

    new_users_predictions_df = pd.DataFrame(predicted, columns=Y.columns)
    # Fonksiyonu kullanarak dönüşüm uygulayın
    
    one_hot_df = convert_to_one_hot(new_users_predictions_df)
    # print(one_hot_df)

    question_weights = calculate_question_weights(one_hot_df)
    print(question_weights)

    json_compatible_item_data = {key: int(value) for key, value in question_weights.items()}


    return json_compatible_item_data



def convert_to_one_hot(df, category_labels=None):
    if category_labels is None:
        category_labels = ["hiç", "az", "orta", "sık", "çoksık"]
    
    transformed_dfs = []
    for idx, column in enumerate(df.columns):
        # Sütun indexini kullanarak soru numarasını oluştur (index 0'dan başlar)
        question_number = idx + 1  # İnsanların anlamasını kolaylaştırmak için 1'den başlat
        
        # One-hot encoding oluşturmak için her kategori için bir sütun oluşturun
        for index, label in enumerate(category_labels):
            transformed_dfs.append(
                pd.DataFrame(
                    {f"{question_number}_{column}_{label}": (df[column] == index).astype(int)}
                )
            )
    
    # Tüm dönüştürülmüş DataFrame'leri yatay olarak birleştir
    final_df = pd.concat(transformed_dfs, axis=1)
    return final_df


def calculate_question_weights(df):
    # Soru ağırlıklarını saklayacak sözlük
    question_weights = {}
    
    # Sütun isimlerini soru numarasına göre grupla
    question_columns = {}
    for col in df.columns:
        # Sütun ismindeki ilk sayıyı soru numarası olarak al
        question_number = ''.join(filter(str.isdigit, col.split('_')[0]))
        # Eğer question_number boş değilse işleme devam et
        if question_number:
            if question_number not in question_columns:
                question_columns[question_number] = []
            question_columns[question_number].append(col)

    # Her soru numarası için ağırlıkları hesapla
    for question, columns in question_columns.items():
        total_weight = 0
        for col in columns:
            if 'hiç' in col or 'az' in col:
                total_weight -= df[col].sum()
            elif 'sık' in col or 'çoksık' in col:
                total_weight += df[col].sum()
        question_weights[question] = total_weight

    return question_weights


@router.get("/survey")
def calculate_without_ai(user_method: Optional[int] = None, db: Session = Depends(get_db)):
    # model = load('model.joblib')
    # query_meals = db.query(models.UserResponses).statement

    # max_company_id = db.query(func.max(UserResponses.company_id)).scalar() or 0

    if user_method == 1:
        max_company_id = db.query(func.max(models.UserResponses.company_id)).scalar() or 0
        query_meals = db.query(models.UserResponses).filter(models.UserResponses.company_id == max_company_id)
    elif user_method == 2:
        query_meals = db.query(models.UserResponses)
    else:
        raise HTTPException(status_code=400, detail="Invalid method provided")

    data = pd.read_sql_query(query_meals.statement, db.bind)

    # data = pd.read_csv('user_responses_numeric.csv')

    # print(data.head())

    # Girdi (X) ve Hedef (Y) Değişkenlerini Belirleme
    X = data[['age','gender','activity_status','marital_status']]
    Y = data.drop(['id', 'age','gender','activity_status','marital_status', 'company_id'],axis=1)

    # new_users_predictions_df = pd.DataFrame(predicted, columns=Y.columns)
    # Fonksiyonu kullanarak dönüşüm uygulayın
    
    one_hot_df = convert_to_one_hot(Y)
    # print(one_hot_df)

    question_weights = calculate_question_weights(one_hot_df)
    print(question_weights)

    json_compatible_item_data = {key: int(value) for key, value in question_weights.items()}


    return json_compatible_item_data