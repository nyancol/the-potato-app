import pandas as pd
import pyarrow as pa
from deltalake import write_deltalake

potato_location_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("country", pa.string()),
            ("city", pa.string()),
            ("address", pa.string()),
            ("post_code", pa.string()),
            ("from_timestamp", pa.date32()),
            ("to_timestamp", pa.date32()),
])

potato_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("gender", pa.string()),
            ("birth_date", pa.date32()),
            ("birth_country", pa.string()),
            ("birth_city", pa.string()),
            ("nationalities", pa.list_(pa.string())),
            ("email", pa.string()),
            ("phone", pa.string()),
        ])

def potatoes_card():
    df = pd.read_csv("../rawdata/potatoes_identity_card.csv", sep=";",
                     dtype={"phone": "string"})
    df["birth_date"] = pd.to_datetime(df["birth_date"], dayfirst=True)
    df["nationalities"] = df["nationalities"].apply(lambda n: n.split(','))
    print(df)
    write_deltalake("../store/potatoes_card", df, schema=potato_schema,
                    mode='overwrite', overwrite_schema=True)


def potato_locations():
    df = pd.read_csv("../rawdata/potato_locations.csv", sep=";")
    df["from_timestamp"] = pd.to_datetime(df["from_timestamp"], dayfirst=True)
    df["to_timestamp"] = pd.to_datetime(df["to_timestamp"], dayfirst=True)
    print(df)
    write_deltalake("../store/potato_locations", df, schema=potato_location_schema,
                    mode='overwrite', overwrite_schema=True)


if __name__ == "__main__":
    potatoes_card()
    potato_locations()
