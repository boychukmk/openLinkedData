import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import sys


WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"


def get_diseases_from_wikidata():
    query = """
               SELECT DISTINCT ?disease ?diseaseLabel ?description ?icd10 ?subclassOfLabel 
           ?causeLabel ?fatalityRate ?diagnosticMethodLabel ?treatmentLabel ?symptomLabel 
           ?relatedGeneLabel WHERE {
          ?disease wdt:P31 wd:Q12136.  
          
         
          ?disease wdt:P780 ?symptom.
          ?disease wdt:P2176 ?treatment.
          ?disease wdt:P828 ?cause.
          OPTIONAL { ?disease wdt:P1995 ?icd10. } 
          OPTIONAL { ?disease wdt:P279 ?subclassOf. }  
          OPTIONAL { ?disease wdt:P828 ?cause. }  
          OPTIONAL { ?disease wdt:P1193 ?fatalityRate. }  
          OPTIONAL { ?disease wdt:P2176 ?treatment. }  
          OPTIONAL { ?disease schema:description ?description. FILTER (LANG(?description) = "en") }
        
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "en".  
            ?disease rdfs:label ?diseaseLabel.
            ?subclassOf rdfs:label ?subclassOfLabel.
            ?cause rdfs:label ?causeLabel.
            ?symptom rdfs:label ?symptomLabel.
            ?diagnosticMethod rdfs:label ?diagnosticMethodLabel.
            ?treatment rdfs:label ?treatmentLabel.
            ?relatedGene rdfs:label ?relatedGeneLabel.
          }
        }
    
    """

    response = requests.get(WIKIDATA_SPARQL_URL, params={"format": "json", "query": query})

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise Exception("Ошибка декодирования JSON. Возможно, сервер вернул пустой ответ.")

    diseases_dict = {}

    for item in data["results"]["bindings"]:
        disease_id = item["disease"]["value"].split("/")[-1]
        disease_url = f"https://www.wikidata.org/wiki/{disease_id}"  # Генерируем ссылку

        disease_name = item["diseaseLabel"]["value"]

        if disease_name not in diseases_dict:
            diseases_dict[disease_name] = {
                "id": disease_id,
                "name": disease_name.lower(),
                "url": disease_url,
                "description": item.get("description", {}).get("value", "No description available"),
                "icd10": item.get("icd10", {}).get("value", "N/A"),
                "subclass_of": item.get("subclassOfLabel", {}).get("value", "Unknown"),
                "causes": set(),
                "symptoms": set(),
                "fatality_rate": item.get("fatalityRate", {}).get("value", "N/A"),
                "diagnostic_methods": set(),
                "treatments": set(),
                "related_genes": set(),
            }

        # Добавляем множественные значения в `set()`
        if "causeLabel" in item:
            diseases_dict[disease_name]["causes"].add(item["causeLabel"]["value"])
        if "symptomLabel" in item:
            diseases_dict[disease_name]["symptoms"].add(item["symptomLabel"]["value"])
        if "diagnosticMethodLabel" in item:
            diseases_dict[disease_name]["diagnostic_methods"].add(item["diagnosticMethodLabel"]["value"])
        if "treatmentLabel" in item:
            diseases_dict[disease_name]["treatments"].add(item["treatmentLabel"]["value"])
        if "relatedGeneLabel" in item:
            diseases_dict[disease_name]["related_genes"].add(item["relatedGeneLabel"]["value"])

    # Преобразуем множества в списки для удобства
    for disease in diseases_dict.values():
        disease["causes"] = list(disease["causes"])
        disease["symptoms"] = list(disease["symptoms"])
        disease["diagnostic_methods"] = list(disease["diagnostic_methods"])
        disease["treatments"] = list(disease["treatments"])
        disease["related_genes"] = list(disease["related_genes"])

    return list(diseases_dict.values())


def get_hospitals_from_wikidata(country_code):
    query = f"""
    SELECT DISTINCT ?hospital ?hospitalLabel ?geo ?hospitalDescription ?website ?wikiImportURL ?image ?address WHERE {{
      ?hospital wdt:P31/wdt:P279* wd:Q16917;  # Тип - больница
                wdt:P625 ?geo;  # Географические координаты
                wdt:P17 wd:{country_code}.  # Фильтр по стране
      OPTIONAL {{ ?hospital schema:description ?hospitalDescription. FILTER(LANG(?hospitalDescription) = "en") }}  # Описание
      OPTIONAL {{ ?hospital wdt:P856 ?website. }}  # Официальный сайт
      OPTIONAL {{ ?hospital wdt:P4656 ?wikiImportURL. }}  # URL из Wikimedia import
      OPTIONAL {{ ?hospital wdt:P18 ?image. }}  # Фото больницы
      OPTIONAL {{ ?hospital wdt:P6375 ?address. }}  # Адрес

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 500
    """
    user_agent = "WDQS-Hospital-Map Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(WIKIDATA_SPARQL_URL, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    hospitals = []
    for item in results["results"]["bindings"]:
        coordinates = item["geo"]["value"].replace("Point(", "").replace(")", "").split(" ")
        latitude, longitude = float(coordinates[1]), float(coordinates[0])

        image_url = None
        if "image" in item:
            image_name = item["image"]["value"].split("/")[-1]  # Получаем имя файла
            image_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{image_name}"  # Формируем URL

        # Додаємо адресу, якщо вона є, або координати
        address = item.get("address", {}).get("value", f"Coordinates: {latitude}, {longitude}")

        hospitals.append({
            "name": item["hospitalLabel"]["value"],
            "latitude": latitude,
            "longitude": longitude,
            "description": item.get("hospitalDescription", {}).get("value", "No description available"),
            "website": item.get("website", {}).get("value", None),
            "wikimedia_url": item.get("wikiImportURL", {}).get("value", None),
            "wikidata_url": f"https://www.wikidata.org/wiki/{item['hospital']['value'].split('/')[-1]}",
            "image": image_url,
            "address": address
        })

    return hospitals


def get_drug_illness_graph():
    query = """
        SELECT DISTINCT ?item ?itemLabel ?rgb ?link
        WHERE
        {
          VALUES ?toggle { true false }
          ?disease wdt:P699 ?doid;
                   wdt:P279+ wd:Q18123741;
                   wdt:P2176 ?drug.
          ?drug rdfs:label ?drugLabel.
            FILTER(LANG(?drugLabel) = "en").
          ?disease rdfs:label ?diseaseLabel.
            FILTER(LANG(?diseaseLabel) = "en").
          BIND(IF(?toggle,?disease,?drug) AS ?item).
          BIND(IF(?toggle,?diseaseLabel,?drugLabel) AS ?itemLabel).
          BIND(IF(?toggle,"FFA500","7FFF00") AS ?rgb).
          BIND(IF(?toggle,"",?disease) AS ?link).
        }
        """
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    sparql = SPARQLWrapper(WIKIDATA_SPARQL_URL, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    data = [
        {
            "item": res["item"]["value"],
            "label": res["itemLabel"]["value"],
            "color": res["rgb"]["value"],
            "link": res.get("link", {}).get("value", "")
        }
        for res in results["results"]["bindings"]
    ]
    return data
