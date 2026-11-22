"""Herramientas del agente de música de los años 80.

Catálogo de canciones reales publicadas entre 1980 y 1989, con solo
metadatos (título, artista, año, categoría y país de origen). No se
incluyen letras ni enlaces.
"""

from __future__ import annotations

from langchain_core.tools import tool


# Información de los artistas del catálogo.
ARTISTAS: dict[str, dict[str, str]] = {
    "Michael Jackson": {
        "pais": "Estados Unidos",
        "estilo": "pop",
        "actividad_80s": "1979-1989",
    },
    "Madonna": {
        "pais": "Estados Unidos",
        "estilo": "pop",
        "actividad_80s": "1982-1989",
    },
    "Prince": {
        "pais": "Estados Unidos",
        "estilo": "pop / funk",
        "actividad_80s": "1978-1989",
    },
    "The Police": {
        "pais": "Reino Unido",
        "estilo": "new wave / rock",
        "actividad_80s": "1977-1986",
    },
    "Duran Duran": {
        "pais": "Reino Unido",
        "estilo": "new wave / synth-pop",
        "actividad_80s": "1978-1989",
    },
    "Depeche Mode": {
        "pais": "Reino Unido",
        "estilo": "synth-pop",
        "actividad_80s": "1980-1989",
    },
    "U2": {
        "pais": "Irlanda",
        "estilo": "rock",
        "actividad_80s": "1976-1989",
    },
    "Queen": {
        "pais": "Reino Unido",
        "estilo": "rock",
        "actividad_80s": "1970-1989",
    },
    "Bon Jovi": {
        "pais": "Estados Unidos",
        "estilo": "hard rock",
        "actividad_80s": "1983-1989",
    },
    "Metallica": {
        "pais": "Estados Unidos",
        "estilo": "metal",
        "actividad_80s": "1981-1989",
    },
    "Los Prisioneros": {
        "pais": "Chile",
        "estilo": "rock en español / new wave",
        "actividad_80s": "1983-1989",
    },
    "Soda Stereo": {
        "pais": "Argentina",
        "estilo": "rock en español",
        "actividad_80s": "1982-1989",
    },
}


# Catálogo de canciones (solo metadatos).
CANCIONES: list[dict] = [
    # Pop
    {"titulo": "Billie Jean", "artista": "Michael Jackson", "año": 1982, "categoria": "pop", "pais": "Estados Unidos"},
    {"titulo": "Thriller", "artista": "Michael Jackson", "año": 1982, "categoria": "pop", "pais": "Estados Unidos"},
    {"titulo": "Beat It", "artista": "Michael Jackson", "año": 1982, "categoria": "pop", "pais": "Estados Unidos"},
    {"titulo": "Like a Virgin", "artista": "Madonna", "año": 1984, "categoria": "pop", "pais": "Estados Unidos"},
    {"titulo": "Material Girl", "artista": "Madonna", "año": 1984, "categoria": "pop", "pais": "Estados Unidos"},
    {"titulo": "Purple Rain", "artista": "Prince", "año": 1984, "categoria": "pop", "pais": "Estados Unidos"},
    {"titulo": "When Doves Cry", "artista": "Prince", "año": 1984, "categoria": "pop", "pais": "Estados Unidos"},
    # Baladas
    {"titulo": "Crazy for You", "artista": "Madonna", "año": 1985, "categoria": "baladas", "pais": "Estados Unidos"},
    {"titulo": "Human Nature", "artista": "Michael Jackson", "año": 1982, "categoria": "baladas", "pais": "Estados Unidos"},
    {"titulo": "Who Wants to Live Forever", "artista": "Queen", "año": 1986, "categoria": "baladas", "pais": "Reino Unido"},
    {"titulo": "Trátame suavemente", "artista": "Soda Stereo", "año": 1985, "categoria": "baladas", "pais": "Argentina"},
    # Bailable
    {"titulo": "Into the Groove", "artista": "Madonna", "año": 1985, "categoria": "bailable", "pais": "Estados Unidos"},
    {"titulo": "Wanna Be Startin' Somethin'", "artista": "Michael Jackson", "año": 1982, "categoria": "bailable", "pais": "Estados Unidos"},
    {"titulo": "1999", "artista": "Prince", "año": 1982, "categoria": "bailable", "pais": "Estados Unidos"},
    # New wave
    {"titulo": "Don't Stand So Close to Me", "artista": "The Police", "año": 1980, "categoria": "new wave", "pais": "Reino Unido"},
    {"titulo": "Every Little Thing She Does Is Magic", "artista": "The Police", "año": 1981, "categoria": "new wave", "pais": "Reino Unido"},
    {"titulo": "Hungry Like the Wolf", "artista": "Duran Duran", "año": 1982, "categoria": "new wave", "pais": "Reino Unido"},
    {"titulo": "Rio", "artista": "Duran Duran", "año": 1982, "categoria": "new wave", "pais": "Reino Unido"},
    # Synth-pop
    {"titulo": "Just Can't Get Enough", "artista": "Depeche Mode", "año": 1981, "categoria": "synth-pop", "pais": "Reino Unido"},
    {"titulo": "People Are People", "artista": "Depeche Mode", "año": 1984, "categoria": "synth-pop", "pais": "Reino Unido"},
    {"titulo": "Never Let Me Down Again", "artista": "Depeche Mode", "año": 1987, "categoria": "synth-pop", "pais": "Reino Unido"},
    # Rock
    {"titulo": "With or Without You", "artista": "U2", "año": 1987, "categoria": "rock", "pais": "Irlanda"},
    {"titulo": "Sunday Bloody Sunday", "artista": "U2", "año": 1983, "categoria": "rock", "pais": "Irlanda"},
    {"titulo": "Radio Ga Ga", "artista": "Queen", "año": 1984, "categoria": "rock", "pais": "Reino Unido"},
    {"titulo": "I Want to Break Free", "artista": "Queen", "año": 1984, "categoria": "rock", "pais": "Reino Unido"},
    # Hard rock y metal
    {"titulo": "Livin' on a Prayer", "artista": "Bon Jovi", "año": 1986, "categoria": "hard rock y metal", "pais": "Estados Unidos"},
    {"titulo": "You Give Love a Bad Name", "artista": "Bon Jovi", "año": 1986, "categoria": "hard rock y metal", "pais": "Estados Unidos"},
    {"titulo": "Master of Puppets", "artista": "Metallica", "año": 1986, "categoria": "hard rock y metal", "pais": "Estados Unidos"},
    {"titulo": "One", "artista": "Metallica", "año": 1988, "categoria": "hard rock y metal", "pais": "Estados Unidos"},
    # Rock en español
    {"titulo": "La voz de los '80", "artista": "Los Prisioneros", "año": 1984, "categoria": "rock en español", "pais": "Chile"},
    {"titulo": "El baile de los que sobran", "artista": "Los Prisioneros", "año": 1986, "categoria": "rock en español", "pais": "Chile"},
    {"titulo": "Nada personal", "artista": "Soda Stereo", "año": 1985, "categoria": "rock en español", "pais": "Argentina"},
    {"titulo": "Persiana americana", "artista": "Soda Stereo", "año": 1986, "categoria": "rock en español", "pais": "Argentina"},
]


def _normalizar(texto: str) -> str:
    return (texto or "").strip().lower()


@tool
def buscar_canciones(consulta: str) -> list[dict]:
    """Busca canciones por título o artista en el catálogo ochentero.

    consulta: texto a buscar (título o artista). Devuelve una lista de
    canciones con metadatos. Si no hay coincidencias, devuelve lista vacía.
    """
    clave = _normalizar(consulta)
    if not clave:
        return []
    resultados: list[dict] = []
    for cancion in CANCIONES:
        titulo = _normalizar(cancion["titulo"])
        artista = _normalizar(cancion["artista"])
        if clave in titulo or clave in artista or titulo in clave or artista in clave:
            resultados.append(dict(cancion))
    return resultados


@tool
def buscar_artista(nombre: str) -> dict:
    """Devuelve la ficha del artista y sus canciones del catálogo.

    nombre: nombre del artista. Si no está en el catálogo, devuelve un
    diccionario vacío.
    """
    clave = _normalizar(nombre)
    if not clave:
        return {}
    artista_encontrado = None
    for nombre_artista, datos in ARTISTAS.items():
        if clave in _normalizar(nombre_artista) or _normalizar(nombre_artista) in clave:
            artista_encontrado = (nombre_artista, datos)
            break
    if artista_encontrado is None:
        return {}
    nombre_artista, datos = artista_encontrado
    canciones = [dict(c) for c in CANCIONES if _normalizar(c["artista"]) == _normalizar(nombre_artista)]
    return {
        "nombre": nombre_artista,
        "pais": datos["pais"],
        "estilo": datos["estilo"],
        "actividad_80s": datos["actividad_80s"],
        "canciones": canciones,
    }


@tool
def listar_por_categoria(categoria: str, cantidad: int) -> list[dict]:
    """Lista canciones de una categoría, hasta la cantidad solicitada.

    categoria: categoría (pop, rock, new wave, synth-pop, baladas, hard rock
    y metal, bailable, rock en español). cantidad: máximo de canciones a
    devolver. Devuelve lista vacía si no hay coincidencias.
    """
    cat = _normalizar(categoria)
    try:
        limite = int(cantidad)
    except (TypeError, ValueError):
        return []
    if limite <= 0 or not cat:
        return []
    resultados: list[dict] = []
    for cancion in CANCIONES:
        if _normalizar(cancion["categoria"]) == cat:
            resultados.append(dict(cancion))
            if len(resultados) >= limite:
                break
    return resultados


@tool
def sugerir_cancion(interes: str) -> list[dict]:
    """Sugiere una o dos canciones adecuadas al interés del usuario.

    interes: texto libre con el gusto o interés. Devuelve hasta dos canciones
    del catálogo. Si no hay coincidencia, devuelve lista vacía.
    """
    texto = _normalizar(interes)
    if not texto:
        return []

    # Mapa de palabras clave a categoría.
    mapa_categoria = [
        ("synth", "synth-pop"),
        ("synth-pop", "synth-pop"),
        ("new wave", "new wave"),
        ("metal", "hard rock y metal"),
        ("hard rock", "hard rock y metal"),
        ("balada", "baladas"),
        ("bailable", "bailable"),
        ("bailar", "bailable"),
        ("pop", "pop"),
        ("rock en español", "rock en español"),
        ("español", "rock en español"),
        ("latino", "rock en español"),
        ("chile", "rock en español"),
        ("rock", "rock"),
    ]

    categoria_destino = None
    for palabra, cat in mapa_categoria:
        if palabra in texto:
            categoria_destino = cat
            break

    # Si menciona un artista, priorizar sus canciones.
    artista_destino = None
    for nombre_artista in ARTISTAS:
        if _normalizar(nombre_artista) in texto:
            artista_destino = nombre_artista
            break

    candidatos: list[dict] = []
    if artista_destino is not None:
        candidatos = [dict(c) for c in CANCIONES if _normalizar(c["artista"]) == _normalizar(artista_destino)]
    elif categoria_destino is not None:
        candidatos = [dict(c) for c in CANCIONES if _normalizar(c["categoria"]) == categoria_destino]

    return candidatos[:2]
