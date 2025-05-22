from flask import Flask, render_template_string
import requests
import re

app = Flask(__name__)

# API Headers and URLs
JINA_TOKEN = "jina_c8655362db9449fbbcc0dd09ab9b7203qsrLJERJviertMWrfJECzaHpWFGD"
HEADERS = {"Authorization": f"Bearer {JINA_TOKEN}"}
OMIE_URL = "https://r.jina.ai/https://www.omie.es/pt"
MIBGAS_URL = "https://r.jina.ai/https://www.mibgas.es/pt"

# Extract OMIE prices
def fetch_omie_data():
    response = requests.get(OMIE_URL, headers=HEADERS)
    markdown = response.text

    result = {"spain": {}, "portugal": {}}

    spain = re.search(r"#### Preço medio Espanha\s*\n([0-9.,\-]+)€/MWh\s*#### Máximo\s*\n([0-9.,\-]+)€/MWh\s*#### Minimo\s*\n([0-9.,\-]+)€/MWh", markdown)
    if spain:
        result["spain"] = {"avg": spain.group(1), "max": spain.group(2), "min": spain.group(3)}

    portugal = re.search(r"#### Preço medio Portugal\s*\n([0-9.,\-]+)€/MWh\s*#### Máximo\s*\n([0-9.,\-]+)€/MWh\s*#### Minimo\s*\n([0-9.,\-]+)€/MWh", markdown)
    if portugal:
        result["portugal"] = {"avg": portugal.group(1), "max": portugal.group(2), "min": portugal.group(3)}

    return result

# Extract MIBGAS prices
def fetch_mibgas_data():
    response = requests.get(MIBGAS_URL, headers=HEADERS)
    markdown = response.text

    prices = []
    pattern = r"#### Day Ahead (ES|PT).*?\n([0-9.,]+)€/MWh\s*\n\*\*([0-9.,]+)\*\* €/MWh\s*\n\*\*([0-9.,]+)\*\*%"
    matches = re.findall(pattern, markdown, re.DOTALL)

    for market, price, change, percent in matches:
        prices.append({
            "market": market,
            "price": price,
            "change": change,
            "percent": percent
        })

    return prices

@app.route("/")
def index():
    omie = fetch_omie_data()
    mibgas = fetch_mibgas_data()

    return render_template_string("""
    <h2>📊 OMIE - Preços Médios</h2>
    <h3>Espanha</h3>
    <ul>
        <li><strong>Médio:</strong> {{ omie.spain.avg }} €/MWh</li>
        <li><strong>Máximo:</strong> {{ omie.spain.max }} €/MWh</li>
        <li><strong>Mínimo:</strong> {{ omie.spain.min }} €/MWh</li>
    </ul>
    <h3>Portugal</h3>
    <ul>
        <li><strong>Médio:</strong> {{ omie.portugal.avg }} €/MWh</li>
        <li><strong>Máximo:</strong> {{ omie.portugal.max }} €/MWh</li>
        <li><strong>Mínimo:</strong> {{ omie.portugal.min }} €/MWh</li>
    </ul>

    <h2>🟢 MIBGAS - Day Ahead</h2>
    {% for entry in mibgas %}
    <h4>Mercado: {{ entry.market }}</h4>
    <ul>
        <li><strong>Preço:</strong> {{ entry.price }} €/MWh</li>
        <li><strong>Variação:</strong> {{ entry.change }} €/MWh</li>
        <li><strong>Percentual:</strong> {{ entry.percent }} %</li>
    </ul>
    {% endfor %}
    """, omie=omie, mibgas=mibgas)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
