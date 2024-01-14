from app import db, app
from app.models import Patate
from deltalake import DeltaTable
from pathlib import Path

# if len(sys.argv) >= 1 and sys.argv[1] == "prod":
base_path = Path("/Users/i501383/Documents/the-potato-app/store")
# else:
# base_path = Path("/Users/i501383/Documents/the-potato-app/store_test")

def init_patates(db):
    df = DeltaTable(base_path / "potatoes_card").to_pandas()
    print(df)
    for patate in df.apply(lambda row: Patate(first_name=row["first_name"],
                                                last_name=row["last_name"],
                                                gender=row["gender"],
                                                birth_date=row["birth_date"],
                                                birth_country=row["birth_country"],
                                                birth_city=row["birth_city"],
                                                email=row["email"]), axis=1):
        db.session.add(patate)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        init_patates(db)
