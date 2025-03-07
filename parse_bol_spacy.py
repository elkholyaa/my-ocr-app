"""
File: parse_bol_spacy.py
Purpose:
    - Parses raw text extracted from a Bill of Lading PDF (e.g., "065-2024 MBL MEDUP1966175.pdf")
      and returns a structured dictionary matching the desired JSON structure.
      
Target JSON Structure:
{
  "BILL_OF_LADING_No": "MEDUP1966175",
  "SHIPPER": "INTERCROMA SA, Rua Conde D'eu, 800- Bairro Alpino, Phone (47) 3631-4600 - Fax (47) 3631-4604, 89286-691 Sao Bento do Sul - SC - Brazil, CNPJ 005577130001",
  "CONSIGNEE": "MUSCAT WOODEN PALLETS L.L.C., P.O. BOX - 284, AUQADEN 217, SALALAH, SULTANETE OF OMAN, PHONE: +968 23219649, FAX: +968 23219632",
  "Total_Gross_Weight": "50000.000 Kgs",
  "Total_Items": 88,
  "Number_of_Containers": 2,
  "Containers": [
    {
      "container_number": "BEAU5862453",
      "container_size": "40' HIGH CUBE",
      "Seal_Number": "FJ21074021",
      "Description_of_Packages_and_Goods": "44 PALLET of IN 2X40'HC CONTAINERS WITH 88 PALLETS WITH 100,374 CBM OF SAWN TIMBER PALLET AS PER PROFORMA INVOICE 065/2024 DUE: 24BR001928059-7 RUC: 4BR00557713200000000000000001242455 NCM 44071100 COMMERCIAL INVOICE 065/2024 HS CODE: 44071190 FREIGHT PREPAID ABROAD AS PER AGREEMENT WOODEN PACKAGE USED: TREATED/CERTIFIED 44071100 HS Code:440711 Marks and Numbers: MADE IN BRAZIL MUSCAT WOODEN 001/088",
      "Gross_Cargo_Weight": "25,000.000 Kgs"
    },
    {
      "container_number": "BMOU5932452",
      "container_size": "40' HIGH CUBE",
      "Seal_Number": "FJ21154465",
      "Description_of_Packages_and_Goods": "44 PALLET of . 44071100 HS Code:440711 Marks and Numbers: .",
      "Gross_Cargo_Weight": "25,000.000 Kgs"
    }
  ]
}

Role & Relation:
    - This module is used after extracting raw text (e.g., via pdfplumber) to structure the data.
    - The returned dictionary is converted to JSON in the FastAPI endpoint.
Educational Comments:
    - We avoid hard-coding specific company names by using structural markers (e.g., "SHIPPER:" and "CONSIGNEE:").
    - spaCy is used to extract organization entities from text blocks via the extract_org() function.
    - Regex patterns capture numeric fields and container details in a generalized manner.
"""

import re
import spacy

# Load the spaCy model (ensure you have installed it with: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def extract_org(text_block: str) -> str:
    """
    Processes a text block with spaCy to extract organization entities.
    Returns a comma-separated string of organization names if found; otherwise, returns the cleaned text block.
    """
    doc = nlp(text_block)
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    return ", ".join(orgs) if orgs else text_block.strip()

def parse_bol_spacy(text: str) -> dict:
    """
    Parses raw text from a Bill of Lading PDF and returns a structured dictionary.
    Uses a combination of regex and spaCy to extract:
      - BILL_OF_LADING_No
      - SHIPPER (extracted from the block after "SHIPPER:")
      - CONSIGNEE (extracted from the block after "CONSIGNEE:")
      - Total_Gross_Weight, Total_Items, Number_of_Containers
      - Containers array with container details (container_number, container_size, Seal_Number, description, and Gross_Cargo_Weight)
    """
    # Normalize text: convert CRLF to LF and collapse extra spaces.
    text = text.replace('\r\n', '\n')
    text = re.sub(r'\s+', ' ', text)

    result = {}

    # 1. Extract BILL_OF_LADING_No (e.g., "MEDUP1966175")
    bol_match = re.search(r'\b(MEDUP\d+)\b', text, re.IGNORECASE)
    result["BILL_OF_LADING_No"] = bol_match.group(1) if bol_match else ""

    # 2. Extract SHIPPER: From "SHIPPER:" to next marker.
    shipper_match = re.search(
        r'SHIPPER:\s*([\s\S]*?)(?=(CONSIGNEE:|NOTIFY PARTIES:|PLACE OF RECEIPT:|$))',
        text,
        re.IGNORECASE
    )
    if shipper_match:
        shipper_block = shipper_match.group(1).strip()
        result["SHIPPER"] = extract_org(shipper_block)
    else:
        result["SHIPPER"] = ""

    # 3. Extract CONSIGNEE: From "CONSIGNEE:" to next marker.
    consignee_match = re.search(
        r'CONSIGNEE:\s*([\s\S]*?)(?=(VESSEL|NOTIFY PARTIES:|PLACE OF RECEIPT:|$))',
        text,
        re.IGNORECASE
    )
    if consignee_match:
        consignee_block = consignee_match.group(1).strip()
        result["CONSIGNEE"] = extract_org(consignee_block)
    else:
        result["CONSIGNEE"] = ""

    # 4. Extract Total_Gross_Weight (e.g., "50000.000 Kgs")
    weight_match = re.search(r'Total Gross Weight\s*:\s*([\d.,]+\s*Kgs)', text, re.IGNORECASE)
    result["Total_Gross_Weight"] = weight_match.group(1).strip() if weight_match else ""

    # 5. Extract Total_Items (e.g., "88")
    items_match = re.search(r'Total Items\s*:\s*(\d+)', text, re.IGNORECASE)
    result["Total_Items"] = int(items_match.group(1)) if items_match else 0

    # 6. Extract Number_of_Containers (e.g., "2 x 40HC" or "2 x 40' HIGH CUBE")
    container_count_match = re.search(r'(\d+)\s*x\s*(?:40HC|40\'\s*HIGH\s*CUBE)', text, re.IGNORECASE)
    result["Number_of_Containers"] = int(container_count_match.group(1)) if container_count_match else 0

    # 7. Compute Gross_Cargo_Weight per container.
    container_weight = ""
    if result["Total_Gross_Weight"] and result["Number_of_Containers"]:
        clean_weight = re.sub(r'[^0-9.]', '', result["Total_Gross_Weight"])
        try:
            total_weight = float(clean_weight)
            count = result["Number_of_Containers"]
            container_weight = f"{total_weight / count:,.3f} Kgs"
        except Exception:
            container_weight = ""
    
    # 8. Extract container details:
    #    - Container number: generalized pattern (4 letters + digits)
    #    - Seal_Number: code starting with FJ (e.g., FJ21074021)
    #    - Container size: matches "40' HIGH CUBE" or "40HC"
    #    - Description: starts with "44 PALLET" until next container or end.
    containers = []
    container_regex = re.compile(
        r'((?:\w{4}\d+))'                         # container_number (e.g., BEAU5862453, BMOU5932452, HPCUxxxx)
        r'[^\n]*?\bSEAL\s*[:]*\s*(FJ\d+)\b'        # Seal_Number (e.g., FJ21074021)
        r'[^\n]*?(40(?:\'\s*HIGH\s*CUBE|HC))'       # container_size (e.g., 40' HIGH CUBE or 40HC)
        r'[\s\S]*?(44 PALLET[\s\S]*?)(?=(?:\w{4}\d+)|$)',  # description from "44 PALLET" to next container block or end
        re.IGNORECASE
    )
    for m in container_regex.finditer(text):
        container_number = m.group(1).strip()
        seal_number = m.group(2).strip()
        container_size = m.group(3).strip()
        description = re.sub(r'\s+', ' ', m.group(4)).strip()
        containers.append({
            "container_number": container_number,
            "container_size": container_size,
            "Seal_Number": seal_number,
            "Description_of_Packages_and_Goods": description,
            "Gross_Cargo_Weight": container_weight,
        })
    result["Containers"] = containers

    return result

if __name__ == "__main__":
    # For testing: read raw text from a file and print the parsed JSON.
    with open("sample_extracted_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()
    import json
    parsed = parse_bol_spacy(raw_text)
    print(json.dumps(parsed, indent=2))
