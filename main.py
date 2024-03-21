import sqlite3
import csv
from flask import Flask, render_template, request

# gets pokemon
def get_pokemon(query: str):
    """Takes an SQL query and cursor and returns a list of pokemon"""
    conn = sqlite3.connect("pokedex.db")
    c = conn.cursor()
    c.execute(query)
    # if the previous query was an insert, select the last added pokemon
    if query.startswith("INSERT"):
        query = "SELECT * FROM Pokemon ORDER BY ID DESC"
        c.execute(query)
        pokemons = [c.fetchone()]
    else:
        # gets results and renders webpage
        pokemons = c.fetchall()
    # commits and closes connection
    conn.commit()
    conn.close()
    return pokemons

# main event loop
# creates connection and cursor
conn = sqlite3.connect("pokedex.db")
c = conn.cursor()
# creates table if it does not exist
c.execute("""
CREATE TABLE IF NOT EXISTS Pokemon(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT UNIQUE,
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

# reads csv file and inserts it into database
with open("Pokemon.csv") as file:
    reader = csv.reader(file)
    header = next(reader)
    for pokemon in reader:
        data = pokemon
        # formats data
        for i in range(len(data)):
            if i in range(4,12):
                data[i] = int(data[i])
            if i == 12:
                if data[i] == "TRUE":
                    data[i] = 1
                else:
                    data[i] = 0
        # inserts data, except id because autoincremet amazing
        c.execute("""
        INSERT OR IGNORE INTO Pokemon(Name, Type1, Type2, Total, HP, Attack, Defence, Sp_Atk, 
        Sp_Def, Speed, Generation, Legendary) VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?)
        """, data[1:])

# commits and closes
conn.commit()
conn.close()

# creates flask webapp
app = Flask(__name__)

# damn... this code kinda ass.
# routes
@app.route('/')
def index():
    query = "SELECT * FROM Pokemon WHERE ID <= 10"
    pokemons = get_pokemon(query)
    return render_template("index.html", pokemons = pokemons)

@app.route('/number', methods=["GET", "POST"])
def numberOfPokemon():
    if request.method == "GET":
        return render_template("number.html")
    # post
    number = request.form.get("number")
    if not number:
        return render_template("number.html", message = "Please enter a number")
    number = int(number)
    # gets the total number of pokemon and verifies the number entered
    conn = sqlite3.connect("pokedex.db")
    c = conn.cursor()
    c.execute("SELECT Count(ID) FROM Pokemon")
    totalNumberOfPokemon = c.fetchone()[0]
    conn.commit()
    conn.close()

    # if the number is not valid, return an error.
    if number > totalNumberOfPokemon or number <= 0:
        return render_template("number.html", message="Please enter a valid number of Pokemon.")
    # else, execute query
    query = "SELECT * FROM Pokemon"
    pokemons = get_pokemon(query)[:number]
    return render_template("index.html", pokemons = pokemons)

@app.route('/type', methods=["GET", "POST"])
def pokemonWithType():
    if request.method == "GET":
        return render_template("type.html")
    # post
    type = request.form.get("type")
    query = "SELECT * FROM Pokemon WHERE Pokemon.Type1 = '{}' OR Pokemon.Type2 = '{}'".format(type,type)
    print(query)
    pokemons = get_pokemon(query)
    return render_template("index.html", pokemons = pokemons[0:1])

@app.route('/totalbase', methods=["GET", "POST"])
def pokemonWithTotalBaseStat():
    if request.method == "GET":
        return render_template("totalbase.html")
    # post
    totalbase = request.form.get("total")
    if not totalbase:
        return render_template("totalbase.html", message = "Please enter a total base stat")
    totalbase = int(totalbase)
    query = "SELECT * FROM Pokemon WHERE total = {}".format(totalbase)
    pokemons = get_pokemon(query)
    if pokemons:
        return render_template("index.html", pokemons = pokemons)
    else:
        return render_template("totalbase.html", message = "There are no pokemon with the total base stat specified")
    
@app.route('/minstats', methods=["GET", "POST"])
def pokemonWithMinStats():
    if request.method == "GET":
        return render_template("minstats.html")
    # post
    spatk = request.form.get("spatk")
    spdef = request.form.get("spdef")
    speed = request.form.get("speed")
    if not spatk or not spdef or not speed:
        return render_template("minstats.html", message = "Please enter the special attack, special defence, and speed")
    spatk = int(spatk)
    spdef = int(spdef)
    speed = int(speed)
    query = "SELECT * FROM Pokemon WHERE Sp_Atk >= {} AND Sp_Def >= {} AND Speed >= {}".format(spatk, spdef, speed)
    pokemons = get_pokemon(query)
    if pokemons:
        return render_template("index.html", pokemons = pokemons)
    else:
        return render_template("minstats.html", message = "There are no pokemon with the minimum specified")
    
@app.route("/legendary", methods=["GET", "POST"])
def legendaryWithTypes():
    if request.method == "GET":
        return render_template("legendary.html")
    # post
    type1 = request.form.get("type1")
    type2 = request.form.get("type2").strip()
    query = "SELECT * FROM Pokemon WHERE Legendary = 1 AND Type1 = '{}' AND Type2 = '{}' OR Legendary = 1 AND Type1 = '{}' AND Type2 = '{}'".format(type1, type2, type2, type1)
    pokemons = get_pokemon(query)
    if pokemons:
        return render_template("index.html", pokemons = pokemons)
    else:
        return render_template("legendary.html", message = "There are no legendary pokemon with the types specified")

@app.route("/insert", methods=["GET", "POST"])
def insert():
    if request.method == "GET":
        return render_template("insert.html")
    # post
    name = request.form.get("name")
    type1 = request.form.get("type1")
    type2 = request.form.get("type2").strip()
    hp = request.form.get("hp")
    atk = request.form.get("atk")
    defence = request.form.get("def")
    spatk = request.form.get("spatk")
    spdef = request.form.get("spdef")
    speed = request.form.get("speed")
    gen = request.form.get("gen")
    legendary = request.form.get("legendary")

    # presence check
    if not name or not hp or not atk or not defence or not spatk or not spdef or not speed or not gen or not legendary:
        return render_template("insert.html", message = "Please enter all of the stats of the pokemon.")
    # formatting
    hp = int(hp)
    atk = int(atk)
    defence = int(defence)
    spatk = int(spatk)
    spdef = int(spdef)
    speed = int(speed)
    gen = int(gen)
    if legendary == "True":
        legendary = 1
    else:
        legendary = 0
    # range check
    if hp < 0  or atk < 0 or defence < 0 or spatk < 0 or spdef < 0 or speed < 0 or gen < 1:
        return render_template("insert.html", message = "Please enter make sure all of the stats are valid.")
    
    total = hp + atk + defence + spatk + spdef + speed
    
    query = """INSERT OR IGNORE INTO Pokemon (Name, Type1, Type2, Total, HP, Attack, Defence, Sp_Atk, Sp_Def, Speed, Generation, Legendary)
    VALUES ('{}','{}','{}',{},{},{},{},{},{},{},{},{})
    """
    query = query.format(name, type1, type2, total, hp, atk, defence, spatk, spdef, speed, gen, legendary)
    print(query)
    pokemons = get_pokemon(query)
    return render_template("index.html", pokemons = pokemons)

@app.route("/minhp", methods=["GET", "POST"])
def typeWithMinHP():
    if request.method == "GET":
        return render_template("minhp.html")
    # post
    minhp = request.form.get("hp") 
    if not minhp:
        return render_template("minhp.html", message = "Please enter a minimum HP")
    minhp = int(minhp)
    if minhp < 0:
        return render_template("minhp.html", message = "Please enter a valid HP number")
    query = "SELECT Type1, Count(ID) FROM Pokemon WHERE HP >= {} GROUP BY Type1 ORDER BY HP DESC".format(minhp)
    # connect to db and create cursor
    conn = sqlite3.connect("pokedex.db")
    c = conn.cursor()
    c.execute(query)
    results = c.fetchall()
    print(results)
    if not results:
        return render_template("minhp.html", message = "There are no pokemon with a HP equal to or above to the amount specified.")
    return render_template("index.html", minhptypes = results)

# runs flask webapp
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)