# Future Roadmap & Improvement Ideas

These ideas are slated for future development cycles after SEMRAG v4 is completed.

## 1. Neural Re-ranking (Cross-Encoders)
- **Concept**: Use a second-stage re-ranker (e.g., BGE-Reranker) to refine the top-k vector/graph results.
- **Goal**: Higher precision and less noise in the final context.

## 2. Agentic Multi-hop Reasoning (Plan-and-Execute)
- **Concept**: A stateful LangGraph agent that can decide to perform multiple retrieval steps.
- **Goal**: Solve complex, multi-step queries that require deep discovery.

## 3. Automated RAG Evaluation (RAGAS / DeepEval)
- **Concept**: LLM-as-a-judge scoring for Faithfulness, Relevancy, and Precision.
- **Goal**: Quantitative quality monitoring for production deployments.

## 4. Multi-modal Ingestion
- **Concept**: Extract and index images, diagrams, and tables using CLIP or multi-modal LLMs.
- **Goal**: Support for technical documentation with rich visual data.
