from django.urls import path

from . import views

urlpatterns = [
    path("", views.pokemon_list, name="pokemon_list"),
    path("pokemon/nuevo/", views.pokemon_create, name="pokemon_create"),
    path("pokemon/<int:id>/editar/", views.pokemon_edit, name="pokemon_edit"),
    path("pokemon/<int:id>/eliminar/", views.pokemon_delete, name="pokemon_delete"),
    path("sprites/", views.pokemon_sprites_list, name="pokemon_sprites_list"),
    path("sprites/nuevo/", views.pokemon_sprites_create, name="pokemon_sprites_create"),
    path("sprites/<int:id>/editar/", views.pokemon_sprites_edit, name="pokemon_sprites_edit"),
    path("sprites/<int:id>/eliminar/", views.pokemon_sprites_delete, name="pokemon_sprites_delete"),
    path("<int:id>", views.pokemon_details, name="pokemon_details"),
]