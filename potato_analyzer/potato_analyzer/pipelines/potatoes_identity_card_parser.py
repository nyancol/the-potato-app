import pandas as pd
import pyarrow as pa
from deltalake import write_deltalake, DeltaTable
import subprocess as sp
import json

card_schema = pa.schema([
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("gender", pa.string()),
            ("birth_date", pa.date32()),
            ("nationalities", pa.list_(pa.string())),
        ])
    
def main():
    df = pd.read_csv("../rawdata/potatoes_identity_card.csv", sep=";")
    df["birth_date"] = pd.to_datetime(df["birth_date"], dayfirst=True)
    df["nationalities"] = df["nationalities"].apply(lambda n: n.split(','))
    print(df)
    write_deltalake("../store/potatoes_card", df, schema=card_schema, mode='overwrite', overwrite_schema=True)

if __name__ == "__main__":
    main()