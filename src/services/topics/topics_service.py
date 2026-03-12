import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_topics(sentences, n_topics=5, n_keywords=5):
    sentences = [s for s in sentences if len(s.strip()) > 10]

    if len(sentences) == 0:
        return []

    if len(sentences) < n_topics:
        n_topics = len(sentences)

    embeddings = model.encode(sentences)

    kmeans = KMeans(n_clusters=n_topics, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    clusters = {}

    for sentence, label in zip(sentences, labels):
        clusters.setdefault(label, []).append(sentence)

    topics = []

    for cluster_sentences in clusters.values():
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)

        tfidf = vectorizer.fit_transform(cluster_sentences)
        feature_names = np.array(vectorizer.get_feature_names_out())

        scores = tfidf.sum(axis=0).A1
        top_words = feature_names[scores.argsort()[-n_keywords:]][::-1]

        topics.append(top_words.tolist())

    return topics
