import pandas as pd
from deltalake import DeltaTable, write_deltalake
from openai import OpenAI
import json
import pyarrow as pa
from datetime import date
from dotenv import load_dotenv

load_dotenv()


def generate_potato_description(env, first_name, last_name, person_card, year_range):
    df = DeltaTable("./store/messages").to_pandas(partitions=[("type", "=", "text")])

    messages_size = 500 if env == "prod" else 50
    conversations = ["patates_conv_id"]
    
    df = df[(df["sender_name"] == first_name + " " + last_name) & (df["year"].isin(year_range))][["timestamp_ms", "content"]]
    messages_list = df[df["content"].str.len() > 20]["content"].head(messages_size).tolist()


    client = OpenAI()
    
    prompt = f"""Here are sample messages from {first_name}, from a group chat with other friends who is {person_card}. Generate a field
    a json to describe {first_name} that person along these fields:

- Communication Style (json field "communication_style" like {{"topic1": "description1", "topic2": "decription2"}}):
    Note how each friend communicates – whether they use humor, sarcasm, or are more straightforward.
    Identify any unique phrases, inside jokes, or language quirks that are specific to each person.
    Interests and Hobbies:

- Observe discussions about hobbies, interests, and passions (json field "interests" like {{"topic1": "description1", "topic2": "decription2"}}):
    Highlight any shared activities, such as sports, movies, books, or other cultural pursuits.

- Personality Traits (json field "personality" like {{"topic1": "description1", "topic2": "decription2"}}):
    Identify key personality traits that stand out in conversations (e.g., extroverted, introverted, adventurous, analytical)
    Note how they handle various situations – are they calm, enthusiastic, or empathetic?

- Roles in the Group (json field "role_in_group" in the form of a string):
    Recognize any roles each friend plays in the group dynamic (e.g., the planner, the mediator, the comedian).

- Memorable Stories (json field "memorable_stories" like {{"topic1": "description1", "topic2": "decription2"}}):
    Pick out memorable anecdotes or stories shared in the group that define each friend's character. Mention any significant life events
    or experiences that have been discussed.

- Plans and Aspirations (json field "plans_aspirations" like {{"topic1": "description1", "topic2": "decription2"}}):
    Gather information on future plans, goals, or aspirations that have been discussed. Include any ambitions or dreams that
    friends have shared in the group.

Here below are the messages extracts:
"""
    prompt_context = prompt + "\n" + str(messages_list)



    model = "gpt-4-1106-preview" if env == "prod" else "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": "You are an assistant, skilled in describing people and their personalities from their text messages, which outputs in JSON."},
        {"role": "user", "content": prompt_context}
        ]
    )
    description_response = json.loads(completion.choices[0].message.content)
    return {
            "communication_style": description_response["communication_style"],
            "interests": description_response["interests"],
            "personality": description_response["personality"],
            "role_in_group": description_response["role_in_group"],
            "memorable_stories": description_response["memorable_stories"],
            "plans_aspirations": description_response["plans_aspirations"],
            "messages_size_inference": len(messages_list),
            "conversation_sources": conversations,
            "prompt": prompt,
            }


def load_potatoes():
    df = DeltaTable("./store/potatoes_card").to_pandas()
    df["yo"] = df["birth_date"].apply(lambda bd: int((date.today() - bd).days / 365))
    df["gender"] = df["gender"].apply(lambda g: "man" if g == "male" else "woman")
    df["description"] = df.apply(lambda row: f'{row["yo"]} years old young {", ".join(row["nationalities"])} {row["gender"]}', axis=1)
    potato_cards = [{"first_name": row["first_name"], "last_name": row["last_name"], "description": row["description"]}
                    for row in df.to_dict(orient="records")]
    return potato_cards


def write_potato_descriptions(env, potato_descriptions):
    potato_description_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("communication_style", pa.map_(pa.string(), pa.string())),
            ("interests", pa.map_(pa.string(), pa.string())),
            ("personality", pa.map_(pa.string(), pa.string())),
            ("role_in_group", pa.string()),
            ("memorable_stories", pa.map_(pa.string(), pa.string())),
            ("plans_aspirations", pa.map_(pa.string(), pa.string())),
            ("messages_size_inference", pa.int32()),
            ("year_range", pa.list_(pa.int32())),
            ("conversation_sources", pa.list_(pa.string())),
            ("prompt", pa.string()),
        ])

    df_description_ai = pd.DataFrame(potato_descriptions)
    for field in ["communication_style", "interests", "personality", "memorable_stories", "plans_aspirations", ]:
        df_description_ai[field] = df_description_ai[field].apply(lambda cs: {str(k): str(v) for k, v in cs.items()})
    description_table_path = "./store/potato_description_ai" if env == "prod" else "./store_test/potato_description_ai"
    write_deltalake(description_table_path, df_description_ai, schema=potato_description_schema, mode='append')


if __name__ == "__main__":
    year_range = [2019, 2021, 2023]
    personalities = []
    env = "prod"
    for card in load_potatoes():
        for year in year_range:
            personality = generate_potato_description(env, card["first_name"], card["last_name"], card["description"], [year])
            personalities.append({**personality, **{"first_name": card["first_name"], "last_name": card["last_name"],
                                                   "year_range": [year]}})
    write_potato_descriptions(env, personalities)