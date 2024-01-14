import pandas as pd
from deltalake import DeltaTable, write_deltalake
from openai import OpenAI
import json
from uuid import uuid4
import requests
import pyarrow as pa
from datetime import date
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
    return image_path


def generate_totem(env, first_name, last_name, communication_style, interests, personality, role_in_group,
                   memorable_stories, plans_aspirations, existing_spirit_animals):
    client = OpenAI()
    
    existing_spirit_animals_prompt = {'that is not ' + ', '.join(existing_spirit_animals) if existing_spirit_animals  else ''}
    prompt = f"""Generate the spirit animal of a friend named {first_name}, who has the following caracteristics:
    Personality: '{personality}'
    Communication style: '{communication_style}'
    Interests: '{interests}'
    The person role in a group of friends: '{role_in_group}'
    Memorable stories: '{memorable_stories}'
    Plans and aspirations: '{plans_aspirations}'.
    Be creative in the choice of an animal, it can be real or mythological animals from all over the world.
    You must generate a JSON with three string fields: 'spirit_animal', 'spirit_animal_description' and 'allegorical_image_description',
    where in 'allegorical_image_description' you describe an artistic and alegorical image of that person represented by the spirit
    animal. Be only descriptive of the image without commenting on the meaning, in a way it could be interpreted by a text-to-image AI,
    this image cannot contain written text. Please."""

    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in describing people and their personalities from their text messages, which outputs in JSON."},
        {"role": "user", "content": prompt}
        ]
    )
    totem_ai_response = json.loads(completion.choices[0].message.content)
    print(totem_ai_response)
    image_path = generate_totem_image(env, totem_ai_response["allegorical_image_description"], first_name, last_name)

    return {
            "spirit_animal": totem_ai_response["spirit_animal"],
            "spirit_animal_description": totem_ai_response["spirit_animal_description"],
            "allegorical_image_description": totem_ai_response["allegorical_image_description"],
            "image_path": image_path,
            "image_prompt": prompt,
            "text-to-image_ai": "OpenAI DALL-E 3",
            }


def load_potatoes(env, year_range):
    potato_description_path = "./store/potato_description_ai" if env == "prod" else "./store_test/potato_description_ai"
    df = DeltaTable(potato_description_path).to_pandas(columns=["first_name", "last_name", "communication_style",
                                                                "interests", "personality", "role_in_group", "memorable_stories",
                                                                "plans_aspirations", "year_range"])
    df = df[df.year_range.apply(lambda yr: yr[0] == year_range[0])]
    return df.to_dict(orient="records")


def write_totems(env, totems):
    totem_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("spirit_animal", pa.string()),
            ("spirit_animal_description", pa.string()),
            ("allegorical_image_description", pa.string()),
            ("year_range", pa.list_(pa.int32())),
            ("image_path", pa.string()),
            ("image_prompt", pa.string()),
            ("text-to-image_ai", pa.string()),
        ])

    df_totem_ai = pd.DataFrame(totems)
    totem_table_path = "./store/totem_ai" if env == "prod" else "./store_test/totem_ai"
    write_deltalake(totem_table_path, df_totem_ai, schema=totem_schema, mode='append')


if __name__ == "__main__":
    existing_spirit_animals = []
    totems = []
    year_range = [2023]
    env = "prod"
    for card in load_potatoes(env, year_range):
        totem = generate_totem(env, card["first_name"], card["last_name"], card["communication_style"], card["interests"],
                               card["personality"], card["role_in_group"], card["memorable_stories"], card["plans_aspirations"], 
                               existing_spirit_animals)
        totems.append({**totem, **{"first_name": card["first_name"], "last_name": card["last_name"], "year_range": card["year_range"]}})
    write_totems(env, totems)