import pandas as pd
from deltalake import DeltaTable, write_deltalake
from openai import OpenAI
import json
from uuid import uuid4
import requests
import pyarrow as pa
from datetime import date
from dotenv import load_dotenv


def generate_totem_description(env,person_name, person_description, messages_list, existing_spirit_animals):
    client = OpenAI()
    
    existing_spirit_animals_prompt = {'that is not ' + ', '.join(existing_spirit_animals) if existing_spirit_animals  else ''}
    prompt = f"""Here are sample messages from {person_name}, from a group chat with other friends who is {person_description}. Generate a field
    'description' to describe {person_name}, and from that description, generate two fields fields 'spirit_animal' and 'spirit_animal_description'
    describe {person_name}'s spirit animal. Then, generate a last field 'allegorical_image_description' to describe an artistic image and
    alegorical of that person in a way it could be interpreted by a text-to-image AI, this image cannot contain written text:
     {messages_list}"""

    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in describing people and their personalities from their text messages, which outputs in JSON."},
        {"role": "user", "content": prompt}
        ]
    )
    return json.loads(completion.choices[0].message.content), prompt


def generate_totem_image(env, image_description, first_name):
    client = OpenAI()
    model = "dall-e-3" if env == "prod" else "dall-e-2"
    size = "1024x1024" if env == "prod" else "256x256"
    quality = "hd" if env == "prod" else "standard"
    response = client.images.generate(
        model=model,
        prompt=image_description,
        size=size,
        quality=quality,
        n=1,
    )
    image_url = response.data[0].url
    image_path = "../store/totem_images/" if env == "prod" else "../store_test/totem_images/"
    image_path += f"{first_name + '-' + str(uuid4())}.png"
    with open(image_path, mode="wb") as f:
        f.write(requests.get(image_url).content)
    return image_path


def generate_totem(env, first_name, last_name, person_card, year_range, existing_spirit_animals):
    df = DeltaTable("../store/messages").to_pandas(partitions=[("type", "=", "text")])

    messages_size = 500 if env == "prod" else 50
    conversations = ["patates_conv_id"]
    
    df = df[(df["sender_name"] == first_name + " " + last_name) & (df["year"].isin(year_range))][["timestamp_ms", "content"]]
    messages_list = df[df["content"].str.len() > 20]["content"].head(messages_size).tolist()

    totem_ai_response, totem_description_prompt = generate_totem_description(env, first_name, person_card, messages_list, existing_spirit_animals)
    image_path = generate_totem_image(env, totem_ai_response["allegorical_image_description"], first_name)

    return {"first_name": first_name,
            "last_name": last_name,
            "description": totem_ai_response["description"],
            "spirit_animal": totem_ai_response["spirit_animal"],
            "spirit_animal_description": totem_ai_response["spirit_animal_description"],
            "allegorical_image_description": totem_ai_response["allegorical_image_description"],
            "messages_size_inference": len(messages_list),
            "year_range": year_range,
            "conversation_sources": conversations,
            "prompt": totem_description_prompt,
            "image_path": image_path,
            "image_prompt": totem_ai_response["allegorical_image_description"],
            "text-to-image_ai": "OpenAI DALL-E 3",
            }


def load_potatoes():
    df = DeltaTable("../store/potatoes_card").to_pandas()
    df["yo"] = df["birth_date"].apply(lambda bd: int((date.today() - bd).days / 365))
    df["description"] = df.apply(lambda row: f'{row["yo"]} years old young {", ".join(row["nationalities"])} {row["gender"]}', axis=1)
    potato_cards = [{"first_name": row["first_name"], "last_name": row["last_name"], "description": row["description"]}
                    for row in df.to_dict(orient="records")]
    return potato_cards


def write_totems(env, totems):
    totem_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("description", pa.string()),
            ("spirit_animal", pa.string()),
            ("spirit_animal_description", pa.string()),
            ("allegorical_image_description", pa.string()),
            ("messages_size_inference", pa.int32()),
            ("year_range", pa.list_(pa.int32())),
            ("conversation_sources", pa.list_(pa.string())),
            ("prompt", pa.string()),
            ("image_path", pa.string()),
            ("image_prompt", pa.string()),
            ("text-to-image_ai", pa.string()),
        ])

    df_totem_ai = pd.DataFrame(totems)
    totem_table_path = "../store/totem_ai" if env == "prod" else "../store_test/totem_ai"
    write_deltalake(totem_table_path, df_totem_ai, schema=totem_schema, mode='append')


if __name__ == "__main__":
    existing_spirit_animals = []
    year_range = [2023]
    totems = []
    env = "test"
    for card in load_potatoes():
        totems.append(generate_totem(env, card["first_name"], card["last_name"], card["description"], year_range, existing_spirit_animals))
        break
    write_totems(env, totems)