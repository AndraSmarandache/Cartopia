"""
Similar product recommendations using TF-IDF and cosine similarity.

Idea: turn each product's text (name + description + specs) into a vector of word
weights (TF-IDF). Products with similar wording have similar vectors. We measure
similarity with the cosine of the angle between vectors (1 = identical, 0 = orthogonal).
Then we return the top_k other products whose vectors are closest to the current product.

Used on the product detail page for the "Similar products" section.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def _tokenize(text):
    """Simple tokenization: lowercase, keep only alphanumeric words."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', re.findall(r'\w+', (text or '').lower()))


def get_product_text(product):
    """
    Concatenate all searchable text for a product into one string
    TF-IDF will tokenize this and assign weights; more text = more chance to match
    """
    parts = [
        product.name or '',
        product.description or '',
        product.specifications or '',
    ]
    return ' '.join(parts)


def get_similar_products(product, all_products, top_k=4):
    """
    Return the top_k products most similar to "product" by text similarity

    Steps:
    1. Build one text "blob" per product (name + description + specifications)
    2. TF-IDF vectorizer: converts each "blob" to a vector of term weights
       - TF = how often the term appears in this document
       - IDF = how rare the term is across all documents (rare terms get higher weight)
       - stop_words = 'english' removes "the", "and", etc. max_features caps vocabulary size
    3. cosine_similarity(tfidf) gives a matrix: sim[i,j] = similarity between doc i and j
    4. We take the row for our product (idx), sort other products by score descending,
       skip self and zero/negative scores, and return the first top_k Product instances
    """
    if not all_products or len(all_products) < 2:
        return []
    texts = [get_product_text(p) for p in all_products]
    product_ids = [p.id for p in all_products]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    try:
        tfidf = vectorizer.fit_transform(texts)
    except Exception:
        return []
    # Shape: (n_products, n_features) -> (n_products, n_products) similarity matrix
    sim = cosine_similarity(tfidf)
    idx = product_ids.index(product.id)
    scores = list(enumerate(sim[idx]))  # (index, similarity_score) for each product
    scores.sort(key=lambda x: -x[1]) # sort by similarity score descending
    out = []
    for i, score in scores:
        if i == idx or score <= 0:
            continue
        out.append(all_products[i])
        if len(out) >= top_k:
            break
    return out
