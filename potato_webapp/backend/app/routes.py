from flask import jsonify, send_from_directory, request
from flask_cors import CORS
from pathlib import Path
from deltalake import DeltaTable
import json
from app import app
import sys


CORS(app) # , resources={r"/api/*": {"origins": "http://localhost:8080"}})  # Update with your frontend URL

# if len(sys.argv) >= 1 and sys.argv[1] == "prod":
base_path = Path("/Users/i501383/Documents/potato_gallery/store")
# else:
# base_path = Path("/Users/i501383/Documents/potato_gallery/store_test")


@app.route("/api/images/data/", methods=["GET"])
def get_image_data():
    try:
        year_param = request.args.get("year", type=int)
    except ValueError:
        return jsonify({"error": "Invalid year parameter"}), 400

    df = DeltaTable(base_path / "totem_ai").to_pandas(columns=["first_name", "last_name", "spirit_animal",
                                                               "spirit_animal_description", "image_path", "year_range"])
    df = df[df.year_range.apply(lambda yr: len(yr) == 1 and yr[0] == year_param)]
    df["filename"] = df["image_path"].apply(lambda p: p.split('/')[-1])
    totem_records = json.loads(df.to_json(orient="records"))    
    return jsonify(totem_records)


@app.route('/api/images/<filename>')
def get_image(filename):
    return send_from_directory(base_path / "totem_images", filename)


@app.route("/api/images/pokemon-data/", methods=["GET"])
def get_pokemon_data():
    try:
        year_param = request.args.get("year", type=int)
    except ValueError:
        return jsonify({"error": "Invalid year parameter"}), 400

    df = DeltaTable(base_path / "pokemon_ai").to_pandas(columns=["first_name", "last_name", "pokemon_name",
                                                               "pokemon_description", "L1_image_path", "L2_image_path",
                                                               "L3_image_path", "year_range"])
    df = df[df.year_range.apply(lambda yr: len(yr) == 1 and yr[0] == 2023)]
    df["images"] = df.apply(lambda row: [row["L1_image_path"].split('/')[-1],
                                       row["L2_image_path"].split('/')[-1],
                                       row["L3_image_path"].split('/')[-1],
                                       ], axis=1)
    pokemon_records = json.loads(df.to_json(orient="records")) 
    return jsonify(pokemon_records)


@app.route('/api/pokemon-images/<filename>')
def get_pokemon_image(filename):
    return send_from_directory(base_path / "pokemon_images", filename)
