import sqlite3
import csv
from flask import Flask, render_template, request

# creates connection and cursor
conn = sqlite3.connect("pokedex.db")
c = conn.cursor()

# creates table if it does not exist
c.execute("""
CREATE TABLE IF NOT EXISTS Pokemon(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Type1 TEXT,
    Type2 TEXT,
    Total INTEGER,
    HP INTEGER,
    Attack INTEGER,
    Defence INTEGER,
    Sp_Atk INTEGER,
    Sp_Def INTEGER,
    Speed INTEGER,
    Generation INTEGER,
    Legendary INTEGER
);
""")

# insert function
def insert(pokemon: list):
    """Accepts a pokemon and inserts them into the database"""
    data = pokemon
    # formats data
    for i in range(len(data)):
        if i in range(4,12):
            data[i] = int(data[i])
        if i == 12:
            data[i] = int(bool(data[i]))
    # inserts data, except id because autoincremet amazing
    c.execute("""
    INSERT OR IGNORE INTO Pokemon(Name, Type1, Type2, Total, HP, Attack, Defence, Sp_Atk, 
    Sp_Def, Speed, Generation, Legendary) VALUES
    (?,?,?,?,?,?,?,?,?,?,?,?)
    """, data[1:])

# input validation for types
def types_validation(stat: str) -> bool:
    return stat.capitalize() in ["Normal", "Fire", "Water", "Grass", "Flying",
    "Fighting", "Poison","Electric", "Ground", "Rock", "Psychic", "Ice", "Bug", "Ghost",
    "Steel", "Dragon", "Dark", "Fairy",""]

# main event loop
# reads csv file and inserts it into database
with open("Pokemon.csv") as file:
    reader = csv.reader(file)
    header = next(reader)
    for pokemon in reader:
        insert(pokemon)
    conn.commit()

# creates flask webapp
app = Flask(__name__)

# routes
@app.route('/', methods = ["GET", "POST"])
def index():
    query = request.form.get("query", "SELECT * FROM Pokemon WHERE ID <= 10")
    pokemons = c.execute(query)
    return render_template("index.html", pokemons = pokemons)

# runs flask webapp
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    # waits till the server is shut down, and closes database and commits changes
    conn.commit()
    conn.close()