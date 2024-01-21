import json
from time import sleep
from uuid import uuid4
from datetime import date

from openai import OpenAI
from deltalake import DeltaTable, write_deltalake
import requests
import pandas as pd
import pyarrow as pa
from dotenv import load_dotenv

load_dotenv()


def generate_pokemon_description(env, first_name, communication_style, interests, personality, role_in_group,
                                 memorable_stories, plans_aspirations):
    client = OpenAI()

    prompt = f"""Generate as a JSON object, a pokemon representing a friend named {first_name}, who has the following
    caracteristics:
    Personality: '{personality}'
    Communication style: '{communication_style}'
    Interests: '{interests}'
    The person role in a group of friends: '{role_in_group}'
    Memorable stories: '{memorable_stories}'
    Plans and aspirations: '{plans_aspirations}'.

    If that person where to be a pokemon, what would be his/her "pokemon_name" and "pokemon_description"?

    Additionnaly, generate three artistic image descriptions, representing what that person would look like as a
    pokemon, in a way it could be interpreted by a text-to-image AI, for all three pokemon evolution levels,
    "L1_image_description", "L2_image_description",  "L3_image_description". These levels are: starter (when the
    pokemon is small and cute), normal (when the pokemon is at it's normal form) and super ultra legendary
    (when the pokemon is at its mightiest). Be only descriptive of the image without commenting on the meaning
    and repetitive in the description for the different levels, they will be interpreted independently.
    Return a json with five fields: "pokemon_name", "pokemon_description", "L1_image_description",
    "L2_image_description",  "L3_image_description"."""

    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": """You are a poetic assistant, skilled in describing people and their
        personalities as pokemons images based on a desciption, which outputs in JSON."""},
                {"role": "user", "content": prompt}
            ]
        )
    return json.loads(completion.choices[0].message.content), prompt


def generate_pokemon_image(env, first_name, last_name, evolution, image_description):
    prompt = f"""Create an image in the style of a pokemon card representing {image_description}.
    Do not write any text in the image."""

    client = OpenAI()
    model = "dall-e-3" if env == "prod" else "dall-e-2"
    size = "1024x1024" if env == "prod" else "256x256"
    quality = "hd" if env == "prod" else "standard"
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    image_url = response.data[0].url
    image_path = "./pokemon_images/" if env == "prod" else "./store_test/pokemon_images/"
    image_path += f"{first_name}-{last_name}-{evolution}-{str(uuid4())}.png"
    with open(image_path, mode="wb") as f:
        f.write(requests.get(image_url).content)
    return image_path


def generate_pokemon(env, first_name, last_name, communication_style, interests, personality, role_in_group,
                     memorable_stories, plans_aspirations):
    pokemon_description, prompt = generate_pokemon_description(env, first_name, communication_style, interests,
                                                               personality, role_in_group, memorable_stories,
                                                               plans_aspirations)
    for i in range(1, 4):
        pokemon_description[f"L{i}_image_path"] = generate_pokemon_image(env, first_name, last_name, i,
                                                                         pokemon_description[f"L{i}_image_description"])
    return {**pokemon_description, **{"prompt": prompt, "text-to-image_ai": "OpenAI DALL-E 3"}}


def load_potatoes(env, year_range):
    potato_description_path = "./store/potato_description_ai" if env == "prod" else "./store_test/potato_description_ai"
    df = DeltaTable(potato_description_path).to_pandas(columns=["first_name", "last_name", "communication_style",
                                                                "interests", "personality", "role_in_group",
                                                                "memorable_stories", "plans_aspirations", "year_range"])
    df = df[df.year_range.apply(lambda yr: yr[0] == year_range[0])]
    return df.to_dict(orient="records")


def write_pokemons(env, pokemons):
    pokemon_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("pokemon_name", pa.string()),
            ("pokemon_description", pa.string()),
            ("L1_image_description", pa.string()),
            ("L2_image_description", pa.string()),
            ("L3_image_description", pa.string()),
            ("L1_image_path", pa.string()),
            ("L2_image_path", pa.string()),
            ("L3_image_path", pa.string()),
            ("year_range", pa.list_(pa.int32())),
            ("prompt", pa.string()),
            ("text-to-image_ai", pa.string()),
        ])

    df_totem_ai = pd.DataFrame(pokemons)
    pokemon_table_path = "./store/pokemon_ai" if env == "prod" else "./store_test/pokemon_ai"
    write_deltalake(pokemon_table_path, df_totem_ai, schema=pokemon_schema, mode='append')


if __name__ == "__main__":
    env = "test"
    year_range = [2023]
    pokemons = []
    for potato in load_potatoes(env, year_range):
        # sleep(60)
        pokemon = generate_pokemon(env, potato["first_name"], potato["last_name"], potato["communication_style"],
                                   potato["interests"], potato["personality"], potato["role_in_group"],
                                   potato["memorable_stories"], potato["plans_aspirations"])
        pokemons.append({**pokemon, **{"year_range": year_range, "first_name": potato["first_name"],
                                        "last_name": potato["last_name"]}})
        break
    write_pokemons(env, pokemons)
