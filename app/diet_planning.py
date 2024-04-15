import pandas as pd
import pulp as pl
from collections import defaultdict
import random
from app.schemas import Meal, NutrientValues, DayMenu, WeeklyMenu
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
import app.models
import json
import pandas as pd
import pulp as pl
from collections import defaultdict
import random
from app.schemas import Meal, NutrientValues, DayMenu, WeeklyMenu

def normalize_preferences(user_preferences):
    min_score = min(user_preferences.values())
    offset = abs(min_score) if min_score < 0 else 0
    normalized_preferences = {k: v + offset + 1 for k, v in user_preferences.items()}
    return normalized_preferences

def calculate_preferences_percentages(user_preferences):
    normalized_preferences = normalize_preferences(user_preferences)
    total_score = sum(normalized_preferences.values())
    percentages = {k: (v / total_score) * 100 for k, v in normalized_preferences.items()}
    return percentages


def get_diet_menu(week: int,  user_preferences: dict[str, int], db: Session):
  
    
    query_meals = db.query(app.models.Meal).statement
    df1 = pd.read_sql_query(query_meals, db.bind)

    df2 = pd.read_csv("set2.csv")

    df1_indexed = df1.set_index("id")

    user_age = 25
    user_gender = "Kadın"
    week = 1
   
    # Kullanıcı tercihleri (örnek olarak verilen tercihler)
    # user_preferences = {'5': 2, '6': 6, '7': 14, '8': -5, '9': 12, '10': 7, '11': 9, '12': 5, '13': 6, '14': 46, '15': 1, '16': 4, '17': 3, '18': -3, '19': 3, '20': 9}

    # Tercih yüzdelerini hesaplama
    preferences_percentages = calculate_preferences_percentages(user_preferences)
    print("Tercih Yüzdeleri:", preferences_percentages)

    # JSON dosyasından kategori verilerini yükleme
    with open('detailed_foods.json', 'r') as f:
        detailed_foods = json.load(f)



    categories = defaultdict(list)

    for item in detailed_foods:
        # Tercih yüzdesine göre bu kategoriye ait yemeklerin sıralanması
        preference_score = user_preferences.get(str(item['id']), 0)
        
        # Yemeklerin her bir kategorisini ve bu kategorideki yemek ID'lerini tercih skoruna göre sıralı şekilde kaydedilmesi
        categories[item['plate_category']] += [(food_id, preference_score) for food_id in item['food_ids']]

    # Her kategorideki yemekleri tercih skorlarına göre sıralayıp, sadece ID'lerin alınması
    for category, foods in categories.items():
        sorted_food_ids = [food_id for food_id, _ in sorted(foods, key=lambda x: x[1], reverse=True)]
        categories[category] = sorted_food_ids

    # Sonuçların gösterimi
    print("Kategorilere göre yemek ID'leri (Tercih yüzdesine göre sıralı):", dict(categories))
    


    print(f"user_age {user_age}, user_gender {user_gender}")

    def parse_age_group(age_group):
        lower, upper = map(int, age_group.split("-"))
        return range(lower, upper + 1)  # üst sınıra 1 ekliyoruz


    limits = df2[
        (df2["Cinsiyet"] == user_gender)
        & (df2["Yaş Grubu"].apply(lambda x: user_age in parse_age_group(x)))
    ].iloc[0]

    def find_mandatory_dish_id(df, used_dishes):
        for dish_name in mandatory_dish_names:
            dish_row = df[df["food"] == dish_name]
            if not dish_row.empty:
                dish_id = dish_row.iloc[0]["id"]
                if dish_id not in used_dishes:
                    return dish_id, dish_name
        return None, None

    all_mandatory_dish_names = [
        "Etli Nohut",
        "Etli Kuru Fasulye",
        "Zeytinyağlı Barbunya",
        "Börülce Salatası",
        "Mercimek Salatası",
        "Piyaz",
    ]

    mandatory_dish_names = random.sample(all_mandatory_dish_names, 4)

    mandatory_dish_ids = [
        df1[df1["food"] == name].iloc[0]["id"]
        for name in mandatory_dish_names
        if not df1[df1["food"] == name].empty
    ]


    vegetable_meals_ids = [
        123,
        124,
        125,
        126,
        127,
        128,
        130,
        131,
        132,
        133,
        144,
        145,
        146,
        147,
        148,
        149,
        150,
    ]
    salad_meals_ids = df1[
        df1["food"].str.contains("Salata")
        & df1["id"].isin(categories["dessert_salad"])
    ]["id"].tolist()

    soup_meals_ids = [
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        82,
        83,
        84,
        85,
        86,
        87,
        88,
        89,
        90,
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
        100,
    ]
    compote_hosaf_meals_ids = [167, 168, 169, 170, 171]

    etli_dolma_sarma_ids = df1[
        df1["food"].str.contains("Etli")
        & (
            df1["food"].str.contains("Dolma")
            | df1["food"].str.contains("Sarma")
        )
    ]["id"].tolist()

    pilav_ids = df1[df1["food"].str.contains("Pilav")]["id"].tolist()

    # Pirinç pilavı, yayla çorbası ve sütlaç aynı güne verilmemelidir.
    specified_meal_ids = df1[
        df1["food"].str.contains(
            "Pirinç Pilavı|Şehriyeli Pirinç Pilavı|Yayla Çorbası|Sütlaç", regex=True
        )
    ]["id"].tolist()


    used_dishes = set()
    used_mandatory_dishes = set()

    df1["color"] = df1["color"].str.lower()
    df1["consistency"] = df1["consistency"].str.lower()

    available_colors = df1["color"].drop_duplicates().values.tolist()
    available_textures = df1["consistency"].drop_duplicates().values.tolist()

    weekly_menus = []


    # Kullanıcı tercihlerine göre yemek puanlarını hesaplama

    dish_costs = {food_id: preferences_percentages.get(str(item['id']), 0)
                for item in detailed_foods for food_id in item['food_ids']}


    
    def update_objective_function(prob, dish_vars, dish_costs):
        cost_function = pl.lpSum([dish_costs[dish_id] * dish_vars[dish_id] for dish_id in dish_vars])
        prob.setObjective(cost_function)


    for week in range(1, week + 1):
        # print(f"{week}. Hafta Menüleri\n")
        mandatory_dish_day = random.choice(range(1, 6))
        mandatory_dish_id, mandatory_dish_name = None, None

        weekly_menu = WeeklyMenu(week=week, menus=[]) 

        for day in range(1, 6):
            prob = pl.LpProblem(f"Menu_Optimization_{week}_{day}", pl.LpMaximize)

            available_dishes = list(
                set(df1["id"]) - used_dishes - set(mandatory_dish_ids)
            )

            if day == mandatory_dish_day:
                # available_dishes = list(set(df1["id"]) - used_dishes)
                available_dishes = list(
                    set(df1["id"]) - used_dishes - set(mandatory_dish_ids[week:])
                )

            dish_vars = pl.LpVariable.dicts("Dish", available_dishes, 0, 1, pl.LpBinary)

            # print("available_dishes 1: ", available_dishes)
            # print("dish_vars 1: ", dish_vars)


            for nutrient in ["energy", "carbohydrate", "protein", "fat", "fiber"]:
                lower_limit = float(limits[nutrient].split("-")[0])
                upper_limit = float(limits[nutrient].split("-")[1])

                prob += pl.LpConstraint(
                    e=pl.lpSum(
                        [
                            df1_indexed.loc[i][nutrient] * dish_vars[i]
                            for i in available_dishes
                        ]
                    ),
                    sense=pl.LpConstraintGE,
                    name=f"{nutrient}_lower_bound",
                    rhs=lower_limit,
                )

                prob += pl.LpConstraint(
                    e=pl.lpSum(
                        [
                            df1_indexed.loc[i][nutrient] * dish_vars[i]
                            for i in available_dishes
                        ]
                    ),
                    sense=pl.LpConstraintLE,
                    name=f"{nutrient}_upper_bound",
                    rhs=upper_limit,
                )

            for cat, rng in categories.items():
                prob += (
                    pl.lpSum([dish_vars[i] for i in available_dishes if i in rng]) == 1
                )


            for color in available_colors:
                prob += (
                    pl.lpSum(
                        [
                            dish_vars[i]
                            for i in available_dishes
                            if df1_indexed.loc[i]["color"] == color
                        ]
                    )
                    <= 2
                )
            for texture in available_textures:
                prob += (
                    pl.lpSum(
                        [
                            dish_vars[i]
                            for i in available_dishes
                            if df1_indexed.loc[i]["consistency"] == texture
                        ]
                    )
                    <= 2
                )

            for veg_meal_id in vegetable_meals_ids:
                for salad_meal_id in salad_meals_ids:
                    if (
                        veg_meal_id in available_dishes
                        and salad_meal_id in available_dishes
                    ):
                        prob += dish_vars[veg_meal_id] + dish_vars[salad_meal_id] <= 1

            for soup_meal_id in soup_meals_ids:
                for compote_hosaf_meal_id in compote_hosaf_meals_ids:
                    if (
                        soup_meal_id in available_dishes
                        and compote_hosaf_meal_id in available_dishes
                    ):
                        prob += (
                            dish_vars[soup_meal_id] + dish_vars[compote_hosaf_meal_id]
                            <= 1
                        )

            for etli_dolma_sarma_id in etli_dolma_sarma_ids:
                for pilav_id in pilav_ids:
                    if (
                        etli_dolma_sarma_id in available_dishes
                        and pilav_id in available_dishes
                    ):
                        prob += (
                            dish_vars[etli_dolma_sarma_id] + dish_vars[pilav_id] <= 1
                        )
            specified_meal_ids = [
                meal_id for meal_id in specified_meal_ids if meal_id in dish_vars
            ]
            prob += (
                pl.lpSum([dish_vars[meal_id] for meal_id in specified_meal_ids]) <= 1
            )

            if day == mandatory_dish_day:
                mandatory_dish_id, mandatory_dish_name = find_mandatory_dish_id(
                    df1, used_mandatory_dishes
                )
                if mandatory_dish_id is None:
                    print("Uygun zorunlu yemek kalmadı.")
                else:
                    used_mandatory_dishes.add(mandatory_dish_id)
                    prob += dish_vars[mandatory_dish_id] == 1
                    used_dishes.add(mandatory_dish_id)
            

            update_objective_function(prob, dish_vars, dish_costs)
    

     

            prob.solve(pl.PULP_CBC_CMD(msg=False))
            # print(f"{day}. Gün Menüsü:")
            total_nutrients = defaultdict(float)

            for v in prob.variables():
                if v.varValue == 1:
                    dish_id = int(v.name.split("_")[1])
                    

                    used_dishes.add(dish_id)


            selected_dishes = [i for i in available_dishes if dish_vars[i].value() == 1]
            day_menu_meals = [Meal(
                id=int(i),
                food=df1_indexed.loc[i]["food"],
                price=df1_indexed.loc[i]["price"],
                color=df1_indexed.loc[i]["color"],
                consistency=df1_indexed.loc[i]["consistency"]
              
            ) for i in selected_dishes]
            
            total_nutrient_values = NutrientValues(
                energy=sum(df1_indexed.loc[i]["energy"] for i in selected_dishes),
                carbohydrate=sum(df1_indexed.loc[i]["carbohydrate"] for i in selected_dishes),
                protein=sum(df1_indexed.loc[i]["protein"] for i in selected_dishes),
                fat=sum(df1_indexed.loc[i]["fat"] for i in selected_dishes),
                fiber=sum(df1_indexed.loc[i]["fiber"] for i in selected_dishes)
            )
            
            day_menu = DayMenu(status=f"{prob.status}", day = day, menu=day_menu_meals, total_nutrient_values=total_nutrient_values)
            weekly_menu.menus.append(day_menu)

        weekly_menus.append(weekly_menu)
        # print("weekly_menus: ", weekly_menus)

    return weekly_menus


# print(get_diet_menu())
 


