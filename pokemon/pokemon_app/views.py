from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PokemonForm, PokemonSpritesForm
from .models import Pokemon, PokemonSprites

# Create your views here.
def pokemon_list(request):
	search_term = request.GET.get("q", "").strip()
	pokemon_list = Pokemon.objects.select_related("sprites").order_by("id")
	if search_term:
		pokemon_list = pokemon_list.filter(name__icontains=search_term)

	paginator = Paginator(pokemon_list, 20)
	page_obj = paginator.get_page(request.GET.get("page"))
	page_range = range(
		max(1, page_obj.number - 2),
		min(page_obj.paginator.num_pages, page_obj.number + 2) + 1,
	)
	return render(
		request,
		"pokemon/pokemon_list.html",
		{
			"page_obj": page_obj,
			"pokemons": page_obj.object_list,
			"page_range": page_range,
			"search_term": search_term,
		},
	)

def pokemon_details(request, id):
	pokemon = get_object_or_404(Pokemon, id=id)
	return render(request, "pokemon/pokemon_details.html", {"pokemon":pokemon})

def pokemon_create(request):
	if request.method == "POST":
		form = PokemonForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("pokemon_list")
	else:
		form = PokemonForm()
	return render(request, "pokemon/pokemon_form.html", {"form": form, "title": "Agregar Pokémon"})

def pokemon_edit(request, id):
	pokemon = get_object_or_404(Pokemon, id=id)
	if request.method == "POST":
		form = PokemonForm(request.POST, instance=pokemon)
		if form.is_valid():
			form.save()
			return redirect("pokemon_list")
	else:
		form = PokemonForm(instance=pokemon)
	return render(request, "pokemon/pokemon_form.html", {"form": form, "title": "Editar Pokémon"})

def pokemon_delete(request, id):
	pokemon = get_object_or_404(Pokemon, id=id)
	if request.method == "POST":
		pokemon.delete()
		return redirect("pokemon_list")
	return render(request, "pokemon/confirm_delete.html", {
		"object_name": pokemon.name,
		"cancel_url": "pokemon_list",
	})

def pokemon_sprites_list(request):
	sprites = PokemonSprites.objects.all().order_by("id")
	return render(request, "pokemon/sprites_list.html", {"sprites_list": sprites})

def pokemon_sprites_create(request):
	if request.method == "POST":
		form = PokemonSpritesForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("pokemon_sprites_list")
	else:
		form = PokemonSpritesForm()
	return render(request, "pokemon/sprites_form.html", {"form": form, "title": "Agregar sprites"})

def pokemon_sprites_edit(request, id):
	sprites = get_object_or_404(PokemonSprites, id=id)
	if request.method == "POST":
		form = PokemonSpritesForm(request.POST, instance=sprites)
		if form.is_valid():
			form.save()
			return redirect("pokemon_sprites_list")
	else:
		form = PokemonSpritesForm(instance=sprites)
	return render(request, "pokemon/sprites_form.html", {"form": form, "title": "Editar sprites"})

def pokemon_sprites_delete(request, id):
	sprites = get_object_or_404(PokemonSprites, id=id)
	linked_pokemons = Pokemon.objects.filter(sprites=sprites)
	if request.method == "POST" and not linked_pokemons.exists():
		sprites.delete()
		return redirect("pokemon_sprites_list")
	return render(request, "pokemon/confirm_delete.html", {
		"object_name": f"sprites #{sprites.id}",
		"cancel_url": "pokemon_sprites_list",
		"linked_pokemons": linked_pokemons,
	})
	
