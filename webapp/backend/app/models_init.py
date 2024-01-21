from pathlib import Path
from deltalake import DeltaTable
from app import db, app, migrate
from app.models import Patate, PatateLocation, SpiritAnimal, Pokemon

# if len(sys.argv) >= 1 and sys.argv[1] == "prod":
base_path = Path("/Users/i501383/Documents/the-potato-app/store")
# else:
# base_path = Path("/Users/i501383/Documents/the-potato-app/store_test")

def init_patates(db):
    df_patates = DeltaTable(base_path / "potatoes_card").to_pandas()
    df_patate_locations = DeltaTable(base_path / "potato_locations").to_pandas()
    df_spirit_animal = DeltaTable(base_path / "totem").to_pandas()
    df_pokemon = DeltaTable(base_path / "pokemon_ai").to_pandas()

    new_patate = lambda row: Patate(first_name=row["first_name"],
                                    last_name=row["last_name"],
                                    gender=row["gender"],
                                    birth_date=row["birth_date"],
                                    birth_country=row["birth_country"],
                                    birth_city=row["birth_city"],
                                    email=row["email"],
                                    phone=row["phone"])
    for patate in df_patates.apply(new_patate, axis=1):
        db.session.add(patate)

    patates = Patate.query.all()
    for i, row in df_patate_locations.iterrows():
        patate_id = Patate.query.filter_by(first_name=row["first_name"],
                                           last_name=row["last_name"]).first().id
        patate_location = PatateLocation(patate_id,
                                         row["from_timestamp"],
                                         row["to_timestamp"],
                                         row["city"],
                                         row["country"],
                                         row["address"],
                                         row["post_code"])
        db.session.add(patate_location)

    for i, row in df_spirit_animal.iterrows():
        patate_id = Patate.query.filter_by(first_name=row["first_name"],
                                           last_name=row["last_name"]).first().id
        spirit_animal = SpiritAnimal(patate_id,
                                         row["spirit_animal"],
                                         row["spirit_animal_description"],
                                         row["image_path"])
        db.session.add(spirit_animal)

    for i, row in df_pokemon.iterrows():
        patate_id = Patate.query.filter_by(first_name=row["first_name"],
                                           last_name=row["last_name"]).first().id
        pokemon = Pokemon(patate_id, row["pokemon_name"],
                          row["L1_image_description"],row["L2_image_description"],
                          row["L3_image_description"], row["L1_image_path"],
                          row["L2_image_path"], row["L3_image_path"])
        db.session.add(pokemon)
    db.session.commit()


if __name__ == "__main__":
    migrate.init_app(app, db)
    with app.app_context():
        init_patates(db)
