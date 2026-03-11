"""
BM25 (simplified) search over product titles.
"""
import re # regular expressions
import math
from collections import defaultdict # defaultdict is a dictionary that will return a default value for a key that is not found


def tokenize(text):
    """Lowercase and split into words (alphanumeric)."""
    if not text:
        return []
   # find all words in the text, make them lowercase and return them as a list
    return re.findall(r'\w+', text.lower()) # regex, w means word, + means one or more


def build_index(products):
    """
    Build a BM25 index from a list of products (each with .id, .name).
    Returns (doc_lengths, term_doc_freq, term_freqs, N, avgdl).
    """
    doc_lengths = {}
    term_freqs = defaultdict(lambda: defaultdict(int))  # product_id -> term -> count
    doc_freq = defaultdict(int)  # term -> number of docs containing it

    for p in products:
        terms = tokenize(p.name) # tokenize the product name
        doc_lengths[p.id] = len(terms) # how many terms are in the product name
        seen = set() # set is a collection of unique elements
        for t in terms:
            term_freqs[p.id][t] += 1 # count the number of times the term appears in the product name (frequency vector)
            if t not in seen:
                seen.add(t)
                doc_freq[t] += 1 # document frequency for the term

    N = len(products) # number of products
    avgdl = sum(doc_lengths.values()) / N if N else 0 # average document length
    return doc_lengths, term_freqs, doc_freq, N, avgdl


def bm25_score(query_terms, product_id, doc_lengths, term_freqs, doc_freq, N, avgdl, k1 = 1.5, b =0.75):
    """
    BM25 score for one document (product) given query terms.
    IDF(t) = log((N - n_t + 0.5) / (n_t + 0.5) + 1) - inverse document frequency (bigger score if the term is rare), where
        N is the number of products, n_t is the number of products containing the term t
   
    score = sum_t (IDF(t) * (f(t,D) * (k1+1)) / (f(t,D) + k1 * (1 - b + b * |D|/avgdl))) - score for the product, where
        |D| is the length of the product
        avgdl is the average document length
        k1 and b are parameters that control the importance of the term frequency and the document length (tuning parameters)
        IDF(t) is the inverse document frequency of the term t
        f(t,D) is the frequency of the term t in the product D

    It's an improvement over the TF-IDF score because it takes into account the length of the product. For example, 
    a product with a long name will have a lower score than a product with a short name, even if the terms in the query are the same.
    """
    if avgdl <= 0:
        return 0.0
    dl = doc_lengths.get(product_id, 0) # length of the product
    score = 0.0
    for t in query_terms:
        n_t = doc_freq.get(t, 0) # number of products containing the term t
        idf = math.log((N - n_t + 0.5) / (n_t + 0.5) + 1.0)
        f_td = term_freqs.get(product_id, {}).get(t, 0) # frequency of the term t in the product
        if f_td == 0:
            continue
        denom = f_td + k1 * (1 - b + b * dl / avgdl)
        score += idf * (f_td * (k1 + 1)) / denom
    return score


def search_products_bm25(products, query_string):
    """
    Search products by title using BM25 (simplified).
    Returns list of (product, score) for products that have at least one query term in the title,
    sorted by score descending.
    """
    if not products or not query_string or not query_string.strip():
        return []

    query_terms = tokenize(query_string.strip())
    if not query_terms:
        return []

    doc_lengths, term_freqs, doc_freq, N, avgdl = build_index(products)
    product_by_id = {p.id: p for p in products} # dictionary of products by id

    scored = []
    for pid in doc_lengths: # iterate over the products
        # check if the product contains any of the query terms
        if any(term_freqs.get(pid, {}).get(t, 0) > 0 for t in query_terms):
            s = bm25_score(query_terms, pid, doc_lengths, term_freqs, doc_freq, N, avgdl) # calculate the score for the product
            if s > 0:
                scored.append((product_by_id[pid], s))

    scored.sort(key=lambda x: -x[1]) # sort the products by score descending
    return [p for p, _ in scored] # return a list of the products, sorted by score descending
