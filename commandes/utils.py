# commandes/utils.py

import phonenumbers
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
import pycountry

def get_country_calling_codes():
    """
    Retourne une liste de tuples (indicatif, pays)
    Ex : [('+226', '🇧🇫 Burkina Faso'), ('+33', '🇫🇷 France'), ...]
    """
    CHOICES = []
    bf_code = '+226'

    # Ajout du Burkina Faso en premier
    CHOICES.append((bf_code, "🇧🇫 Burkina Faso (+226) - Défaut"))

    seen = set([bf_code])

    for code, regions in sorted(COUNTRY_CODE_TO_REGION_CODE.items()):
        try:
            region = regions[0]
            country = pycountry.countries.get(alpha_2=region)
            if not country:
                continue

            flag = chr(127397 + ord(region[0])) + chr(127397 + ord(region[1]))
            phone_code = f"+{code}"

            if phone_code not in seen:
                CHOICES.append((phone_code, f"{flag} {country.name} ({phone_code})"))
                seen.add(phone_code)
        except Exception:
            continue

    return CHOICES

COUNTRY_CODES_CHOICES = get_country_calling_codes()
