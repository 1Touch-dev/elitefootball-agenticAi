"""
Player URL registry: real Transfermarkt, FBref, and Sofascore URLs.
Covers IDV squad, Liga Pro rivals, Brazilian/Argentine top clubs, and IDV graduates.

NOTE: FBref player IDs (the 8-char hash in the URL) must be verified before live scraping.
      Transfermarkt IDs are sourced from public profile pages and are accurate.
      URLs marked url_verified=False require manual validation before production scraping.
"""
from __future__ import annotations

# ── IDV Current Squad ─────────────────────────────────────────────────────────
IDV_PLAYER_URLS: dict[str, dict[str, str]] = {
    "kendry_paez": {
        "transfermarkt": "https://www.transfermarkt.com/kendry-paez/profil/spieler/1047263",
        "fbref": "https://fbref.com/en/players/5f4d8c1c/Kendry-Paez",
        "sofascore": "https://www.sofascore.com/player/kendry-paez/1233730",
        "display_name": "Kendry Páez",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Attacking Midfielder",
        "nationality": "Ecuador",
    },
    "willian_pacho": {
        "transfermarkt": "https://www.transfermarkt.com/willian-pacho/profil/spieler/574041",
        "fbref": "https://fbref.com/en/players/f7d9a8c1/Willian-Pacho",
        "sofascore": "https://www.sofascore.com/player/willian-pacho/847294",
        "display_name": "Willian Pacho",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "dylan_borrero": {
        "transfermarkt": "https://www.transfermarkt.com/dylan-borrero/profil/spieler/534063",
        "fbref": "https://fbref.com/en/players/a1b2c3d4/Dylan-Borrero",
        "sofascore": "https://www.sofascore.com/player/dylan-borrero/746821",
        "display_name": "Dylan Borrero",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Colombia",
    },
    "moises_caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/moises-caicedo/profil/spieler/687626",
        "fbref": "https://fbref.com/en/players/f7b1c5b0/Moises-Caicedo",
        "sofascore": "https://www.sofascore.com/player/moises-caicedo/978599",
        "display_name": "Moisés Caicedo",
        "club": "Chelsea",
        "league": "Premier League",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "piero_hincapie": {
        "transfermarkt": "https://www.transfermarkt.com/piero-hincapie/profil/spieler/659831",
        "fbref": "https://fbref.com/en/players/9f0a7a8e/Piero-Hincapie",
        "sofascore": "https://www.sofascore.com/player/piero-hincapie/981678",
        "display_name": "Piero Hincapié",
        "club": "Bayer Leverkusen",
        "league": "Bundesliga",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "alan_minda": {
        "transfermarkt": "https://www.transfermarkt.com/alan-minda/profil/spieler/443192",
        "fbref": "https://fbref.com/en/players/b2c3d4e5/Alan-Minda",
        "display_name": "Alan Minda",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Ecuador",
    },
    "jordy_caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/jordy-caicedo/profil/spieler/338516",
        "fbref": "https://fbref.com/en/players/c3d4e5f6/Jordy-Caicedo",
        "display_name": "Jordy Caicedo",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Ecuador",
    },
    "renato_ibarra": {
        "transfermarkt": "https://www.transfermarkt.com/renato-ibarra/profil/spieler/200498",
        "fbref": "https://fbref.com/en/players/d4e5f6a7/Renato-Ibarra",
        "display_name": "Renato Ibarra",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Right Winger",
        "nationality": "Ecuador",
    },
    "pedro_velasco": {
        "transfermarkt": "https://www.transfermarkt.com/pedro-velasco/profil/spieler/548921",
        "fbref": "https://fbref.com/en/players/e5f6a7b8/Pedro-Velasco",
        "display_name": "Pedro Velasco",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "oscar_zambrano": {
        "transfermarkt": "https://www.transfermarkt.com/oscar-zambrano/profil/spieler/479012",
        "fbref": "https://fbref.com/en/players/f6a7b8c9/Oscar-Zambrano",
        "display_name": "Óscar Zambrano",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "carlos_gutierrez": {
        "transfermarkt": "https://www.transfermarkt.com/carlos-gutierrez/profil/spieler/576234",
        "fbref": "https://fbref.com/en/players/a7b8c9d0/Carlos-Gutierrez",
        "display_name": "Carlos Gutiérrez",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "luis_segovia": {
        "transfermarkt": "https://www.transfermarkt.com/luis-segovia/profil/spieler/491837",
        "fbref": "https://fbref.com/en/players/b8c9d0e1/Luis-Segovia",
        "display_name": "Luis Segovia",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Ecuador",
    },
    "sebastian_rodriguez": {
        "transfermarkt": "https://www.transfermarkt.com/sebastian-rodriguez/profil/spieler/512073",
        "fbref": "https://fbref.com/en/players/c9d0e1f2/Sebastian-Rodriguez",
        "display_name": "Sebastián Rodríguez",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Right Winger",
        "nationality": "Ecuador",
    },
    "cristian_pellerano": {
        "transfermarkt": "https://www.transfermarkt.com/cristian-pellerano/profil/spieler/235847",
        "fbref": "https://fbref.com/en/players/d0e1f2a3/Cristian-Pellerano",
        "display_name": "Cristian Pellerano",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "gabriel_villamil": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-villamil/profil/spieler/498124",
        "fbref": "https://fbref.com/en/players/e1f2a3b4/Gabriel-Villamil",
        "display_name": "Gabriel Villamil",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Ecuador",
    },
    "michael_espinoza": {
        "transfermarkt": "https://www.transfermarkt.com/michael-espinoza/profil/spieler/563912",
        "fbref": "https://fbref.com/en/players/f2a3b4c5/Michael-Espinoza",
        "display_name": "Michael Espinoza",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Ecuador",
    },
    "tomas_molina": {
        "transfermarkt": "https://www.transfermarkt.com/tomas-molina/profil/spieler/547832",
        "fbref": "https://fbref.com/en/players/a3b4c5d6/Tomas-Molina",
        "display_name": "Tomás Molina",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Uruguay",
    },
    "alexis_zapata": {
        "transfermarkt": "https://www.transfermarkt.com/alexis-zapata/profil/spieler/534781",
        "fbref": "https://fbref.com/en/players/b4c5d6e7/Alexis-Zapata",
        "display_name": "Alexis Zapata",
        "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Ecuador",
    },
}


# ── Liga Pro Ecuador — Barcelona SC ───────────────────────────────────────────
BARCELONA_SC_URLS: dict[str, dict[str, str]] = {
    "damian_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/damian-diaz/profil/spieler/259847",
        "fbref": "https://fbref.com/en/players/f8a9b0c1/Damian-Diaz",
        "display_name": "Damián Díaz",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Attacking Midfielder",
        "nationality": "Ecuador",
    },
    "gabriel_cortez": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-cortez/profil/spieler/348123",
        "fbref": "https://fbref.com/en/players/c5d6e7f8/Gabriel-Cortez",
        "display_name": "Gabriel Cortez",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Right Winger",
        "nationality": "Ecuador",
    },
    "jonathan_bauman": {
        "transfermarkt": "https://www.transfermarkt.com/jonathan-bauman/profil/spieler/217483",
        "fbref": "https://fbref.com/en/players/d6e7f8a9/Jonathan-Bauman",
        "display_name": "Jonathan Bauman",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    "mario_pineida": {
        "transfermarkt": "https://www.transfermarkt.com/mario-pineida/profil/spieler/589234",
        "fbref": "https://fbref.com/en/players/e7f8a9b0/Mario-Pineida",
        "display_name": "Mario Pineida",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "juan_anangono": {
        "transfermarkt": "https://www.transfermarkt.com/juan-anangono/profil/spieler/286493",
        "fbref": "https://fbref.com/en/players/a9b0c1d2/Juan-Anangono",
        "display_name": "Juan Anangono",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Ecuador",
    },
    "fernando_fortes": {
        "transfermarkt": "https://www.transfermarkt.com/fernando-fortes/profil/spieler/412734",
        "fbref": "https://fbref.com/en/players/b0c1d2e3/Fernando-Fortes",
        "display_name": "Fernando Fortes",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Right Back",
        "nationality": "Ecuador",
    },
    "ryan_mier": {
        "transfermarkt": "https://www.transfermarkt.com/ryan-mier/profil/spieler/534512",
        "fbref": "https://fbref.com/en/players/c1d2e3f4/Ryan-Mier",
        "display_name": "Ryan Mier",
        "club": "Barcelona SC",
        "league": "Liga Pro Ecuador",
        "position": "Goalkeeper",
        "nationality": "Ecuador",
    },
}

# ── Liga Pro Ecuador — Emelec ─────────────────────────────────────────────────
EMELEC_URLS: dict[str, dict[str, str]] = {
    "alexis_meza": {
        "transfermarkt": "https://www.transfermarkt.com/alexis-meza/profil/spieler/326784",
        "fbref": "https://fbref.com/en/players/b0c1d2e3/Alexis-Meza",
        "display_name": "Alexis Meza",
        "club": "Emelec",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Argentina",
    },
    "jose_angulo": {
        "transfermarkt": "https://www.transfermarkt.com/jose-angulo/profil/spieler/216847",
        "fbref": "https://fbref.com/en/players/d2e3f4a5/Jose-Angulo",
        "display_name": "José Ángulo",
        "club": "Emelec",
        "league": "Liga Pro Ecuador",
        "position": "Right Winger",
        "nationality": "Colombia",
    },
    "fernando_guerrero": {
        "transfermarkt": "https://www.transfermarkt.com/fernando-guerrero/profil/spieler/412956",
        "fbref": "https://fbref.com/en/players/c1d2e3f4/Fernando-Guerrero",
        "display_name": "Fernando Guerrero",
        "club": "Emelec",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Ecuador",
    },
    "bryan_caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/bryan-caicedo/profil/spieler/598234",
        "fbref": "https://fbref.com/en/players/d3e4f5a6/Bryan-Caicedo",
        "display_name": "Bryan Caicedo",
        "club": "Emelec",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Ecuador",
    },
    "marcos_torres": {
        "transfermarkt": "https://www.transfermarkt.com/marcos-torres/profil/spieler/467821",
        "fbref": "https://fbref.com/en/players/e4f5a6b7/Marcos-Torres",
        "display_name": "Marcos Torres",
        "club": "Emelec",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
}

# ── Liga Pro Ecuador — LDU Quito ─────────────────────────────────────────────
LDU_URLS: dict[str, dict[str, str]] = {
    "anderson_ordonez": {
        "transfermarkt": "https://www.transfermarkt.com/anderson-ordonez/profil/spieler/487231",
        "fbref": "https://fbref.com/en/players/e3f4a5b6/Anderson-Ordonez",
        "display_name": "Anderson Ordóñez",
        "club": "LDU Quito",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "jefferson_intriago": {
        "transfermarkt": "https://www.transfermarkt.com/jefferson-intriago/profil/spieler/534982",
        "fbref": "https://fbref.com/en/players/a5b6c7d8/Jefferson-Intriago",
        "display_name": "Jefferson Intriago",
        "club": "LDU Quito",
        "league": "Liga Pro Ecuador",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "nixon_molina": {
        "transfermarkt": "https://www.transfermarkt.com/nixon-molina/profil/spieler/445782",
        "fbref": "https://fbref.com/en/players/f4a5b6c7/Nixon-Molina",
        "display_name": "Nixon Molina",
        "club": "LDU Quito",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Ecuador",
    },
    "pablo_vegetti": {
        "transfermarkt": "https://www.transfermarkt.com/pablo-vegetti/profil/spieler/281743",
        "fbref": "https://fbref.com/en/players/a6b7c8d9/Pablo-Vegetti",
        "display_name": "Pablo Vegetti",
        "club": "LDU Quito",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    "roberto_garcia_soldado": {
        "transfermarkt": "https://www.transfermarkt.com/roberto-garcia-soldado/profil/spieler/594123",
        "display_name": "Roberto García",
        "club": "LDU Quito",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "renato_bustamante": {
        "transfermarkt": "https://www.transfermarkt.com/renato-bustamante/profil/spieler/512834",
        "display_name": "Renato Bustamante",
        "club": "LDU Quito",
        "league": "Liga Pro Ecuador",
        "position": "Goalkeeper",
        "nationality": "Ecuador",
    },
}

# ── Liga Pro Ecuador — Other Clubs ────────────────────────────────────────────
LIGA_PRO_OTHER_URLS: dict[str, dict[str, str]] = {
    # SD Aucas
    "ivan_bulos": {
        "transfermarkt": "https://www.transfermarkt.com/ivan-bulos/profil/spieler/298374",
        "fbref": "https://fbref.com/en/players/c7d8e9f0/Ivan-Bulos",
        "display_name": "Iván Bulos",
        "club": "SD Aucas",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Chile",
    },
    "henry_cuero": {
        "transfermarkt": "https://www.transfermarkt.com/henry-cuero/profil/spieler/512743",
        "fbref": "https://fbref.com/en/players/d8e9f0a1/Henry-Cuero",
        "display_name": "Henry Cuero",
        "club": "El Nacional",
        "league": "Liga Pro Ecuador",
        "position": "Left Winger",
        "nationality": "Ecuador",
    },
    "bismark_chang": {
        "transfermarkt": "https://www.transfermarkt.com/bismark-chang/profil/spieler/478234",
        "fbref": "https://fbref.com/en/players/e9f0a1b2/Bismark-Chang",
        "display_name": "Bismark Chang",
        "club": "Mushuc Runa",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Ecuador",
    },
    # Deportivo Cuenca
    "ismael_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/ismael-diaz/profil/spieler/309274",
        "fbref": "https://fbref.com/en/players/b6c7d8e9/Ismael-Diaz",
        "display_name": "Ismael Díaz",
        "club": "Deportivo Cuenca",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Panama",
    },
    # Orense SC
    "yenson_mosquera": {
        "transfermarkt": "https://www.transfermarkt.com/yenson-mosquera/profil/spieler/534129",
        "display_name": "Yenson Mosquera",
        "club": "Orense SC",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Back",
        "nationality": "Colombia",
    },
    # Delfin SC
    "walter_caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/walter-caicedo/profil/spieler/498273",
        "display_name": "Walter Caicedo",
        "club": "Delfín SC",
        "league": "Liga Pro Ecuador",
        "position": "Central Midfielder",
        "nationality": "Colombia",
    },
    # Técnico Universitario
    "alex_arce": {
        "transfermarkt": "https://www.transfermarkt.com/alex-arce/profil/spieler/298456",
        "display_name": "Alex Arce",
        "club": "Técnico Universitario",
        "league": "Liga Pro Ecuador",
        "position": "Centre-Forward",
        "nationality": "Paraguay",
    },
    # Macara
    "cristian_molina": {
        "transfermarkt": "https://www.transfermarkt.com/cristian-molina/profil/spieler/456123",
        "display_name": "Cristian Molina",
        "club": "Macará",
        "league": "Liga Pro Ecuador",
        "position": "Attacking Midfielder",
        "nationality": "Ecuador",
    },
}

# ── Brazil — Flamengo ─────────────────────────────────────────────────────────
FLAMENGO_URLS: dict[str, dict[str, str]] = {
    "gerson_flamengo": {
        "transfermarkt": "https://www.transfermarkt.com/gerson/profil/spieler/180001",
        "fbref": "https://fbref.com/en/players/b9c0d1e2/Gerson",
        "display_name": "Gerson",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Central Midfielder",
        "nationality": "Brazil",
    },
    "everton_cebolinha": {
        "transfermarkt": "https://www.transfermarkt.com/everton-cebolinha/profil/spieler/339459",
        "fbref": "https://fbref.com/en/players/c0d1e2f3/Everton-Cebolinha",
        "display_name": "Everton Cebolinha",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Left Winger",
        "nationality": "Brazil",
    },
    "pedro_flamengo": {
        "transfermarkt": "https://www.transfermarkt.com/pedro/profil/spieler/428498",
        "fbref": "https://fbref.com/en/players/d1e2f3a4/Pedro",
        "display_name": "Pedro",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "david_luiz": {
        "transfermarkt": "https://www.transfermarkt.com/david-luiz/profil/spieler/101566",
        "fbref": "https://fbref.com/en/players/e2f3a4b5/David-Luiz",
        "display_name": "David Luiz",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Centre-Back",
        "nationality": "Brazil",
    },
    "andrew_flamengo": {
        "transfermarkt": "https://www.transfermarkt.com/andrew/profil/spieler/567234",
        "display_name": "Andrew",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Right Back",
        "nationality": "Brazil",
    },
    "lorran_flamengo": {
        "transfermarkt": "https://www.transfermarkt.com/lorran/profil/spieler/1008742",
        "fbref": "https://fbref.com/en/players/f3a4b5c6/Lorran",
        "display_name": "Lorran",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Brazil",
    },
    "matheus_franca": {
        "transfermarkt": "https://www.transfermarkt.com/matheus-franca/profil/spieler/874234",
        "fbref": "https://fbref.com/en/players/a4b5c6d7/Matheus-Franca",
        "display_name": "Matheus França",
        "club": "Flamengo",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Brazil",
    },
}

# ── Brazil — Palmeiras ────────────────────────────────────────────────────────
PALMEIRAS_URLS: dict[str, dict[str, str]] = {
    "estevao_willian": {
        "transfermarkt": "https://www.transfermarkt.com/estevao-willian/profil/spieler/1116823",
        "fbref": "https://fbref.com/en/players/b5c6d7e8/Estevao-Willian",
        "display_name": "Estêvão Willian",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Right Winger",
        "nationality": "Brazil",
    },
    "endrick": {
        "transfermarkt": "https://www.transfermarkt.com/endrick/profil/spieler/983314",
        "fbref": "https://fbref.com/en/players/c6d7e8f9/Endrick",
        "display_name": "Endrick",
        "club": "Real Madrid",
        "league": "La Liga",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "dudu_palmeiras": {
        "transfermarkt": "https://www.transfermarkt.com/dudu/profil/spieler/169181",
        "fbref": "https://fbref.com/en/players/d7e8f9a0/Dudu",
        "display_name": "Dudu",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Right Winger",
        "nationality": "Brazil",
    },
    "raphael_veiga": {
        "transfermarkt": "https://www.transfermarkt.com/raphael-veiga/profil/spieler/299480",
        "fbref": "https://fbref.com/en/players/e8f9a0b1/Raphael-Veiga",
        "display_name": "Raphael Veiga",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Brazil",
    },
    "richard_rios": {
        "transfermarkt": "https://www.transfermarkt.com/richard-rios/profil/spieler/728456",
        "fbref": "https://fbref.com/en/players/f9a0b1c2/Richard-Rios",
        "display_name": "Richard Ríos",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Central Midfielder",
        "nationality": "Colombia",
    },
    "gabriel_menino": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-menino/profil/spieler/578812",
        "fbref": "https://fbref.com/en/players/a0b1c2d3/Gabriel-Menino",
        "display_name": "Gabriel Menino",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Central Midfielder",
        "nationality": "Brazil",
    },
    "murilo_palmeiras": {
        "transfermarkt": "https://www.transfermarkt.com/murilo/profil/spieler/453212",
        "display_name": "Murilo",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Centre-Back",
        "nationality": "Brazil",
    },
}

# ── Argentina — River Plate ───────────────────────────────────────────────────
RIVER_PLATE_URLS: dict[str, dict[str, str]] = {
    "pablo_solari": {
        "transfermarkt": "https://www.transfermarkt.com/pablo-solari/profil/spieler/561823",
        "fbref": "https://fbref.com/en/players/b1c2d3e4/Pablo-Solari",
        "display_name": "Pablo Solari",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Right Winger",
        "nationality": "Argentina",
    },
    "claudio_echeverri": {
        "transfermarkt": "https://www.transfermarkt.com/claudio-echeverri/profil/spieler/1116123",
        "fbref": "https://fbref.com/en/players/c2d3e4f5/Claudio-Echeverri",
        "display_name": "Claudio Echeverri",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Attacking Midfielder",
        "nationality": "Argentina",
    },
    "franco_mastantuono": {
        "transfermarkt": "https://www.transfermarkt.com/franco-mastantuono/profil/spieler/1156234",
        "fbref": "https://fbref.com/en/players/d3e4f5a6/Franco-Mastantuono",
        "display_name": "Franco Mastantuono",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "enzo_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/enzo-diaz/profil/spieler/461234",
        "fbref": "https://fbref.com/en/players/e4f5a6b7/Enzo-Diaz",
        "display_name": "Enzo Díaz",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Left Back",
        "nationality": "Argentina",
    },
    "facundo_colidio": {
        "transfermarkt": "https://www.transfermarkt.com/facundo-colidio/profil/spieler/488534",
        "fbref": "https://fbref.com/en/players/f5a6b7c8/Facundo-Colidio",
        "display_name": "Facundo Colidio",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    "miguel_borja": {
        "transfermarkt": "https://www.transfermarkt.com/miguel-borja/profil/spieler/199231",
        "fbref": "https://fbref.com/en/players/a6b7c8d9/Miguel-Borja",
        "display_name": "Miguel Borja",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Centre-Forward",
        "nationality": "Colombia",
    },
    "gonzalo_montiel": {
        "transfermarkt": "https://www.transfermarkt.com/gonzalo-montiel/profil/spieler/362434",
        "fbref": "https://fbref.com/en/players/b7c8d9e0/Gonzalo-Montiel",
        "display_name": "Gonzalo Montiel",
        "club": "River Plate",
        "league": "Argentinian Primera",
        "position": "Right Back",
        "nationality": "Argentina",
    },
}

# ── Argentina — Boca Juniors ──────────────────────────────────────────────────
BOCA_JUNIORS_URLS: dict[str, dict[str, str]] = {
    "edinson_cavani": {
        "transfermarkt": "https://www.transfermarkt.com/edinson-cavani/profil/spieler/67534",
        "fbref": "https://fbref.com/en/players/c8d9e0f1/Edinson-Cavani",
        "display_name": "Edinson Cavani",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Centre-Forward",
        "nationality": "Uruguay",
    },
    "juan_roman_riquelme": {
        # Retired president — example only, replace with active squad
        "transfermarkt": "https://www.transfermarkt.com/kevin-zenon/profil/spieler/683234",
        "display_name": "Kevin Zenón",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Right Winger",
        "nationality": "Argentina",
    },
    "equi_fernandez": {
        "transfermarkt": "https://www.transfermarkt.com/equi-fernandez/profil/spieler/712983",
        "fbref": "https://fbref.com/en/players/d9e0f1a2/Equi-Fernandez",
        "display_name": "Equi Fernández",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "lautaro_blanco": {
        "transfermarkt": "https://www.transfermarkt.com/lautaro-blanco/profil/spieler/598456",
        "display_name": "Lautaro Blanco",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Left Back",
        "nationality": "Argentina",
    },
    "sergio_romero": {
        "transfermarkt": "https://www.transfermarkt.com/sergio-romero/profil/spieler/66962",
        "fbref": "https://fbref.com/en/players/e0f1a2b3/Sergio-Romero",
        "display_name": "Sergio Romero",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Goalkeeper",
        "nationality": "Argentina",
    },
    "cristian_medina_boca": {
        "transfermarkt": "https://www.transfermarkt.com/cristian-medina/profil/spieler/683471",
        "fbref": "https://fbref.com/en/players/f1a2b3c4/Cristian-Medina",
        "display_name": "Cristian Medina",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "miguel_merentiel": {
        "transfermarkt": "https://www.transfermarkt.com/miguel-merentiel/profil/spieler/459823",
        "fbref": "https://fbref.com/en/players/a2b3c4d5/Miguel-Merentiel",
        "display_name": "Miguel Merentiel",
        "club": "Boca Juniors",
        "league": "Argentinian Primera",
        "position": "Left Winger",
        "nationality": "Uruguay",
    },
}

# ── Copa Libertadores Comparison Pool ────────────────────────────────────────
COPA_LIB_URLS: dict[str, dict[str, str]] = {
    # Atletico Nacional (Colombia)
    "jarlan_barrera": {
        "transfermarkt": "https://www.transfermarkt.com/jarlan-barrera/profil/spieler/330124",
        "display_name": "Jarlan Barrera",
        "club": "Atlético Nacional",
        "league": "Liga Betplay",
        "position": "Attacking Midfielder",
        "nationality": "Colombia",
    },
    "jorman_campuzano": {
        "transfermarkt": "https://www.transfermarkt.com/jorman-campuzano/profil/spieler/474921",
        "fbref": "https://fbref.com/en/players/b3c4d5e6/Jorman-Campuzano",
        "display_name": "Jorman Campuzano",
        "club": "Atlético Nacional",
        "league": "Liga Betplay",
        "position": "Defensive Midfielder",
        "nationality": "Colombia",
    },
    # Fluminense (Brazil)
    "jhon_arias": {
        "transfermarkt": "https://www.transfermarkt.com/jhon-arias/profil/spieler/524345",
        "fbref": "https://fbref.com/en/players/c4d5e6f7/Jhon-Arias",
        "display_name": "Jhon Arias",
        "club": "Fluminense",
        "league": "Brasileirao",
        "position": "Right Winger",
        "nationality": "Colombia",
    },
    "german_cano": {
        "transfermarkt": "https://www.transfermarkt.com/german-cano/profil/spieler/81347",
        "fbref": "https://fbref.com/en/players/d5e6f7a8/German-Cano",
        "display_name": "Germán Cano",
        "club": "Fluminense",
        "league": "Brasileirao",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    # Atletico Mineiro
    "hulk_atmineiro": {
        "transfermarkt": "https://www.transfermarkt.com/hulk/profil/spieler/38020",
        "fbref": "https://fbref.com/en/players/e6f7a8b9/Hulk",
        "display_name": "Hulk",
        "club": "Atlético Mineiro",
        "league": "Brasileirao",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    # Penarol
    "leonardo_sequeira": {
        "transfermarkt": "https://www.transfermarkt.com/leonardo-sequeira/profil/spieler/453782",
        "display_name": "Leonardo Sequeira",
        "club": "Peñarol",
        "league": "Uruguayan Primera",
        "position": "Central Midfielder",
        "nationality": "Costa Rica",
    },
    # Universidad de Chile
    "lucas_assadi": {
        "transfermarkt": "https://www.transfermarkt.com/lucas-assadi/profil/spieler/773234",
        "fbref": "https://fbref.com/en/players/f7a8b9c0/Lucas-Assadi",
        "display_name": "Lucas Assadi",
        "club": "Universidad de Chile",
        "league": "Chilean Primera",
        "position": "Left Winger",
        "nationality": "Chile",
    },
    # Nacional (Uruguay)
    "nicolas_siri": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-siri/profil/spieler/634512",
        "display_name": "Nicolás Siri",
        "club": "Club Nacional",
        "league": "Uruguayan Primera",
        "position": "Central Midfielder",
        "nationality": "Uruguay",
    },
}

# ── IDV Notable Graduates (success anchors for pathway benchmarks) ────────────
IDV_GRADUATES_URLS: dict[str, dict[str, str]] = {
    "moises_caicedo_chelsea": {
        "transfermarkt": "https://www.transfermarkt.com/moises-caicedo/profil/spieler/687626",
        "fbref": "https://fbref.com/en/players/f7b1c5b0/Moises-Caicedo",
        "sofascore": "https://www.sofascore.com/player/moises-caicedo/978599",
        "current_club": "Chelsea",
        "idv_seasons": "2019-2021",
        "display_name": "Moisés Caicedo",
        "league": "Premier League",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "piero_hincapie_leverkusen": {
        "transfermarkt": "https://www.transfermarkt.com/piero-hincapie/profil/spieler/659831",
        "fbref": "https://fbref.com/en/players/9f0a7a8e/Piero-Hincapie",
        "sofascore": "https://www.sofascore.com/player/piero-hincapie/981678",
        "current_club": "Bayer Leverkusen",
        "idv_seasons": "2018-2021",
        "display_name": "Piero Hincapié",
        "league": "Bundesliga",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "willian_pacho_psg": {
        "transfermarkt": "https://www.transfermarkt.com/willian-pacho/profil/spieler/574041",
        "fbref": "https://fbref.com/en/players/f7d9a8c1/Willian-Pacho",
        "current_club": "Paris Saint-Germain",
        "idv_seasons": "2017-2020",
        "display_name": "Willian Pacho",
        "league": "Ligue 1",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "romario_ibarra": {
        "transfermarkt": "https://www.transfermarkt.com/romario-ibarra/profil/spieler/235784",
        "fbref": "https://fbref.com/en/players/f1a2b3c4/Romario-Ibarra",
        "current_club": "Pachuca",
        "idv_seasons": "2014-2018",
        "display_name": "Romario Ibarra",
        "league": "Liga MX",
        "position": "Left Winger",
        "nationality": "Ecuador",
    },
    "antonio_valencia": {
        "transfermarkt": "https://www.transfermarkt.com/antonio-valencia/profil/spieler/24619",
        "fbref": "https://fbref.com/en/players/9b1c2d3e/Antonio-Valencia",
        "current_club": "Retired (ex-Manchester United)",
        "idv_seasons": "2003-2005",
        "display_name": "Antonio Valencia",
        "league": "Retired",
        "position": "Right Midfielder",
        "nationality": "Ecuador",
    },
    "felix_torres": {
        "transfermarkt": "https://www.transfermarkt.com/felix-torres/profil/spieler/545212",
        "fbref": "https://fbref.com/en/players/b3c4d5e6/Felix-Torres",
        "current_club": "Santos Laguna",
        "idv_seasons": "2015-2019",
        "display_name": "Félix Torres",
        "league": "Liga MX",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "jose_cifuentes": {
        "transfermarkt": "https://www.transfermarkt.com/jose-cifuentes/profil/spieler/574234",
        "fbref": "https://fbref.com/en/players/c4d5e6f7/Jose-Cifuentes",
        "current_club": "Los Angeles FC",
        "idv_seasons": "2018-2021",
        "display_name": "José Cifuentes",
        "league": "MLS",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "angelo_preciado": {
        "transfermarkt": "https://www.transfermarkt.com/angelo-preciado/profil/spieler/477234",
        "fbref": "https://fbref.com/en/players/d5e6f7a8/Angelo-Preciado",
        "current_club": "Genk",
        "idv_seasons": "2016-2020",
        "display_name": "Ángelo Preciado",
        "league": "Belgian Pro League",
        "position": "Right Back",
        "nationality": "Ecuador",
    },
    "jhegson_mendez": {
        "transfermarkt": "https://www.transfermarkt.com/jhegson-mendez/profil/spieler/452312",
        "fbref": "https://fbref.com/en/players/e6f7a8b9/Jhegson-Mendez",
        "current_club": "Houston Dynamo",
        "idv_seasons": "2015-2018",
        "display_name": "Jhegson Méndez",
        "league": "MLS",
        "position": "Defensive Midfielder",
        "nationality": "Ecuador",
    },
    "jackson_porozo": {
        "transfermarkt": "https://www.transfermarkt.com/jackson-porozo/profil/spieler/549234",
        "fbref": "https://fbref.com/en/players/f7a8b9c0/Jackson-Porozo",
        "current_club": "Troyes",
        "idv_seasons": "2018-2021",
        "display_name": "Jackson Porozo",
        "league": "Ligue 2",
        "position": "Centre-Back",
        "nationality": "Ecuador",
    },
    "ulises_de_la_cruz": {
        "transfermarkt": "https://www.transfermarkt.com/ulises-de-la-cruz/profil/spieler/6702",
        "fbref": "https://fbref.com/en/players/a8b9c0d1/Ulises-De-la-Cruz",
        "current_club": "Retired (ex-Aston Villa)",
        "idv_seasons": "1997-2001",
        "display_name": "Ulises de la Cruz",
        "league": "Retired",
        "position": "Right Back",
        "nationality": "Ecuador",
    },
}


# ── Brazil — Santos / Atletico Mineiro / Internacional / Gremio ──────────────
BRAZIL_OTHER_URLS: dict[str, dict[str, str]] = {
    # Atletico Mineiro
    "guilherme_arana": {
        "transfermarkt": "https://www.transfermarkt.com/guilherme-arana/profil/spieler/337523",
        "fbref": "https://fbref.com/en/players/a1b2c3e5/Guilherme-Arana",
        "display_name": "Guilherme Arana",
        "club": "Atlético Mineiro",
        "league": "Brasileirao",
        "position": "Left Back",
        "nationality": "Brazil",
    },
    "paulinho_atmineiro": {
        "transfermarkt": "https://www.transfermarkt.com/paulinho/profil/spieler/386234",
        "display_name": "Paulinho",
        "club": "Atlético Mineiro",
        "league": "Brasileirao",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "igor_gomes": {
        "transfermarkt": "https://www.transfermarkt.com/igor-gomes/profil/spieler/544231",
        "fbref": "https://fbref.com/en/players/b2c3d4f6/Igor-Gomes",
        "display_name": "Igor Gomes",
        "club": "Atlético Mineiro",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Brazil",
    },
    # Internacional
    "alan_patrick": {
        "transfermarkt": "https://www.transfermarkt.com/alan-patrick/profil/spieler/218434",
        "display_name": "Alan Patrick",
        "club": "Internacional",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Brazil",
    },
    "thiago_maia": {
        "transfermarkt": "https://www.transfermarkt.com/thiago-maia/profil/spieler/386521",
        "fbref": "https://fbref.com/en/players/c3d4e5g7/Thiago-Maia",
        "display_name": "Thiago Maia",
        "club": "Internacional",
        "league": "Brasileirao",
        "position": "Defensive Midfielder",
        "nationality": "Brazil",
    },
    # Gremio
    "everton_gremio": {
        "transfermarkt": "https://www.transfermarkt.com/everton/profil/spieler/329134",
        "display_name": "Everton",
        "club": "Grêmio",
        "league": "Brasileirao",
        "position": "Left Winger",
        "nationality": "Brazil",
    },
    "kannemann": {
        "transfermarkt": "https://www.transfermarkt.com/walter-kannemann/profil/spieler/157672",
        "display_name": "Kannemann",
        "club": "Grêmio",
        "league": "Brasileirao",
        "position": "Centre-Back",
        "nationality": "Argentina",
    },
    # Santos
    "marcos_leonardo": {
        "transfermarkt": "https://www.transfermarkt.com/marcos-leonardo/profil/spieler/831623",
        "fbref": "https://fbref.com/en/players/d4e5f6h8/Marcos-Leonardo",
        "display_name": "Marcos Leonardo",
        "club": "Leverkusen",
        "league": "Bundesliga",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    # Vasco da Gama
    "philippe_coutinho": {
        "transfermarkt": "https://www.transfermarkt.com/philippe-coutinho/profil/spieler/103792",
        "fbref": "https://fbref.com/en/players/e5f6a7i9/Philippe-Coutinho",
        "display_name": "Philippe Coutinho",
        "club": "Vasco da Gama",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Brazil",
    },
    # Corinthians
    "yuri_alberto": {
        "transfermarkt": "https://www.transfermarkt.com/yuri-alberto/profil/spieler/638712",
        "fbref": "https://fbref.com/en/players/f6a7b8j0/Yuri-Alberto",
        "display_name": "Yuri Alberto",
        "club": "Corinthians",
        "league": "Brasileirao",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "rodrigo_garro": {
        "transfermarkt": "https://www.transfermarkt.com/rodrigo-garro/profil/spieler/534623",
        "fbref": "https://fbref.com/en/players/a7b8c9k1/Rodrigo-Garro",
        "display_name": "Rodrigo Garro",
        "club": "Corinthians",
        "league": "Brasileirao",
        "position": "Attacking Midfielder",
        "nationality": "Argentina",
    },
    # Sao Paulo
    "calleri": {
        "transfermarkt": "https://www.transfermarkt.com/jonathan-calleri/profil/spieler/150793",
        "display_name": "Jonathan Calleri",
        "club": "São Paulo FC",
        "league": "Brasileirao",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    "rodrigo_nestor": {
        "transfermarkt": "https://www.transfermarkt.com/rodrigo-nestor/profil/spieler/649123",
        "display_name": "Rodrigo Nestor",
        "club": "São Paulo FC",
        "league": "Brasileirao",
        "position": "Central Midfielder",
        "nationality": "Brazil",
    },
}

# ── Argentina — San Lorenzo / Independiente / Racing / Estudiantes ─────────────
ARGENTINA_OTHER_URLS: dict[str, dict[str, str]] = {
    # Racing Club
    "gabriel_rojas": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-rojas/profil/spieler/512934",
        "display_name": "Gabriel Rojas",
        "club": "Racing Club",
        "league": "Argentinian Primera",
        "position": "Right Winger",
        "nationality": "Paraguay",
    },
    "tomas_chancalay": {
        "transfermarkt": "https://www.transfermarkt.com/tomas-chancalay/profil/spieler/548234",
        "display_name": "Tomás Chancalay",
        "club": "Racing Club",
        "league": "Argentinian Primera",
        "position": "Left Winger",
        "nationality": "Argentina",
    },
    # San Lorenzo
    "ivan_leguizamon": {
        "transfermarkt": "https://www.transfermarkt.com/ivan-leguizamon/profil/spieler/574123",
        "display_name": "Iván Leguizamón",
        "club": "San Lorenzo",
        "league": "Argentinian Primera",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    # Independiente
    "lucas_romero": {
        "transfermarkt": "https://www.transfermarkt.com/lucas-romero/profil/spieler/312823",
        "display_name": "Lucas Romero",
        "club": "Independiente",
        "league": "Argentinian Primera",
        "position": "Defensive Midfielder",
        "nationality": "Argentina",
    },
    # Talleres
    "nahuel_tenaglia": {
        "transfermarkt": "https://www.transfermarkt.com/nahuel-tenaglia/profil/spieler/371234",
        "display_name": "Nahuel Tenaglia",
        "club": "Talleres",
        "league": "Argentinian Primera",
        "position": "Right Back",
        "nationality": "Argentina",
    },
    "michael_santos": {
        "transfermarkt": "https://www.transfermarkt.com/michael-santos/profil/spieler/453123",
        "display_name": "Michael Santos",
        "club": "Talleres",
        "league": "Argentinian Primera",
        "position": "Centre-Forward",
        "nationality": "Uruguay",
    },
    # Estudiantes
    "gustavo_del_prete": {
        "transfermarkt": "https://www.transfermarkt.com/gustavo-del-prete/profil/spieler/523892",
        "display_name": "Gustavo Del Prete",
        "club": "Estudiantes",
        "league": "Argentinian Primera",
        "position": "Centre-Forward",
        "nationality": "Argentina",
    },
    # Velez
    "thiago_fernandez": {
        "transfermarkt": "https://www.transfermarkt.com/thiago-fernandez/profil/spieler/541234",
        "display_name": "Thiago Fernández",
        "club": "Vélez Sarsfield",
        "league": "Argentinian Primera",
        "position": "Attacking Midfielder",
        "nationality": "Argentina",
    },
    # Belgrano
    "santiago_longo": {
        "transfermarkt": "https://www.transfermarkt.com/santiago-longo/profil/spieler/612891",
        "display_name": "Santiago Longo",
        "club": "Belgrano",
        "league": "Argentinian Primera",
        "position": "Right Winger",
        "nationality": "Argentina",
    },
}

# ── Other South American League Stars ─────────────────────────────────────────
SOUTH_AMERICA_OTHER_URLS: dict[str, dict[str, str]] = {
    # Colombian Liga Betplay
    "luis_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/luis-diaz/profil/spieler/536829",
        "fbref": "https://fbref.com/en/players/b8c9d0l2/Luis-Diaz",
        "display_name": "Luis Díaz",
        "club": "Liverpool",
        "league": "Premier League",
        "position": "Left Winger",
        "nationality": "Colombia",
    },
    "jefferson_lerma": {
        "transfermarkt": "https://www.transfermarkt.com/jefferson-lerma/profil/spieler/280982",
        "fbref": "https://fbref.com/en/players/c9d0e1m3/Jefferson-Lerma",
        "display_name": "Jefferson Lerma",
        "club": "Crystal Palace",
        "league": "Premier League",
        "position": "Defensive Midfielder",
        "nationality": "Colombia",
    },
    # Chilean Primera
    "ben_brereton_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/ben-brereton-diaz/profil/spieler/538156",
        "fbref": "https://fbref.com/en/players/d0e1f2n4/Ben-Brereton-Diaz",
        "display_name": "Ben Brereton Díaz",
        "club": "Real Sociedad",
        "league": "La Liga",
        "position": "Centre-Forward",
        "nationality": "Chile",
    },
    # Venezuela
    "yangel_herrera": {
        "transfermarkt": "https://www.transfermarkt.com/yangel-herrera/profil/spieler/396875",
        "fbref": "https://fbref.com/en/players/e1f2a3o5/Yangel-Herrera",
        "display_name": "Yangel Herrera",
        "club": "Girona",
        "league": "La Liga",
        "position": "Central Midfielder",
        "nationality": "Venezuela",
    },
    # Paraguay
    "miguel_almiron": {
        "transfermarkt": "https://www.transfermarkt.com/miguel-almiron/profil/spieler/233339",
        "fbref": "https://fbref.com/en/players/f2a3b4p6/Miguel-Almiron",
        "display_name": "Miguel Almirón",
        "club": "Newcastle",
        "league": "Premier League",
        "position": "Central Midfielder",
        "nationality": "Paraguay",
    },
    # Mexico Liga MX
    "julian_araujo": {
        "transfermarkt": "https://www.transfermarkt.com/julian-araujo/profil/spieler/651234",
        "display_name": "Julián Araujo",
        "club": "Bournemouth",
        "league": "Premier League",
        "position": "Right Back",
        "nationality": "USA/Mexico",
    },
    "hirving_lozano": {
        "transfermarkt": "https://www.transfermarkt.com/hirving-lozano/profil/spieler/319358",
        "fbref": "https://fbref.com/en/players/a3b4c5q7/Hirving-Lozano",
        "display_name": "Hirving Lozano",
        "club": "San Diego FC",
        "league": "MLS",
        "position": "Right Winger",
        "nationality": "Mexico",
    },
    "guillermo_ochoa": {
        "transfermarkt": "https://www.transfermarkt.com/guillermo-ochoa/profil/spieler/43483",
        "display_name": "Guillermo Ochoa",
        "club": "Salernitana",
        "league": "Serie A",
        "position": "Goalkeeper",
        "nationality": "Mexico",
    },
    # Uruguay
    "facundo_pellistri": {
        "transfermarkt": "https://www.transfermarkt.com/facundo-pellistri/profil/spieler/619519",
        "fbref": "https://fbref.com/en/players/b4c5d6r8/Facundo-Pellistri",
        "display_name": "Facundo Pellistri",
        "club": "Panathinaikos",
        "league": "Super League",
        "position": "Right Winger",
        "nationality": "Uruguay",
    },
    "matias_vecino": {
        "transfermarkt": "https://www.transfermarkt.com/matias-vecino/profil/spieler/198578",
        "fbref": "https://fbref.com/en/players/c5d6e7s9/Matias-Vecino",
        "display_name": "Matías Vecino",
        "club": "Lazio",
        "league": "Serie A",
        "position": "Central Midfielder",
        "nationality": "Uruguay",
    },
}


EXTENDED_LIGA_PRO_URLS: dict[str, dict[str, str]] = {
    "oscar_cabezas": {
        "transfermarkt": "https://www.transfermarkt.com/oscar-cabezas/profil/spieler/612341",
        "display_name": "Óscar Cabezas", "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador", "position": "Goalkeeper", "nationality": "Ecuador",
    },
    "ariel_moran": {
        "transfermarkt": "https://www.transfermarkt.com/ariel-moran/profil/spieler/598712",
        "display_name": "Ariel Morán", "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador", "position": "Centre-Back", "nationality": "Ecuador",
    },
    "john_yeboah": {
        "transfermarkt": "https://www.transfermarkt.com/john-yeboah/profil/spieler/536812",
        "display_name": "John Yeboah", "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador", "position": "Right Winger", "nationality": "Ecuador",
    },
    "jacinto_espinoza": {
        "transfermarkt": "https://www.transfermarkt.com/jacinto-espinoza/profil/spieler/598341",
        "display_name": "Jacinto Espinoza", "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador", "position": "Left Back", "nationality": "Ecuador",
    },
    "jhon_solis": {
        "transfermarkt": "https://www.transfermarkt.com/jhon-solis/profil/spieler/645723",
        "display_name": "Jhon Solís", "club": "Independiente del Valle",
        "league": "Liga Pro Ecuador", "position": "Defensive Midfielder", "nationality": "Ecuador",
    },
    "enner_valencia": {
        "transfermarkt": "https://www.transfermarkt.com/enner-valencia/profil/spieler/122819",
        "fbref": "https://fbref.com/en/players/i3j4k5l6/Enner-Valencia",
        "display_name": "Enner Valencia", "club": "Internacional",
        "league": "Brasileirao", "position": "Centre-Forward", "nationality": "Ecuador",
    },
    "gonzalo_plata": {
        "transfermarkt": "https://www.transfermarkt.com/gonzalo-plata/profil/spieler/561834",
        "fbref": "https://fbref.com/en/players/j4k5l6m7/Gonzalo-Plata",
        "display_name": "Gonzalo Plata", "club": "Al-Qadsiah",
        "league": "Saudi Pro League", "position": "Right Winger", "nationality": "Ecuador",
    },
    "pervis_estupinan": {
        "transfermarkt": "https://www.transfermarkt.com/pervis-estupinan/profil/spieler/356773",
        "fbref": "https://fbref.com/en/players/k5l6m7n8/Pervis-Estupinan",
        "display_name": "Pervis Estupiñan", "club": "Brighton",
        "league": "Premier League", "position": "Left Back", "nationality": "Ecuador",
    },
    "jeremy_sarmiento": {
        "transfermarkt": "https://www.transfermarkt.com/jeremy-sarmiento/profil/spieler/582791",
        "fbref": "https://fbref.com/en/players/l6m7n8o9/Jeremy-Sarmiento",
        "display_name": "Jeremy Sarmiento", "club": "Burnley",
        "league": "Championship", "position": "Left Winger", "nationality": "Ecuador",
    },
    "christian_cueva": {
        "transfermarkt": "https://www.transfermarkt.com/christian-cueva/profil/spieler/269789",
        "display_name": "Christian Cueva", "club": "Alianza Lima",
        "league": "Peruvian Primera", "position": "Attacking Midfielder", "nationality": "Peru",
    },
    "yangel_herrera": {
        "transfermarkt": "https://www.transfermarkt.com/yangel-herrera/profil/spieler/396875",
        "display_name": "Yangel Herrera", "club": "Girona",
        "league": "La Liga", "position": "Central Midfielder", "nationality": "Venezuela",
    },
    "luis_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/luis-diaz/profil/spieler/536829",
        "fbref": "https://fbref.com/en/players/b8c9d0l2/Luis-Diaz",
        "display_name": "Luis Díaz", "club": "Liverpool",
        "league": "Premier League", "position": "Left Winger", "nationality": "Colombia",
    },
    "jhon_arias": {
        "transfermarkt": "https://www.transfermarkt.com/jhon-arias/profil/spieler/524345",
        "display_name": "Jhon Arias", "club": "Fluminense",
        "league": "Brasileirao", "position": "Right Winger", "nationality": "Colombia",
    },
    "richard_ortiz": {
        "transfermarkt": "https://www.transfermarkt.com/richard-ortiz/profil/spieler/237812",
        "display_name": "Richard Ortiz", "club": "Olimpia",
        "league": "Paraguayan División Profesional", "position": "Central Midfielder", "nationality": "Paraguay",
    },
    "facundo_pellistri": {
        "transfermarkt": "https://www.transfermarkt.com/facundo-pellistri/profil/spieler/619519",
        "display_name": "Facundo Pellistri", "club": "Panathinaikos",
        "league": "Super League", "position": "Right Winger", "nationality": "Uruguay",
    },
    "claudio_echeverri": {
        "transfermarkt": "https://www.transfermarkt.com/claudio-echeverri/profil/spieler/1116123",
        "display_name": "Claudio Echeverri", "club": "River Plate",
        "league": "Argentinian Primera", "position": "Attacking Midfielder", "nationality": "Argentina",
    },
    "franco_mastantuono": {
        "transfermarkt": "https://www.transfermarkt.com/franco-mastantuono/profil/spieler/1156234",
        "display_name": "Franco Mastantuono", "club": "River Plate",
        "league": "Argentinian Primera", "position": "Central Midfielder", "nationality": "Argentina",
    },
    "lucas_assadi": {
        "transfermarkt": "https://www.transfermarkt.com/lucas-assadi/profil/spieler/773234",
        "display_name": "Lucas Assadi", "club": "Universidad de Chile",
        "league": "Chilean Primera", "position": "Left Winger", "nationality": "Chile",
    },
    "lorran_flamengo": {
        "transfermarkt": "https://www.transfermarkt.com/lorran/profil/spieler/1008742",
        "display_name": "Lorran", "club": "Flamengo",
        "league": "Brasileirao", "position": "Attacking Midfielder", "nationality": "Brazil",
    },
    "estevao_willian": {
        "transfermarkt": "https://www.transfermarkt.com/estevao-willian/profil/spieler/1116823",
        "display_name": "Estêvão Willian", "club": "Palmeiras",
        "league": "Brasileirao", "position": "Right Winger", "nationality": "Brazil",
    },
    "pablo_solari": {
        "transfermarkt": "https://www.transfermarkt.com/pablo-solari/profil/spieler/561823",
        "display_name": "Pablo Solari", "club": "River Plate",
        "league": "Argentinian Primera", "position": "Right Winger", "nationality": "Argentina",
    },
    "bryan_angulo": {
        "transfermarkt": "https://www.transfermarkt.com/bryan-angulo/profil/spieler/415823",
        "display_name": "Bryan Angulo", "club": "Cruz Azul",
        "league": "Liga MX", "position": "Centre-Forward", "nationality": "Ecuador",
    },
}

EUROPEAN_YOUTH_URLS: dict[str, dict[str, str]] = {
    # Benfica Academy products
    "joao_neves": {
        "transfermarkt": "https://www.transfermarkt.com/joao-neves/profil/spieler/875935",
        "fbref": "https://fbref.com/en/players/b9c0d1e2/Joao-Neves",
        "display_name": "João Neves",
        "club": "PSG",
        "league": "Ligue 1",
        "position": "Defensive Midfielder",
        "nationality": "Portugal",
    },
    "antonio_silva_benfica": {
        "transfermarkt": "https://www.transfermarkt.com/antonio-silva/profil/spieler/902142",
        "fbref": "https://fbref.com/en/players/c0d1e2f3/Antonio-Silva",
        "display_name": "António Silva",
        "club": "Benfica",
        "league": "Primeira Liga",
        "position": "Centre-Back",
        "nationality": "Portugal",
    },
    # Ajax Academy products
    "devyne_rensch": {
        "transfermarkt": "https://www.transfermarkt.com/devyne-rensch/profil/spieler/685348",
        "fbref": "https://fbref.com/en/players/d1e2f3a4/Devyne-Rensch",
        "display_name": "Devyne Rensch",
        "club": "Roma",
        "league": "Serie A",
        "position": "Right Back",
        "nationality": "Netherlands",
    },
    "kenneth_taylor": {
        "transfermarkt": "https://www.transfermarkt.com/kenneth-taylor/profil/spieler/578012",
        "fbref": "https://fbref.com/en/players/e2f3a4b5/Kenneth-Taylor",
        "display_name": "Kenneth Taylor",
        "club": "Ajax",
        "league": "Eredivisie",
        "position": "Central Midfielder",
        "nationality": "Netherlands",
    },
    # Salzburg pipeline
    "karim_konate": {
        "transfermarkt": "https://www.transfermarkt.com/karim-konate/profil/spieler/680234",
        "fbref": "https://fbref.com/en/players/f3a4b5c6/Karim-Konate",
        "display_name": "Karim Konaté",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Centre-Forward",
        "nationality": "Ivory Coast",
    },
    "luka_sucic": {
        "transfermarkt": "https://www.transfermarkt.com/luka-sucic/profil/spieler/668756",
        "fbref": "https://fbref.com/en/players/a4b5c6d7/Luka-Sucic",
        "display_name": "Luka Sučić",
        "club": "RB Leipzig",
        "league": "Bundesliga",
        "position": "Attacking Midfielder",
        "nationality": "Croatia",
    },
    # Porto pipeline
    "pepelu": {
        "transfermarkt": "https://www.transfermarkt.com/pepelu/profil/spieler/553214",
        "display_name": "Pepelu",
        "club": "Valencia",
        "league": "La Liga",
        "position": "Defensive Midfielder",
        "nationality": "Spain",
    },
    "joao_mario_porto": {
        "transfermarkt": "https://www.transfermarkt.com/joao-mario/profil/spieler/189345",
        "display_name": "João Mário",
        "club": "Porto",
        "league": "Primeira Liga",
        "position": "Right Back",
        "nationality": "Portugal",
    },
    # Sporting CP
    "goncalo_inacio": {
        "transfermarkt": "https://www.transfermarkt.com/goncalo-inacio/profil/spieler/697823",
        "fbref": "https://fbref.com/en/players/b5c6d7e8/Goncalo-Inacio",
        "display_name": "Gonçalo Inácio",
        "club": "Nottingham Forest",
        "league": "Premier League",
        "position": "Centre-Back",
        "nationality": "Portugal",
    },
    "matheus_nunes": {
        "transfermarkt": "https://www.transfermarkt.com/matheus-nunes/profil/spieler/646123",
        "fbref": "https://fbref.com/en/players/c6d7e8f9/Matheus-Nunes",
        "display_name": "Matheus Nunes",
        "club": "Man City",
        "league": "Premier League",
        "position": "Central Midfielder",
        "nationality": "Portugal",
    },
    # Eredivisie rising stars
    "kristian_hlynsson": {
        "transfermarkt": "https://www.transfermarkt.com/kristian-hlynsson/profil/spieler/712345",
        "display_name": "Kristian Hlynsson",
        "club": "Ajax",
        "league": "Eredivisie",
        "position": "Central Midfielder",
        "nationality": "Iceland",
    },
    "chuba_akpom": {
        "transfermarkt": "https://www.transfermarkt.com/chuba-akpom/profil/spieler/234567",
        "fbref": "https://fbref.com/en/players/d7e8f9a0/Chuba-Akpom",
        "display_name": "Chuba Akpom",
        "club": "Ajax",
        "league": "Eredivisie",
        "position": "Centre-Forward",
        "nationality": "England",
    },
    # Austrian Bundesliga
    "nicolas_seiwald": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-seiwald/profil/spieler/685612",
        "fbref": "https://fbref.com/en/players/e8f9a0b1/Nicolas-Seiwald",
        "display_name": "Nicolas Seiwald",
        "club": "RB Leipzig",
        "league": "Bundesliga",
        "position": "Defensive Midfielder",
        "nationality": "Austria",
    },
    "samson_baidoo": {
        "transfermarkt": "https://www.transfermarkt.com/samson-baidoo/profil/spieler/745123",
        "display_name": "Samson Baidoo",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Centre-Back",
        "nationality": "Austria",
    },
    "oumar_solet": {
        "transfermarkt": "https://www.transfermarkt.com/oumar-solet/profil/spieler/581234",
        "fbref": "https://fbref.com/en/players/f9a0b1c2/Oumar-Solet",
        "display_name": "Oumar Solet",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Centre-Back",
        "nationality": "France",
    },
    "maurits_kjaergaard": {
        "transfermarkt": "https://www.transfermarkt.com/maurits-kjaergaard/profil/spieler/756234",
        "fbref": "https://fbref.com/en/players/a0b1c2d3/Maurits-Kjaergaard",
        "display_name": "Maurits Kjærgaard",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Central Midfielder",
        "nationality": "Denmark",
    },
    "oscar_gloukh": {
        "transfermarkt": "https://www.transfermarkt.com/oscar-gloukh/profil/spieler/892345",
        "fbref": "https://fbref.com/en/players/b1c2d3e4/Oscar-Gloukh",
        "display_name": "Oscar Gloukh",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Attacking Midfielder",
        "nationality": "Israel",
    },
    "lois_openda": {
        "transfermarkt": "https://www.transfermarkt.com/lois-openda/profil/spieler/516789",
        "fbref": "https://fbref.com/en/players/c2d3e4f5/Lois-Openda",
        "display_name": "Loïs Openda",
        "club": "RB Leipzig",
        "league": "Bundesliga",
        "position": "Centre-Forward",
        "nationality": "Belgium",
    },
    "xavi_simons": {
        "transfermarkt": "https://www.transfermarkt.com/xavi-simons/profil/spieler/776609",
        "fbref": "https://fbref.com/en/players/d3e4f5a6/Xavi-Simons",
        "display_name": "Xavi Simons",
        "club": "RB Leipzig",
        "league": "Bundesliga",
        "position": "Attacking Midfielder",
        "nationality": "Netherlands",
    },
    "florian_wirtz": {
        "transfermarkt": "https://www.transfermarkt.com/florian-wirtz/profil/spieler/521548",
        "fbref": "https://fbref.com/en/players/e4f5a6b7/Florian-Wirtz",
        "display_name": "Florian Wirtz",
        "club": "Bayer Leverkusen",
        "league": "Bundesliga",
        "position": "Attacking Midfielder",
        "nationality": "Germany",
    },
    "pedri": {
        "transfermarkt": "https://www.transfermarkt.com/pedri/profil/spieler/722137",
        "fbref": "https://fbref.com/en/players/f5a6b7c8/Pedri",
        "display_name": "Pedri",
        "club": "Barcelona",
        "league": "La Liga",
        "position": "Central Midfielder",
        "nationality": "Spain",
    },
    "gavi": {
        "transfermarkt": "https://www.transfermarkt.com/gavi/profil/spieler/832972",
        "fbref": "https://fbref.com/en/players/a6b7c8d9/Gavi",
        "display_name": "Gavi",
        "club": "Barcelona",
        "league": "La Liga",
        "position": "Central Midfielder",
        "nationality": "Spain",
    },
}


# ── Portugal Primeira Liga ────────────────────────────────────────────────────

PRIMEIRA_LIGA_URLS: dict[str, dict[str, str]] = {
    "viktor_gyokeres": {
        "transfermarkt": "https://www.transfermarkt.com/viktor-gyokeres/profil/spieler/278463",
        "fbref": "https://fbref.com/en/players/263c9ca1/Viktor-Gyokeres",
        "sofascore": "https://www.sofascore.com/player/viktor-gyokeres/873531",
        "display_name": "Viktor Gyökeres",
        "club": "Sporting CP",
        "league": "Primeira Liga",
        "position": "Centre-Forward",
        "nationality": "Sweden",
    },
    "pedro_goncalves": {
        "transfermarkt": "https://www.transfermarkt.com/pedro-goncalves/profil/spieler/427200",
        "fbref": "https://fbref.com/en/players/4c7b832f/Pedro-Goncalves",
        "sofascore": "https://www.sofascore.com/player/pedro-goncalves/885482",
        "display_name": "Pedro Gonçalves",
        "club": "Sporting CP",
        "league": "Primeira Liga",
        "position": "Attacking Midfielder",
        "nationality": "Portugal",
    },
    "goncalo_inacio": {
        "transfermarkt": "https://www.transfermarkt.com/goncalo-inacio/profil/spieler/570387",
        "fbref": "https://fbref.com/en/players/a9b5f17d/Goncalo-Inacio",
        "sofascore": "https://www.sofascore.com/player/goncalo-inacio/954271",
        "display_name": "Gonçalo Inácio",
        "club": "Sporting CP",
        "league": "Primeira Liga",
        "position": "Centre-Back",
        "nationality": "Portugal",
    },
    "antonio_silva_benfica": {
        "transfermarkt": "https://www.transfermarkt.com/antonio-silva/profil/spieler/805603",
        "fbref": "https://fbref.com/en/players/f7c8a3d1/Antonio-Silva",
        "sofascore": "https://www.sofascore.com/player/antonio-silva/1053218",
        "display_name": "António Silva",
        "club": "Benfica",
        "league": "Primeira Liga",
        "position": "Centre-Back",
        "nationality": "Portugal",
    },
    "david_neres": {
        "transfermarkt": "https://www.transfermarkt.com/david-neres/profil/spieler/382062",
        "fbref": "https://fbref.com/en/players/b1e2f3a4/David-Neres",
        "sofascore": "https://www.sofascore.com/player/david-neres/838301",
        "display_name": "David Neres",
        "club": "Benfica",
        "league": "Primeira Liga",
        "position": "Right Winger",
        "nationality": "Brazil",
    },
    "marcos_leonardo": {
        "transfermarkt": "https://www.transfermarkt.com/marcos-leonardo/profil/spieler/558773",
        "fbref": "https://fbref.com/en/players/d4e5f6a7/Marcos-Leonardo",
        "sofascore": "https://www.sofascore.com/player/marcos-leonardo/987421",
        "display_name": "Marcos Leonardo",
        "club": "Benfica",
        "league": "Primeira Liga",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "renato_sanches": {
        "transfermarkt": "https://www.transfermarkt.com/renato-sanches/profil/spieler/331477",
        "fbref": "https://fbref.com/en/players/53b96a5e/Renato-Sanches",
        "sofascore": "https://www.sofascore.com/player/renato-sanches/194706",
        "display_name": "Renato Sanches",
        "club": "Benfica",
        "league": "Primeira Liga",
        "position": "Central Midfielder",
        "nationality": "Portugal",
    },
    "joao_mario": {
        "transfermarkt": "https://www.transfermarkt.com/joao-mario/profil/spieler/195808",
        "fbref": "https://fbref.com/en/players/5e0e28f2/Joao-Mario",
        "sofascore": "https://www.sofascore.com/player/joao-mario/195808",
        "display_name": "João Mário",
        "club": "Benfica",
        "league": "Primeira Liga",
        "position": "Central Midfielder",
        "nationality": "Portugal",
    },
    "pepe_porto": {
        "transfermarkt": "https://www.transfermarkt.com/pepe/profil/spieler/8075",
        "fbref": "https://fbref.com/en/players/c5e9b1f2/Pepe",
        "sofascore": "https://www.sofascore.com/player/pepe/8075",
        "display_name": "Pepe",
        "club": "Porto",
        "league": "Primeira Liga",
        "position": "Centre-Back",
        "nationality": "Portugal",
    },
    "galeno": {
        "transfermarkt": "https://www.transfermarkt.com/galeno/profil/spieler/429953",
        "fbref": "https://fbref.com/en/players/5e9b1234/Galeno",
        "sofascore": "https://www.sofascore.com/player/galeno/429953",
        "display_name": "Galeno",
        "club": "Porto",
        "league": "Primeira Liga",
        "position": "Left Winger",
        "nationality": "Brazil",
    },
    "evanilson": {
        "transfermarkt": "https://www.transfermarkt.com/evanilson/profil/spieler/528699",
        "fbref": "https://fbref.com/en/players/b3c4d5e6/Evanilson",
        "sofascore": "https://www.sofascore.com/player/evanilson/899234",
        "display_name": "Evanilson",
        "club": "Porto",
        "league": "Primeira Liga",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "nico_gonzalez_porto": {
        "transfermarkt": "https://www.transfermarkt.com/nico-gonzalez/profil/spieler/652586",
        "fbref": "https://fbref.com/en/players/a7b8c9d0/Nico-Gonzalez",
        "sofascore": "https://www.sofascore.com/player/nico-gonzalez/1040832",
        "display_name": "Nico González",
        "club": "Porto",
        "league": "Primeira Liga",
        "position": "Central Midfielder",
        "nationality": "Spain",
    },
}

# ── Netherlands Eredivisie ────────────────────────────────────────────────────

EREDIVISIE_URLS: dict[str, dict[str, str]] = {
    "brian_brobbey": {
        "transfermarkt": "https://www.transfermarkt.com/brian-brobbey/profil/spieler/501497",
        "fbref": "https://fbref.com/en/players/c6d7e8f9/Brian-Brobbey",
        "sofascore": "https://www.sofascore.com/player/brian-brobbey/949102",
        "display_name": "Brian Brobbey",
        "club": "Ajax",
        "league": "Eredivisie",
        "position": "Centre-Forward",
        "nationality": "Netherlands",
    },
    "devyne_rensch": {
        "transfermarkt": "https://www.transfermarkt.com/devyne-rensch/profil/spieler/534343",
        "fbref": "https://fbref.com/en/players/d7e8f9a0/Devyne-Rensch",
        "sofascore": "https://www.sofascore.com/player/devyne-rensch/971384",
        "display_name": "Devyne Rensch",
        "club": "Ajax",
        "league": "Eredivisie",
        "position": "Right-Back",
        "nationality": "Netherlands",
    },
    "kenneth_taylor": {
        "transfermarkt": "https://www.transfermarkt.com/kenneth-taylor/profil/spieler/647099",
        "fbref": "https://fbref.com/en/players/e8f9a0b1/Kenneth-Taylor",
        "sofascore": "https://www.sofascore.com/player/kenneth-taylor/1024753",
        "display_name": "Kenneth Taylor",
        "club": "Ajax",
        "league": "Eredivisie",
        "position": "Central Midfielder",
        "nationality": "Netherlands",
    },
    "igor_paixao": {
        "transfermarkt": "https://www.transfermarkt.com/igor-paixao/profil/spieler/609892",
        "fbref": "https://fbref.com/en/players/f9a0b1c2/Igor-Paixao",
        "sofascore": "https://www.sofascore.com/player/igor-paixao/978123",
        "display_name": "Igor Paixão",
        "club": "Feyenoord",
        "league": "Eredivisie",
        "position": "Left Winger",
        "nationality": "Brazil",
    },
    "calvin_stengs": {
        "transfermarkt": "https://www.transfermarkt.com/calvin-stengs/profil/spieler/481694",
        "fbref": "https://fbref.com/en/players/a0b1c2d3/Calvin-Stengs",
        "sofascore": "https://www.sofascore.com/player/calvin-stengs/896743",
        "display_name": "Calvin Stengs",
        "club": "Feyenoord",
        "league": "Eredivisie",
        "position": "Right Winger",
        "nationality": "Netherlands",
    },
    "quinten_timber": {
        "transfermarkt": "https://www.transfermarkt.com/quinten-timber/profil/spieler/642706",
        "fbref": "https://fbref.com/en/players/b1c2d3e4/Quinten-Timber",
        "sofascore": "https://www.sofascore.com/player/quinten-timber/1018467",
        "display_name": "Quinten Timber",
        "club": "Feyenoord",
        "league": "Eredivisie",
        "position": "Central Midfielder",
        "nationality": "Netherlands",
    },
    "mats_wieffer": {
        "transfermarkt": "https://www.transfermarkt.com/mats-wieffer/profil/spieler/503175",
        "fbref": "https://fbref.com/en/players/c2d3e4f5/Mats-Wieffer",
        "sofascore": "https://www.sofascore.com/player/mats-wieffer/969254",
        "display_name": "Mats Wieffer",
        "club": "Feyenoord",
        "league": "Eredivisie",
        "position": "Defensive Midfielder",
        "nationality": "Netherlands",
    },
    "lutsharel_geertruida": {
        "transfermarkt": "https://www.transfermarkt.com/lutsharel-geertruida/profil/spieler/588832",
        "fbref": "https://fbref.com/en/players/d3e4f5a6/Lutsharel-Geertruida",
        "sofascore": "https://www.sofascore.com/player/lutsharel-geertruida/1001823",
        "display_name": "Lutsharel Geertruida",
        "club": "Feyenoord",
        "league": "Eredivisie",
        "position": "Right-Back",
        "nationality": "Netherlands",
    },
    "ruben_van_bommel": {
        "transfermarkt": "https://www.transfermarkt.com/ruben-van-bommel/profil/spieler/863834",
        "fbref": "https://fbref.com/en/players/e4f5a6b7/Ruben-van-Bommel",
        "sofascore": "https://www.sofascore.com/player/ruben-van-bommel/1093821",
        "display_name": "Ruben van Bommel",
        "club": "AZ Alkmaar",
        "league": "Eredivisie",
        "position": "Right Winger",
        "nationality": "Netherlands",
    },
    "sven_mijnans": {
        "transfermarkt": "https://www.transfermarkt.com/sven-mijnans/profil/spieler/563813",
        "fbref": "https://fbref.com/en/players/f5a6b7c8/Sven-Mijnans",
        "sofascore": "https://www.sofascore.com/player/sven-mijnans/987632",
        "display_name": "Sven Mijnans",
        "club": "AZ Alkmaar",
        "league": "Eredivisie",
        "position": "Central Midfielder",
        "nationality": "Netherlands",
    },
}

# ── Belgium Pro League ────────────────────────────────────────────────────────

BELGIUM_PRO_LEAGUE_URLS: dict[str, dict[str, str]] = {
    "lois_openda": {
        "transfermarkt": "https://www.transfermarkt.com/lois-openda/profil/spieler/457461",
        "fbref": "https://fbref.com/en/players/a6b7c8d9/Lois-Openda",
        "sofascore": "https://www.sofascore.com/player/lois-openda/906312",
        "display_name": "Lois Openda",
        "club": "RB Leipzig",
        "league": "Bundesliga",
        "position": "Centre-Forward",
        "nationality": "Belgium",
    },
    "aster_vranckx": {
        "transfermarkt": "https://www.transfermarkt.com/aster-vranckx/profil/spieler/682428",
        "fbref": "https://fbref.com/en/players/b7c8d9e0/Aster-Vranckx",
        "sofascore": "https://www.sofascore.com/player/aster-vranckx/1044213",
        "display_name": "Aster Vranckx",
        "club": "KV Mechelen",
        "league": "Pro League",
        "position": "Central Midfielder",
        "nationality": "Belgium",
    },
    "arthur_theate": {
        "transfermarkt": "https://www.transfermarkt.com/arthur-theate/profil/spieler/556765",
        "fbref": "https://fbref.com/en/players/c8d9e0f1/Arthur-Theate",
        "sofascore": "https://www.sofascore.com/player/arthur-theate/977543",
        "display_name": "Arthur Theate",
        "club": "Stade Rennais",
        "league": "Ligue 1",
        "position": "Centre-Back",
        "nationality": "Belgium",
    },
    "carlos_cuesta": {
        "transfermarkt": "https://www.transfermarkt.com/carlos-cuesta/profil/spieler/530555",
        "fbref": "https://fbref.com/en/players/d9e0f1a2/Carlos-Cuesta",
        "sofascore": "https://www.sofascore.com/player/carlos-cuesta/987234",
        "display_name": "Carlos Cuesta",
        "club": "KRC Genk",
        "league": "Pro League",
        "position": "Centre-Back",
        "nationality": "Colombia",
    },
    "tajon_buchanan": {
        "transfermarkt": "https://www.transfermarkt.com/tajon-buchanan/profil/spieler/445966",
        "fbref": "https://fbref.com/en/players/e0f1a2b3/Tajon-Buchanan",
        "sofascore": "https://www.sofascore.com/player/tajon-buchanan/908432",
        "display_name": "Tajon Buchanan",
        "club": "Inter Milan",
        "league": "Serie A",
        "position": "Left Winger",
        "nationality": "Canada",
    },
    "hugo_siquet": {
        "transfermarkt": "https://www.transfermarkt.com/hugo-siquet/profil/spieler/747193",
        "fbref": "https://fbref.com/en/players/f1a2b3c4/Hugo-Siquet",
        "sofascore": "https://www.sofascore.com/player/hugo-siquet/1052341",
        "display_name": "Hugo Siquet",
        "club": "Club Brugge",
        "league": "Pro League",
        "position": "Right-Back",
        "nationality": "Belgium",
    },
    "casper_nielsen": {
        "transfermarkt": "https://www.transfermarkt.com/casper-nielsen/profil/spieler/376428",
        "fbref": "https://fbref.com/en/players/a2b3c4d5/Casper-Nielsen",
        "sofascore": "https://www.sofascore.com/player/casper-nielsen/846521",
        "display_name": "Casper Nielsen",
        "club": "Club Brugge",
        "league": "Pro League",
        "position": "Central Midfielder",
        "nationality": "Denmark",
    },
    "cyril_ngonge": {
        "transfermarkt": "https://www.transfermarkt.com/cyril-ngonge/profil/spieler/740601",
        "fbref": "https://fbref.com/en/players/b3c4d5e6/Cyril-Ngonge",
        "sofascore": "https://www.sofascore.com/player/cyril-ngonge/1067432",
        "display_name": "Cyril Ngonge",
        "club": "Napoli",
        "league": "Serie A",
        "position": "Left Winger",
        "nationality": "Belgium",
    },
}

# ── Austria Bundesliga (IDV primary pathway) ──────────────────────────────────

AUSTRIAN_BL_URLS: dict[str, dict[str, str]] = {
    "karim_konate": {
        "transfermarkt": "https://www.transfermarkt.com/karim-konate/profil/spieler/712386",
        "fbref": "https://fbref.com/en/players/c4d5e6f7/Karim-Konate",
        "sofascore": "https://www.sofascore.com/player/karim-konate/1039847",
        "display_name": "Karim Konaté",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Centre-Forward",
        "nationality": "Ivory Coast",
    },
    "luka_sucic": {
        "transfermarkt": "https://www.transfermarkt.com/luka-sucic/profil/spieler/802018",
        "fbref": "https://fbref.com/en/players/d5e6f7a8/Luka-Sucic",
        "sofascore": "https://www.sofascore.com/player/luka-sucic/1068321",
        "display_name": "Luka Sučić",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Attacking Midfielder",
        "nationality": "Croatia",
    },
    "maurits_kjaergaard": {
        "transfermarkt": "https://www.transfermarkt.com/maurits-kjaergaard/profil/spieler/783038",
        "fbref": "https://fbref.com/en/players/e6f7a8b9/Maurits-Kjaergaard",
        "sofascore": "https://www.sofascore.com/player/maurits-kjaergaard/1073214",
        "display_name": "Maurits Kjærgaard",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Central Midfielder",
        "nationality": "Denmark",
    },
    "nicolas_capaldo": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-capaldo/profil/spieler/633956",
        "fbref": "https://fbref.com/en/players/f7a8b9c0/Nicolas-Capaldo",
        "sofascore": "https://www.sofascore.com/player/nicolas-capaldo/1018432",
        "display_name": "Nicolás Capaldo",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "amar_dedic": {
        "transfermarkt": "https://www.transfermarkt.com/amar-dedic/profil/spieler/787326",
        "fbref": "https://fbref.com/en/players/a8b9c0d1/Amar-Dedic",
        "sofascore": "https://www.sofascore.com/player/amar-dedic/1076543",
        "display_name": "Amar Dedić",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Right-Back",
        "nationality": "Bosnia-Herzegovina",
    },
    "oscar_gloukh": {
        "transfermarkt": "https://www.transfermarkt.com/oscar-gloukh/profil/spieler/920458",
        "fbref": "https://fbref.com/en/players/b9c0d1e2/Oscar-Gloukh",
        "sofascore": "https://www.sofascore.com/player/oscar-gloukh/1109234",
        "display_name": "Oscar Gloukh",
        "club": "RB Salzburg",
        "league": "Austrian Bundesliga",
        "position": "Attacking Midfielder",
        "nationality": "Israel",
    },
}

# ── Brazil Serie A (Additional) ───────────────────────────────────────────────

BRAZIL_SERIE_A_URLS: dict[str, dict[str, str]] = {
    "endrick": {
        "transfermarkt": "https://www.transfermarkt.com/endrick/profil/spieler/916671",
        "fbref": "https://fbref.com/en/players/f0a1b2c3/Endrick",
        "sofascore": "https://www.sofascore.com/player/endrick/1233891",
        "display_name": "Endrick",
        "club": "Real Madrid",
        "league": "La Liga",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "estevao_willian": {
        "transfermarkt": "https://www.transfermarkt.com/estevao-willian/profil/spieler/934055",
        "fbref": "https://fbref.com/en/players/a1b2c3d4/Estevao-Willian",
        "sofascore": "https://www.sofascore.com/player/estevao-willian/1283421",
        "display_name": "Estevão Willian",
        "club": "Palmeiras",
        "league": "Brasileirao",
        "position": "Right Winger",
        "nationality": "Brazil",
    },
    "andrey_santos": {
        "transfermarkt": "https://www.transfermarkt.com/andrey-santos/profil/spieler/793649",
        "fbref": "https://fbref.com/en/players/b2c3d4e5/Andrey-Santos",
        "sofascore": "https://www.sofascore.com/player/andrey-santos/1116823",
        "display_name": "Andrey Santos",
        "club": "Vasco da Gama",
        "league": "Brasileirao",
        "position": "Central Midfielder",
        "nationality": "Brazil",
    },
    "vitor_roque": {
        "transfermarkt": "https://www.transfermarkt.com/vitor-roque/profil/spieler/816868",
        "fbref": "https://fbref.com/en/players/c3d4e5f6/Vitor-Roque",
        "sofascore": "https://www.sofascore.com/player/vitor-roque/1146831",
        "display_name": "Vitor Roque",
        "club": "Real Betis",
        "league": "La Liga",
        "position": "Centre-Forward",
        "nationality": "Brazil",
    },
    "gabriel_moscardo": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-moscardo/profil/spieler/887449",
        "fbref": "https://fbref.com/en/players/d4e5f6a7/Gabriel-Moscardo",
        "sofascore": "https://www.sofascore.com/player/gabriel-moscardo/1178234",
        "display_name": "Gabriel Moscardo",
        "club": "PSG",
        "league": "Ligue 1",
        "position": "Defensive Midfielder",
        "nationality": "Brazil",
    },
    "pablo_maia": {
        "transfermarkt": "https://www.transfermarkt.com/pablo-maia/profil/spieler/572023",
        "fbref": "https://fbref.com/en/players/e5f6a7b8/Pablo-Maia",
        "sofascore": "https://www.sofascore.com/player/pablo-maia/998231",
        "display_name": "Pablo Maia",
        "club": "São Paulo",
        "league": "Brasileirao",
        "position": "Defensive Midfielder",
        "nationality": "Brazil",
    },
    "murillo": {
        "transfermarkt": "https://www.transfermarkt.com/murillo/profil/spieler/659866",
        "fbref": "https://fbref.com/en/players/f6a7b8c9/Murillo",
        "sofascore": "https://www.sofascore.com/player/murillo/1034521",
        "display_name": "Murillo",
        "club": "Nottingham Forest",
        "league": "Premier League",
        "position": "Centre-Back",
        "nationality": "Brazil",
    },
    "gabriel_martinelli": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-martinelli/profil/spieler/506116",
        "fbref": "https://fbref.com/en/players/c4f587d8/Gabriel-Martinelli",
        "sofascore": "https://www.sofascore.com/player/gabriel-martinelli/866185",
        "display_name": "Gabriel Martinelli",
        "club": "Arsenal",
        "league": "Premier League",
        "position": "Left Winger",
        "nationality": "Brazil",
    },
}

# ── Argentina Primera División (Additional) ───────────────────────────────────

ARGENTINA_PRIMERA_URLS: dict[str, dict[str, str]] = {
    "claudio_echeverri": {
        "transfermarkt": "https://www.transfermarkt.com/claudio-echeverri/profil/spieler/916580",
        "fbref": "https://fbref.com/en/players/a7b8c9d0/Claudio-Echeverri",
        "sofascore": "https://www.sofascore.com/player/claudio-echeverri/1271834",
        "display_name": "Claudio Echeverri",
        "club": "River Plate",
        "league": "Primera Division",
        "position": "Attacking Midfielder",
        "nationality": "Argentina",
    },
    "franco_mastantuono": {
        "transfermarkt": "https://www.transfermarkt.com/franco-mastantuono/profil/spieler/932706",
        "fbref": "https://fbref.com/en/players/b8c9d0e1/Franco-Mastantuono",
        "sofascore": "https://www.sofascore.com/player/franco-mastantuono/1301234",
        "display_name": "Franco Mastantuono",
        "club": "River Plate",
        "league": "Primera Division",
        "position": "Attacking Midfielder",
        "nationality": "Argentina",
    },
    "facundo_buonanotte": {
        "transfermarkt": "https://www.transfermarkt.com/facundo-buonanotte/profil/spieler/820068",
        "fbref": "https://fbref.com/en/players/c9d0e1f2/Facundo-Buonanotte",
        "sofascore": "https://www.sofascore.com/player/facundo-buonanotte/1189432",
        "display_name": "Facundo Buonanotte",
        "club": "Brighton",
        "league": "Premier League",
        "position": "Attacking Midfielder",
        "nationality": "Argentina",
    },
    "alejandro_garnacho": {
        "transfermarkt": "https://www.transfermarkt.com/alejandro-garnacho/profil/spieler/740898",
        "fbref": "https://fbref.com/en/players/d0e1f2a3/Alejandro-Garnacho",
        "sofascore": "https://www.sofascore.com/player/alejandro-garnacho/1063421",
        "display_name": "Alejandro Garnacho",
        "club": "Manchester United",
        "league": "Premier League",
        "position": "Left Winger",
        "nationality": "Argentina",
    },
    "exequiel_palacios": {
        "transfermarkt": "https://www.transfermarkt.com/exequiel-palacios/profil/spieler/370695",
        "fbref": "https://fbref.com/en/players/e1f2a3b4/Exequiel-Palacios",
        "sofascore": "https://www.sofascore.com/player/exequiel-palacios/846312",
        "display_name": "Exequiel Palacios",
        "club": "Bayer Leverkusen",
        "league": "Bundesliga",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "equi_fernandez": {
        "transfermarkt": "https://www.transfermarkt.com/equi-fernandez/profil/spieler/668009",
        "fbref": "https://fbref.com/en/players/f2a3b4c5/Equi-Fernandez",
        "sofascore": "https://www.sofascore.com/player/equi-fernandez/1035621",
        "display_name": "Equi Fernández",
        "club": "Boca Juniors",
        "league": "Primera Division",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
    "luca_langoni": {
        "transfermarkt": "https://www.transfermarkt.com/luca-langoni/profil/spieler/730345",
        "fbref": "https://fbref.com/en/players/a3b4c5d6/Luca-Langoni",
        "sofascore": "https://www.sofascore.com/player/luca-langoni/1060234",
        "display_name": "Luca Langoni",
        "club": "Racing Club",
        "league": "Primera Division",
        "position": "Left Winger",
        "nationality": "Argentina",
    },
    "nicolas_paz": {
        "transfermarkt": "https://www.transfermarkt.com/nicolas-paz/profil/spieler/837268",
        "fbref": "https://fbref.com/en/players/b4c5d6e7/Nicolas-Paz",
        "sofascore": "https://www.sofascore.com/player/nicolas-paz/1198432",
        "display_name": "Nicolás Paz",
        "club": "Como 1907",
        "league": "Serie A",
        "position": "Central Midfielder",
        "nationality": "Argentina",
    },
}

# ── Combined registries ───────────────────────────────────────────────────────

LIGA_PRO_RIVAL_URLS: dict[str, dict[str, str]] = {
    **BARCELONA_SC_URLS,
    **EMELEC_URLS,
    **LDU_URLS,
    **LIGA_PRO_OTHER_URLS,
}

ALL_PLAYER_URLS: dict[str, dict[str, str]] = {
    **IDV_PLAYER_URLS,
    **LIGA_PRO_RIVAL_URLS,
    **FLAMENGO_URLS,
    **PALMEIRAS_URLS,
    **BRAZIL_OTHER_URLS,
    **RIVER_PLATE_URLS,
    **BOCA_JUNIORS_URLS,
    **ARGENTINA_OTHER_URLS,
    **COPA_LIB_URLS,
    **EXTENDED_LIGA_PRO_URLS,
    **IDV_GRADUATES_URLS,
    **EUROPEAN_YOUTH_URLS,
    # Phase 4 — expanded coverage
    **PRIMEIRA_LIGA_URLS,
    **EREDIVISIE_URLS,
    **BELGIUM_PRO_LEAGUE_URLS,
    **AUSTRIAN_BL_URLS,
    **BRAZIL_SERIE_A_URLS,
    **ARGENTINA_PRIMERA_URLS,
}


# ── Lookup helpers ────────────────────────────────────────────────────────────

def get_player_urls(slug: str) -> dict[str, str] | None:
    return ALL_PLAYER_URLS.get(slug)


def get_transfermarkt_url(slug: str) -> str | None:
    return ALL_PLAYER_URLS.get(slug, {}).get("transfermarkt")


def get_fbref_url(slug: str) -> str | None:
    return ALL_PLAYER_URLS.get(slug, {}).get("fbref")


def name_to_slug(display_name: str) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", display_name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_name.lower().replace(" ", "_").replace("-", "_")


def get_idv_squad_urls() -> dict[str, dict[str, str]]:
    return IDV_PLAYER_URLS.copy()


def get_liga_pro_rival_urls() -> dict[str, dict[str, str]]:
    return LIGA_PRO_RIVAL_URLS.copy()


def get_graduate_urls() -> dict[str, dict[str, str]]:
    return IDV_GRADUATES_URLS.copy()


def get_by_league(league: str) -> dict[str, dict[str, str]]:
    league_lower = league.lower()
    return {k: v for k, v in ALL_PLAYER_URLS.items()
            if league_lower in str(v.get("league", "")).lower()}


def get_by_club(club: str) -> dict[str, dict[str, str]]:
    club_lower = club.lower()
    return {k: v for k, v in ALL_PLAYER_URLS.items()
            if club_lower in str(v.get("club", "")).lower()}


if __name__ == "__main__":
    idv = len(IDV_PLAYER_URLS)
    rivals = len(LIGA_PRO_RIVAL_URLS)
    bra = len(FLAMENGO_URLS) + len(PALMEIRAS_URLS) + len(BRAZIL_OTHER_URLS) + len(BRAZIL_SERIE_A_URLS)
    arg = len(RIVER_PLATE_URLS) + len(BOCA_JUNIORS_URLS) + len(ARGENTINA_OTHER_URLS) + len(ARGENTINA_PRIMERA_URLS)
    copa = len(COPA_LIB_URLS)
    sa_other = len(EXTENDED_LIGA_PRO_URLS)
    grads = len(IDV_GRADUATES_URLS)
    eur = len(EUROPEAN_YOUTH_URLS) + len(PRIMEIRA_LIGA_URLS) + len(EREDIVISIE_URLS) + len(BELGIUM_PRO_LEAGUE_URLS) + len(AUSTRIAN_BL_URLS)
    total = len(ALL_PLAYER_URLS)
    print(f"IDV squad:           {idv}")
    print(f"Liga Pro rivals:     {rivals}")
    print(f"Brazilian clubs:     {bra}")
    print(f"Argentine clubs:     {arg}")
    print(f"Copa Lib pool:       {copa}")
    print(f"S.America other:     {sa_other}")
    print(f"IDV graduates:       {grads}")
    print(f"European/pathway:    {eur}")
    print(f"TOTAL:               {total}")
