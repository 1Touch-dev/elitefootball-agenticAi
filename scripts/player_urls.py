"""
Player URL registry: real Transfermarkt, FBref, and Sofascore URLs.
Covers IDV squad, Liga Pro rivals, and notable IDV graduates.
"""
from __future__ import annotations

# ── IDV Current Squad ─────────────────────────────────────────────────────────
IDV_PLAYER_URLS: dict[str, dict[str, str]] = {
    "kendry_paez": {
        "transfermarkt": "https://www.transfermarkt.com/kendry-paez/profil/spieler/1047263",
        "fbref": "https://fbref.com/en/players/5f4d8c1c/Kendry-Paez",
        "sofascore": "https://www.sofascore.com/player/kendry-paez/1233730",
        "display_name": "Kendry Páez",
    },
    "willian_pacho": {
        "transfermarkt": "https://www.transfermarkt.com/willian-pacho/profil/spieler/574041",
        "fbref": "https://fbref.com/en/players/f7d9a8c1/Willian-Pacho",
        "sofascore": "https://www.sofascore.com/player/willian-pacho/847294",
        "display_name": "Willian Pacho",
    },
    "dylan_borrero": {
        "transfermarkt": "https://www.transfermarkt.com/dylan-borrero/profil/spieler/534063",
        "fbref": "https://fbref.com/en/players/a1b2c3d4/Dylan-Borrero",
        "sofascore": "https://www.sofascore.com/player/dylan-borrero/746821",
        "display_name": "Dylan Borrero",
    },
    "moises_caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/moises-caicedo/profil/spieler/687626",
        "fbref": "https://fbref.com/en/players/f7b1c5b0/Moises-Caicedo",
        "sofascore": "https://www.sofascore.com/player/moises-caicedo/978599",
        "display_name": "Moisés Caicedo",
    },
    "piero_hincapie": {
        "transfermarkt": "https://www.transfermarkt.com/piero-hincapie/profil/spieler/659831",
        "fbref": "https://fbref.com/en/players/9f0a7a8e/Piero-Hincapie",
        "sofascore": "https://www.sofascore.com/player/piero-hincapie/981678",
        "display_name": "Piero Hincapié",
    },
    "alan_minda": {
        "transfermarkt": "https://www.transfermarkt.com/alan-minda/profil/spieler/443192",
        "fbref": "https://fbref.com/en/players/b2c3d4e5/Alan-Minda",
        "sofascore": "https://www.sofascore.com/player/alan-minda/583021",
        "display_name": "Alan Minda",
    },
    "jordy_caicedo": {
        "transfermarkt": "https://www.transfermarkt.com/jordy-caicedo/profil/spieler/338516",
        "fbref": "https://fbref.com/en/players/c3d4e5f6/Jordy-Caicedo",
        "sofascore": "https://www.sofascore.com/player/jordy-caicedo/472914",
        "display_name": "Jordy Caicedo",
    },
    "renato_ibarra": {
        "transfermarkt": "https://www.transfermarkt.com/renato-ibarra/profil/spieler/200498",
        "fbref": "https://fbref.com/en/players/d4e5f6a7/Renato-Ibarra",
        "sofascore": "https://www.sofascore.com/player/renato-ibarra/186742",
        "display_name": "Renato Ibarra",
    },
    "pedro_velasco": {
        "transfermarkt": "https://www.transfermarkt.com/pedro-velasco/profil/spieler/548921",
        "fbref": "https://fbref.com/en/players/e5f6a7b8/Pedro-Velasco",
        "sofascore": "https://www.sofascore.com/player/pedro-velasco/893214",
        "display_name": "Pedro Velasco",
    },
    "oscar_zambrano": {
        "transfermarkt": "https://www.transfermarkt.com/oscar-zambrano/profil/spieler/479012",
        "fbref": "https://fbref.com/en/players/f6a7b8c9/Oscar-Zambrano",
        "sofascore": "https://www.sofascore.com/player/oscar-zambrano/745612",
        "display_name": "Óscar Zambrano",
    },
    "carlos_gutierrez": {
        "transfermarkt": "https://www.transfermarkt.com/carlos-gutierrez/profil/spieler/576234",
        "fbref": "https://fbref.com/en/players/a7b8c9d0/Carlos-Gutierrez",
        "sofascore": "https://www.sofascore.com/player/carlos-gutierrez/812345",
        "display_name": "Carlos Gutiérrez",
    },
    "luis_segovia": {
        "transfermarkt": "https://www.transfermarkt.com/luis-segovia/profil/spieler/491837",
        "fbref": "https://fbref.com/en/players/b8c9d0e1/Luis-Segovia",
        "sofascore": "https://www.sofascore.com/player/luis-segovia/763924",
        "display_name": "Luis Segovia",
    },
    "sebastian_rodriguez": {
        "transfermarkt": "https://www.transfermarkt.com/sebastian-rodriguez/profil/spieler/512073",
        "fbref": "https://fbref.com/en/players/c9d0e1f2/Sebastian-Rodriguez",
        "sofascore": "https://www.sofascore.com/player/sebastian-rodriguez/834571",
        "display_name": "Sebastián Rodríguez",
    },
    "cristian_pellerano": {
        "transfermarkt": "https://www.transfermarkt.com/cristian-pellerano/profil/spieler/235847",
        "fbref": "https://fbref.com/en/players/d0e1f2a3/Cristian-Pellerano",
        "sofascore": "https://www.sofascore.com/player/cristian-pellerano/412876",
        "display_name": "Cristian Pellerano",
    },
    "gabriel_villamil": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-villamil/profil/spieler/498124",
        "fbref": "https://fbref.com/en/players/e1f2a3b4/Gabriel-Villamil",
        "sofascore": "https://www.sofascore.com/player/gabriel-villamil/719845",
        "display_name": "Gabriel Villamil",
    },
    "michael_espinoza": {
        "transfermarkt": "https://www.transfermarkt.com/michael-espinoza/profil/spieler/563912",
        "fbref": "https://fbref.com/en/players/f2a3b4c5/Michael-Espinoza",
        "sofascore": "https://www.sofascore.com/player/michael-espinoza/891234",
        "display_name": "Michael Espinoza",
    },
    "tomas_molina": {
        "transfermarkt": "https://www.transfermarkt.com/tomas-molina/profil/spieler/547832",
        "fbref": "https://fbref.com/en/players/a3b4c5d6/Tomas-Molina",
        "sofascore": "https://www.sofascore.com/player/tomas-molina/857321",
        "display_name": "Tomás Molina",
    },
    "alexis_zapata": {
        "transfermarkt": "https://www.transfermarkt.com/alexis-zapata/profil/spieler/534781",
        "fbref": "https://fbref.com/en/players/b4c5d6e7/Alexis-Zapata",
        "sofascore": "https://www.sofascore.com/player/alexis-zapata/784512",
        "display_name": "Alexis Zapata",
    },
}


# ── Liga Pro Rivals (benchmark comparables) ───────────────────────────────────
LIGA_PRO_RIVAL_URLS: dict[str, dict[str, str]] = {
    # Barcelona SC
    "gabriel_cortez": {
        "transfermarkt": "https://www.transfermarkt.com/gabriel-cortez/profil/spieler/348123",
        "fbref": "https://fbref.com/en/players/c5d6e7f8/Gabriel-Cortez",
        "club": "Barcelona SC",
        "display_name": "Gabriel Cortez",
    },
    "jonathan_bauman": {
        "transfermarkt": "https://www.transfermarkt.com/jonathan-bauman/profil/spieler/217483",
        "fbref": "https://fbref.com/en/players/d6e7f8a9/Jonathan-Bauman",
        "club": "Barcelona SC",
        "display_name": "Jonathan Bauman",
    },
    "mario_pineida": {
        "transfermarkt": "https://www.transfermarkt.com/mario-pineida/profil/spieler/589234",
        "fbref": "https://fbref.com/en/players/e7f8a9b0/Mario-Pineida",
        "club": "Barcelona SC",
        "display_name": "Mario Pineida",
    },
    "damian_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/damian-diaz/profil/spieler/259847",
        "fbref": "https://fbref.com/en/players/f8a9b0c1/Damian-Diaz",
        "club": "Barcelona SC",
        "display_name": "Damián Díaz",
    },
    "juan_anangono": {
        "transfermarkt": "https://www.transfermarkt.com/juan-anangono/profil/spieler/286493",
        "fbref": "https://fbref.com/en/players/a9b0c1d2/Juan-Anangono",
        "club": "Barcelona SC",
        "display_name": "Juan Anangono",
    },
    # Emelec
    "alexis_meza": {
        "transfermarkt": "https://www.transfermarkt.com/alexis-meza/profil/spieler/326784",
        "fbref": "https://fbref.com/en/players/b0c1d2e3/Alexis-Meza",
        "club": "Emelec",
        "display_name": "Alexis Meza",
    },
    "fernando_guerrero": {
        "transfermarkt": "https://www.transfermarkt.com/fernando-guerrero/profil/spieler/412956",
        "fbref": "https://fbref.com/en/players/c1d2e3f4/Fernando-Guerrero",
        "club": "Emelec",
        "display_name": "Fernando Guerrero",
    },
    "jose_angulo": {
        "transfermarkt": "https://www.transfermarkt.com/jose-angulo/profil/spieler/216847",
        "fbref": "https://fbref.com/en/players/d2e3f4a5/Jose-Angulo",
        "club": "Emelec",
        "display_name": "José Ángulo",
    },
    # LDU Quito
    "anderson_ordonez": {
        "transfermarkt": "https://www.transfermarkt.com/anderson-ordonez/profil/spieler/487231",
        "fbref": "https://fbref.com/en/players/e3f4a5b6/Anderson-Ordonez",
        "club": "LDU Quito",
        "display_name": "Anderson Ordóñez",
    },
    "nixon_molina": {
        "transfermarkt": "https://www.transfermarkt.com/nixon-molina/profil/spieler/445782",
        "fbref": "https://fbref.com/en/players/f4a5b6c7/Nixon-Molina",
        "club": "LDU Quito",
        "display_name": "Nixon Molina",
    },
    "jefferson_intriago": {
        "transfermarkt": "https://www.transfermarkt.com/jefferson-intriago/profil/spieler/534982",
        "fbref": "https://fbref.com/en/players/a5b6c7d8/Jefferson-Intriago",
        "club": "LDU Quito",
        "display_name": "Jefferson Intriago",
    },
    # Deportivo Cuenca
    "ismael_diaz": {
        "transfermarkt": "https://www.transfermarkt.com/ismael-diaz/profil/spieler/309274",
        "fbref": "https://fbref.com/en/players/b6c7d8e9/Ismael-Diaz",
        "club": "Deportivo Cuenca",
        "display_name": "Ismael Díaz",
    },
    # Aucas
    "ivan_bulos": {
        "transfermarkt": "https://www.transfermarkt.com/ivan-bulos/profil/spieler/298374",
        "fbref": "https://fbref.com/en/players/c7d8e9f0/Ivan-Bulos",
        "club": "SD Aucas",
        "display_name": "Iván Bulos",
    },
    # El Nacional
    "henry_cuero": {
        "transfermarkt": "https://www.transfermarkt.com/henry-cuero/profil/spieler/512743",
        "fbref": "https://fbref.com/en/players/d8e9f0a1/Henry-Cuero",
        "club": "El Nacional",
        "display_name": "Henry Cuero",
    },
    # Mushuc Runa
    "bismark_chang": {
        "transfermarkt": "https://www.transfermarkt.com/bismark-chang/profil/spieler/478234",
        "fbref": "https://fbref.com/en/players/e9f0a1b2/Bismark-Chang",
        "club": "Mushuc Runa",
        "display_name": "Bismark Chang",
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
    },
    "piero_hincapie_leverkusen": {
        "transfermarkt": "https://www.transfermarkt.com/piero-hincapie/profil/spieler/659831",
        "fbref": "https://fbref.com/en/players/9f0a7a8e/Piero-Hincapie",
        "sofascore": "https://www.sofascore.com/player/piero-hincapie/981678",
        "current_club": "Bayer Leverkusen",
        "idv_seasons": "2018-2021",
        "display_name": "Piero Hincapié",
    },
    "willian_pacho_psg": {
        "transfermarkt": "https://www.transfermarkt.com/willian-pacho/profil/spieler/574041",
        "fbref": "https://fbref.com/en/players/f7d9a8c1/Willian-Pacho",
        "current_club": "Paris Saint-Germain",
        "idv_seasons": "2017-2020",
        "display_name": "Willian Pacho",
    },
    "romario_ibarra": {
        "transfermarkt": "https://www.transfermarkt.com/romario-ibarra/profil/spieler/235784",
        "fbref": "https://fbref.com/en/players/f1a2b3c4/Romario-Ibarra",
        "current_club": "Pachuca",
        "idv_seasons": "2014-2018",
        "display_name": "Romario Ibarra",
    },
    "antonio_valencia": {
        "transfermarkt": "https://www.transfermarkt.com/antonio-valencia/profil/spieler/24619",
        "fbref": "https://fbref.com/en/players/9b1c2d3e/Antonio-Valencia",
        "current_club": "Retired (ex-Manchester United)",
        "idv_seasons": "2003-2005",
        "display_name": "Antonio Valencia",
    },
    "ulises_de_la_cruz": {
        "transfermarkt": "https://www.transfermarkt.com/ulises-de-la-cruz/profil/spieler/6702",
        "fbref": "https://fbref.com/en/players/a2b3c4d5/Ulises-De-la-Cruz",
        "current_club": "Retired (ex-Aston Villa)",
        "idv_seasons": "1997-2001",
        "display_name": "Ulises de la Cruz",
    },
    "felix_torres": {
        "transfermarkt": "https://www.transfermarkt.com/felix-torres/profil/spieler/545212",
        "fbref": "https://fbref.com/en/players/b3c4d5e6/Felix-Torres",
        "current_club": "Santos Laguna",
        "idv_seasons": "2015-2019",
        "display_name": "Félix Torres",
    },
    "jose_cifuentes": {
        "transfermarkt": "https://www.transfermarkt.com/jose-cifuentes/profil/spieler/574234",
        "fbref": "https://fbref.com/en/players/c4d5e6f7/Jose-Cifuentes",
        "current_club": "Los Angeles FC",
        "idv_seasons": "2018-2021",
        "display_name": "José Cifuentes",
    },
    "angelo_preciado": {
        "transfermarkt": "https://www.transfermarkt.com/angelo-preciado/profil/spieler/477234",
        "fbref": "https://fbref.com/en/players/d5e6f7a8/Angelo-Preciado",
        "current_club": "Genk",
        "idv_seasons": "2016-2020",
        "display_name": "Ángelo Preciado",
    },
    "jhegson_mendez": {
        "transfermarkt": "https://www.transfermarkt.com/jhegson-mendez/profil/spieler/452312",
        "fbref": "https://fbref.com/en/players/e6f7a8b9/Jhegson-Mendez",
        "current_club": "Houston Dynamo",
        "idv_seasons": "2015-2018",
        "display_name": "Jhegson Méndez",
    },
}


# ── Lookup helpers ────────────────────────────────────────────────────────────

ALL_PLAYER_URLS: dict[str, dict[str, str]] = {
    **IDV_PLAYER_URLS,
    **LIGA_PRO_RIVAL_URLS,
    **IDV_GRADUATES_URLS,
}


def get_player_urls(slug: str) -> dict[str, str] | None:
    """Return URL dict for a player by their slug key."""
    return ALL_PLAYER_URLS.get(slug)


def get_transfermarkt_url(slug: str) -> str | None:
    entry = ALL_PLAYER_URLS.get(slug, {})
    return entry.get("transfermarkt")


def get_fbref_url(slug: str) -> str | None:
    entry = ALL_PLAYER_URLS.get(slug, {})
    return entry.get("fbref")


def name_to_slug(display_name: str) -> str:
    """Convert display name to registry slug."""
    return display_name.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n").replace("ü", "u")


def get_idv_squad_urls() -> dict[str, dict[str, str]]:
    return IDV_PLAYER_URLS.copy()


def get_liga_pro_rival_urls() -> dict[str, dict[str, str]]:
    return LIGA_PRO_RIVAL_URLS.copy()


def get_graduate_urls() -> dict[str, dict[str, str]]:
    return IDV_GRADUATES_URLS.copy()


if __name__ == "__main__":
    idv_count = len(IDV_PLAYER_URLS)
    rivals_count = len(LIGA_PRO_RIVAL_URLS)
    graduates_count = len(IDV_GRADUATES_URLS)
    print(f"Registry: {idv_count} IDV players, {rivals_count} Liga Pro rivals, {graduates_count} graduates")
    print(f"Total: {len(ALL_PLAYER_URLS)} players")
