import json
from time import sleep
from datetime import date
from uuid import uuid4

import pandas as pd
from deltalake import DeltaTable, write_deltalake
from openai import OpenAI
import requests
import pyarrow as pa
from dotenv import load_dotenv


load_dotenv()


def generate_totem_image(env, image_description, first_name, last_name):
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
    image_path = "./store/totem_images/" if env == "prod" else "./store_test/totem_images/"
    image_path += f"{first_name}-{last_name}-{str(uuid4())}.png"
    with open(image_path, mode="wb") as f:
        f.write(requests.get(image_url).content)
    sleep(60)
    return image_path



def generate_totem(env, first_name, description, historical_personality):
    client = OpenAI()

    prompt = f"""Generate the spirit animal of a friend named {first_name}, who is
    {description} and has the following personality through the years:"""

    for personality in historical_personality:
        year_prompt = f"""Year {personality["year_range"][0]};
    Personality: '{personality["personality"]}'
    Communication style: '{personality["communication_style"]}'
    Interests: '{personality["interests"]}'
    The person role in a group of friends: '{personality["role_in_group"]}'
    Memorable stories: '{personality["memorable_stories"]}'
    Plans and aspirations: '{personality["plans_aspirations"]}'.
"""
        prompt += "\n" + year_prompt

    prompt += """Be creative in the choice of an animal, it can be any real animal from all over the world.
    You must generate a JSON with two string fields: 'animal', 'description'. Please."""
    # real or mythological animals
    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": """You are a skilled assistant in describing people and their
    personalities from their text messages, which outputs in JSON."""},
        {"role": "user", "content": prompt}
        ]
    )
    return json.loads(completion.choices[0].message.content)


def generate_totem_description(env, first_name, last_name, description, spirit_animal, personality):
    client = OpenAI()

    prompt = f"""I have a friend named {first_name}, who is {description}, whose spirit animal is
    {spirit_animal["animal"]} because {spirit_animal["description"]}. In the year
    {personality["year_range"][0]}, {first_name}'s personality can be described as:
    Personality: '{personality["personality"]}'
    Communication style: '{personality["communication_style"]}'
    Interests: '{personality["interests"]}'
    The person role in a group of friends: '{personality["role_in_group"]}'
    Memorable stories: '{personality["memorable_stories"]}'
    Plans and aspirations: '{personality["plans_aspirations"]}'.

    Describe an artistic, alegorical and detailed image representing the spirit animal ({spirit_animal["animal"]})
    with allegoric personality traits of {first_name}. Be only descriptive of the image without commenting on
    the meaning, in a way it could be interpreted by a text-to-image AI, this image cannot contain written text.
    You must return two sentences ('description' type: string and 'interpretation' type: string)  as a JSON structure,
    one for the image figurative 'description' and for the image 'interpretation'."""

    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": """You are a poetic assistant, skilled in describing people and their
        personalities from their text messages, which outputs in JSON."""},
        {"role": "user", "content": prompt}
        ]
    )
    totem_ai_response = json.loads(completion.choices[0].message.content)
    print(totem_ai_response)
    image_path = generate_totem_image(env, totem_ai_response["description"], first_name, last_name)

    return {
            "description": totem_ai_response["description"],
            "interpretation": totem_ai_response["interpretation"],
            "image_path": image_path,
            "image_prompt": prompt,
            "text-to-image_ai": "OpenAI DALL-E 3",
            }


def load_potatoes_personality(env, first_name, last_name):
    potato_description_path = "./store/potato_description_ai" if env == "prod" else "./store_test/potato_description_ai"
    df = DeltaTable(potato_description_path).to_pandas(columns=["first_name", "last_name", "communication_style",
                                                                "interests", "personality", "role_in_group",
                                                                "memorable_stories", "plans_aspirations", "year_range"])
    df = df[(df.first_name == first_name) & (df.last_name == last_name)]
    return df.to_dict(orient="records")


def load_potatoes():
    df = DeltaTable("./store/potatoes_card").to_pandas()
    df["yo"] = df["birth_date"].apply(lambda bd: int((date.today() - bd).days / 365))
    df["gender"] = df["gender"].apply(lambda g: "man" if g == "male" else "woman")
    df = df[df.first_name == "Julie"]
    description_lambda = lambda row: f'{row["yo"]} years old young {", ".join(row["nationalities"])} {row["gender"]}'
    df["description"] = df.apply(description_lambda, axis=1)
    potato_cards = [{"first_name": row["first_name"], "last_name": row["last_name"], "description": row["description"]}
                    for row in df.to_dict(orient="records")]
    return potato_cards


def write_totems(env, totems):
    totem_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("animal", pa.string()),
            ("description", pa.string()),
        ])
    df_totem_ai = pd.DataFrame(totems)
    totem_table_path = "./store/totem" if env == "prod" else "./store_test/totem"
    write_deltalake(totem_table_path, df_totem_ai, schema=totem_schema, mode='append')


def write_totem_details(env, totems):
    totem_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("description", pa.string()),
            ("interpretation", pa.string()),
            ("year_range", pa.list_(pa.int32())),
            ("image_path", pa.string()),
            ("image_prompt", pa.string()),
            ("text-to-image_ai", pa.string()),
        ])

    df_totem_ai = pd.DataFrame(totems)
    totem_table_path = "./store/totem_description" if env == "prod" else "./store_test/totem_description"
    write_deltalake(totem_table_path, df_totem_ai, schema=totem_schema, mode='append')


if __name__ == "__main__":
    existing_spirit_animals = []
    totems = []
    totems_yearly = []
    env = "prod"
    for potato in load_potatoes():
        personality_history = load_potatoes_personality(env, first_name=potato["first_name"], last_name=potato["last_name"])
        totem = generate_totem(env, potato["first_name"], potato["description"], personality_history)
        print(totem)
        totems.append({**totem, **{"first_name": potato["first_name"], "last_name": potato["last_name"]}})
        for personality in personality_history:
            totem_description = generate_totem_description(env, potato["first_name"], potato["last_name"],
                                                           potato["description"], totem, personality)
            totems_yearly.append({**totem_description, **{"first_name": potato["first_name"],
                                                          "last_name": potato["last_name"],
                                                          "year_range": personality["year_range"]}})
    write_totems(env, totems)
    write_totem_details(env, totems_yearly)
