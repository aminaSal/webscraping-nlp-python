
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
