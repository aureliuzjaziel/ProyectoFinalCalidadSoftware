from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from .models import Pokemon, PokemonSprites
from .services.pokemon_service import get_pokemons, load_pokemons

# Create your tests here.


class LoadPokemonsTests(TestCase):
	@patch("pokemon_app.services.pokemon_service.requests.get")
	def test_get_pokemons_follows_all_api_pages(self, requests_get_mock):
		next_page_url = "https://pokeapi.co/api/v2/pokemon/?offset=100&limit=100"
		first_page = Mock(status_code=200)
		first_page.json.return_value = {
			"results": [{"name": "bulbasaur"}],
			"next": next_page_url,
		}
		last_page = Mock(status_code=200)
		last_page.json.return_value = {
			"results": [{"name": "ivysaur"}],
			"next": None,
		}
		requests_get_mock.side_effect = [first_page, last_page]

		result = get_pokemons()

		self.assertEqual(result, [{"name": "bulbasaur"}, {"name": "ivysaur"}])
		self.assertEqual(requests_get_mock.call_count, 2)

	@patch("pokemon_app.services.pokemon_service.get_pokemon")
	@patch("pokemon_app.services.pokemon_service.get_pokemons")
	def test_updates_existing_and_creates_missing_pokemons(
		self, get_pokemons_mock, get_pokemon_mock
	):
		existing_sprites = PokemonSprites.objects.create(
			front_default="https://example.com/existing-front.png",
			back_default="https://example.com/existing-back.png",
			front_shiny="https://example.com/existing-front-shiny.png",
			back_shiny="https://example.com/existing-back-shiny.png",
		)
		Pokemon.objects.create(
			id=1,
			name="bulbasaur",
			height=7,
			weight=69,
			order=1,
			sprites=existing_sprites,
		)
		get_pokemons_mock.return_value = [
			{"name": "bulbasaur"},
			{"name": "ivysaur"},
		]
		get_pokemon_mock.side_effect = [
			{
				"id": 1,
				"name": "bulbasaur",
				"height": 7,
				"weight": 69,
				"order": 1,
				"base_experience": 64,
				"types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
				"sprites": {
					"front_default": "https://example.com/bulbasaur-front.png",
					"back_default": "https://example.com/bulbasaur-back.png",
					"front_shiny": "https://example.com/bulbasaur-front-shiny.png",
					"back_shiny": "https://example.com/bulbasaur-back-shiny.png",
				},
			},
			{
				"id": 2,
				"name": "ivysaur",
				"height": 10,
				"weight": 130,
				"order": 2,
				"base_experience": 142,
				"types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
				"sprites": {
					"front_default": "https://example.com/ivysaur-front.png",
					"back_default": "https://example.com/ivysaur-back.png",
					"front_shiny": "https://example.com/ivysaur-front-shiny.png",
					"back_shiny": "https://example.com/ivysaur-back-shiny.png",
				},
			},
		]

		result = load_pokemons()

		self.assertEqual(Pokemon.objects.count(), 2)
		self.assertEqual(result, "Pokemons cargados: 2")
		self.assertEqual(get_pokemon_mock.call_count, 2)
		bulbasaur = Pokemon.objects.get(id=1)
		self.assertEqual(bulbasaur.type_1, "grass")
		self.assertEqual(bulbasaur.type_2, "poison")
		self.assertEqual(bulbasaur.base_experience, 64)


class PokemonListViewTests(TestCase):
	def test_search_filters_pokemon_names_without_case_sensitivity(self):
		sprites = PokemonSprites.objects.create(
			front_default="https://example.com/search-front.png",
			back_default="https://example.com/search-back.png",
			front_shiny="https://example.com/search-front-shiny.png",
			back_shiny="https://example.com/search-back-shiny.png",
		)
		Pokemon.objects.create(
			name="Pikachu",
			height=4,
			weight=60,
			order=25,
			sprites=sprites,
		)
		Pokemon.objects.create(
			name="Raichu",
			height=8,
			weight=300,
			order=26,
			sprites=sprites,
		)

		response = self.client.get(reverse("pokemon_list"), {"q": "PIKA"})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["search_term"], "PIKA")
		self.assertEqual(
			list(response.context["pokemons"].values_list("name", flat=True)),
			["Pikachu"],
		)
		self.assertContains(response, "PIKA")

	def test_page_query_displays_the_requested_pokemon_page(self):
		sprites = PokemonSprites.objects.create(
			front_default="https://example.com/pokemon.png",
			back_default="https://example.com/pokemon-back.png",
			front_shiny="https://example.com/pokemon-shiny.png",
			back_shiny="https://example.com/pokemon-back-shiny.png",
		)
		Pokemon.objects.bulk_create([
				Pokemon(
					id=pokemon_id,
					name=f"pokemon-{pokemon_id}",
					height=10,
					weight=100,
					order=pokemon_id,
					sprites=sprites,
				)
				for pokemon_id in range(1, 22)
		])

		response = self.client.get(reverse("pokemon_list"), {"page": 2})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["page_obj"].number, 2)
		self.assertContains(response, "pokemon-21")
		self.assertNotContains(response, "pokemon-1</h2>")
		self.assertContains(response, '?page=1')


class PokemonCrudTests(TestCase):
	def setUp(self):
		self.sprites = PokemonSprites.objects.create(
			front_default="https://example.com/front.png",
			back_default="https://example.com/back.png",
			front_shiny="https://example.com/front-shiny.png",
			back_shiny="https://example.com/back-shiny.png",
		)
		self.pokemon = Pokemon.objects.create(
			name="bulbasaur",
			height=7,
			weight=69,
			order=1,
			type_1="grass",
			type_2="poison",
			base_experience=64,
			sprites=self.sprites,
		)

	def test_create_and_edit_pokemon(self):
		response = self.client.post(reverse("pokemon_create"), {
			"name": "ivysaur",
			"height": 10,
			"weight": 130,
			"order": 2,
			"type_1": "grass",
			"type_2": "poison",
			"base_experience": 142,
			"sprites": self.sprites.id,
		})
		self.assertRedirects(response, reverse("pokemon_list"))
		ivysaur = Pokemon.objects.get(name="ivysaur")

		response = self.client.post(reverse("pokemon_edit", args=[ivysaur.id]), {
			"name": "ivysaur-updated",
			"height": 10,
			"weight": 130,
			"order": 2,
			"type_1": "grass",
			"type_2": "poison",
			"base_experience": 150,
			"sprites": self.sprites.id,
		})
		self.assertRedirects(response, reverse("pokemon_list"))
		ivysaur.refresh_from_db()
		self.assertEqual(ivysaur.name, "ivysaur-updated")
		self.assertEqual(ivysaur.base_experience, 150)

	def test_delete_pokemon(self):
		response = self.client.post(reverse("pokemon_delete", args=[self.pokemon.id]))
		self.assertRedirects(response, reverse("pokemon_list"))
		self.assertFalse(Pokemon.objects.filter(id=self.pokemon.id).exists())

	def test_create_and_edit_sprites(self):
		response = self.client.post(reverse("pokemon_sprites_create"), {
			"front_default": "https://example.com/other-front.png",
			"back_default": "https://example.com/other-back.png",
			"front_shiny": "https://example.com/other-front-shiny.png",
			"back_shiny": "https://example.com/other-back-shiny.png",
		})
		self.assertRedirects(response, reverse("pokemon_sprites_list"))
		new_sprites = PokemonSprites.objects.get(front_default="https://example.com/other-front.png")

		response = self.client.post(reverse("pokemon_sprites_edit", args=[new_sprites.id]), {
			"front_default": "https://example.com/changed-front.png",
			"back_default": "https://example.com/other-back.png",
			"front_shiny": "https://example.com/other-front-shiny.png",
			"back_shiny": "https://example.com/other-back-shiny.png",
		})
		self.assertRedirects(response, reverse("pokemon_sprites_list"))
		new_sprites.refresh_from_db()
		self.assertEqual(new_sprites.front_default, "https://example.com/changed-front.png")

	def test_cannot_delete_sprites_used_by_pokemon(self):
		response = self.client.post(reverse("pokemon_sprites_delete", args=[self.sprites.id]))
		self.assertEqual(response.status_code, 200)
		self.assertTrue(PokemonSprites.objects.filter(id=self.sprites.id).exists())
		self.assertContains(response, "No se pueden eliminar estos sprites")

	def test_delete_unused_sprites(self):
		unused_sprites = PokemonSprites.objects.create(
			front_default="https://example.com/unused-front.png",
			back_default="https://example.com/unused-back.png",
			front_shiny="https://example.com/unused-front-shiny.png",
			back_shiny="https://example.com/unused-back-shiny.png",
		)
		response = self.client.post(reverse("pokemon_sprites_delete", args=[unused_sprites.id]))
		self.assertRedirects(response, reverse("pokemon_sprites_list"))
		self.assertFalse(PokemonSprites.objects.filter(id=unused_sprites.id).exists())
