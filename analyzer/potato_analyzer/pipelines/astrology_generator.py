import json
from datetime import datetime
from uuid import uuid4

import pandas as pd
from deltalake import DeltaTable, write_deltalake
from openai import OpenAI
import requests
import pyarrow as pa
from dotenv import load_dotenv


load_dotenv()


def generate_zodiac_image(env, image_description, first_name, last_name):
    client = OpenAI()
    model = "dall-e-3" if env == "prod" else "dall-e-2"
    size = "1024x1024" if env == "prod" else "256x256"
    quality = "standard" if env == "prod" else "standard" # Do no generate 'hd' images yet
    response = client.images.generate(
        model=model,
        prompt=image_description,
        size=size,
        quality=quality,
        n=1,
    )
    image_url = response.data[0].url
    image_path = "./store/zodiac_images/" if env == "prod" else "./store_test/zodiac_images/"
    image_path += f"{first_name}-{last_name}-{str(uuid4())}.png"
    with open(image_path, mode="wb") as f:
        f.write(requests.get(image_url).content)
    return image_path


def generate_zodiac(env, first_name, last_name, communication_style, interests, personality, role_in_group,
                   memorable_stories, plans_aspirations, zodiac_sign, existing_zodiacs):
    client = OpenAI()

    existing_zodiacs_prompt = {'that is not ' + ', '.join(existing_zodiacs) if existing_zodiacs  else ''}
    prompt = f"""Generate the horoscope of a friend named {first_name} for the year 2024, who is '{zodiac_sign}' and
    has the following caracteristics:
    Personality: '{personality}'
    Communication style: '{communication_style}'
    Interests: '{interests}'
    The person role in a group of friends: '{role_in_group}'
    Memorable stories: '{memorable_stories}'
    Plans and aspirations: '{plans_aspirations}'.
    You must generate a JSON with 5 string fields: 'love', 'money_and_work', 'health_and_fitness',
    'family_and_friends', 'image_description'.
    In the fields 'love', 'money_and_work', 'health_and_fitness', 'family_and_friends' create the horosope for that
    person for these categories. For the field 'image_description' you describe an artistic and alegorical image of
    that person represented by the his or her zodiac sign ('{zodiac_sign}') and the predicted horoscope.
    Be only descriptive of the image without commenting on the meaning, in a way it could be interpreted by a
    text-to-image AI, this image cannot contain written text. Please."""

    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": """You are a poetic assistant, skilled in seeing the future and people
        horoscope, which outputs in JSON."""},
        {"role": "user", "content": prompt}
        ]
    )
    zodiac_ai_response = json.loads(completion.choices[0].message.content)
    print(zodiac_ai_response)
    image_path = generate_zodiac_image(env, zodiac_ai_response["image_description"], first_name, last_name)

    return {
            "love": zodiac_ai_response["love"],
            "money_and_work": zodiac_ai_response["money_and_work"],
            "health_and_fitness": zodiac_ai_response["health_and_fitness"],
            "family_and_friends": zodiac_ai_response["family_and_friends"],
            "image_description": zodiac_ai_response["image_description"],
            "image_path": image_path,
            "image_prompt": prompt,
            "text-to-image_ai": "OpenAI DALL-E 3",
            }


def load_potatoes(env, year_range):
    potato_description_path = "./store/potato_description_ai" if env == "prod" else "./store_test/potato_description_ai"
    potato_path = "./store/potatoes_card"
    df_potato = DeltaTable(potato_path).to_pandas(columns=["first_name", "last_name", "birth_date"])
    df_personalities = DeltaTable(potato_description_path).to_pandas(columns=["first_name", "last_name",
                                                                              "communication_style",
                                                                              "interests", "personality",
                                                                              "role_in_group", "memorable_stories",
                                                                              "plans_aspirations", "year_range"])
    df = df_personalities.set_index("last_name").join(df_potato.set_index("last_name"), lsuffix="_id").reset_index()
    df = df[["first_name", "last_name", "communication_style", "interests", "personality", "role_in_group",
             "memorable_stories", "plans_aspirations", "year_range", "birth_date"]]
    df = df[df.year_range.apply(lambda yr: yr[0] == year_range[0])]
    return df.to_dict(orient="records")


def write_zodiacs(env, zodiacs):
    totem_schema = pa.schema([
            ("zodiac_sign", pa.string()),
            ("love", pa.string()),
            ("money_and_work", pa.string()),
            ("health_and_fitness", pa.string()),
            ("family_and_friends", pa.string()),
            ("image_description", pa.string()),
            ("year_range", pa.list_(pa.int32())),
            ("image_path", pa.string()),
            ("image_prompt", pa.string()),
            ("text-to-image_ai", pa.string()),
        ])


    df_zodiac_ai = pd.DataFrame(zodiacs)
    zodiac_table_path = "./store/zodiac_ai" if env == "prod" else "./store_test/zodiac_ai"
    write_deltalake(zodiac_table_path, df_zodiac_ai, schema=totem_schema, mode='append')



def get_zodiac_sign(date):
    month = date.month
    day = date.day

    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    else:
        return "Capricorn"


if __name__ == "__main__":
    existing_zodiacs = []
    zodiacs = []
    year_range = [2023]
    env = "prod"
    for card in load_potatoes(env, year_range):
        zodiac_sign = get_zodiac_sign(card["birth_date"])
        zodiac = generate_zodiac(env, card["first_name"], card["last_name"], card["communication_style"],
                                 card["interests"], card["personality"], card["role_in_group"],
                                 card["memorable_stories"], card["plans_aspirations"], zodiac_sign, existing_zodiacs)
        zodiacs.append({**zodiac, **{"first_name": card["first_name"], "last_name": card["last_name"],
                                     "year_range": [2024], "zodiac_sign": zodiac_sign}})
        break
    write_zodiacs(env, zodiacs)
