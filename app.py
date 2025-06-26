from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

from flask import Flask

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("gesundheitshelfer.html")

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/api/health", methods=["POST"])
def health_analyse():
    daten = request.get_json()

    if not daten or not daten.get("symptome"):
        return jsonify({"error": "Symptombeschreibung fehlt."}), 400

    prompt = erstelle_prompt(daten)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener medizinischer Gesundheitsassistent. Du stellst keine Diagnosen im rechtlichen Sinne, sondern gibst Einschätzungen und Empfehlungen auf Basis der Nutzereingaben."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        output = response.choices[0].message.content

        teile = output.split("\n\n")
        diagnose = teile[0] if len(teile) > 0 else "Keine Diagnose ermittelbar."
        behandlung = teile[1] if len(teile) > 1 else "Keine Empfehlungen verfügbar."

        return jsonify({"diagnose": diagnose.strip(), "behandlung": behandlung.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def erstelle_prompt(daten):
    wunsch = []
    if "medikamente_check" in daten:
        wunsch.append("rezeptfreie Medikamente")
    if "alternativen_check" in daten:
        wunsch.append("natürliche Alternativen")

    infos = f"""
Geschlecht: {daten.get('geschlecht')}
Alter: {daten.get('alter')}
Größe: {daten.get('groesse')} cm
Gewicht: {daten.get('gewicht')} kg
Raucher: {daten.get('raucher')}
Schwangerschaft/Stillzeit: {daten.get('schwangerschaft') or 'nicht angegeben'}
Vorerkrankungen: {daten.get('vorerkrankungen') or 'keine angegeben'}
Allergien: {daten.get('allergien') or 'keine angegeben'}
Medikamente: {daten.get('medikamente') or 'keine'}
Nahrungsergänzung: {daten.get('nahrung') or 'keine'}
Dauer der Beschwerden: {daten.get('dauer')}
Stresslevel: {daten.get('stress') or 'nicht angegeben'}
Schlafqualität: {daten.get('schlaf') or 'nicht angegeben'}
Reiseverlauf: {daten.get('reisen') or 'keine'}
Symptome: {daten.get('symptome')}
Wunsch: {', '.join(wunsch) if wunsch else 'keine Präferenz'}
"""
    return f"""
Hier sind die Angaben einer Person, die Symptome hat und um eine Einschätzung bittet:
{infos}

Gib basierend darauf eine mögliche Ursache (Verdachtsdiagnose) aus – allgemeinverständlich und knapp formuliert.
Danach gib passende Empfehlungen, z. B. Hausmittel, rezeptfreie Präparate oder alternative Möglichkeiten. Weise auch darauf hin, wann ärztliche Hilfe nötig wäre.
"""

# Lokaler Entwicklungsstart (z. B. mit `python app.py`)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
