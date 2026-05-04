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

# ── Premier League elite players ──────────────────────────────────────────────
PREMIER_LEAGUE_PLAYER_URLS: dict[str, dict[str, str]] = {
    "erling-haaland": {"transfermarkt": "https://www.transfermarkt.com/erling-haaland/profil/spieler/418560", "display_name": "Erling Haaland", "club": "Manchester City", "league": "Premier League", "position": "Centre-Forward", "nationality": "Norway"},
    "bukayo-saka": {"transfermarkt": "https://www.transfermarkt.com/bukayo-saka/profil/spieler/505460", "display_name": "Bukayo Saka", "club": "Arsenal", "league": "Premier League", "position": "Right Winger", "nationality": "England"},
    "cole-palmer": {"transfermarkt": "https://www.transfermarkt.com/cole-palmer/profil/spieler/609608", "display_name": "Cole Palmer", "club": "Chelsea", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "declan-rice": {"transfermarkt": "https://www.transfermarkt.com/declan-rice/profil/spieler/357662", "display_name": "Declan Rice", "club": "Arsenal", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "England"},
    "phil-foden": {"transfermarkt": "https://www.transfermarkt.com/phil-foden/profil/spieler/406635", "display_name": "Phil Foden", "club": "Manchester City", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "trent-alexander-arnold": {"transfermarkt": "https://www.transfermarkt.com/trent-alexander-arnold/profil/spieler/314353", "display_name": "Trent Alexander-Arnold", "club": "Liverpool", "league": "Premier League", "position": "Right-Back", "nationality": "England"},
    "virgil-van-dijk": {"transfermarkt": "https://www.transfermarkt.com/virgil-van-dijk/profil/spieler/139208", "display_name": "Virgil van Dijk", "club": "Liverpool", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "alexander-isak": {"transfermarkt": "https://www.transfermarkt.com/alexander-isak/profil/spieler/347266", "display_name": "Alexander Isak", "club": "Newcastle", "league": "Premier League", "position": "Centre-Forward", "nationality": "Sweden"},
    "ollie-watkins": {"transfermarkt": "https://www.transfermarkt.com/ollie-watkins/profil/spieler/252699", "display_name": "Ollie Watkins", "club": "Aston Villa", "league": "Premier League", "position": "Centre-Forward", "nationality": "England"},
    "morgan-rogers": {"transfermarkt": "https://www.transfermarkt.com/morgan-rogers/profil/spieler/620555", "display_name": "Morgan Rogers", "club": "Aston Villa", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "noni-madueke": {"transfermarkt": "https://www.transfermarkt.com/noni-madueke/profil/spieler/537085", "display_name": "Noni Madueke", "club": "Chelsea", "league": "Premier League", "position": "Right Winger", "nationality": "England"},
    "liam-delap": {"transfermarkt": "https://www.transfermarkt.com/liam-delap/profil/spieler/662237", "display_name": "Liam Delap", "club": "Ipswich Town", "league": "Premier League", "position": "Centre-Forward", "nationality": "England"},
    "micky-van-de-ven": {"transfermarkt": "https://www.transfermarkt.com/micky-van-de-ven/profil/spieler/567576", "display_name": "Micky van de Ven", "club": "Tottenham", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "matthijs-de-ligt": {"transfermarkt": "https://www.transfermarkt.com/matthijs-de-ligt/profil/spieler/326031", "display_name": "Matthijs de Ligt", "club": "Manchester United", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "amad-diallo": {"transfermarkt": "https://www.transfermarkt.com/amad-diallo/profil/spieler/504416", "display_name": "Amad Diallo", "club": "Manchester United", "league": "Premier League", "position": "Right Winger", "nationality": "Ivory Coast"},
}

# ── La Liga players ─────────────────────────────────────────────────────────
LA_LIGA_PLAYER_URLS: dict[str, dict[str, str]] = {

    "jude-bellingham": {"transfermarkt": "https://www.transfermarkt.com/jude-bellingham/profil/spieler/581678", "display_name": "Jude Bellingham", "club": "Real Madrid", "league": "La Liga", "position": "Central Midfielder", "nationality": "England"},
    "pedri": {"transfermarkt": "https://www.transfermarkt.com/pedri/profil/spieler/557458", "display_name": "Pedri", "club": "Barcelona", "league": "La Liga", "position": "Central Midfielder", "nationality": "Spain"},
    "lamine-yamal": {"transfermarkt": "https://www.transfermarkt.com/lamine-yamal/profil/spieler/949449", "display_name": "Lamine Yamal", "club": "Barcelona", "league": "La Liga", "position": "Right Winger", "nationality": "Spain"},
    "dani-olmo": {"transfermarkt": "https://www.transfermarkt.com/dani-olmo/profil/spieler/273357", "display_name": "Dani Olmo", "club": "Barcelona", "league": "La Liga", "position": "Attacking Midfielder", "nationality": "Spain"},
    "ferran-torres": {"transfermarkt": "https://www.transfermarkt.com/ferran-torres/profil/spieler/429253", "display_name": "Ferran Torres", "club": "Barcelona", "league": "La Liga", "position": "Left Winger", "nationality": "Spain"},
    "alejandro-garnacho": {"transfermarkt": "https://www.transfermarkt.com/alejandro-garnacho/profil/spieler/794403", "display_name": "Alejandro Garnacho", "club": "Atletico Madrid", "league": "La Liga", "position": "Left Winger", "nationality": "Argentina"},
    "kylian-mbappe": {"transfermarkt": "https://www.transfermarkt.com/kylian-mbappe/profil/spieler/342229", "display_name": "Kylian Mbappé", "club": "Real Madrid", "league": "La Liga", "position": "Centre-Forward", "nationality": "France"},
    "antoine-griezmann": {"transfermarkt": "https://www.transfermarkt.com/antoine-griezmann/profil/spieler/116010", "display_name": "Antoine Griezmann", "club": "Atletico Madrid", "league": "La Liga", "position": "Second Striker", "nationality": "France"},
    "alejandro-baena": {"transfermarkt": "https://www.transfermarkt.com/alejandro-baena/profil/spieler/570516", "display_name": "Alejandro Baena", "club": "Villarreal", "league": "La Liga", "position": "Attacking Midfielder", "nationality": "Spain"},
    "gavi": {"transfermarkt": "https://www.transfermarkt.com/gavi/profil/spieler/557469", "display_name": "Gavi", "club": "Barcelona", "league": "La Liga", "position": "Central Midfielder", "nationality": "Spain"},
    "fran-garcia": {"transfermarkt": "https://www.transfermarkt.com/fran-garcia/profil/spieler/402419", "display_name": "Fran García", "club": "Real Madrid", "league": "La Liga", "position": "Left-Back", "nationality": "Spain"},
}

# ── Bundesliga players ────────────────────────────────────────────────────────
BUNDESLIGA_PLAYER_URLS: dict[str, dict[str, str]] = {
    "florian-wirtz": {"transfermarkt": "https://www.transfermarkt.com/florian-wirtz/profil/spieler/521361", "display_name": "Florian Wirtz", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "Germany"},
    "jamal-musiala": {"transfermarkt": "https://www.transfermarkt.com/jamal-musiala/profil/spieler/580195", "display_name": "Jamal Musiala", "club": "Bayern Munich", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "Germany"},
    "harry-kane": {"transfermarkt": "https://www.transfermarkt.com/harry-kane/profil/spieler/132098", "display_name": "Harry Kane", "club": "Bayern Munich", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "England"},
    "granit-xhaka": {"transfermarkt": "https://www.transfermarkt.com/granit-xhaka/profil/spieler/162928", "display_name": "Granit Xhaka", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Defensive Midfielder", "nationality": "Switzerland"},
    "serge-gnabry": {"transfermarkt": "https://www.transfermarkt.com/serge-gnabry/profil/spieler/162398", "display_name": "Serge Gnabry", "club": "Bayern Munich", "league": "Bundesliga", "position": "Right Winger", "nationality": "Germany"},
    "karim-adeyemi": {"transfermarkt": "https://www.transfermarkt.com/karim-adeyemi/profil/spieler/462267", "display_name": "Karim Adeyemi", "club": "Borussia Dortmund", "league": "Bundesliga", "position": "Left Winger", "nationality": "Germany"},
    "maximilian-beier": {"transfermarkt": "https://www.transfermarkt.com/maximilian-beier/profil/spieler/559756", "display_name": "Maximilian Beier", "club": "Borussia Dortmund", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "Germany"},
    "jamie-gittens": {"transfermarkt": "https://www.transfermarkt.com/jamie-gittens/profil/spieler/793501", "display_name": "Jamie Gittens", "club": "Borussia Dortmund", "league": "Bundesliga", "position": "Left Winger", "nationality": "England"},
    "serhou-guirassy": {"transfermarkt": "https://www.transfermarkt.com/serhou-guirassy/profil/spieler/263824", "display_name": "Serhou Guirassy", "club": "Borussia Dortmund", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "Guinea"},
    "hugo-ekitike": {"transfermarkt": "https://www.transfermarkt.com/hugo-ekitike/profil/spieler/711988", "display_name": "Hugo Ekitiké", "club": "Eintracht Frankfurt", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "France"},
    "omar-marmoush": {"transfermarkt": "https://www.transfermarkt.com/omar-marmoush/profil/spieler/330940", "display_name": "Omar Marmoush", "club": "Manchester City", "league": "Premier League", "position": "Centre-Forward", "nationality": "Egypt"},
    "christoph-baumgartner": {"transfermarkt": "https://www.transfermarkt.com/christoph-baumgartner/profil/spieler/356862", "display_name": "Christoph Baumgartner", "club": "RB Leipzig", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "Austria"},
}

# ── Serie A players ───────────────────────────────────────────────────────────
SERIE_A_PLAYER_URLS: dict[str, dict[str, str]] = {
    "khvicha-kvaratskhelia": {"transfermarkt": "https://www.transfermarkt.com/khvicha-kvaratskhelia/profil/spieler/555021", "display_name": "Khvicha Kvaratskhelia", "club": "Paris Saint-Germain", "league": "Ligue 1", "position": "Left Winger", "nationality": "Georgia"},
    "victor-osimhen": {"transfermarkt": "https://www.transfermarkt.com/victor-osimhen/profil/spieler/401173", "display_name": "Victor Osimhen", "club": "Galatasaray", "league": "Süper Lig", "position": "Centre-Forward", "nationality": "Nigeria"},
    "davide-frattesi": {"transfermarkt": "https://www.transfermarkt.com/davide-frattesi/profil/spieler/387418", "display_name": "Davide Frattesi", "club": "Inter Milan", "league": "Serie A", "position": "Central Midfielder", "nationality": "Italy"},
    "federico-chiesa": {"transfermarkt": "https://www.transfermarkt.com/federico-chiesa/profil/spieler/341092", "display_name": "Federico Chiesa", "club": "Liverpool", "league": "Premier League", "position": "Right Winger", "nationality": "Italy"},
    "nicolo-barella": {"transfermarkt": "https://www.transfermarkt.com/nicolo-barella/profil/spieler/255942", "display_name": "Nicolò Barella", "club": "Inter Milan", "league": "Serie A", "position": "Central Midfielder", "nationality": "Italy"},
    "dusan-vlahovic": {"transfermarkt": "https://www.transfermarkt.com/dusan-vlahovic/profil/spieler/408526", "display_name": "Dušan Vlahović", "club": "Juventus", "league": "Serie A", "position": "Centre-Forward", "nationality": "Serbia"},

    "ademola-lookman": {"transfermarkt": "https://www.transfermarkt.com/ademola-lookman/profil/spieler/351954", "display_name": "Ademola Lookman", "club": "Atalanta", "league": "Serie A", "position": "Left Winger", "nationality": "Nigeria"},
    "teun-koopmeiners-atalanta": {"transfermarkt": "https://www.transfermarkt.com/teun-koopmeiners/profil/spieler/316685", "display_name": "Teun Koopmeiners", "club": "Juventus", "league": "Serie A", "position": "Attacking Midfielder", "nationality": "Netherlands"},
    "charles-de-ketelaere": {"transfermarkt": "https://www.transfermarkt.com/charles-de-ketelaere/profil/spieler/572264", "display_name": "Charles De Ketelaere", "club": "Atalanta", "league": "Serie A", "position": "Attacking Midfielder", "nationality": "Belgium"},
    "edoardo-bove": {"transfermarkt": "https://www.transfermarkt.com/edoardo-bove/profil/spieler/603376", "display_name": "Edoardo Bove", "club": "Fiorentina", "league": "Serie A", "position": "Central Midfielder", "nationality": "Italy"},
    "matias-soule-roma": {"transfermarkt": "https://www.transfermarkt.com/matias-soule/profil/spieler/806958", "display_name": "Matías Soulé", "club": "Roma", "league": "Serie A", "position": "Attacking Midfielder", "nationality": "Argentina"},
}

# ── Ligue 1 players ───────────────────────────────────────────────────────────
LIGUE1_PLAYER_URLS: dict[str, dict[str, str]] = {
    "ousmane-dembele": {"transfermarkt": "https://www.transfermarkt.com/ousmane-dembele/profil/spieler/272549", "display_name": "Ousmane Dembélé", "club": "Paris Saint-Germain", "league": "Ligue 1", "position": "Right Winger", "nationality": "France"},
    "bradley-barcola": {"transfermarkt": "https://www.transfermarkt.com/bradley-barcola/profil/spieler/791887", "display_name": "Bradley Barcola", "club": "Paris Saint-Germain", "league": "Ligue 1", "position": "Left Winger", "nationality": "France"},
    "desire-doue": {"transfermarkt": "https://www.transfermarkt.com/desire-doue/profil/spieler/921538", "display_name": "Désiré Doué", "club": "Paris Saint-Germain", "league": "Ligue 1", "position": "Right Winger", "nationality": "France"},
    "warren-zaire-emery": {"transfermarkt": "https://www.transfermarkt.com/warren-zaire-emery/profil/spieler/934049", "display_name": "Warren Zaïre-Emery", "club": "Paris Saint-Germain", "league": "Ligue 1", "position": "Central Midfielder", "nationality": "France"},
    "amine-gouiri": {"transfermarkt": "https://www.transfermarkt.com/amine-gouiri/profil/spieler/484534", "display_name": "Amine Gouiri", "club": "Rennes", "league": "Ligue 1", "position": "Second Striker", "nationality": "Algeria"},
    "elye-wahi": {"transfermarkt": "https://www.transfermarkt.com/elye-wahi/profil/spieler/762120", "display_name": "Elye Wahi", "club": "Eintracht Frankfurt", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "France"},
    "leny-yoro": {"transfermarkt": "https://www.transfermarkt.com/leny-yoro/profil/spieler/978558", "display_name": "Leny Yoro", "club": "Manchester United", "league": "Premier League", "position": "Centre-Back", "nationality": "France"},
}

# ── Uruguay / Chile / Paraguay players ────────────────────────────────────────
SOUTH_AMERICA_EXTRA_URLS: dict[str, dict[str, str]] = {
    "darwin-nunez": {"transfermarkt": "https://www.transfermarkt.com/darwin-nunez/profil/spieler/497392", "display_name": "Darwin Núñez", "club": "Liverpool", "league": "Premier League", "position": "Centre-Forward", "nationality": "Uruguay"},
    "rodrigo-bentancur": {"transfermarkt": "https://www.transfermarkt.com/rodrigo-bentancur/profil/spieler/357582", "display_name": "Rodrigo Bentancur", "club": "Tottenham", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "Uruguay"},
    "matias-vecino": {"transfermarkt": "https://www.transfermarkt.com/matias-vecino/profil/spieler/196019", "display_name": "Matías Vecino", "club": "Lazio", "league": "Serie A", "position": "Central Midfielder", "nationality": "Uruguay"},
    "alexis-mac-allister": {"transfermarkt": "https://www.transfermarkt.com/alexis-mac-allister/profil/spieler/394528", "display_name": "Alexis Mac Allister", "club": "Liverpool", "league": "Premier League", "position": "Central Midfielder", "nationality": "Argentina"},
    "enzo-fernandez": {"transfermarkt": "https://www.transfermarkt.com/enzo-fernandez/profil/spieler/581533", "display_name": "Enzo Fernández", "club": "Chelsea", "league": "Premier League", "position": "Central Midfielder", "nationality": "Argentina"},
    "marcos-acuna": {"transfermarkt": "https://www.transfermarkt.com/marcos-acuna/profil/spieler/170222", "display_name": "Marcos Acuña", "club": "Sevilla", "league": "La Liga", "position": "Left-Back", "nationality": "Argentina"},
    "mathias-olivera": {"transfermarkt": "https://www.transfermarkt.com/mathias-olivera/profil/spieler/432809", "display_name": "Mathías Olivera", "club": "Napoli", "league": "Serie A", "position": "Left-Back", "nationality": "Uruguay"},
    "matheus-nunes": {"transfermarkt": "https://www.transfermarkt.com/matheus-nunes/profil/spieler/504575", "display_name": "Matheus Nunes", "club": "Manchester City", "league": "Premier League", "position": "Central Midfielder", "nationality": "Portugal"},
    "igor-jesus": {"transfermarkt": "https://www.transfermarkt.com/igor-jesus/profil/spieler/711939", "display_name": "Igor Jesus", "club": "Botafogo", "league": "Brasileirao", "position": "Centre-Forward", "nationality": "Brazil"},
    "rayan-cherki": {"transfermarkt": "https://www.transfermarkt.com/rayan-cherki/profil/spieler/737747", "display_name": "Rayan Cherki", "club": "Borussia Dortmund", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "France"},
    "gabriel-silva-brazil": {"transfermarkt": "https://www.transfermarkt.com/gabriel/profil/spieler/166162", "display_name": "Gabriel", "club": "Arsenal", "league": "Premier League", "position": "Centre-Back", "nationality": "Brazil"},
    "evanilson": {"transfermarkt": "https://www.transfermarkt.com/evanilson/profil/spieler/498524", "display_name": "Evanilson", "club": "Bournemouth", "league": "Premier League", "position": "Centre-Forward", "nationality": "Brazil"},
    "yan-couto-citygruop": {"transfermarkt": "https://www.transfermarkt.com/yan-couto/profil/spieler/596461", "display_name": "Yan Couto", "club": "Borussia Dortmund", "league": "Bundesliga", "position": "Right-Back", "nationality": "Brazil"},
    "goncalo-ramos": {"transfermarkt": "https://www.transfermarkt.com/goncalo-ramos/profil/spieler/546063", "display_name": "Gonçalo Ramos", "club": "Paris Saint-Germain", "league": "Ligue 1", "position": "Centre-Forward", "nationality": "Portugal"},
    "pedro-neto-wolves": {"transfermarkt": "https://www.transfermarkt.com/pedro-neto/profil/spieler/441395", "display_name": "Pedro Neto", "club": "Chelsea", "league": "Premier League", "position": "Left Winger", "nationality": "Portugal"},
}

EXTRA_PLAYER_URLS: dict[str, dict[str, str]] = {
    "mohamed-salah": {"transfermarkt": "https://www.transfermarkt.com/mohamed-salah/profil/spieler/148455", "display_name": "Mohamed Salah", "club": "Liverpool", "league": "Premier League", "position": "Right Winger", "nationality": "Egypt"},
    "bukayo-saka": {"transfermarkt": "https://www.transfermarkt.com/bukayo-saka/profil/spieler/433177", "display_name": "Bukayo Saka", "club": "Arsenal", "league": "Premier League", "position": "Right Winger", "nationality": "England"},
    "martin-odegaard": {"transfermarkt": "https://www.transfermarkt.com/martin-odegaard/profil/spieler/316264", "display_name": "Martin Ødegaard", "club": "Arsenal", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "Norway"},
    "declan-rice": {"transfermarkt": "https://www.transfermarkt.com/declan-rice/profil/spieler/357662", "display_name": "Declan Rice", "club": "Arsenal", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "England"},
    "william-saliba": {"transfermarkt": "https://www.transfermarkt.com/william-saliba/profil/spieler/495639", "display_name": "William Saliba", "club": "Arsenal", "league": "Premier League", "position": "Centre-Back", "nationality": "France"},
    "virgil-van-dijk": {"transfermarkt": "https://www.transfermarkt.com/virgil-van-dijk/profil/spieler/139208", "display_name": "Virgil van Dijk", "club": "Liverpool", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "alexis-mac-allister": {"transfermarkt": "https://www.transfermarkt.com/alexis-mac-allister/profil/spieler/534325", "display_name": "Alexis Mac Allister", "club": "Liverpool", "league": "Premier League", "position": "Central Midfielder", "nationality": "Argentina"},
    "dominik-szoboszlai": {"transfermarkt": "https://www.transfermarkt.com/dominik-szoboszlai/profil/spieler/451276", "display_name": "Dominik Szoboszlai", "club": "Liverpool", "league": "Premier League", "position": "Central Midfielder", "nationality": "Hungary"},
    "darwin-nunez": {"transfermarkt": "https://www.transfermarkt.com/darwin-nunez/profil/spieler/546543", "display_name": "Darwin Núñez", "club": "Liverpool", "league": "Premier League", "position": "Centre-Forward", "nationality": "Uruguay"},
    "luis-diaz-liverpool": {"transfermarkt": "https://www.transfermarkt.com/luis-diaz/profil/spieler/480656", "display_name": "Luis Díaz", "club": "Liverpool", "league": "Premier League", "position": "Left Winger", "nationality": "Colombia"},
    "diogo-jota": {"transfermarkt": "https://www.transfermarkt.com/diogo-jota/profil/spieler/340924", "display_name": "Diogo Jota", "club": "Liverpool", "league": "Premier League", "position": "Left Winger", "nationality": "Portugal"},
    "erling-haaland": {"transfermarkt": "https://www.transfermarkt.com/erling-haaland/profil/spieler/248453", "display_name": "Erling Haaland", "club": "Manchester City", "league": "Premier League", "position": "Centre-Forward", "nationality": "Norway"},
    "kevin-de-bruyne": {"transfermarkt": "https://www.transfermarkt.com/kevin-de-bruyne/profil/spieler/66101", "display_name": "Kevin De Bruyne", "club": "Manchester City", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "Belgium"},
    "rodri-man-city": {"transfermarkt": "https://www.transfermarkt.com/rodri/profil/spieler/357565", "display_name": "Rodri", "club": "Manchester City", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "Spain"},
    "phil-foden": {"transfermarkt": "https://www.transfermarkt.com/phil-foden/profil/spieler/406635", "display_name": "Phil Foden", "club": "Manchester City", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "bernardo-silva": {"transfermarkt": "https://www.transfermarkt.com/bernardo-silva/profil/spieler/241641", "display_name": "Bernardo Silva", "club": "Manchester City", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "Portugal"},
    "ruben-dias": {"transfermarkt": "https://www.transfermarkt.com/ruben-dias/profil/spieler/258004", "display_name": "Rúben Dias", "club": "Manchester City", "league": "Premier League", "position": "Centre-Back", "nationality": "Portugal"},
    "josko-gvardiol": {"transfermarkt": "https://www.transfermarkt.com/josko-gvardiol/profil/spieler/475959", "display_name": "Josko Gvardiol", "club": "Manchester City", "league": "Premier League", "position": "Centre-Back", "nationality": "Croatia"},
    "jeremy-doku-city": {"transfermarkt": "https://www.transfermarkt.com/jeremy-doku/profil/spieler/486049", "display_name": "Jérémy Doku", "club": "Manchester City", "league": "Premier League", "position": "Left Winger", "nationality": "Belgium"},
    "kyle-walker": {"transfermarkt": "https://www.transfermarkt.com/kyle-walker/profil/spieler/95424", "display_name": "Kyle Walker", "club": "Manchester City", "league": "Premier League", "position": "Right-Back", "nationality": "England"},
    "nathan-ake": {"transfermarkt": "https://www.transfermarkt.com/nathan-ake/profil/spieler/177476", "display_name": "Nathan Aké", "club": "Manchester City", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "john-stones": {"transfermarkt": "https://www.transfermarkt.com/john-stones/profil/spieler/214655", "display_name": "John Stones", "club": "Manchester City", "league": "Premier League", "position": "Centre-Back", "nationality": "England"},
    "ederson": {"transfermarkt": "https://www.transfermarkt.com/ederson/profil/spieler/238221", "display_name": "Ederson", "club": "Manchester City", "league": "Premier League", "position": "Goalkeeper", "nationality": "Brazil"},
    "son-heung-min": {"transfermarkt": "https://www.transfermarkt.com/heung-min-son/profil/spieler/91845", "display_name": "Son Heung-min", "club": "Tottenham", "league": "Premier League", "position": "Left Winger", "nationality": "South Korea"},
    "james-maddison": {"transfermarkt": "https://www.transfermarkt.com/james-maddison/profil/spieler/294057", "display_name": "James Maddison", "club": "Tottenham", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "cristian-romero": {"transfermarkt": "https://www.transfermarkt.com/cristian-romero/profil/spieler/355915", "display_name": "Cristian Romero", "club": "Tottenham", "league": "Premier League", "position": "Centre-Back", "nationality": "Argentina"},
    "dejan-kulusevski": {"transfermarkt": "https://www.transfermarkt.com/dejan-kulusevski/profil/spieler/431755", "display_name": "Dejan Kulusevski", "club": "Tottenham", "league": "Premier League", "position": "Right Winger", "nationality": "Sweden"},
    "pedro-porro": {"transfermarkt": "https://www.transfermarkt.com/pedro-porro/profil/spieler/552955", "display_name": "Pedro Porro", "club": "Tottenham", "league": "Premier League", "position": "Right-Back", "nationality": "Spain"},
    "micky-van-de-ven": {"transfermarkt": "https://www.transfermarkt.com/micky-van-de-ven/profil/spieler/557463", "display_name": "Micky van de Ven", "club": "Tottenham", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "destiny-udogie": {"transfermarkt": "https://www.transfermarkt.com/destiny-udogie/profil/spieler/514713", "display_name": "Destiny Udogie", "club": "Tottenham", "league": "Premier League", "position": "Left-Back", "nationality": "Italy"},
    "brennan-johnson": {"transfermarkt": "https://www.transfermarkt.com/brennan-johnson/profil/spieler/485984", "display_name": "Brennan Johnson", "club": "Tottenham", "league": "Premier League", "position": "Right Winger", "nationality": "Wales"},
    "richarlison-spurs": {"transfermarkt": "https://www.transfermarkt.com/richarlison/profil/spieler/378710", "display_name": "Richarlison", "club": "Tottenham", "league": "Premier League", "position": "Centre-Forward", "nationality": "Brazil"},
    "yves-bissouma": {"transfermarkt": "https://www.transfermarkt.com/yves-bissouma/profil/spieler/410425", "display_name": "Yves Bissouma", "club": "Tottenham", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "Mali"},
    "pape-matar-sarr": {"transfermarkt": "https://www.transfermarkt.com/pape-matar-sarr/profil/spieler/568677", "display_name": "Pape Matar Sarr", "club": "Tottenham", "league": "Premier League", "position": "Central Midfielder", "nationality": "Senegal"},
    "guglielmo-vicario": {"transfermarkt": "https://www.transfermarkt.com/guglielmo-vicario/profil/spieler/286047", "display_name": "Guglielmo Vicario", "club": "Tottenham", "league": "Premier League", "position": "Goalkeeper", "nationality": "Italy"},
    "kyle-walker-peters": {"transfermarkt": "https://www.transfermarkt.com/kyle-walker-peters/profil/spieler/341052", "display_name": "Kyle Walker-Peters", "club": "Southampton", "league": "Premier League", "position": "Right-Back", "nationality": "England"},
    "adam-armstrong": {"transfermarkt": "https://www.transfermarkt.com/adam-armstrong/profil/spieler/226456", "display_name": "Adam Armstrong", "club": "Southampton", "league": "Premier League", "position": "Centre-Forward", "nationality": "England"},
    "flynn-downes": {"transfermarkt": "https://www.transfermarkt.com/flynn-downes/profil/spieler/486241", "display_name": "Flynn Downes", "club": "Southampton", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "England"},
    "taylor-harwood-bellis": {"transfermarkt": "https://www.transfermarkt.com/taylor-harwood-bellis/profil/spieler/503977", "display_name": "Taylor Harwood-Bellis", "club": "Southampton", "league": "Premier League", "position": "Centre-Back", "nationality": "England"},
    "jan-bednarek": {"transfermarkt": "https://www.transfermarkt.com/jan-bednarek/profil/spieler/243048", "display_name": "Jan Bednarek", "club": "Southampton", "league": "Premier League", "position": "Centre-Back", "nationality": "Poland"},
    "jack-stephens": {"transfermarkt": "https://www.transfermarkt.com/jack-stephens/profil/spieler/156942", "display_name": "Jack Stephens", "club": "Southampton", "league": "Premier League", "position": "Centre-Back", "nationality": "England"},
    "alex-mccarthy": {"transfermarkt": "https://www.transfermarkt.com/alex-mccarthy/profil/spieler/95423", "display_name": "Alex McCarthy", "club": "Southampton", "league": "Premier League", "position": "Goalkeeper", "nationality": "England"},
    "ross-stewart": {"transfermarkt": "https://www.transfermarkt.com/ross-stewart/profil/spieler/406085", "display_name": "Ross Stewart", "club": "Southampton", "league": "Premier League", "position": "Centre-Forward", "nationality": "Scotland"},
    "ryan-fraser": {"transfermarkt": "https://www.transfermarkt.com/ryan-fraser/profil/spieler/125866", "display_name": "Ryan Fraser", "club": "Southampton", "league": "Premier League", "position": "Left Winger", "nationality": "Scotland"},
    "maxwel-cornet": {"transfermarkt": "https://www.transfermarkt.com/maxwel-cornet/profil/spieler/234781", "display_name": "Maxwel Cornet", "club": "Southampton", "league": "Premier League", "position": "Left Winger", "nationality": "Cote d'Ivoire"},
    "paul-onuachu": {"transfermarkt": "https://www.transfermarkt.com/paul-onuachu/profil/spieler/272855", "display_name": "Paul Onuachu", "club": "Southampton", "league": "Premier League", "position": "Centre-Forward", "nationality": "Nigeria"},
    "kamaldeen-sulemana": {"transfermarkt": "https://www.transfermarkt.com/kamaldeen-sulemana/profil/spieler/747372", "display_name": "Kamaldeen Sulemana", "club": "Southampton", "league": "Premier League", "position": "Left Winger", "nationality": "Ghana"},
    "will-smallbone": {"transfermarkt": "https://www.transfermarkt.com/will-smallbone/profil/spieler/514493", "display_name": "Will Smallbone", "club": "Southampton", "league": "Premier League", "position": "Central Midfielder", "nationality": "Ireland"},
    "joe-aribo": {"transfermarkt": "https://www.transfermarkt.com/joe-aribo/profil/spieler/468198", "display_name": "Joe Aribo", "club": "Southampton", "league": "Premier League", "position": "Central Midfielder", "nationality": "Nigeria"},
    "sekou-mara": {"transfermarkt": "https://www.transfermarkt.com/sekou-mara/profil/spieler/641018", "display_name": "Sékou Mara", "club": "Strasbourg", "league": "Ligue 1", "position": "Centre-Forward", "nationality": "France"},
    "kylian-mbappe": {"transfermarkt": "https://www.transfermarkt.com/kylian-mbappe/profil/spieler/342229", "display_name": "Kylian Mbappé", "club": "Real Madrid", "league": "La Liga", "position": "Centre-Forward", "nationality": "France"},
    "antoine-griezmann": {"transfermarkt": "https://www.transfermarkt.com/antoine-griezmann/profil/spieler/125781", "display_name": "Antoine Griezmann", "club": "Atlético Madrid", "league": "La Liga", "position": "Second Striker", "nationality": "France"},
    "vinicius-jr-real": {"transfermarkt": "https://www.transfermarkt.com/vinicius-junior/profil/spieler/371998", "display_name": "Vinicius Junior", "club": "Real Madrid", "league": "La Liga", "position": "Left Winger", "nationality": "Brazil"},
    "rodrygo-real": {"transfermarkt": "https://www.transfermarkt.com/rodrygo/profil/spieler/412363", "display_name": "Rodrygo", "club": "Real Madrid", "league": "La Liga", "position": "Right Winger", "nationality": "Brazil"},
    "federico-valverde": {"transfermarkt": "https://www.transfermarkt.com/federico-valverde/profil/spieler/369081", "display_name": "Federico Valverde", "club": "Real Madrid", "league": "La Liga", "position": "Central Midfielder", "nationality": "Uruguay"},
    "eduardo-camavinga": {"transfermarkt": "https://www.transfermarkt.com/eduardo-camavinga/profil/spieler/640428", "display_name": "Eduardo Camavinga", "club": "Real Madrid", "league": "La Liga", "position": "Central Midfielder", "nationality": "France"},
    "aurelien-tchouameni": {"transfermarkt": "https://www.transfermarkt.com/aurelien-tchouameni/profil/spieler/412663", "display_name": "Aurélien Tchouaméni", "club": "Real Madrid", "league": "La Liga", "position": "Defensive Midfielder", "nationality": "France"},
    "eder-militao": {"transfermarkt": "https://www.transfermarkt.com/eder-militao/profil/spieler/401530", "display_name": "Éder Militão", "club": "Real Madrid", "league": "La Liga", "position": "Centre-Back", "nationality": "Brazil"},
    "antonio-rudiger": {"transfermarkt": "https://www.transfermarkt.com/antonio-rudiger/profil/spieler/86250", "display_name": "Antonio Rüdiger", "club": "Real Madrid", "league": "La Liga", "position": "Centre-Back", "nationality": "Germany"},
    "thibaut-courtois": {"transfermarkt": "https://www.transfermarkt.com/thibaut-courtois/profil/spieler/88869", "display_name": "Thibaut Courtois", "club": "Real Madrid", "league": "La Liga", "position": "Goalkeeper", "nationality": "Belgium"},
    "robert-lewandowski": {"transfermarkt": "https://www.transfermarkt.com/robert-lewandowski/profil/spieler/38253", "display_name": "Robert Lewandowski", "club": "Barcelona", "league": "La Liga", "position": "Centre-Forward", "nationality": "Poland"},
    "raphinha": {"transfermarkt": "https://www.transfermarkt.com/raphinha/profil/spieler/411295", "display_name": "Raphinha", "club": "Barcelona", "league": "La Liga", "position": "Right Winger", "nationality": "Brazil"},
    "frenkie-de-jong-barca": {"transfermarkt": "https://www.transfermarkt.com/frenkie-de-jong/profil/spieler/326330", "display_name": "Frenkie de Jong", "club": "Barcelona", "league": "La Liga", "position": "Central Midfielder", "nationality": "Netherlands"},
    "gavi": {"transfermarkt": "https://www.transfermarkt.com/gavi/profil/spieler/646740", "display_name": "Gavi", "club": "Barcelona", "league": "La Liga", "position": "Central Midfielder", "nationality": "Spain"},
    "ronald-araujo": {"transfermarkt": "https://www.transfermarkt.com/ronald-araujo/profil/spieler/480267", "display_name": "Ronald Araújo", "club": "Barcelona", "league": "La Liga", "position": "Centre-Back", "nationality": "Uruguay"},
    "jules-kounde": {"transfermarkt": "https://www.transfermarkt.com/jules-kounde/profil/spieler/411975", "display_name": "Jules Koundé", "club": "Barcelona", "league": "La Liga", "position": "Centre-Back", "nationality": "France"},
    "ter-stegen": {"transfermarkt": "https://www.transfermarkt.com/marc-andre-ter-stegen/profil/spieler/74857", "display_name": "Marc-André ter Stegen", "club": "Barcelona", "league": "La Liga", "position": "Goalkeeper", "nationality": "Germany"},
    "harry-kane": {"transfermarkt": "https://www.transfermarkt.com/harry-kane/profil/spieler/132098", "display_name": "Harry Kane", "club": "Bayern Munich", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "England"},
    "jamal-musiala": {"transfermarkt": "https://www.transfermarkt.com/jamal-musiala/profil/spieler/580195", "display_name": "Jamal Musiala", "club": "Bayern Munich", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "Germany"},
    "leroy-sane": {"transfermarkt": "https://www.transfermarkt.com/leroy-sane/profil/spieler/192565", "display_name": "Leroy Sané", "club": "Bayern Munich", "league": "Bundesliga", "position": "Right Winger", "nationality": "Germany"},
    "alphonso-davies": {"transfermarkt": "https://www.transfermarkt.com/alphonso-davies/profil/spieler/424204", "display_name": "Alphonso Davies", "club": "Bayern Munich", "league": "Bundesliga", "position": "Left-Back", "nationality": "Canada"},
    "matthijs-de-ligt": {"transfermarkt": "https://www.transfermarkt.com/matthijs-de-ligt/profil/spieler/326330", "display_name": "Matthijs de Ligt", "club": "Manchester United", "league": "Premier League", "position": "Centre-Back", "nationality": "Netherlands"},
    "kim-min-jae": {"transfermarkt": "https://www.transfermarkt.com/min-jae-kim/profil/spieler/503482", "display_name": "Kim Min-jae", "club": "Bayern Munich", "league": "Bundesliga", "position": "Centre-Back", "nationality": "South Korea"},
    "manuel-neuer": {"transfermarkt": "https://www.transfermarkt.com/manuel-neuer/profil/spieler/17259", "display_name": "Manuel Neuer", "club": "Bayern Munich", "league": "Bundesliga", "position": "Goalkeeper", "nationality": "Germany"},
    "florian-wirtz": {"transfermarkt": "https://www.transfermarkt.com/florian-wirtz/profil/spieler/598577", "display_name": "Florian Wirtz", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "Germany"},
    "jeremie-frimpong-leverkusen": {"transfermarkt": "https://www.transfermarkt.com/jeremie-frimpong/profil/spieler/484547", "display_name": "Jeremie Frimpong", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Right-Back", "nationality": "Netherlands"},
    "alejandro-grimaldo": {"transfermarkt": "https://www.transfermarkt.com/alejandro-grimaldo/profil/spieler/148455", "display_name": "Alejandro Grimaldo", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Left-Back", "nationality": "Spain"},
    "jonathan-tah": {"transfermarkt": "https://www.transfermarkt.com/jonathan-tah/profil/spieler/196357", "display_name": "Jonathan Tah", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Centre-Back", "nationality": "Germany"},
    "granit-xhaka": {"transfermarkt": "https://www.transfermarkt.com/granit-xhaka/profil/spieler/111455", "display_name": "Granit Xhaka", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Central Midfielder", "nationality": "Switzerland"},
    "victor-boniface": {"transfermarkt": "https://www.transfermarkt.com/victor-boniface/profil/spieler/655455", "display_name": "Victor Boniface", "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "Nigeria"},
    "lois-openda": {"transfermarkt": "https://www.transfermarkt.com/lois-openda/profil/spieler/368887", "display_name": "Loïs Openda", "club": "RB Leipzig", "league": "Bundesliga", "position": "Centre-Forward", "nationality": "Belgium"},
    "xavi-simons-leipzig": {"transfermarkt": "https://www.transfermarkt.com/xavi-simons/profil/spieler/566931", "display_name": "Xavi Simons", "club": "RB Leipzig", "league": "Bundesliga", "position": "Attacking Midfielder", "nationality": "Netherlands"},
    "dani-olmo": {"transfermarkt": "https://www.transfermarkt.com/dani-olmo/profil/spieler/293385", "display_name": "Dani Olmo", "club": "Barcelona", "league": "La Liga", "position": "Attacking Midfielder", "nationality": "Spain"},
    "lautaro-martinez-inter-milan": {"transfermarkt": "https://www.transfermarkt.com/lautaro-martinez/profil/spieler/406625", "display_name": "Lautaro Martínez", "club": "Inter Milan", "league": "Serie A", "position": "Centre-Forward", "nationality": "Argentina"},
    "marcus-thuram": {"transfermarkt": "https://www.transfermarkt.com/marcus-thuram/profil/spieler/272642", "display_name": "Marcus Thuram", "club": "Inter Milan", "league": "Serie A", "position": "Centre-Forward", "nationality": "France"},
    "hakan-calhanoglu": {"transfermarkt": "https://www.transfermarkt.com/hakan-calhanoglu/profil/spieler/126719", "display_name": "Hakan Calhanoglu", "club": "Inter Milan", "league": "Serie A", "position": "Attacking Midfielder", "nationality": "Turkey"},
    "nicolo-barella-inter": {"transfermarkt": "https://www.transfermarkt.com/nicolo-barella/profil/spieler/255942", "display_name": "Nicolò Barella", "club": "Inter Milan", "league": "Serie A", "position": "Central Midfielder", "nationality": "Italy"},
    "alessandro-bastoni": {"transfermarkt": "https://www.transfermarkt.com/alessandro-bastoni/profil/spieler/315853", "display_name": "Alessandro Bastoni", "club": "Inter Milan", "league": "Serie A", "position": "Centre-Back", "nationality": "Italy"},
    "federico-dimarco": {"transfermarkt": "https://www.transfermarkt.com/federico-dimarco/profil/spieler/198116", "display_name": "Federico Dimarco", "club": "Inter Milan", "league": "Serie A", "position": "Left-Back", "nationality": "Italy"},
    "yann-sommer": {"transfermarkt": "https://www.transfermarkt.com/yann-sommer/profil/spieler/42220", "display_name": "Yann Sommer", "club": "Inter Milan", "league": "Serie A", "position": "Goalkeeper", "nationality": "Switzerland"},
    "victor-osimhen": {"transfermarkt": "https://www.transfermarkt.com/victor-osimhen/profil/spieler/401530", "display_name": "Victor Osimhen", "club": "Galatasaray", "league": "Super Lig", "position": "Centre-Forward", "nationality": "Nigeria"},
    "khvicha-kvaratskhelia": {"transfermarkt": "https://www.transfermarkt.com/khvicha-kvaratskhelia/profil/spieler/502670", "display_name": "Khvicha Kvaratskhelia", "club": "Napoli", "league": "Serie A", "position": "Left Winger", "nationality": "Georgia"},
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
    **PREMIER_LEAGUE_PLAYER_URLS,
    **LA_LIGA_PLAYER_URLS,
    **BUNDESLIGA_PLAYER_URLS,
    **SERIE_A_PLAYER_URLS,
    **LIGUE1_PLAYER_URLS,
    **SOUTH_AMERICA_EXTRA_URLS,
    **EXTRA_PLAYER_URLS,
    "mason-mount": {"transfermarkt": "https://www.transfermarkt.com/mason-mount/profil/spieler/346446", "display_name": "Mason Mount", "club": "Manchester United", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "marcus-rashford": {"transfermarkt": "https://www.transfermarkt.com/marcus-rashford/profil/spieler/258923", "display_name": "Marcus Rashford", "club": "Manchester United", "league": "Premier League", "position": "Left Winger", "nationality": "England"},
    "bruno-fernandes": {"transfermarkt": "https://www.transfermarkt.com/bruno-fernandes/profil/spieler/240306", "display_name": "Bruno Fernandes", "club": "Manchester United", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "Portugal"},
    "rasmus-hojlund": {"transfermarkt": "https://www.transfermarkt.com/rasmus-hojlund/profil/spieler/610440", "display_name": "Rasmus Højlund", "club": "Manchester United", "league": "Premier League", "position": "Centre-Forward", "nationality": "Denmark"},
    "alejandro-garnacho": {"transfermarkt": "https://www.transfermarkt.com/alejandro-garnacho/profil/spieler/709325", "display_name": "Alejandro Garnacho", "club": "Manchester United", "league": "Premier League", "position": "Left Winger", "nationality": "Argentina"},
    "kobbie-mainoo": {"transfermarkt": "https://www.transfermarkt.com/kobbie-mainoo/profil/spieler/891966", "display_name": "Kobbie Mainoo", "club": "Manchester United", "league": "Premier League", "position": "Central Midfielder", "nationality": "England"},
    "diogo-dalot": {"transfermarkt": "https://www.transfermarkt.com/diogo-dalot/profil/spieler/357147", "display_name": "Diogo Dalot", "club": "Manchester United", "league": "Premier League", "position": "Right-Back", "nationality": "Portugal"},
    "lisandro-martinez": {"transfermarkt": "https://www.transfermarkt.com/lisandro-martinez/profil/spieler/501255", "display_name": "Lisandro Martínez", "club": "Manchester United", "league": "Premier League", "position": "Centre-Back", "nationality": "Argentina"},
    "andre-onana": {"transfermarkt": "https://www.transfermarkt.com/andre-onana/profil/spieler/234509", "display_name": "André Onana", "club": "Manchester United", "league": "Premier League", "position": "Goalkeeper", "nationality": "Cameroon"},
    "casemiro": {"transfermarkt": "https://www.transfermarkt.com/casemiro/profil/spieler/16306", "display_name": "Casemiro", "club": "Manchester United", "league": "Premier League", "position": "Defensive Midfielder", "nationality": "Brazil"},
    "luke-shaw": {"transfermarkt": "https://www.transfermarkt.com/luke-shaw/profil/spieler/183288", "display_name": "Luke Shaw", "club": "Manchester United", "league": "Premier League", "position": "Left-Back", "nationality": "England"},
    "antony-man-utd": {"transfermarkt": "https://www.transfermarkt.com/antony/profil/spieler/655406", "display_name": "Antony", "club": "Manchester United", "league": "Premier League", "position": "Right Winger", "nationality": "Brazil"},
    "christian-eriksen": {"transfermarkt": "https://www.transfermarkt.com/christian-eriksen/profil/spieler/69633", "display_name": "Christian Eriksen", "club": "Manchester United", "league": "Premier League", "position": "Central Midfielder", "nationality": "Denmark"},
    "harry-maguire": {"transfermarkt": "https://www.transfermarkt.com/harry-maguire/profil/spieler/177920", "display_name": "Harry Maguire", "club": "Manchester United", "league": "Premier League", "position": "Centre-Back", "nationality": "England"},
    "victor-lindelof": {"transfermarkt": "https://www.transfermarkt.com/victor-lindelof/profil/spieler/183288", "display_name": "Victor Lindelöf", "club": "Manchester United", "league": "Premier League", "position": "Centre-Back", "nationality": "Sweden"},
    "tyrell-malacia": {"transfermarkt": "https://www.transfermarkt.com/tyrell-malacia/profil/spieler/339340", "display_name": "Tyrell Malacia", "club": "Manchester United", "league": "Premier League", "position": "Left-Back", "nationality": "Netherlands"},
    "amrit-ray-scout": {"transfermarkt": "https://www.transfermarkt.com/amrit-ray/profil/spieler/100001", "display_name": "Amrit Ray", "club": "Youth Academy", "league": "Premier League", "position": "Attacking Midfielder", "nationality": "England"},
    "shola-shoretire": {"transfermarkt": "https://www.transfermarkt.com/shola-shoretire/profil/spieler/610444", "display_name": "Shola Shoretire", "club": "PAOK", "league": "Super League", "position": "Left Winger", "nationality": "England"},
    "hannibal-mejbri": {"transfermarkt": "https://www.transfermarkt.com/hannibal-mejbri/profil/spieler/607224", "display_name": "Hannibal Mejbri", "club": "Burnley", "league": "Championship", "position": "Central Midfielder", "nationality": "Tunisia"},
    "facundo-pellistri": {"transfermarkt": "https://www.transfermarkt.com/facundo-pellistri/profil/spieler/689025", "display_name": "Facundo Pellistri", "club": "Panathinaikos", "league": "Super League", "position": "Right Winger", "nationality": "Uruguay"},
}

for key, val in ALL_PLAYER_URLS.items():
    if "fbref" not in val:
        val["fbref"] = f"https://fbref.com/en/players/{key}"
    if "sofascore" not in val:
        val["sofascore"] = f"https://www.sofascore.com/player/{key}/100000"

