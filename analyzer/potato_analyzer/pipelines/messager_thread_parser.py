from pathlib import Path
import subprocess as sp
import json

import pandas as pd
import pyarrow as pa
from deltalake import write_deltalake, DeltaTable

messenger_schema = pa.schema([
            ("id", pa.string()),
            ("messenger_id", pa.string()),
            ("version", pa.int32()),
])

messages_bronze_schema = pa.schema([
            ("sender_name", pa.string()),
            ("photos", pa.list_(pa.struct([("uri", pa.string()), ("creation_timestamp", pa.timestamp("us"))]))),
            ("timestamp_ms", pa.timestamp("us")),
            ("reactions", pa.list_(pa.struct([("reaction", pa.string()), ("actor", pa.string())]))),
            ("type", pa.string()),
            ("content", pa.string()),
            ("gifs", pa.list_(pa.struct([("uri", pa.string())]))),
            ("videos", pa.list_(pa.struct([("uri", pa.string()), ("creation_timestamp", pa.timestamp("us"))]))),
            ("share", pa.struct([("link", pa.string())])),
            ("audio_files", pa.list_(pa.struct([("uri", pa.string()), ("creation_timestamp", pa.timestamp("us"))]))),
            ("sticker", pa.struct([("uri", pa.string()), ("ai_stickers", pa.list_(pa.string()))])),
            ("call_duration", pa.int32()),
            ("messenger_id", pa.string())
        ])

messages_silver_schema = pa.schema([
            ("sender_name", pa.string()),
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("photos", pa.list_(pa.struct([("uri", pa.string()), ("creation_timestamp", pa.timestamp("us"))]))),
            ("timestamp_ms", pa.timestamp("us")),
            ("reactions", pa.list_(pa.struct([("reaction", pa.string()), ("actor", pa.string())]))),
            ("type", pa.string()),
            ("content", pa.string()),
            ("gifs", pa.list_(pa.struct([("uri", pa.string())]))),
            ("videos", pa.list_(pa.struct([("uri", pa.string()), ("creation_timestamp", pa.timestamp("us"))]))),
            ("share", pa.struct([("link", pa.string())])),
            ("audio_files", pa.list_(pa.struct([("uri", pa.string()), ("creation_timestamp", pa.timestamp("us"))]))),
            ("sticker", pa.struct([("uri", pa.string()), ("ai_stickers", pa.list_(pa.string()))])),
            ("call_duration", pa.int32()),
            ("conversation_id", pa.string()),
            ("year", pa.int32()),
            ("month", pa.int32()),
        ])


def create_messenger_convs():
    df = pd.read_csv("../rawdata/messenger_conversations.csv", sep=";")
    write_deltalake("../store/messenger_conversations", df, schema=messenger_schema,
                    mode="overwrite")


def parse_message_file(content):
    participants = content["participants"]
    messages = []
    for entry in content["messages"]:
        if "content" in entry:
            type = "text"
        elif "videos" in entry:
            type = "videos"
        elif "photos" in entry:
            type = "photos"
        elif "gifs" in entry:
            type = "gifs"
        elif "audio_files" in entry:
            type = "audio"
        elif "sticker" in entry:
            type = "sticker"
        elif "files" in entry:
            type = "file"
        elif "is_unsent" in entry:
            pass
        elif set(entry.keys()) <= {"sender_name", "timestamp_ms", "is_geoblocked_for_viewer", "reactions"}:
            pass
        else:
            raise Exception(f"Unknown message type for entry '{entry}'")
        messages.append({**entry, **{"type": type}})
    return messages

def create_silver_messages_table():
    df_messenger_ids = DeltaTable("../store/messenger_conversations").to_pandas(columns=["messenger_id", "id"])
    df = DeltaTable("../store/rw_messages", ).to_pandas()
    df = df.set_index("messenger_id").join(df_messenger_ids.set_index("messenger_id"))
    df = df.rename(columns={'id': 'conversation_id'})

    df["year"] = df["timestamp_ms"].dt.year
    df["month"] = df["timestamp_ms"].dt.month

    df["first_name"] = df["sender_name"].apply(lambda name: name.split(' ')[0])
    df["last_name"] = df["sender_name"].apply(lambda name: ' '.join(name.split(' ')[1:]))

    df["reactions"] = df["reactions"].apply(lambda r: list() if r is  None else r)
    df["photos"] = df["photos"].apply(lambda r: list() if r is None else r)

    write_deltalake("../store/messages", df, schema=messages_silver_schema, mode='overwrite',
                    partition_by=["conversation_id", "year", "type"], overwrite_schema=True)
    print(len(df))


def create_bronze_messages_table(messenger_id):
    rawdata_path = Path("../rawdata/your_activity_across_facebook/messages/inbox/" + messenger_id)
    messages = []

    for path in rawdata_path.rglob('*.json'):
        print(path)
        res = sp.run(f"cat {path} | jq . | iconv -f utf8 -t latin1 > {path}_decoded.json", shell=True)
        decoded_file = Path(f"{path}_decoded.json")
        with open(decoded_file, mode="r", encoding="utf-8") as f:
            messages.extend(parse_message_file(json.load(f)))
        decoded_file.unlink()


    df = pd.DataFrame(messages)
    df["messenger_id"] = messenger_id
    df["timestamp_ms"] = df["timestamp_ms"] * 1000

    if "sticker" not in df.columns:
        df["sticker"] = dict()

    if "share" not in df.columns:
        df["share"] = dict()

    if "gifs" not in df.columns:
        df["gifs"] = [None] * len(df)

    if "reactions" not in df.columns:
        df["reactions"] = [None] * len(df)

    if "photos" in df.columns:
        photo_fix_lambda = lambda phts: [{"uri": p["uri"],
                                          "creation_timestamp": p["creation_timestamp"] * 1000} for p in phts]
        photos_fix = df["photos"].dropna().apply(photo_fix_lambda)
        df["photos"] = photos_fix
    else:
        df["photos"] = None

    if "videos" in df.columns:
        video_fix_lambda = lambda vds: [{"uri": v["uri"],
                                         "creation_timestamp": v["creation_timestamp"] * 1000} for v in vds]
        videos_fix = df["videos"].dropna().apply(video_fix_lambda)
        df["videos"] = videos_fix
    else:
        df["videos"] = [None] * len(df)

    if "audio_files" in df.columns:
        audio_fix_lambda = lambda auds: [{"uri": a["uri"],
                                          "creation_timestamp": a["creation_timestamp"] * 1000} for a in auds]
        audio_fix = df["audio_files"].dropna().apply(audio_fix_lambda)
        df["audio_files"] = audio_fix
    else:
        df["audio_files"] = [None] * len(df)

    if "call_duration" not in df.columns:
        df["call_duration"] = None

    write_deltalake("../store/rw_messages", df, schema=messages_bronze_schema, mode='append', overwrite_schema=True)
    print(len(df))
    return df


if __name__ == "__main__":
    create_messenger_convs()
    messenger_ids = DeltaTable("../store/messenger_conversations").to_pandas()["messenger_id"].tolist()
    for m_id in messenger_ids:
        create_bronze_messages_table(m_id)
    create_silver_messages_table()
