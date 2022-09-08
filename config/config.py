import os

__VERSION__ = '1.4.1'
__APPNAME__ = 'Shopee Crawler'


CATEGORY_ID_MAP = {
    'Celulares y Gadgets': 11069113,
    'Electrodomésticos': 11069114,
    'Bolsas de Hombre': 11069106,
    'Viajes y Equipaje': 11069108,
    'Calzado de Mujer': 11069110,
    'Videojuegos': 11069112,
    'Joyas y Relojes': 11069101,
    'Belleza': 11069094,
    'Ropa de Mujer': 11069111,
    'Deportes y Fitness': 11069096,
    'Computación': 11069107,
    'Juguetes y Hobbies': 11069098,
    'Accesorios para Vehículos': 11069117,
    'Papelería': 11069116,
    'Ropa de Hombre': 11069104,
    'Calzado de Hombre': 11069105,
    'Bolsos de Mujer': 11069109,
    'Mascotas': 11069095,
    'Salud': 11069099,
    'Tecnología': 11069115,
    'Herramientas para el hogar': 11115402,
    'Moda para Bebés y Niños': 11069100,
    'Madre y Bebé': 11069097,
    'Accesorios de Moda': 11069102,
    'Hogar y Vida': 11069103
}

SORT_MAP = {
    'Ascending': 'asc',
    'Descending': 'desc'
}

LOCATION_MAP = {
    'Internacional': 'Internacional',
    'Vendedor Nacional': 'Vendedor Nacional',
    'Both': 'Internacional,Vendedor Nacional'
}

FILTER_MAP = {
    'Relevancia': 'relevancy',
    'Último': 'ctime',
    'Top Ventas': 'sales',
    'Precio': 'price'
}

BASE_URL = 'https://shopee.com.co/api/v4/search/search_items'
IMAGE_BASE_URL = 'https://cf.shopee.com.co/file/'
CRAWL_PARAMS = {
    'by': 'price',
    'keyword': 'iphone 11',
    'limit': 60,
    'locations': 'Internacional',
    'match_id': 11069113,
    'newest': 0,
    'order': 'asc',
    'page_type': 'search',
    'scenario': 'PAGE_CATEGORY_SEARCH',
    'skip_autocorrect': 1,
    'version': 2
}

# CATEGORY_ID_MAP = {
#     11069113: {
#         'es': 'Celulares y Gadgets',
#         'en': ''
#     },
#     11069114: {
#         'es': 'Electrodomésticos',
#         'en': ''
#     },
#     11069106: {
#         'es': 'Bolsas de Hombre',
#         'en': ''
#     },
#     11069108: {
#         'es': 'Viajes y Equipaje',
#         'en': ''
#     },
#     11069110: {
#         'es': 'Calzado de Mujer',
#         'en': ''
#     },
#     11069112: {
#         'es': 'Videojuegos',
#         'en': '',
#     },
#     11069101: {
#         'es': 'Joyas y Relojes',
#         'en': ''
#     },
#     11069094: {
#         'es': 'Belleza',
#         'en': ''
#     },
#     11069111: {
#         'es': 'Ropa de Mujer',
#         'en': ''
#     },
#     11069096: {
#         'es': 'Deportes y Fitness',
#         'en': ''
#     },
#     11069107: {
#         'es': 'Computación',
#         'en': ''
#     },
#     11069098: {
#         'es': 'Juguetes y Hobbies',
#         'en': ''
#     },
#     11069117: {
#         'es': 'Accesorios para Vehículos',
#         'en': ''
#     },
#     11069116: {
#         'es': 'Papelería',
#         'en': ''
#     },
#     11069104: {
#         'es': 'Ropa de Hombre',
#         'en': ''
#     },
#     11069105: {
#         'es': 'Calzado de Hombre',
#         'en': ''
#     },
#     11069109: {
#         'es': 'Bolsos de Mujer',
#         'en': ''
#     },
#     11069095: {
#         'es': 'Mascotas',
#         'en': ''
#     },
#     11069099: {
#         'es': 'Salud',
#         'en': ''
#     },
#     11069115: {
#         'es': 'Tecnología',
#         'en': ''
#     },
#     11115402: {
#         'es': 'Herramientas para el hogar',
#         'en': ''
#     },
#     11069100: {
#         'es': 'Moda para Bebés y Niños',
#         'en': ''
#     },
#     11069097: {
#         'es': 'Madre y Bebé',
#         'en': ''
#     },
#     11069102: {
#         'es': 'Accesorios de Moda',
#         'en': ''
#     },
#     11069103: {
#         'es': 'Hogar y Vida',
#         'en': ''
#     }
# }