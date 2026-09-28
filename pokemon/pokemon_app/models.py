from django.db import models

# Create your models here.

class PokemonSprites(models.Model):
    front_default = models.URLField()
    back_default = models.URLField()
    front_shiny = models.URLField()
    back_shiny = models.URLField()

    def __str__(self):
        return self.front_default

class Pokemon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    height = models.IntegerField()
    weight = models.IntegerField()
    order = models.IntegerField()
    type_1 = models.CharField(max_length=20, blank=True, default="")
    type_2 = models.CharField(max_length=20, blank=True, default="")
    base_experience = models.PositiveIntegerField(default=0)
    sprites = models.ForeignKey(PokemonSprites, on_delete=models.CASCADE)

    def __str__(self):
        return self.name