from flask import Flask, render_template_string
import requests
import re

app = Flask(__name__)

JINA_URL_OMIE = "https://r.jina.ai/https://www.omie.es/pt"
JINA_TOKEN = "jina_c8655362db9449fbbcc0dd09ab9b7203qsrLJERJviertMWrfJECzaHpWFGD"
HEADERS = {"Authorization": f"Bearer {JINA_TOKEN}"}

def fetch_omie_data():
    response = requests.get(JINA_URL_OMIE, headers=HEADERS)
    markdown = response.text

    result = {"spain": {}, "portugal": {}}

    spain = re.search(r"#### Preço medio Espanha\s*\n([0-9.,\-]+)€/MWh\s*#### Máximo\s*\n([0-9.,\-]+)€/MWh\s*#### Minimo\s*\n([0-9.,\-]+)€/MWh", markdown)
    if spain:
        result["spain"] = {"avg": spain.group(1), "max": spain.group(2), "min": spain.group(3)}

    portugal = re.search(r"#### Preço medio Portugal\s*\n([0-9.,\-]+)€/MWh\s*#### Máximo\s*\n([0-9.,\-]+)€/MWh\s*#### Minimo\s*\n([0-9.,\-]+)€/MWh", markdown)
    if portugal:
        result["portugal"] = {"avg": portugal.group(1), "max": portugal.group(2), "min": portugal.group(3)}

    return result

@app.route("/")
def index():
    data = fetch_omie_data()
    return render_template_string("""
    <h2>📊 OMIE - Preços Médios</h2>
    <h3>Espanha</h3>
    <ul>
        <li><strong>Médio:</strong> {{ spain.avg }} €/MWh</li>
        <li><strong>Máximo:</strong> {{ spain.max }} €/MWh</li>
        <li><strong>Mínimo:</strong> {{ spain.min }} €/MWh</li>
    </ul>
    <h3>Portugal</h3>
    <ul>
        <li><strong>Médio:</strong> {{ portugal.avg }} €/MWh</li>
        <li><strong>Máximo:</strong> {{ portugal.max }} €/MWh</li>
        <li><strong>Mínimo:</strong> {{ portugal.min }} €/MWh</li>
    </ul>
    """, spain=data["spain"], portugal=data["portugal"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
