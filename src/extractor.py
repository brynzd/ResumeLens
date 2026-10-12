import os
import re
import json

def extract_resume_entities(text_content: str) -> dict:
    """
    Extracts full contact information, professional experience, education,
    and technology/tool tokens from a plaintext resume using regular expressions.
    """
    patterns = {
        # Name detection (capitalized words at the beginning of lines)
        "name": r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+",

        # Email addresses
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",

        # Phone numbers (international or local formats)
        "phone": r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",

        # Years of experience (e.g., "3 years of experience")
        "experience_years": r"(\d+)\s*(?:years?|anos?|años?)\s*(?:of)?\s*(?:experience)?",

        # Academic background / Degrees
        "education": r"(B\.?Sc\.?|M\.?Sc\.?|Ph\.?D\.?|Bachelor|Master|Engineering|Computer Science|Ingeniería|Systems Engineering)",

        # Comprehensive technology and tools tokens for all 4 profiles
        "technologies": r"\b(JS|Javascript|React\.?js|React|NodeJS|Node\.js|Python|Pandas|PyTorch|Spark|Airflow|Git|Postgres|PostgreSQL|TypeScript|TS|Angular|Vue|CSS|Tailwind|Docker|Kubernetes|AWS|GCP|Terraform|Django|Spring Boot|SQL|MongoDB|Scala|NumPy|Scikit-Learn|sklearn)\b"
    }

    extracted_data = {}

    # Extract Name
    name_match = re.search(patterns["name"], text_content, re.MULTILINE)
    extracted_data["name"] = name_match.group(0) if name_match else "Unknown"

    # Extract Email
    emails = re.findall(patterns["email"], text_content)
    extracted_data["email"] = emails[0] if emails else "Unknown"

    # Extract Phone
    phones = re.findall(patterns["phone"], text_content)
    extracted_data["phone"] = phones[0] if phones else "Unknown"

    # Extract Years of Experience
    exp_match = re.search(patterns["experience_years"], text_content, re.IGNORECASE)
    extracted_data["experience_years"] = exp_match.group(1) if exp_match else "0"

    # Extract Education (unique entries)
    education_matches = re.findall(patterns["education"], text_content, re.IGNORECASE)
    extracted_data["education"] = list(set(education_matches))

    # Extract Technologies and Tools (unique entries, case-insensitive check via regex)
    tech_matches = re.findall(patterns["technologies"], text_content, re.IGNORECASE)
    extracted_data["technologies"] = list(set(tech_matches))

    return extracted_data

def save_extracted_data(extracted_data: dict, output_path: str = "extracted_resume.json"):
    """
    Saves the structured extracted data into a persistent file (JSON format),
    ensuring that the parent directory exists beforehand.
    """
    # Get the directory path from output_path (if any)
    directory = os.path.dirname(output_path)
    if directory:
        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)