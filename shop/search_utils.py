"""
BM25 (simplified) search over product titles.
Supports: exact terms, substring matching (e.g. "lap" in "laptop"),
and Levenshtein (fuzzy) for typo tolerance.
"""
import re
import math
from collections import defaultdict


def levenshtein_distance(a, b):
    """
    Edit distance between two strings (insert, delete, substitute).
    Used for fuzzy search: e.g. "laptp" matches "laptop".
    """
    if not a:
        return len(b)
    if not b:
        return len(a)
    # dynamic programming: dp[i][j] = distance for a[:i], b[:j]
    n, m = len(a), len(b)
    prev = list(range(m + 1))  # row 0: distance from "" to b[:j]
    for i in range(1, n + 1):
        curr = [i]
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1  # substitute cost
            curr.append(min(
                prev[j] + 1,      # delete a[i-1]
                curr[j - 1] + 1,  # insert b[j-1]
                prev[j - 1] + cost,  # substitute or match
            ))
        prev = curr
    return prev[m]


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


def _substring_tf_df(products, query_terms):
    """
    Substring matching for the BM25 score (used for the search).
    It's an improvement over the exact term match because it allows partial matches.
    For example, "lap" matches "laptop".
    """
    doc_lengths = {}
    term_freqs = defaultdict(lambda: defaultdict(int))
    doc_freq = defaultdict(int)

    for p in products:
        terms = tokenize(p.name)
        doc_lengths[p.id] = len(terms)
        for q in query_terms:  # iterate over the query terms
            count = sum(1 for t in terms if q in t)  # count how many product terms contain the query term as substring
            if count > 0:
                term_freqs[p.id][q] = count  # frequency of the query term in the product
                doc_freq[q] += 1  # document frequency for the query term

    N = len(products)
    avgdl = sum(doc_lengths.values()) / N if N else 0
    return doc_lengths, term_freqs, doc_freq, N, avgdl


def _substring_and_fuzzy_tf_df(products, query_terms, max_levenshtein=2):
    """
    Substring + Levenshtein fuzzy: a product term matches query term q if
    - q is a substring of the term (e.g. "lap" in "laptop"), or
    - Levenshtein distance <= max_levenshtein (typo tolerance), only when query term
      has length >= 3 and product term length is close to query length
    """
    doc_lengths = {}
    term_freqs = defaultdict(lambda: defaultdict(int))
    doc_freq = defaultdict(int)

    for p in products:
        terms = tokenize(p.name)
        doc_lengths[p.id] = len(terms)
        for q in query_terms:
            count = 0
            for t in terms:
                if q in t:
                    # substring match: e.g. "lap" in "laptop"
                    count += 1
                elif max_levenshtein and len(q) >= 3 and len(t) >= 2:
                    # fuzzy only for longer query terms and similar-length product terms (avoid false matches)
                    if abs(len(t) - len(q)) <= max_levenshtein:
                        d = levenshtein_distance(q, t)
                        if d <= max_levenshtein:
                            count += 1  # typo tolerance: e.g. "laptp" matches "laptop"
            if count > 0:
                term_freqs[p.id][q] = count
                doc_freq[q] += 1

    N = len(products)
    avgdl = sum(doc_lengths.values()) / N if N else 0
    return doc_lengths, term_freqs, doc_freq, N, avgdl


def search_products_bm25(products, query_string, substring_matching=False, fuzzy_typo=True, max_levenshtein=2):
    """
    Search products by title using BM25 (simplified) or substring matching
    Returns a list of products that have at least one query term in the title, sorted by score descending
    """
    if not products or not query_string or not query_string.strip():
        return []

    query_terms = tokenize(query_string.strip())
    if not query_terms:
        return []

    # choose index: exact terms, substring only, or substring + Levenshtein fuzzy
    if substring_matching:
        if fuzzy_typo and max_levenshtein:
            doc_lengths, term_freqs, doc_freq, N, avgdl = _substring_and_fuzzy_tf_df(
                products, query_terms, max_levenshtein=max_levenshtein
            )
        else:
            doc_lengths, term_freqs, doc_freq, N, avgdl = _substring_tf_df(products, query_terms)
    else:
        doc_lengths, term_freqs, doc_freq, N, avgdl = build_index(products)

    product_by_id = {p.id: p for p in products} # dictionary of products by id

    scored = [] # list of products and their scores
    for pid in doc_lengths: # iterate over the products
        # check if the product has at least one query term in the title
        if any(term_freqs.get(pid, {}).get(q, 0) > 0 for q in query_terms): 
            s = bm25_score(query_terms, pid, doc_lengths, term_freqs, doc_freq, N, avgdl) # calculate the score for the product
            if s > 0:
                scored.append((product_by_id[pid], s))

    scored.sort(key=lambda x: -x[1]) # sort the products by score descending
    return [p for p, _ in scored] # return a list of the products, sorted by score descending
