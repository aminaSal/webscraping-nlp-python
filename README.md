# webscraping and NLP analysis with python
# Overview

This project automates the extraction and textual analysis of news articles from two media outlets: Le Monde (France) and Midi Madagasikara (Madagascar).
It includes web scraping, data cleaning, dataset construction, statistical comparison, and NLP-based insights extracted from article titles using word clouds and keyword analysis.
The goal is to understand each newspaper’s publication patterns, editorial priorities, and dominant themes.

# Technologies & Libraries

- Python
- requests, re, time, datetime
- pandas, csv, os
- unidecode for text normalization
- matplotlib for visualisation
- wordcloud
- nltk (stopwords)
- collections.defaultdict

# 📁 Repository Structure

webscraping-nlp/
├── data/                    # Extracted articles (CSV + article texts)
├── notebooks/               # notebooks (analysis, visuals)
├── visuals/                 # Word clouds
├── src/
    ├── post.py              # Web scraping logic for both newspapers, Cleaning + HTML entity correction, nlp_analysis, Word clouds & text processing
├── README.md
