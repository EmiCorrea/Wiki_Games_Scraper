from scrapy.item import Item, Field

class GameItem(Item):
    Nombre = Field()
    Img_URL = Field()
    Distribuidoras = Field()
    Desarrolladores = Field()
    Artistas = Field()
    Compositores = Field()
    Plataformas = Field()
    Generos = Field()
    Modos = Field()
    MainPageUrl = Field()
    Lanzamiento = Field()