import re

def extract_resume_entities(text_content: str) -> dict:
    """
    Extrae información de contacto y tokens tecnológicos de un currículum en texto plano
    utilizando expresiones regulares.
    """
    patterns = {
        "name": r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "technologies": r"\b(JS|Javascript|React\.?js|React|NodeJS|Node\.js|Python|Pandas|PyTorch|Spark|Airflow|Git|Postgres|PostgreSQL)\b"
    }

    extracted_data = {}

    # Búsqueda de nombre (coincidencia única al inicio)
    name_match = re.search(patterns["name"], text_content, re.MULTILINE)
    extracted_data["name"] = name_match.group(0) if name_match else None

    # Búsqueda de correos electrónicos
    extracted_data["email"] = re.findall(patterns["email"], text_content)

    # Búsqueda de tecnologías (todas las ocurrencias en el texto)
    extracted_data["technologies"] = re.findall(patterns["technologies"], text_content, re.IGNORECASE)

    return extracted_data