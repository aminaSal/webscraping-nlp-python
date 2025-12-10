# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:39:38 2024

@author: salla
"""

import pandas as pd
import requests
import re
import os
import csv
from datetime import datetime
import time
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud
from collections import defaultdict
from unidecode import unidecode

import importlib.metadata
version = importlib.metadata.version("csv")
print(version)

# Expressions régulières pour Le Monde
LEMONDE_ARTICLE_LINK_REGEX = re.compile(r'<a class="teaser__link"[^>]*?href="([^"]+?)"')
LEMONDE_TITLE_REGEX = re.compile(r'<h3 class="teaser__title">(.*?)</h3>', re.DOTALL)
LEMONDE_DESCRIPTION_REGEX = re.compile(
    r'<p class="article__desc(?: article__desc--opinion)?">(.*?)</p>|'
    r'<p id="js-summary-live" class="summary__sirius-live">(.*?)</p>',
    re.DOTALL
)

# Expressions régulières pour Midi Madagasikara
MIDI_ARTICLE_LINK_REGEX = re.compile(
    r'<a href="(https://midi-madagasikara.mg/[^"]+?)"[^>]*?class="[^"]*?td-image-wrap[^"]*?"[^>]*?title="[^"]+?"',
    re.DOTALL
)
MIDI_TITLE_REGEX = re.compile(r'<h1 class="tdb-title-text">(.*?)</h1>', re.DOTALL)
MIDI_DESCRIPTION_REGEX = re.compile(r'<p>(.*?)</p>', re.DOTALL)

# Constantes
data_dir = os.path.join(os.getcwd(), "data")
os.makedirs(data_dir, exist_ok=True)

# Fichier CSV global
global_csv_path = os.path.join(data_dir, "global_articles.csv")
global_file_exists = os.path.exists(global_csv_path)

# Création ou ouverture du fichier global
with open(global_csv_path, mode="a", encoding="utf-8", newline="") as global_file:
    global_writer = csv.writer(global_file, delimiter=";")
    if not global_file_exists:
        global_writer.writerow(["Titre", "URL", "Description", "Date", "Presse", "Catégorie"])

# Fonctions communes
def create_directory_structure(newspaper, category):
    """Crée les sous-dossiers par presse et catégorie."""
    today_date = datetime.now().strftime("%Y-%m-%d")
    category_dir = os.path.join(data_dir, today_date, newspaper, category)
    os.makedirs(category_dir, exist_ok=True)
    return category_dir

def save_articles_to_csv(articles, category, newspaper, global_writer):
    """Sauvegarde les articles dans des fichiers CSV individuels et dans le fichier global."""
    category_dir = create_directory_structure(newspaper, category)
    individual_file_path = os.path.join(category_dir, f"{category}_{newspaper}.csv")

    # Fichier individuel
    with open(individual_file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Titre", "URL", "Description", "Date", "Presse", "Catégorie"])

        for article in articles:
            row = [
                article["title"],
                article["url"],
                article["description"],
                datetime.now().strftime("%Y-%m-%d"),
                newspaper,
                category,
            ]
            writer.writerow(row)

            # Ajout au fichier global
            global_writer.writerow(row)

    print(f"Articles sauvegardés dans : {individual_file_path}")

def fetch_html(url):
    """Récupère le contenu HTML d'une URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Fonctions spécifiques à Le Monde
def get_lemonde_articles(category_url):
    """Récupère les articles de la catégorie pour Le Monde."""
    html_content = fetch_html(category_url)
    links = LEMONDE_ARTICLE_LINK_REGEX.findall(html_content)
    titles = LEMONDE_TITLE_REGEX.findall(html_content)

    articles = []
    for link, title in zip(links, titles):
        clean_title = re.sub(r'\s+', ' ', title).strip()
        if "live-testimony" in clean_title.lower():
            continue
        full_url = link if link.startswith("https") else f"https://www.lemonde.fr{link}"
        articles.append({"title": clean_title, "url": full_url, "description": ""})
    return articles[:10]

def get_lemonde_description(article):
    """Ajoute la description pour un article du Monde."""
    html_content = fetch_html(article["url"])
    desc_match = LEMONDE_DESCRIPTION_REGEX.search(html_content)
    if desc_match:
        description = re.sub(r'\s+', ' ', desc_match.group(1) or desc_match.group(2)).strip()
        article["description"] = description
    else:
        article["description"] = "No description found"

# Fonctions spécifiques à Midi Madagasikara
def get_midi_articles(category_url):
    """Récupère les articles de la catégorie pour Midi Madagasikara."""
    html_content = fetch_html(category_url)
    links = MIDI_ARTICLE_LINK_REGEX.findall(html_content)

    articles = []
    for link in links:
        articles.append({"title": "", "url": link, "description": ""})
    return articles[:4]

def get_midi_title_and_description(article):
    """Ajoute le titre et la description pour un article de Midi Madagasikara."""
    html_content = fetch_html(article["url"])
    title_match = MIDI_TITLE_REGEX.search(html_content)
    desc_match = MIDI_DESCRIPTION_REGEX.search(html_content)

    article["title"] = re.sub(r'\s+', ' ', title_match.group(1)).strip() if title_match else "No title found"
    article["description"] = re.sub(r'\s+', ' ', desc_match.group(1)).strip()[:500] if desc_match else "No description found"

# Execution principale
if __name__ == "__main__":
    # Catégories pour chaque journal
    newspapers = {
        "Le Monde": [
            {"url": "https://www.lemonde.fr/economie/", "name": "economie"},
            {"url": "https://www.lemonde.fr/international/", "name": "international"},
            {"url": "https://www.lemonde.fr/politique/", "name": "politique"},
            {"url": "https://www.lemonde.fr/societe/", "name": "societe"}
        ],
        "Midi Madagasikara": [
            {"url": "https://midi-madagasikara.mg/category/economie/", "name": "economie"},
            {"url": "https://midi-madagasikara.mg/category/monde/", "name": "monde"},
            {"url": "https://midi-madagasikara.mg/category/politique/", "name": "politique"},
            {"url": "https://midi-madagasikara.mg/category/societe/", "name": "societe"}
        ]
    }

    with open(global_csv_path, mode="a", encoding="utf-8", newline="") as global_file:
        global_writer = csv.writer(global_file, delimiter=";")
        for newspaper, categories in newspapers.items():
            for category in categories:
                print(f"Collecte des articles pour {newspaper}, catégorie : {category['name']}")
                if newspaper == "Le Monde":
                    articles = get_lemonde_articles(category["url"])
                    for article in articles:
                        get_lemonde_description(article)
                elif newspaper == "Midi Madagasikara":
                    articles = get_midi_articles(category["url"])
                    for article in articles:
                        get_midi_title_and_description(article)

                save_articles_to_csv(articles, category["name"], newspaper, global_writer)
                time.sleep(2)  # Pause entre les requêtes pour éviter les blocages



################## Creation des nuages de mots par Presse et par Categorie



import seaborn as sns

# Charger les données globales
file_path = './data/global_articles.csv'
data = pd.read_csv(file_path, delimiter=";", encoding="utf-8")

# Vérifier et afficher les premières lignes
print(data.head())

# Renommer les catégories pour regrouper Monde et International
data['Catégorie'] = data['Catégorie'].replace({'monde': 'international'})

# Regrouper les données par presse et catégorie
summary = data.groupby(['Presse', 'Catégorie']).size().reset_index(name='Nombre d\'articles')

# Filtrer pour ne conserver que les catégories pertinentes
categories_to_compare = ['international', 'politique', 'economie', 'societe']
summary = summary[summary['Catégorie'].isin(categories_to_compare)]

# Configurer le style des graphiques
sns.set(style="whitegrid")

# Créer un graphique en barres
plt.figure(figsize=(12, 6))
sns.barplot(
    x='Catégorie',
    y='Nombre d\'articles',
    hue='Presse',
    data=summary,
    palette='viridis'
)

# Ajouter des labels et un titre
plt.title('Comparaison des articles par presse et catégorie', fontsize=14)
plt.xlabel('Catégories', fontsize=12)
plt.ylabel('Nombre d\'articles', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Presse', fontsize=10, title_fontsize=12)
plt.tight_layout()

# Afficher ou sauvegarder le graphique
plt.savefig('./data/articles_comparison.png')  # Sauvegarde le graphique dans un fichier
plt.show()



import nltk
nltk.download('stopwords')

# Charger le fichier global
file_path = "data/global_articles.csv"  # Chemin du fichier global
data = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
print(data)

# Nettoyage de texte
def clean_text(text):
    """Nettoie le texte brut en enlevant les caractères spéciaux, chiffres, liens, etc."""
    text = re.sub(r"http\S+", "", text)  # Enlever les liens
    text = unidecode(text)  # Normaliser les caractères spéciaux (é -> e, ç -> c, etc.)
    text = text.lower()  # Convertir en minuscules
    text = re.sub(r"\s+", " ", text)  # Supprimer les espaces multiples
    return text.strip()

# Appliquer le nettoyage
#data["cleaned_description"] = data["Description"].fillna("").apply(clean_text)
data["cleaned_title"] = data["Titre"].fillna("").apply(clean_text)
# Charger les stopwords
stop_words = set(stopwords.words("french")).union({'a', 'fait', 'tout', 'ça', 'deux', "d'une", "d'un", 'une', 'un', 'ete', "qu'il'", "l'assassinat", "plus", "apres" })

def generate_wordcloud(text, title):
    """Génère un nuage de mots à partir du texte nettoyé."""
    wordcloud = WordCloud(
        width=800, height=400, background_color="white",
        stopwords=stop_words, colormap="viridis"
    ).generate(text)
    
    # Afficher le nuage de mots
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(title, fontsize=16)
    plt.axis("off")
    plt.show()

# Créer des nuages de mots par presse et catégorie
grouped_data = defaultdict(str)

for _, row in data.iterrows():
    key = (row["Presse"], row["Catégorie"])
    grouped_data[key] += " " + row["cleaned_title"]

for (newspaper, category), text in grouped_data.items():
    print(f"Nuage de mots pour {newspaper} - {category}")
    generate_wordcloud(text, f"{newspaper} - {category}")

















