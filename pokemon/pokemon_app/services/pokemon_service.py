import  requests
from ..models import PokemonSprites, Pokemon

API_URL = "https://pokeapi.co/api/v2/pokemon/"


def get_pokemon(name):
    response = requests.get(f"{API_URL}{name}")
    if response.status_code != 200:
        return None
    return response.json()

#sin limites al cargar
def get_pokemons(offset=0, limit=100):
    pokemons = []
    url = API_URL
    params = {"offset": offset, "limit": limit}

    while url:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return None

        data = response.json()
        pokemons.extend(data.get("results", []))

        url = data.get("next")
        params = None  # La URL de la página siguiente ya incluye sus parámetros.

    return pokemons


def load_pokemons():
    pokemon_responses = get_pokemons()
    if pokemon_responses is None:
        return f"No se pudieron cargar los Pokemons: {Pokemon.objects.count()}"

    for pr in pokemon_responses:
        name = pr.get("name")
        if not name:
            continue

        pokemon = get_pokemon(name)
        if not pokemon:
            continue 
        types = pokemon.get("types") or []
        sprites_data = pokemon.get("sprites") or {}
        sprites, __ = PokemonSprites.objects.get_or_create(
            front_default=sprites_data.get("front_default") or "",
            back_default=sprites_data.get("back_default") or "",
            front_shiny=sprites_data.get("front_shiny") or "",
            back_shiny=sprites_data.get("back_shiny") or "",
        )

        Pokemon.objects.update_or_create(
            id=pokemon.get("id"),
            defaults={
                "name": pokemon.get("name"),
                "height": pokemon.get("height"),
                "weight": pokemon.get("weight"),
                "order": pokemon.get("order"),
                "type_1": types[0].get("type", {}).get("name", "") if types else "",
                "type_2": types[1].get("type", {}).get("name", "") if len(types) > 1 else "",
                "base_experience": pokemon.get("base_experience") or 0,
                "sprites": sprites,
            },
        )
    return f"Pokemons cargados: {Pokemon.objects.count()}"