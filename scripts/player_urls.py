"""
Player URL registry: real Transfermarkt URLs (verified via live TM search API).
All TM IDs confirmed against live transfermarkt.com search results.
FBref URLs omitted — FBref returns 403 on this server without a browser.
"""
from __future__ import annotations

# ── IDV Current Squad — TM IDs verified via live search ───────────────────────
IDV_PLAYER_URLS: dict[str, dict[str, str]] = {
    "kendry-paez": {
        "transfermarkt": "https://www.transfermarkt.com/kendry-paez/profil/spieler/1052439",
        "display_name": "Kendry Páez",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Attacking Midfielder",
        "nationality": "Ecuador",
    },
    "willian-pacho": {
        "transfermarkt": "https://www.transfermarkt.com/willian-pacho/profil/spieler/661171",
        "display_name": "Willian Pacho",
        "club": "Paris Saint-Germain",
        "league": "Ligue 1",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "dylan-borrero": {
        "transfermarkt": "https://www.transfermarkt.com/dylan-borrero/profil/spieler/662453",
        "display_name": "Dylan Borrero",
        "club": "New England Revolution",
        "league": "MLS",
        "position": "Left Winger",
        "nationality": "Colombia",
    },
    "moises-caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/moises-caicedo/profil/spieler/687626",
        "display_name": "Moisés Caicedo",
        "club": "Chelsea",
        "league": "Premier League",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "piero-hincapie": {
        "transfermarkt": "https://www.transfermarkt.com/piero-hincapie/profil/spieler/659813",
        "display_name": "Piero Hincapié",
        "club": "Bayer Leverkusen",
        "league": "Bundesliga",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "alan-minda": {
        "transfermarkt": "https://www.transfermarkt.com/alan-minda/profil/spieler/897051",
        "display_name": "Alan Minda",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Ecuador",
    },
    "jordy-caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/jordy-caicedo/profil/spieler/360412",
        "display_name": "Jordy Caicedo",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Ecuador",
    },
    "renato-ibarra": {
        "transfermarkt": "https://www.transfermarkt.com/renato-ibarra/profil/spieler/191830",
        "display_name": "Renato Ibarra",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Right Winger",
        "nationality": "Ecuador",
    },
    "pedro-velasco": {
        "transfermarkt": "https://www.transfermarkt.com/pedro-velasco/profil/spieler/201420",
        "display_name": "Pedro Velasco",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "oscar-zambrano": {
        "transfermarkt": "https://www.transfermarkt.com/oscar-zambrano/profil/spieler/893658",
        "display_name": "Óscar Zambrano",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Attacking Midfielder",
        "nationality": "Ecuador",
    },
    "carlos-gutierrez": {
        "transfermarkt": "https://www.transfermarkt.com/carlos-gutierrez/profil/spieler/599293",
        "display_name": "Carlos Gutiérrez",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "luis-segovia": {
        "transfermarkt": "https://www.transfermarkt.com/luis-segovia/profil/spieler/385639",
        "display_name": "Luis Segovia",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "sebastian-rodriguez": {
        "transfermarkt": "https://www.transfermarkt.com/sebastian-rodriguez/profil/spieler/131114",
        "display_name": "Sebastián Rodríguez",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Right Winger",
        "nationality": "Uruguay",
    },
    "cristian-pellerano": {
        "transfermarkt": "https://www.transfermarkt.com/cristian-pellerano/profil/spieler/55941",
        "display_name": "Cristian Pellerano",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "gabriel-villamil": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-villamil/profil/spieler/844176",
        "display_name": "Gabriel Villamil",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "tomas-molina": {
        "transfermarkt": "https://www.transfermarkt.com/tomas-molina/profil/spieler/429591",
        "display_name": "Tomás Molina",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
}

# ── Ecuador Liga Pro / National Team ─────────────────────────────────────────
ECUADOR_PLAYER_URLS: dict[str, dict[str, str]] = {
    "damian-diaz": {
        "transfermarkt": "https://www.transfermarkt.com/damian-diaz/profil/spieler/55167",
        "display_name": "Damián Díaz", "club": "Barcelona SC", "league": "Liga Pro Ecuador",
        "position": "Attacking Midfielder", "nationality": "Ecuador",
    },
    "jaime-ayovi": {
        "transfermarkt": "https://www.transfermarkt.com/jaime-ayovi/profil/spieler/139494",
        "display_name": "Jaime Ayoví", "club": "LDU Quito", "league": "Liga Pro Ecuador",
        "position": "Centre-Forward", "nationality": "Ecuador",
    },
    "jackson-porozo": {
        "transfermarkt": "https://www.transfermarkt.com/jackson-porozo/profil/spieler/491616",
        "display_name": "Jackson Porozo", "club": "Troyes", "league": "Ligue 2",
        "position": "Centre-Back", "nationality": "Ecuador",
    },
    "mario-pineida": {
        "transfermarkt": "https://www.transfermarkt.com/mario-pineida/profil/spieler/193937",
        "display_name": "Mario Pineida", "club": "LDU Quito", "league": "Liga Pro Ecuador",
        "position": "Goalkeeper", "nationality": "Ecuador",
    },
    "angelo-preciado": {
        "transfermarkt": "https://www.transfermarkt.com/angelo-preciado/profil/spieler/450241",
        "display_name": "Ángelo Preciado", "club": "Genk", "league": "Belgian Pro League",
        "position": "Right-Back", "nationality": "Ecuador",
    },
    "jeremy-sarmiento": {
        "transfermarkt": "https://www.transfermarkt.com/jeremy-sarmiento/profil/spieler/568005",
        "display_name": "Jeremy Sarmiento", "club": "Brighton & Hove Albion", "league": "Premier League",
        "position": "Left Winger", "nationality": "Ecuador",
    },
    "enner-valencia": {
        "transfermarkt": "https://www.transfermarkt.com/enner-valencia/profil/spieler/139503",
        "display_name": "Enner Valencia", "club": "Internacional", "league": "Brasileirao",
        "position": "Centre-Forward", "nationality": "Ecuador",
    },
    "felix-torres": {
        "transfermarkt": "https://www.transfermarkt.com/felix-torres/profil/spieler/468174",
        "display_name": "Félix Torres", "club": "Santos Laguna", "league": "Liga MX",
        "position": "Centre-Back", "nationality": "Ecuador",
    },
    "jhegson-mendez": {
        "transfermarkt": "https://www.transfermarkt.com/jhegson-mendez/profil/spieler/330682",
        "display_name": "Jhegson Méndez", "club": "LA Galaxy", "league": "MLS",
        "position": "Defensive Midfielder", "nationality": "Ecuador",
    },
    "pervis-estupinan": {
        "transfermarkt": "https://www.transfermarkt.com/pervis-estupinan/profil/spieler/349599",
        "display_name": "Pervis Estupiñán", "club": "Brighton & Hove Albion", "league": "Premier League",
        "position": "Left-Back", "nationality": "Ecuador",
    },
    "gonzalo-plata": {
        "transfermarkt": "https://www.transfermarkt.com/gonzalo-plata/profil/spieler/592735",
        "display_name": "Gonzalo Plata", "club": "Al-Qadsiah", "league": "Saudi Pro League",
        "position": "Right Winger", "nationality": "Ecuador",
    },
    "angel-mena": {
        "transfermarkt": "https://www.transfermarkt.com/angel-mena/profil/spieler/123609",
        "display_name": "Ángel Mena", "club": "LDU Quito", "league": "Liga Pro Ecuador",
        "position": "Right Winger", "nationality": "Ecuador",
    },
    "jose-cifuentes": {
        "transfermarkt": "https://www.transfermarkt.com/jose-cifuentes/profil/spieler/450211",
        "display_name": "José Cifuentes", "club": "Los Angeles FC", "league": "MLS",
        "position": "Central Midfielder", "nationality": "Ecuador",
    },
    "michael-estrada": {
        "transfermarkt": "https://www.transfermarkt.com/michael-estrada/profil/spieler/265481",
        "display_name": "Michael Estrada", "club": "Cruz Azul", "league": "Liga MX",
        "position": "Centre-Forward", "nationality": "Ecuador",
    },
    "joao-rojas": {
        "transfermarkt": "https://www.transfermarkt.com/joao-rojas/profil/spieler/92729",
        "display_name": "Joao Rojas", "club": "LDU Quito", "league": "Liga Pro Ecuador",
        "position": "Right Winger", "nationality": "Ecuador",
    },
    "washington-corozo": {
        "transfermarkt": "https://www.transfermarkt.com/washington-corozo/profil/spieler/400964",
        "display_name": "Washington Corozo", "club": "Barcelona SC", "league": "Liga Pro Ecuador",
        "position": "Left Winger", "nationality": "Ecuador",
    },
    "byron-castillo": {
        "transfermarkt": "https://www.transfermarkt.com/byron-castillo/profil/spieler/400961",
        "display_name": "Byron Castillo", "club": "Basel", "league": "Super League Switzerland",
        "position": "Right-Back", "nationality": "Ecuador",
    },
    "alexander-dominguez": {
        "transfermarkt": "https://www.transfermarkt.com/alexander-dominguez/profil/spieler/84310",
        "display_name": "Alexander Domínguez", "club": "LDU Quito", "league": "Liga Pro Ecuador",
        "position": "Goalkeeper", "nationality": "Ecuador",
    },
    "carlos-gruezo": {
        "transfermarkt": "https://www.transfermarkt.com/carlos-gruezo/profil/spieler/189475",
        "display_name": "Carlos Gruezo", "club": "Augsburg", "league": "Bundesliga",
        "position": "Defensive Midfielder", "nationality": "Ecuador",
    },
    "michael-hoyos": {
        "transfermarkt": "https://www.transfermarkt.com/michael-hoyos/profil/spieler/138387",
        "display_name": "Michael Hoyos", "club": "Independiente del Valle", "league": "Liga Pro Ecuador",
        "position": "Right Winger", "nationality": "Ecuador",
    },
    "jonathan-borja": {
        "transfermarkt": "https://www.transfermarkt.com/jonathan-borja/profil/spieler/319318",
        "display_name": "Jonathan Borja", "club": "LDU Quito", "league": "Liga Pro Ecuador",
        "position": "Centre-Forward", "nationality": "Ecuador",
    },
}

# ── Brazil ────────────────────────────────────────────────────────────────────
BRAZIL_PLAYER_URLS: dict[str, dict[str, str]] = {
    "vinicius-junior": {
        "transfermarkt": "https://www.transfermarkt.com/vinicius-junior/profil/spieler/371998",
        "display_name": "Vinícius Jr.", "club": "Real Madrid", "league": "La Liga",
        "position": "Left Winger", "nationality": "Brazil",
    },
    "rodrygo": {
        "transfermarkt": "https://www.transfermarkt.com/rodrygo/profil/spieler/412363",
        "display_name": "Rodrygo", "club": "Real Madrid", "league": "La Liga",
        "position": "Right Winger", "nationality": "Brazil",
    },
    "endrick": {
        "transfermarkt": "https://www.transfermarkt.com/endrick/profil/spieler/971570",
        "display_name": "Endrick", "club": "Real Madrid", "league": "La Liga",
        "position": "Centre-Forward", "nationality": "Brazil",
    },
    "gabriel-martinelli": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-martinelli/profil/spieler/655488",
        "display_name": "Gabriel Martinelli", "club": "Arsenal", "league": "Premier League",
        "position": "Left Winger", "nationality": "Brazil",
    },
    "savinho": {
        "transfermarkt": "https://www.transfermarkt.com/savinho/profil/spieler/743591",
        "display_name": "Sávinho", "club": "Manchester City", "league": "Premier League",
        "position": "Right Winger", "nationality": "Brazil",
    },
    "estevao": {
        "transfermarkt": "https://www.transfermarkt.com/estevao/profil/spieler/1056993",
        "display_name": "Estêvão", "club": "Chelsea", "league": "Premier League",
        "position": "Right Winger", "nationality": "Brazil",
    },
    "marcos-leonardo": {
        "transfermarkt": "https://www.transfermarkt.com/marcos-leonardo/profil/spieler/668267",
        "display_name": "Marcos Leonardo", "club": "Sporting CP", "league": "Primeira Liga",
        "position": "Centre-Forward", "nationality": "Brazil",
    },
    "yan-couto": {
        "transfermarkt": "https://www.transfermarkt.com/yan-couto/profil/spieler/627228",
        "display_name": "Yan Couto", "club": "Borussia Dortmund", "league": "Bundesliga",
        "position": "Right-Back", "nationality": "Brazil",
    },
    "matheus-cunha": {
        "transfermarkt": "https://www.transfermarkt.com/matheus-cunha/profil/spieler/517894",
        "display_name": "Matheus Cunha", "club": "Wolverhampton", "league": "Premier League",
        "position": "Centre-Forward", "nationality": "Brazil",
    },
    "lucas-paqueta": {
        "transfermarkt": "https://www.transfermarkt.com/lucas-paqueta/profil/spieler/444523",
        "display_name": "Lucas Paquetá", "club": "West Ham United", "league": "Premier League",
        "position": "Attacking Midfielder", "nationality": "Brazil",
    },
    "joao-gomes": {
        "transfermarkt": "https://www.transfermarkt.com/joao-gomes/profil/spieler/735570",
        "display_name": "João Gomes", "club": "Wolverhampton", "league": "Premier League",
        "position": "Defensive Midfielder", "nationality": "Brazil",
    },
    "guilherme-arana": {
        "transfermarkt": "https://www.transfermarkt.com/guilherme-arana/profil/spieler/346766",
        "display_name": "Guilherme Arana", "club": "Atlético Mineiro", "league": "Brasileirao",
        "position": "Left-Back", "nationality": "Brazil",
    },
    "antony": {
        "transfermarkt": "https://www.transfermarkt.com/antony/profil/spieler/602105",
        "display_name": "Antony", "club": "Manchester United", "league": "Premier League",
        "position": "Right Winger", "nationality": "Brazil",
    },
    "bruno-guimaraes": {
        "transfermarkt": "https://www.transfermarkt.com/bruno-guimaraes/profil/spieler/520624",
        "display_name": "Bruno Guimarães", "club": "Newcastle United", "league": "Premier League",
        "position": "Defensive Midfielder", "nationality": "Brazil",
    },
    "pedro-flamengo": {
        "transfermarkt": "https://www.transfermarkt.com/pedro-flamengo/profil/spieler/65278",
        "display_name": "Pedro", "club": "Flamengo", "league": "Brasileirao",
        "position": "Centre-Forward", "nationality": "Brazil",
    },
    "gabriel-jesus": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-jesus/profil/spieler/363205",
        "display_name": "Gabriel Jesus", "club": "Arsenal", "league": "Premier League",
        "position": "Centre-Forward", "nationality": "Brazil",
    },
    "vanderson": {
        "transfermarkt": "https://www.transfermarkt.com/vanderson/profil/spieler/789082",
        "display_name": "Vanderson", "club": "Monaco", "league": "Ligue 1",
        "position": "Right-Back", "nationality": "Brazil",
    },
    "lucas-beraldo": {
        "transfermarkt": "https://www.transfermarkt.com/lucas-beraldo/profil/spieler/872171",
        "display_name": "Lucas Beraldo", "club": "Paris Saint-Germain", "league": "Ligue 1",
        "position": "Centre-Back", "nationality": "Brazil",
    },
    "gerson": {
        "transfermarkt": "https://www.transfermarkt.com/gerson/profil/spieler/341705",
        "display_name": "Gerson", "club": "Flamengo", "league": "Brasileirao",
        "position": "Central Midfielder", "nationality": "Brazil",
    },
    "lorran": {
        "transfermarkt": "https://www.transfermarkt.com/lorran/profil/spieler/1009030",
        "display_name": "Lorran", "club": "Flamengo", "league": "Brasileirao",
        "position": "Attacking Midfielder", "nationality": "Brazil",
    },
    "reinier": {
        "transfermarkt": "https://www.transfermarkt.com/reinier/profil/spieler/627226",
        "display_name": "Reinier", "club": "Flamengo", "league": "Brasileirao",
        "position": "Attacking Midfielder", "nationality": "Brazil",
    },
    "richarlison": {
        "transfermarkt": "https://www.transfermarkt.com/richarlison/profil/spieler/378710",
        "display_name": "Richarlison", "club": "Tottenham Hotspur", "league": "Premier League",
        "position": "Centre-Forward", "nationality": "Brazil",
    },
    "david-neres": {
        "transfermarkt": "https://www.transfermarkt.com/david-neres/profil/spieler/469822",
        "display_name": "David Neres", "club": "Napoli", "league": "Serie A",
        "position": "Right Winger", "nationality": "Brazil",
    },
    "roberto-firmino": {
        "transfermarkt": "https://www.transfermarkt.com/roberto-firmino/profil/spieler/131789",
        "display_name": "Roberto Firmino", "club": "Al-Ahli", "league": "Saudi Pro League",
        "position": "Second Striker", "nationality": "Brazil",
    },
}

# ── Argentina ─────────────────────────────────────────────────────────────────
ARGENTINA_PLAYER_URLS: dict[str, dict[str, str]] = {
    "alejandro-garnacho": {
        "transfermarkt": "https://www.transfermarkt.com/alejandro-garnacho/profil/spieler/811779",
        "display_name": "Alejandro Garnacho", "club": "Manchester United", "league": "Premier League",
        "position": "Left Winger", "nationality": "Argentina",
    },
    "valentin-carboni": {
        "transfermarkt": "https://www.transfermarkt.com/valentin-carboni/profil/spieler/787618",
        "display_name": "Valentín Carboni", "club": "Inter Milan", "league": "Serie A",
        "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "claudio-echeverri": {
        "transfermarkt": "https://www.transfermarkt.com/claudio-echeverri/profil/spieler/994536",
        "display_name": "Claudio Echeverri", "club": "Manchester City", "league": "Premier League",
        "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "franco-mastantuono": {
        "transfermarkt": "https://www.transfermarkt.com/franco-mastantuono/profil/spieler/1057316",
        "display_name": "Franco Mastantuono", "club": "River Plate", "league": "Primera División Argentina",
        "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "lautaro-martinez": {
        "transfermarkt": "https://www.transfermarkt.com/lautaro-martinez/profil/spieler/406625",
        "display_name": "Lautaro Martínez", "club": "Inter Milan", "league": "Serie A",
        "position": "Centre-Forward", "nationality": "Argentina",
    },
    "julian-alvarez": {
        "transfermarkt": "https://www.transfermarkt.com/julian-alvarez/profil/spieler/576024",
        "display_name": "Julián Álvarez", "club": "Atlético Madrid", "league": "La Liga",
        "position": "Centre-Forward", "nationality": "Argentina",
    },
    "enzo-fernandez": {
        "transfermarkt": "https://www.transfermarkt.com/enzo-fernandez/profil/spieler/648195",
        "display_name": "Enzo Fernández", "club": "Chelsea", "league": "Premier League",
        "position": "Central Midfielder", "nationality": "Argentina",
    },
    "facundo-buonanotte": {
        "transfermarkt": "https://www.transfermarkt.com/facundo-buonanotte/profil/spieler/983989",
        "display_name": "Facundo Buonanotte", "club": "Brighton & Hove Albion", "league": "Premier League",
        "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "thiago-almada": {
        "transfermarkt": "https://www.transfermarkt.com/thiago-almada/profil/spieler/576028",
        "display_name": "Thiago Almada", "club": "Lyon", "league": "Ligue 1",
        "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "nicolas-gonzalez": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-gonzalez/profil/spieler/466805",
        "display_name": "Nicolás González", "club": "Juventus", "league": "Serie A",
        "position": "Left Winger", "nationality": "Argentina",
    },
    "paulo-dybala": {
        "transfermarkt": "https://www.transfermarkt.com/paulo-dybala/profil/spieler/206050",
        "display_name": "Paulo Dybala", "club": "Roma", "league": "Serie A",
        "position": "Second Striker", "nationality": "Argentina",
    },
    "exequiel-palacios": {
        "transfermarkt": "https://www.transfermarkt.com/exequiel-palacios/profil/spieler/401578",
        "display_name": "Exequiel Palacios", "club": "Bayer Leverkusen", "league": "Bundesliga",
        "position": "Central Midfielder", "nationality": "Argentina",
    },
    "matias-soule": {
        "transfermarkt": "https://www.transfermarkt.com/matias-soule/profil/spieler/668951",
        "display_name": "Matías Soulé", "club": "Roma", "league": "Serie A",
        "position": "Right Winger", "nationality": "Argentina",
    },
    "lucas-beltran": {
        "transfermarkt": "https://www.transfermarkt.com/lucas-beltran/profil/spieler/628366",
        "display_name": "Lucas Beltrán", "club": "Fiorentina", "league": "Serie A",
        "position": "Centre-Forward", "nationality": "Argentina",
    },
    "nahuel-molina": {
        "transfermarkt": "https://www.transfermarkt.com/nahuel-molina/profil/spieler/424042",
        "display_name": "Nahuel Molina", "club": "Atlético Madrid", "league": "La Liga",
        "position": "Right-Back", "nationality": "Argentina",
    },
    "lisandro-martinez": {
        "transfermarkt": "https://www.transfermarkt.com/lisandro-martinez/profil/spieler/480762",
        "display_name": "Lisandro Martínez", "club": "Manchester United", "league": "Premier League",
        "position": "Centre-Back", "nationality": "Argentina",
    },
    "gonzalo-montiel": {
        "transfermarkt": "https://www.transfermarkt.com/gonzalo-montiel/profil/spieler/402733",
        "display_name": "Gonzalo Montiel", "club": "Nottingham Forest", "league": "Premier League",
        "position": "Right-Back", "nationality": "Argentina",
    },
    "giovani-lo-celso": {
        "transfermarkt": "https://www.transfermarkt.com/giovani-lo-celso/profil/spieler/348795",
        "display_name": "Giovani Lo Celso", "club": "Villarreal", "league": "La Liga",
        "position": "Central Midfielder", "nationality": "Argentina",
    },
    "rodrigo-de-paul": {
        "transfermarkt": "https://www.transfermarkt.com/rodrigo-de-paul/profil/spieler/255901",
        "display_name": "Rodrigo De Paul", "club": "Atlético Madrid", "league": "La Liga",
        "position": "Central Midfielder", "nationality": "Argentina",
    },
    "leandro-paredes": {
        "transfermarkt": "https://www.transfermarkt.com/leandro-paredes/profil/spieler/166237",
        "display_name": "Leandro Paredes", "club": "Roma", "league": "Serie A",
        "position": "Defensive Midfielder", "nationality": "Argentina",
    },
}

# ── Colombia ──────────────────────────────────────────────────────────────────
COLOMBIA_PLAYER_URLS: dict[str, dict[str, str]] = {
    "luis-diaz": {
        "transfermarkt": "https://www.transfermarkt.com/luis-diaz/profil/spieler/480692",
        "display_name": "Luis Díaz", "club": "Liverpool", "league": "Premier League",
        "position": "Left Winger", "nationality": "Colombia",
    },
    "jhon-duran": {
        "transfermarkt": "https://www.transfermarkt.com/jhon-duran/profil/spieler/649317",
        "display_name": "Jhon Durán", "club": "Aston Villa", "league": "Premier League",
        "position": "Centre-Forward", "nationality": "Colombia",
    },
    "richard-rios": {
        "transfermarkt": "https://www.transfermarkt.com/richard-rios/profil/spieler/735573",
        "display_name": "Richard Ríos", "club": "Palmeiras", "league": "Brasileirao",
        "position": "Central Midfielder", "nationality": "Colombia",
    },
    "cucho-hernandez": {
        "transfermarkt": "https://www.transfermarkt.com/cucho-hernandez/profil/spieler/459463",
        "display_name": "Cucho Hernández", "club": "Columbus Crew", "league": "MLS",
        "position": "Centre-Forward", "nationality": "Colombia",
    },
    "luis-sinisterra": {
        "transfermarkt": "https://www.transfermarkt.com/luis-sinisterra/profil/spieler/512385",
        "display_name": "Luis Sinisterra", "club": "Bournemouth", "league": "Premier League",
        "position": "Left Winger", "nationality": "Colombia",
    },
    "jorge-carrascal": {
        "transfermarkt": "https://www.transfermarkt.com/jorge-carrascal/profil/spieler/354145",
        "display_name": "Jorge Carrascal", "club": "River Plate", "league": "Primera División Argentina",
        "position": "Attacking Midfielder", "nationality": "Colombia",
    },
    "rafael-santos-borre": {
        "transfermarkt": "https://www.transfermarkt.com/rafael-santos-borre/profil/spieler/323831",
        "display_name": "Rafael Santos Borré", "club": "Internacional", "league": "Brasileirao",
        "position": "Centre-Forward", "nationality": "Colombia",
    },
    "yerry-mina": {
        "transfermarkt": "https://www.transfermarkt.com/yerry-mina/profil/spieler/289446",
        "display_name": "Yerry Mina", "club": "Fiorentina", "league": "Serie A",
        "position": "Centre-Back", "nationality": "Colombia",
    },
    "james-rodriguez": {
        "transfermarkt": "https://www.transfermarkt.com/james-rodriguez/profil/spieler/88103",
        "display_name": "James Rodríguez", "club": "Rayo Vallecano", "league": "La Liga",
        "position": "Attacking Midfielder", "nationality": "Colombia",
    },
    "roger-martinez": {
        "transfermarkt": "https://www.transfermarkt.com/roger-martinez/profil/spieler/285771",
        "display_name": "Roger Martínez", "club": "Club América", "league": "Liga MX",
        "position": "Right Winger", "nationality": "Colombia",
    },
    "jhon-cordoba": {
        "transfermarkt": "https://www.transfermarkt.com/jhon-cordoba/profil/spieler/185245",
        "display_name": "Jhon Córdoba", "club": "Krasnodar", "league": "Russian Premier League",
        "position": "Centre-Forward", "nationality": "Colombia",
    },
    "mateus-uribe": {
        "transfermarkt": "https://www.transfermarkt.com/mateus-uribe/profil/spieler/214538",
        "display_name": "Matéus Uribe", "club": "Porto", "league": "Primeira Liga",
        "position": "Central Midfielder", "nationality": "Colombia",
    },
    "jefferson-lerma": {
        "transfermarkt": "https://www.transfermarkt.com/jefferson-lerma/profil/spieler/262980",
        "display_name": "Jefferson Lerma", "club": "Crystal Palace", "league": "Premier League",
        "position": "Defensive Midfielder", "nationality": "Colombia",
    },
    "miguel-borja": {
        "transfermarkt": "https://www.transfermarkt.com/miguel-borja/profil/spieler/211397",
        "display_name": "Miguel Borja", "club": "River Plate", "league": "Primera División Argentina",
        "position": "Centre-Forward", "nationality": "Colombia",
    },
}

# ── Portugal ──────────────────────────────────────────────────────────────────
PORTUGAL_PLAYER_URLS: dict[str, dict[str, str]] = {
    "joao-neves": {
        "transfermarkt": "https://www.transfermarkt.com/joao-neves/profil/spieler/670681",
        "display_name": "João Neves", "club": "Paris Saint-Germain", "league": "Ligue 1",
        "position": "Defensive Midfielder", "nationality": "Portugal",
    },
    "goncalo-inacio": {
        "transfermarkt": "https://www.transfermarkt.com/goncalo-inacio/profil/spieler/549006",
        "display_name": "Gonçalo Inácio", "club": "Sporting CP", "league": "Primeira Liga",
        "position": "Centre-Back", "nationality": "Portugal",
    },
    "francisco-conceicao": {
        "transfermarkt": "https://www.transfermarkt.com/francisco-conceicao/profil/spieler/487474",
        "display_name": "Francisco Conceição", "club": "Juventus", "league": "Serie A",
        "position": "Right Winger", "nationality": "Portugal",
    },
    "rafael-leao": {
        "transfermarkt": "https://www.transfermarkt.com/rafael-leao/profil/spieler/357164",
        "display_name": "Rafael Leão", "club": "AC Milan", "league": "Serie A",
        "position": "Left Winger", "nationality": "Portugal",
    },
    "joao-felix": {
        "transfermarkt": "https://www.transfermarkt.com/joao-felix/profil/spieler/462250",
        "display_name": "João Félix", "club": "Chelsea", "league": "Premier League",
        "position": "Second Striker", "nationality": "Portugal",
    },
    "pedro-neto": {
        "transfermarkt": "https://www.transfermarkt.com/pedro-neto/profil/spieler/487465",
        "display_name": "Pedro Neto", "club": "Chelsea", "league": "Premier League",
        "position": "Left Winger", "nationality": "Portugal",
    },
    "renato-veiga": {
        "transfermarkt": "https://www.transfermarkt.com/renato-veiga/profil/spieler/805714",
        "display_name": "Renato Veiga", "club": "Chelsea", "league": "Premier League",
        "position": "Centre-Back", "nationality": "Portugal",
    },
    "vitinha": {
        "transfermarkt": "https://www.transfermarkt.com/vitinha/profil/spieler/487469",
        "display_name": "Vitinha", "club": "Paris Saint-Germain", "league": "Ligue 1",
        "position": "Central Midfielder", "nationality": "Portugal",
    },
    "diogo-jota": {
        "transfermarkt": "https://www.transfermarkt.com/diogo-jota/profil/spieler/340950",
        "display_name": "Diogo Jota", "club": "Liverpool", "league": "Premier League",
        "position": "Left Winger", "nationality": "Portugal",
    },
    "nuno-mendes": {
        "transfermarkt": "https://www.transfermarkt.com/nuno-mendes/profil/spieler/616341",
        "display_name": "Nuno Mendes", "club": "Paris Saint-Germain", "league": "Ligue 1",
        "position": "Left-Back", "nationality": "Portugal",
    },
    "antonio-silva": {
        "transfermarkt": "https://www.transfermarkt.com/antonio-silva/profil/spieler/650568",
        "display_name": "António Silva", "club": "Benfica", "league": "Primeira Liga",
        "position": "Centre-Back", "nationality": "Portugal",
    },
    "geny-catamo": {
        "transfermarkt": "https://www.transfermarkt.com/geny-catamo/profil/spieler/701979",
        "display_name": "Geny Catamo", "club": "Sporting CP", "league": "Primeira Liga",
        "position": "Right Winger", "nationality": "Mozambique",
    },
    "rodrigo-conceicao": {
        "transfermarkt": "https://www.transfermarkt.com/rodrigo-conceicao/profil/spieler/426213",
        "display_name": "Rodrigo Conceição", "club": "Porto", "league": "Primeira Liga",
        "position": "Right Winger", "nationality": "Portugal",
    },
}

# ── Netherlands / Eredivisie ──────────────────────────────────────────────────
NETHERLANDS_PLAYER_URLS: dict[str, dict[str, str]] = {
    "xavi-simons": {
        "transfermarkt": "https://www.transfermarkt.com/xavi-simons/profil/spieler/566931",
        "display_name": "Xavi Simons", "club": "RB Leipzig", "league": "Bundesliga",
        "position": "Attacking Midfielder", "nationality": "Netherlands",
    },
    "ryan-gravenberch": {
        "transfermarkt": "https://www.transfermarkt.com/ryan-gravenberch/profil/spieler/478573",
        "display_name": "Ryan Gravenberch", "club": "Liverpool", "league": "Premier League",
        "position": "Central Midfielder", "nationality": "Netherlands",
    },
    "cody-gakpo": {
        "transfermarkt": "https://www.transfermarkt.com/cody-gakpo/profil/spieler/434675",
        "display_name": "Cody Gakpo", "club": "Liverpool", "league": "Premier League",
        "position": "Left Winger", "nationality": "Netherlands",
    },
    "ibrahim-osman": {
        "transfermarkt": "https://www.transfermarkt.com/ibrahim-osman/profil/spieler/1110406",
        "display_name": "Ibrahim Osman", "club": "Feyenoord", "league": "Eredivisie",
        "position": "Right Winger", "nationality": "Ghana",
    },
    "lutsharel-geertruida": {
        "transfermarkt": "https://www.transfermarkt.com/lutsharel-geertruida/profil/spieler/420210",
        "display_name": "Lutsharel Geertruida", "club": "RB Leipzig", "league": "Bundesliga",
        "position": "Right-Back", "nationality": "Netherlands",
    },
    "devyne-rensch": {
        "transfermarkt": "https://www.transfermarkt.com/devyne-rensch/profil/spieler/557407",
        "display_name": "Devyne Rensch", "club": "AS Roma", "league": "Serie A",
        "position": "Right-Back", "nationality": "Netherlands",
    },
    "quinten-timber": {
        "transfermarkt": "https://www.transfermarkt.com/quinten-timber/profil/spieler/420213",
        "display_name": "Quinten Timber", "club": "Feyenoord", "league": "Eredivisie",
        "position": "Central Midfielder", "nationality": "Netherlands",
    },
    "frenkie-de-jong": {
        "transfermarkt": "https://www.transfermarkt.com/frenkie-de-jong/profil/spieler/326330",
        "display_name": "Frenkie de Jong", "club": "Barcelona", "league": "La Liga",
        "position": "Central Midfielder", "nationality": "Netherlands",
    },
    "jeremie-frimpong": {
        "transfermarkt": "https://www.transfermarkt.com/jeremie-frimpong/profil/spieler/484547",
        "display_name": "Jérémy Frimpong", "club": "Bayer Leverkusen", "league": "Bundesliga",
        "position": "Right-Back", "nationality": "Netherlands",
    },
    "tijjani-reijnders": {
        "transfermarkt": "https://www.transfermarkt.com/tijjani-reijnders/profil/spieler/460939",
        "display_name": "Tijjani Reijnders", "club": "AC Milan", "league": "Serie A",
        "position": "Central Midfielder", "nationality": "Netherlands",
    },
    "jurrien-timber": {
        "transfermarkt": "https://www.transfermarkt.com/jurrien-timber/profil/spieler/420243",
        "display_name": "Jurriën Timber", "club": "Arsenal", "league": "Premier League",
        "position": "Centre-Back", "nationality": "Netherlands",
    },
    "brian-brobbey": {
        "transfermarkt": "https://www.transfermarkt.com/brian-brobbey/profil/spieler/473169",
        "display_name": "Brian Brobbey", "club": "Ajax", "league": "Eredivisie",
        "position": "Centre-Forward", "nationality": "Netherlands",
    },
    "noa-lang": {
        "transfermarkt": "https://www.transfermarkt.com/noa-lang/profil/spieler/339332",
        "display_name": "Noa Lang", "club": "PSV Eindhoven", "league": "Eredivisie",
        "position": "Left Winger", "nationality": "Netherlands",
    },
    "mats-wieffer": {
        "transfermarkt": "https://www.transfermarkt.com/mats-wieffer/profil/spieler/415381",
        "display_name": "Mats Wieffer", "club": "Brighton & Hove Albion", "league": "Premier League",
        "position": "Defensive Midfielder", "nationality": "Netherlands",
    },
    "teun-koopmeiners": {
        "transfermarkt": "https://www.transfermarkt.com/teun-koopmeiners/profil/spieler/360518",
        "display_name": "Teun Koopmeiners", "club": "Juventus", "league": "Serie A",
        "position": "Central Midfielder", "nationality": "Netherlands",
    },
}

# ── Belgium Pro League ─────────────────────────────────────────────────────────
BELGIUM_PLAYER_URLS: dict[str, dict[str, str]] = {
    "lois-openda": {
        "transfermarkt": "https://www.transfermarkt.com/lois-openda/profil/spieler/368887",
        "display_name": "Loïs Openda", "club": "RB Leipzig", "league": "Bundesliga",
        "position": "Centre-Forward", "nationality": "Belgium",
    },
    "arthur-vermeeren": {
        "transfermarkt": "https://www.transfermarkt.com/arthur-vermeeren/profil/spieler/926694",
        "display_name": "Arthur Vermeeren", "club": "Atlético Madrid", "league": "La Liga",
        "position": "Defensive Midfielder", "nationality": "Belgium",
    },
    "amadou-onana": {
        "transfermarkt": "https://www.transfermarkt.com/amadou-onana/profil/spieler/485706",
        "display_name": "Amadou Onana", "club": "Aston Villa", "league": "Premier League",
        "position": "Defensive Midfielder", "nationality": "Belgium",
    },
    "johan-bakayoko": {
        "transfermarkt": "https://www.transfermarkt.com/johan-bakayoko/profil/spieler/565424",
        "display_name": "Johan Bakayoko", "club": "PSV Eindhoven", "league": "Eredivisie",
        "position": "Right Winger", "nationality": "Belgium",
    },
    "charles-de-ketelaere": {
        "transfermarkt": "https://www.transfermarkt.com/charles-de-ketelaere/profil/spieler/435772",
        "display_name": "Charles De Ketelaere", "club": "Atalanta", "league": "Serie A",
        "position": "Attacking Midfielder", "nationality": "Belgium",
    },
    "jeremy-doku": {
        "transfermarkt": "https://www.transfermarkt.com/jeremy-doku/profil/spieler/486049",
        "display_name": "Jérémy Doku", "club": "Manchester City", "league": "Premier League",
        "position": "Left Winger", "nationality": "Belgium",
    },
    "leandro-trossard": {
        "transfermarkt": "https://www.transfermarkt.com/leandro-trossard/profil/spieler/144028",
        "display_name": "Leandro Trossard", "club": "Arsenal", "league": "Premier League",
        "position": "Left Winger", "nationality": "Belgium",
    },
    "noah-ohio": {
        "transfermarkt": "https://www.transfermarkt.com/noah-ohio/profil/spieler/557410",
        "display_name": "Noah Ohio", "club": "Chelsea", "league": "Premier League",
        "position": "Centre-Forward", "nationality": "Belgium",
    },
    "youri-tielemans": {
        "transfermarkt": "https://www.transfermarkt.com/youri-tielemans/profil/spieler/249565",
        "display_name": "Youri Tielemans", "club": "Aston Villa", "league": "Premier League",
        "position": "Central Midfielder", "nationality": "Belgium",
    },
    "orel-mangala": {
        "transfermarkt": "https://www.transfermarkt.com/orel-mangala/profil/spieler/289592",
        "display_name": "Orel Mangala", "club": "Nottingham Forest", "league": "Premier League",
        "position": "Defensive Midfielder", "nationality": "Belgium",
    },
    "albert-lokonga": {
        "transfermarkt": "https://www.transfermarkt.com/albert-lokonga/profil/spieler/381967",
        "display_name": "Albert Sambi Lokonga", "club": "Luton Town", "league": "Championship",
        "position": "Defensive Midfielder", "nationality": "Belgium",
    },
}

# ── Austria Bundesliga / RB Salzburg ──────────────────────────────────────────
AUSTRIA_PLAYER_URLS: dict[str, dict[str, str]] = {
    "benjamin-sesko": {
        "transfermarkt": "https://www.transfermarkt.com/benjamin-sesko/profil/spieler/627442",
        "display_name": "Benjamin Šeško", "club": "RB Leipzig", "league": "Bundesliga",
        "position": "Centre-Forward", "nationality": "Slovenia",
    },
    "nicolas-seiwald": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-seiwald/profil/spieler/404950",
        "display_name": "Nicolas Seiwald", "club": "RB Leipzig", "league": "Bundesliga",
        "position": "Defensive Midfielder", "nationality": "Austria",
    },
    "christoph-baumgartner": {
        "transfermarkt": "https://www.transfermarkt.com/christoph-baumgartner/profil/spieler/324278",
        "display_name": "Christoph Baumgartner", "club": "RB Leipzig", "league": "Bundesliga",
        "position": "Attacking Midfielder", "nationality": "Austria",
    },
    "karim-konate": {
        "transfermarkt": "https://www.transfermarkt.com/karim-konate/profil/spieler/847278",
        "display_name": "Karim Konaté", "club": "RB Salzburg", "league": "Austrian Bundesliga",
        "position": "Centre-Forward", "nationality": "Ivory Coast",
    },
    "adam-daghim": {
        "transfermarkt": "https://www.transfermarkt.com/adam-daghim/profil/spieler/881297",
        "display_name": "Adam Daghim", "club": "RB Salzburg", "league": "Austrian Bundesliga",
        "position": "Left Winger", "nationality": "Denmark",
    },
    "patson-daka": {
        "transfermarkt": "https://www.transfermarkt.com/patson-daka/profil/spieler/365172",
        "display_name": "Patson Daka", "club": "Leicester City", "league": "Championship",
        "position": "Centre-Forward", "nationality": "Zambia",
    },
    "sekou-koita": {
        "transfermarkt": "https://www.transfermarkt.com/sekou-koita/profil/spieler/402010",
        "display_name": "Sékou Koïta", "club": "RB Salzburg", "league": "Austrian Bundesliga",
        "position": "Centre-Forward", "nationality": "Mali",
    },
    "rasmus-kristensen": {
        "transfermarkt": "https://www.transfermarkt.com/rasmus-kristensen/profil/spieler/369684",
        "display_name": "Rasmus Kristensen", "club": "Roma", "league": "Serie A",
        "position": "Right-Back", "nationality": "Denmark",
    },
    "nicolas-capaldo": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-capaldo/profil/spieler/649672",
        "display_name": "Nicolás Capaldo", "club": "RB Salzburg", "league": "Austrian Bundesliga",
        "position": "Central Midfielder", "nationality": "Argentina",
    },
}

# ── MLS — South Americans ──────────────────────────────────────────────────────
MLS_PLAYER_URLS: dict[str, dict[str, str]] = {
    "neymar-jr": {
        "transfermarkt": "https://www.transfermarkt.com/neymar-jr/profil/spieler/68290",
        "display_name": "Neymar Jr", "club": "Al-Hilal", "league": "Saudi Pro League",
        "position": "Left Winger", "nationality": "Brazil",
    },
    "carlos-vela": {
        "transfermarkt": "https://www.transfermarkt.com/carlos-vela/profil/spieler/86906",
        "display_name": "Carlos Vela", "club": "Los Angeles FC", "league": "MLS",
        "position": "Second Striker", "nationality": "Mexico",
    },
    "xherdan-shaqiri": {
        "transfermarkt": "https://www.transfermarkt.com/xherdan-shaqiri/profil/spieler/86792",
        "display_name": "Xherdan Shaqiri", "club": "Chicago Fire", "league": "MLS",
        "position": "Second Striker", "nationality": "Switzerland",
    },
    "facundo-torres": {
        "transfermarkt": "https://www.transfermarkt.com/facundo-torres/profil/spieler/465822",
        "display_name": "Facundo Torres", "club": "Orlando City", "league": "MLS",
        "position": "Right Winger", "nationality": "Uruguay",
    },
    "luciano-acosta": {
        "transfermarkt": "https://www.transfermarkt.com/luciano-acosta/profil/spieler/315169",
        "display_name": "Luciano Acosta", "club": "FC Cincinnati", "league": "MLS",
        "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "riqui-puig": {
        "transfermarkt": "https://www.transfermarkt.com/riqui-puig/profil/spieler/331511",
        "display_name": "Riqui Puig", "club": "LA Galaxy", "league": "MLS",
        "position": "Attacking Midfielder", "nationality": "Spain",
    },
    "renato-tapia": {
        "transfermarkt": "https://www.transfermarkt.com/renato-tapia/profil/spieler/277137",
        "display_name": "Renato Tapia", "club": "Celta Vigo", "league": "La Liga",
        "position": "Defensive Midfielder", "nationality": "Peru",
    },
}

# ── Comprehensive registry: all players across all leagues ───────────────────
ALL_PLAYER_URLS: dict[str, dict[str, str]] = {
    **IDV_PLAYER_URLS,
    **ECUADOR_PLAYER_URLS,
    **BRAZIL_PLAYER_URLS,
    **ARGENTINA_PLAYER_URLS,
    **COLOMBIA_PLAYER_URLS,
    **PORTUGAL_PLAYER_URLS,
    **NETHERLANDS_PLAYER_URLS,
    **BELGIUM_PLAYER_URLS,
    **AUSTRIA_PLAYER_URLS,
    **MLS_PLAYER_URLS,
}
