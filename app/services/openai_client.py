from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_products_with_ai(table_text: str) -> str:
    prompt = f"""
Analizează tabelul de mai jos și spune pe scurt:
1. ce produse au interes mare și conversie slabă
2. ce ipoteze ai
3. ce audiențe sau segmente merită investigate

Tabel:
{table_text}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return response.output_text