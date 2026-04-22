import json
import subprocess
import tempfile
from pathlib import Path
from pypdf import PdfReader


ROOT_DIR = Path(__file__).resolve().parent.parent
LUCENE_JAR_PATH = ROOT_DIR / "lucene-java" / "target" / "lucene-search-cli.jar"


def _extract_spec_text_for_lucene(product):
    """
    Prefer PDF text for Lucene indexing when a descriptive PDF exists.
    Fall back to Product.specifications if PDF extraction fails or is unavailable.
    """
    pdf_field = getattr(product, "descriptive_pdf", None)
    if not pdf_field:
        return product.specifications or ""

    try:
        pdf_path = Path(pdf_field.path)
        if not pdf_path.exists():
            return product.specifications or ""

        reader = PdfReader(str(pdf_path))
        chunks = []
        for page in reader.pages:
            chunks.append((page.extract_text() or "").strip())

        text = " ".join(chunk for chunk in chunks if chunk).strip()
        return text or (product.specifications or "")
    except Exception:
        return product.specifications or ""


def _run_lucene_cli(documents, query_text, score_order):
    if not LUCENE_JAR_PATH.exists():
        raise RuntimeError(
            "Lucene Java jar was not found. Build it with: "
            "mvn -f lucene-java/pom.xml clean package"
        )

    payload = {
        "query": query_text,
        "score_order": score_order,
        "documents": documents,
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / "lucene-input.json"
        output_path = tmp_path / "lucene-output.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")

        # call the Java Lucene CLI to index and score this query
        subprocess.run(
            [
                "java",
                "-jar",
                str(LUCENE_JAR_PATH),
                str(input_path),
                str(output_path),
            ],
            cwd=str(ROOT_DIR),
            check=True,
            capture_output=True,
            text=True,
        )

        if not output_path.exists():
            return []
        return json.loads(output_path.read_text(encoding="utf-8"))


def search_specifications_lucene_style(products, query_text, score_order="desc"):
    normalized_query = (query_text or "").strip()
    if not normalized_query:
        return []

    documents = [
        {
            "id": product.id,
            "text": _extract_spec_text_for_lucene(product),
        }
        for product in products
    ]
    lucene_rows = _run_lucene_cli(documents, normalized_query, score_order)

    product_by_id = {product.id: product for product in products}
    results = []
    for row in lucene_rows:
        product = product_by_id.get(int(row["id"]))
        if not product:
            continue
        results.append(
            {
                "product": product,
                "score": float(row["score"]),
            }
        )
    return results


def get_lucene_scoring_note():
    return (
        "Apache Lucene Java computes BM25 scores over indexed specification text. "
        "Higher score means a better match for the query"
    )
