## W20 Telemetry

Upload each previous day's measurement to Azure Blob Storage.

# Handleiding installatie en uitvoeren script upload2azure.py

Het zipfile code_voor_upload2azure.zip bevat volgende bestanden:

```ascii
code_voor_upload2azure
├── .env
├── README.md
├── requirements.txt
└── upload2azure.py
```

Plaats de bestanden in dezelfde directory waarin de dagelijkse directories met ruwe data staan.

- README.md is dit bestand.
- upload2azure.py is het Python script dat elke nacht om 4u30 de lokale ruwe data upload naar Azure Blob storage.
- requirement.txt is een bestand voor het installeren van de benodigde Python biobliotheken
- .env bevat de codes om toegang te verkrijgen tot de Azure Blob Storage. (geheim houden!)

## Volgende stappen installeren en starten het script

1. Verzeker je dat je toegang hebt tot een recente Python interpreter:

```ascii
prompt>python -V
Python 3.11.3
```

2. Zorg ervoor dat het programma pip geïnstalleerd is.
Dit kan op verschillende manieren: <https://pip.pypa.io/en/stable/installation/>
Het eenvoudigste is misschien via ensurepip. Voer volgende commando uit:

```ascii
prompt>python -m ensurepip --upgrade
```

3. Installeer de benodigde Python bibliotheken:

```ascii
prompt>pip install -r requirements.txt
```

4. In een apart venster, start het Python script upload2azure.py in dezelfde map waar de mappen met ruwe data staan en laat het lopen:

```ascii
prompt>python upload2azure.py
```

5. De voortgang van het script is te volgen in het bestand upload2azure.log

6. Om het dagelijks uploaden te beëindigen, stop het script met control-C
7. Om te herstarten, ga naar stap 4
