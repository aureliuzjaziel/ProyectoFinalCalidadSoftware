from django import forms

from .models import Pokemon, PokemonSprites


class PokemonForm(forms.ModelForm):
    class Meta:
        model = Pokemon
        fields = (
            "name",
            "height",
            "weight",
            "order",
            "type_1",
            "type_2",
            "base_experience",
            "sprites",
        )
        labels = {
            "name": "Nombre",
            "height": "Altura (dm)",
            "weight": "Peso (hg)",
            "order": "Orden en la Pokédex",
            "type_1": "Tipo principal",
            "type_2": "Tipo secundario",
            "base_experience": "Experiencia base",
            "sprites": "Sprites",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            )


class PokemonSpritesForm(forms.ModelForm):
    class Meta:
        model = PokemonSprites
        fields = ("front_default", "back_default", "front_shiny", "back_shiny")
        labels = {
            "front_default": "Imagen frontal",
            "back_default": "Imagen trasera",
            "front_shiny": "Imagen frontal variocolor",
            "back_shiny": "Imagen trasera variocolor",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"