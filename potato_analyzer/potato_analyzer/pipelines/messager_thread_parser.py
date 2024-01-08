import pandas as pd
import pyarrow as pa
from deltalake import write_deltalake, DeltaTable
import subprocess as sp
import json

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
            ("call_duration", pa.int32())
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
            ("year", pa.int32()),
            ("month", pa.int32()),
        ])


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
    df = DeltaTable("./store/rw_messages", ).to_pandas()
    df["year"] = df["timestamp_ms"].dt.year
    df["month"] = df["timestamp_ms"].dt.month

    df["first_name"] = df["sender_name"].apply(lambda name: name.split(' ')[0])
    df["last_name"] = df["sender_name"].apply(lambda name: ' '.join(name.split(' ')[1:]))

    df["reactions"] = df["reactions"].apply(lambda r: list() if r is  None else r)
    df["photos"] = df["photos"].apply(lambda r: list() if r is None else r)
    
    write_deltalake("./store/messages", df, schema=messages_silver_schema, mode='overwrite',
                    partition_by=["year", "type"], overwrite_schema=True)


def create_bronze_messages_table():
    messages = []
    rawdata_path = "./rawdata/your_activity_across_facebook/messages/inbox/lespatatesvirerargentmag16940_2365204306876958"

    for i in range(1, 9):
        res = sp.run(f"cat {rawdata_path}/message_{i}.json | jq . | iconv -f utf8 -t latin1 > {rawdata_path}/message_{i}_decoded.json", shell=True)
        with open(f"{rawdata_path}/message_{i}_decoded.json", mode="r", encoding="utf-8") as f:
            messages.extend(parse_message_file(json.load(f)))
    df = pd.DataFrame(messages)
    df["timestamp_ms"] = df["timestamp_ms"] * 1000

    photos_fix = df["photos"].dropna().apply(lambda phts: [{"uri": p["uri"], "creation_timestamp": p["creation_timestamp"] * 1000} for p in phts])
    df["photos"] = photos_fix
    
    videos_fix = df["videos"].dropna().apply(lambda vds: [{"uri": v["uri"], "creation_timestamp": v["creation_timestamp"] * 1000} for v in vds])
    df["videos"] = videos_fix

    audio_fix = df["audio_files"].dropna().apply(lambda auds: [{"uri": a["uri"], "creation_timestamp": a["creation_timestamp"] * 1000} for a in auds])
    df["audio_files"] = audio_fix

    write_deltalake("./store/rw_messages", df, schema=messages_bronze_schema, mode='overwrite')
    print(len(df))
    return df

if __name__ == "__main__":
    create_silver_messages_table()
    # create_bronze_messages_table()
