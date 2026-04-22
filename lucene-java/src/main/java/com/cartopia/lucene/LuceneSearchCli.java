package com.cartopia.lucene;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class LuceneSearchCli {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new IllegalArgumentException("Usage: java -jar lucene-search-cli.jar <input-json-path> <output-json-path>");
        }

        Path inputPath = Path.of(args[0]);
        Path outputPath = Path.of(args[1]);
        String rawInput = Files.readString(inputPath);

        Map<String, Object> payload = MAPPER.readValue(rawInput, new TypeReference<>() {});
        String queryText = ((String) payload.getOrDefault("query", "")).trim();
        String scoreOrder = ((String) payload.getOrDefault("score_order", "desc")).trim().toLowerCase();
        List<Map<String, Object>> docs = (List<Map<String, Object>>) payload.getOrDefault("documents", new ArrayList<>());

        List<Map<String, Object>> results = runLuceneSearch(docs, queryText, scoreOrder);
        MAPPER.writeValue(outputPath.toFile(), results);
    }

    private static List<Map<String, Object>> runLuceneSearch(List<Map<String, Object>> docs, String queryText, String scoreOrder) throws Exception {
        if (queryText.isBlank() || docs.isEmpty()) {
            return Collections.emptyList();
        }

        StandardAnalyzer analyzer = new StandardAnalyzer();
        Directory directory = new RAMDirectory();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        config.setSimilarity(new BM25Similarity());

        try (IndexWriter writer = new IndexWriter(directory, config)) {
            for (Map<String, Object> row : docs) {
                int id = ((Number) row.get("id")).intValue();
                String text = String.valueOf(row.getOrDefault("text", ""));

                Document doc = new Document();
                doc.add(new StoredField("id", id));
                doc.add(new TextField("spec", text, Field.Store.NO));
                writer.addDocument(doc);
            }
        }

        List<Map<String, Object>> results = new ArrayList<>();
        try (DirectoryReader reader = DirectoryReader.open(directory)) {
            IndexSearcher searcher = new IndexSearcher(reader);
            searcher.setSimilarity(new BM25Similarity());

            QueryParser parser = new QueryParser("spec", analyzer);
            Query query = parser.parse(QueryParser.escape(queryText));
            TopDocs topDocs = searcher.search(query, docs.size());

            for (ScoreDoc scoreDoc : topDocs.scoreDocs) {
                Document doc = searcher.doc(scoreDoc.doc);
                int productId = doc.getField("id").numericValue().intValue();
                float score = scoreDoc.score;
                if (score <= 0f) {
                    continue;
                }

                Map<String, Object> item = new HashMap<>();
                item.put("id", productId);
                item.put("score", score);
                results.add(item);
            }
        } finally {
            directory.close();
        }

        if ("asc".equals(scoreOrder)) {
            results.sort((a, b) -> Double.compare(
                ((Number) a.get("score")).doubleValue(),
                ((Number) b.get("score")).doubleValue()
            ));
        }

        return results;
    }
}
