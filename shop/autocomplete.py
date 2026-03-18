from collections import defaultdict


class TrieNode:
    """
    One node in the trie. Each node can have many children, one per character.
    We also store which product IDs have a title that "passes through" this node
    """
    __slots__ = ('children', 'product_ids')

    def __init__(self):
        self.children = defaultdict(TrieNode)  # char -> TrieNode
        self.product_ids = set()  # product IDs whose title has this node on its path


def build_trie(products):
    """
    Build a trie from all product titles (lowercased)

    For each product we walk the trie character by character and add that product's
    ID to every node along the path. So for example "laptop" adds the product to nodes
    for "l", "la", "lap", "lapt", "lapto", "laptop". That way when the user types
    "lap" we can follow the path and immediately get all products whose title
    starts with "lap" (e.g. "Laptop ASUS ...") without scanning all titles

    Returns the root node of the trie
    """
    root = TrieNode()
    for p in products:
        title_lower = (p.name or '').lower().strip()
        if not title_lower:
            continue
        node = root
        for char in title_lower:
            node = node.children[char]
            node.product_ids.add(p.id)
    return root


def get_suggestions(products, prefix, limit=10):
    """
    Return product suggestions whose title starts with "prefix" (case-insensitive)

    Steps:
    1. Build the trie from the given product list
    2. Walk from the root following each character of "prefix"
    3. If we hit a missing character, no product has that prefix -> return []
    4. Otherwise the node we land on has product_ids for all matching titles;
       we map those back to products and return up to "limit" items as
       [{id, title, slug}, ...]

    Note: We rebuild the trie on every call. TO DO: for very large catalogs we could
    cache the trie and invalidate when products change
    """
    if not products or not prefix or not prefix.strip():
        return []
    prefix = prefix.lower().strip()
    root = build_trie(products)
    node = root
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]
    product_by_id = {p.id: p for p in products}
    out = []
    for pid in node.product_ids:
        if len(out) >= limit:
            break
        p = product_by_id.get(pid)
        if p:
            out.append({'id': p.id, 'title': p.name, 'slug': p.slug})
    return out
