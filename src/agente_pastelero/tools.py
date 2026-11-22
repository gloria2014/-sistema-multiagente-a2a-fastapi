"""Herramientas del agente pastelero con catálogo ampliado de repostería."""

from __future__ import annotations

from langchain_core.tools import tool


RECETAS: dict[str, dict[str, str]] = {
    "torta de chocolate": {
        "categoria": "chocolate, tortas, horno",
        "ingredientes": (
            "200 g de chocolate amargo, 200 g de mantequilla, 4 huevos, "
            "200 g de azúcar, 100 g de harina, 1 cucharadita de polvo de hornear."
        ),
        "tiempo": "Preparación 20 min, horneado 35 min a 180 °C.",
        "tecnica": (
            "Derretir el chocolate con la mantequilla a baño maría. Batir huevos "
            "con azúcar hasta blanquear, incorporar el chocolate, luego la harina "
            "tamizada. Hornear en molde enmantequillado."
        ),
    },
    "brownie": {
        "categoria": "chocolate, pastelitos, horno",
        "ingredientes": (
            "200 g de chocolate, 150 g de mantequilla, 3 huevos, 200 g de azúcar, "
            "80 g de harina, 30 g de cacao, 1 pizca de sal."
        ),
        "tiempo": "Preparación 15 min, horneado 25 min a 175 °C.",
        "tecnica": (
            "Derretir chocolate y mantequilla. Mezclar con huevos y azúcar sin "
            "batir en exceso, agregar harina, cacao y sal. Hornear hasta que el "
            "centro esté apenas cuajado para que quede húmedo."
        ),
    },
    "mousse de chocolate": {
        "categoria": "chocolate, postres frios, sin horno",
        "ingredientes": (
            "200 g de chocolate, 3 huevos, 50 g de azúcar, 200 ml de crema de leche."
        ),
        "tiempo": "Preparación 20 min, refrigeración 4 horas.",
        "tecnica": (
            "Derretir el chocolate. Separar claras y yemas: mezclar yemas con el "
            "chocolate, batir claras a nieve con azúcar e incorporar, luego la crema "
            "batida. Refrigerar hasta cuajar."
        ),
    },
    "volcan de chocolate": {
        "categoria": "chocolate, postres calientes, horno, coulant",
        "ingredientes": (
            "150 g de chocolate semiamargo, 150 g de mantequilla, 3 huevos, "
            "3 yemas, 80 g de azúcar flor, 50 g de harina."
        ),
        "tiempo": "Preparación 15 min, horneado 10 a 12 min a 200 °C.",
        "tecnica": (
            "Fundir chocolate y mantequilla. Batir huevos, yemas y azúcar, unir "
            "con el chocolate e integrar la harina. Verter en ramequines enmantequillados "
            "y espolvoreados con cacao. Hornear hasta que los bordes estén firmes y el centro líquido."
        ),
    },
    "trufas de chocolate": {
        "categoria": "chocolate, bombones, sin horno, facil",
        "ingredientes": (
            "250 g de chocolate amargo picado, 150 ml de crema de leche espesa, "
            "20 g de mantequilla, 40 g de cacao amargo en polvo para rebozar."
        ),
        "tiempo": "Preparación 15 min, refrigeración 2 horas.",
        "tecnica": (
            "Calentar la crema hasta casi hervir y volcar sobre el chocolate picado "
            "y la mantequilla. Reposar 2 minutos y emulsionar hasta lograr una ganache "
            "lisa. Refrigerar 2 horas, formar bolitas y pasar por cacao en polvo."
        ),
    },
    "cupcake de vainilla": {
        "categoria": "vainilla, pastelitos, horno, decoracion",
        "ingredientes": (
            "125 g de mantequilla, 125 g de azúcar, 2 huevos, 125 g de harina, "
            "1 cucharadita de polvo de hornear, 1 cucharadita de esencia de vainilla, "
            "60 ml de leche."
        ),
        "tiempo": "Preparación 15 min, horneado 18 min a 180 °C.",
        "tecnica": (
            "Batir mantequilla con azúcar, agregar huevos de a uno, luego los secos "
            "alternando con la leche. Rellenar moldes hasta 2/3 y hornear."
        ),
    },
    "galletas de mantequilla": {
        "categoria": "galletas, masas dulces, horno, mantequilla",
        "ingredientes": (
            "250 g de mantequilla, 125 g de azúcar glas, 1 huevo, 350 g de harina, "
            "1 cucharadita de esencia de vainilla."
        ),
        "tiempo": "Preparación 20 min, refrigerado 30 min, horneado 12 min a 170 °C.",
        "tecnica": (
            "Batir mantequilla con azúcar glas, agregar huevo y vainilla, incorporar "
            "harina. Formar un cilindro, refrigerar, cortar en rodajas y hornear "
            "hasta los bordes dorados."
        ),
    },
    "galletas con chips de chocolate": {
        "categoria": "galletas, chocolate, masas dulces, horno",
        "ingredientes": (
            "150 g de mantequilla pomada, 100 g de azúcar rubia, 80 g de azúcar blanca, "
            "1 huevo, 1 cucharadita de vainilla, 250 g de harina, 1/2 cucharadita de bicarbonato, "
            "180 g de chips de chocolate."
        ),
        "tiempo": "Preparación 15 min, refrigerado 20 min, horneado 12 min a 180 °C.",
        "tecnica": (
            "Cremar la mantequilla con los dos azúcares, añadir el huevo y la vainilla. "
            "Incorporar harina y bicarbonato sin sobrebatir y sumar los chips de chocolate. "
            "Formar bolitas, enfriar y hornear dejando espacio entre cada galleta."
        ),
    },
    "crema pastelera": {
        "categoria": "cremas, rellenos, vainilla, bases de pasteleria",
        "ingredientes": (
            "500 ml de leche, 4 yemas, 100 g de azúcar, 40 g de maicena, "
            "1 vaina de vainilla."
        ),
        "tiempo": "Preparación 15 min, cocción 10 min.",
        "tecnica": (
            "Hervir la leche con vainilla. Mezclar yemas, azúcar y maicena; verter "
            "la leche caliente, cocinar revolviendo hasta espesar. Enfriar con film "
            "en contacto."
        ),
    },
    "pie de limon": {
        "categoria": "frutas, citricos, limon, tartas, merengue, horno",
        "ingredientes": (
            "Base: 200 g de galletas de vainilla molidas y 100 g de mantequilla derretida. "
            "Relleno: 400 g de leche condensada, 4 yemas, 120 ml de jugo de limón fresco. "
            "Cobertura: 4 claras y 160 g de azúcar para el merengue."
        ),
        "tiempo": "Preparación 25 min, horneado 15 min a 175 °C, enfriado 2 horas.",
        "tecnica": (
            "Mezclar galleta molida con mantequilla, forrar el molde y hornear 8 min. "
            "Unir leche condensada con jugo de limón y yemas, verter sobre la base y "
            "hornear 10 min más. Cubrir con merengue suizo batido a picos firmes y dorar."
        ),
    },
    "cheesecake de frutos rojos": {
        "categoria": "queso crema, frutas, frutos rojos, tortas, postres frios",
        "ingredientes": (
            "Base: 200 g de galletas dulces y 90 g de mantequilla. "
            "Relleno: 500 g de queso crema, 150 g de azúcar flor, 250 ml de crema para batir, "
            "10 g de gelatina sin sabor hidratada en 50 ml de agua. "
            "Cobertura: 250 g de frutos rojos (frambuesas, arándanos y frutillas) con 80 g de azúcar."
        ),
        "tiempo": "Preparación 30 min, refrigeración 4 horas.",
        "tecnica": (
            "Compactar las galletas con mantequilla en la base del molde. Batir queso crema "
            "con azúcar flor, incorporar la gelatina disuelta tibia y luego la crema semibatida "
            "con movimientos envolventes. Refrigerar 4 horas y cubrir con compota fría de frutos rojos."
        ),
    },
    "tiramisu": {
        "categoria": "cafe, queso mascarpone, postres frios, sin horno, italiano",
        "ingredientes": (
            "400 g de queso mascarpone, 4 huevos, 100 g de azúcar, 250 ml de café espresso frío, "
            "200 g de galletas champañeras (savoiardi), 30 g de cacao amargo en polvo."
        ),
        "tiempo": "Preparación 25 min, refrigeración 6 horas.",
        "tecnica": (
            "Batir yemas con azúcar a baño maría suave hasta blanquear e integrar el mascarpone. "
            "Montar las claras a nieve e incorporar de forma envolvente. Humedecer brevemente las "
            "champañeras en café, alternar capas de galleta y crema, refrigerar y espolvorear cacao."
        ),
    },
    "alfajores de maicena": {
        "categoria": "masas dulces, manjar, dulce de leche, galletas, horno",
        "ingredientes": (
            "200 g de maicena (fécula de maíz), 100 g de harina, 150 g de mantequilla a temperatura ambiente, "
            "100 g de azúcar flor, 3 yemas, 1 cucharadita de polvo de hornear, ralladura de 1 limón, "
            "300 g de manjar (dulce de leche) y 50 g de coco rallado."
        ),
        "tiempo": "Preparación 25 min, horneado 10 min a 170 °C.",
        "tecnica": (
            "Batir mantequilla con azúcar flor, agregar las yemas de a una y la ralladura. "
            "Incorporar maicena, harina y polvo de hornear tamizados hasta formar una masa suave sin amasar. "
            "Estirar, cortar discos, hornear 10 min sin que doren, enfriar, rellenar con manjar y rodar los bordes por coco."
        ),
    },
    "merengue suizo": {
        "categoria": "decoracion, coberturas, claras, tortas, tecnicas",
        "ingredientes": (
            "150 g de claras de huevo (aprox. 4 claras), 300 g de azúcar blanca, "
            "1 cucharadita de jugo de limón o esencia de vainilla."
        ),
        "tiempo": "Preparación 10 min a baño maría + 10 min de batido.",
        "tecnica": (
            "Llevar las claras y el azúcar a baño maría suave revolviendo constantemente "
            "hasta que los cristales de azúcar se disuelvan por completo (60 °C). Retirar del calor "
            "y batir a velocidad alta hasta que el bol se enfríe y se formen picos firmes y brillantes."
        ),
    },
}


def _formatear_receta(nombre: str, receta: dict[str, str]) -> str:
    return (
        f"Postre: {nombre}\n"
        f"Ingredientes: {receta['ingredientes']}\n"
        f"Tiempo: {receta['tiempo']}\n"
        f"Técnica: {receta['tecnica']}"
    )


def _buscar_recetas_coincidentes(consulta: str) -> list[tuple[str, dict[str, str]]]:
    """Busca recetas por nombre exacto, parcial, categoría o ingrediente."""
    clave = (consulta or "").strip().lower()
    for prefijo in (
        "receta de ",
        "receta para ",
        "una receta de ",
        "dame una receta de ",
        "dame la receta de ",
        "quiero hacer ",
        "como hacer ",
        "cómo hacer ",
        "postre de ",
        "algo con ",
        "algo ",
    ):
        if clave.startswith(prefijo):
            clave = clave[len(prefijo):].strip()

    if not clave or clave in (
        "dulce",
        "receta dulce",
        "postre",
        "postres",
        "catalogo",
        "catálogo",
        "todas",
        "recomendacion",
        "recomendación",
        "cualquiera",
    ):
        # Si piden una receta dulce general o el catálogo, devolvemos una selección variada destacada
        destacadas = ["torta de chocolate", "brownie", "pie de limon", "cheesecake de frutos rojos"]
        return [(n, RECETAS[n]) for n in destacadas if n in RECETAS]

    # 1. Coincidencia exacta por nombre
    if clave in RECETAS:
        return [(clave, RECETAS[clave])]

    # 2. Coincidencia parcial en el nombre del postre
    por_nombre: list[tuple[str, dict[str, str]]] = []
    for nombre, datos in RECETAS.items():
        if clave in nombre or nombre in clave:
            por_nombre.append((nombre, datos))
    if por_nombre:
        return por_nombre

    # 3. Coincidencia por palabras clave en nombre, categoría o ingredientes
    palabras = [
        p for p in clave.split()
        if len(p) > 2 and p not in ("con", "sin", "para", "una", "del", "las", "los", "que", "dulce", "dulces", "receta", "recetas", "postre", "postres")
    ]
    coincidencias: list[tuple[str, dict[str, str]]] = []
    for nombre, datos in RECETAS.items():
        texto_busqueda = f"{nombre} {datos.get('categoria', '')} {datos['ingredientes']}".lower()
        if any(p in texto_busqueda for p in palabras):
            coincidencias.append((nombre, datos))

    return coincidencias


@tool
def catalogo_postres(nombre_postre: str) -> str:
    """Busca y entrega recetas dulces, ingredientes, tiempos y técnicas de pastelería.

    nombre_postre puede ser el nombre específico de un postre (ej. "brownie",
    "torta de chocolate", "pie de limon", "tiramisu"), un ingrediente o tipo
    (ej. "chocolate", "frutas", "sin horno", "galletas") o una solicitud general
    (ej. "receta dulce", "catalogo").
    """
    coincidencias = _buscar_recetas_coincidentes(nombre_postre)
    if not coincidencias:
        disponibles = ", ".join(RECETAS.keys())
        return (
            f"No tengo una receta específica para '{nombre_postre}' en mi catálogo. "
            f"Las recetas dulces que tengo disponibles son: {disponibles}."
        )

    if len(coincidencias) == 1:
        nombre, receta = coincidencias[0]
        return _formatear_receta(nombre, receta)

    # Si hay varias coincidencias (por ejemplo pidió "receta de chocolate" o "receta dulce"),
    # entregamos las primeras 2 completas y listamos las demás opciones encontradas.
    bloques = [_formatear_receta(n, r) for n, r in coincidencias[:2]]
    todos_nombres = ", ".join(n for n, _ in coincidencias)
    catalogo_completo = ", ".join(RECETAS.keys())
    return (
        f"Opciones encontradas en el catálogo ({todos_nombres}):\n\n"
        + "\n\n---\n\n".join(bloques)
        + f"\n\n(Catálogo completo disponible: {catalogo_completo})"
    )


# Sustitutos comunes para ingredientes de pastelería.
SUSTITUTOS: dict[str, str] = {
    "mantequilla": "margarina vegetal, aceite de coco (misma cantidad) o puré de manzana (en bizcochos húmedos).",
    "huevo": "1 cucharada de linaza molida + 3 cucharadas de agua (por cada huevo), o 60 g de puré de plátano.",
    "leche": "leche vegetal (almendra, soja, coco o avena) en la misma proporción (1:1).",
    "azúcar": "azúcar de coco, alulosa, eritritol o miel (si usas miel, reduce un 20% el líquido de la receta).",
    "harina": "harina de avena, harina integral o premezcla sin gluten (1:1 con 1/2 cdta de goma xantana).",
    "chocolate": "cacao amargo en polvo + mantequilla derretida (3 cucharadas de cacao + 1 de mantequilla por cada 30 g).",
    "crema de leche": "crema de coco refrigerada por 12 horas y batida.",
    "queso crema": "yogur griego natural escurrido o ricotta procesada hasta quedar lisa.",
    "maicena": "fécula de papa o almidón de mandioca en la misma cantidad (1:1).",
    "limón": "jugo de naranja, maracuyá o lima en la misma proporción.",
}


@tool
def sustituto_ingrediente(ingrediente: str) -> str:
    """Sugiere sustitutos comunes para un ingrediente de pastelería.

    ingrediente es el nombre del ingrediente (por ejemplo "mantequilla",
    "huevo", "azúcar", "harina", "queso crema"). Devuelve una sugerencia de sustituto.
    """
    clave = (ingrediente or "").strip().lower()
    for nombre, sugerencia in SUSTITUTOS.items():
        if clave in nombre or nombre in clave:
            return f"Sustituto para {nombre}: {sugerencia}"
    disponibles = ", ".join(SUSTITUTOS.keys())
    return (
        f"No tengo un sustituto directo registrado para '{ingrediente}'. "
        f"Puedo darte sustitutos para: {disponibles}."
    )


@tool
def escalar_receta(nombre_postre: str, porciones: int) -> str:
    """Escala los ingredientes de un postre del catálogo a la cantidad de porciones indicada.

    nombre_postre es el nombre del postre y porciones la cantidad deseada.
    Asume que la receta base es para 8 porciones y devuelve el factor a aplicar.
    """
    coincidencias = _buscar_recetas_coincidentes(nombre_postre)
    if not coincidencias:
        disponibles = ", ".join(RECETAS.keys())
        return (
            f"No tengo receta para '{nombre_postre}' en mi catálogo. "
            f"Recetas disponibles para escalar: {disponibles}."
        )
    if porciones <= 0:
        return "La cantidad de porciones debe ser mayor que cero."

    clave, receta = coincidencias[0]
    factor = porciones / 8
    return (
        f"Postre: {clave}\n"
        f"Porciones deseadas: {porciones} (receta base 8 porciones, factor {factor:.2f})\n"
        f"Ingredientes base: {receta['ingredientes']}\n"
        f"Multiplica cada cantidad por {factor:.2f} para obtener las porciones deseadas.\n"
        f"Tiempo: {receta['tiempo']}\n"
        f"Técnica: {receta['tecnica']}"
    )
