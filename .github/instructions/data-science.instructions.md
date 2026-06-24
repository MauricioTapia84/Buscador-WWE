# Data Science Agent Instructions

Purpose: These instructions guide the `data-science` agent on which technologies to consider, recommended workflows, and boundaries when operating in this repository.

Primary technologies to consider:
- Hugging Face Transformers (inference and fine-tuning)
- sentence-transformers for embeddings
- PyTorch and fastai for prototyping/training
- Scikit-learn / XGBoost / LightGBM for tabular baselines
- Vector DBs: PGVector, Milvus, or Pinecone for semantic search
- Model export: TorchScript, ONNX, or Hugging Face Hub for artifacts

Workflows:
1. Data discovery: scan `wrestling-pipeline/data/raw` and `data/processed` for dataset candidates.
2. Prototype: create a small notebook and requirements under `wrestling-pipeline/ml/experiments/<name>`.
3. Evaluate: produce metrics and a short evaluation report in `ml/experiments/<name>/REPORT.md`.
4. Export: provide a `Dockerfile.inference` and `serve.py` that loads the exported model.

Safety & boundaries:
- Do not commit large dataset files (>50MB) to the repo; instead reference external storage or add download scripts.
- Ask the user before adding new heavyweight dependencies to top-level `requirements.txt`.
- Request explicit permission before adding CI workflows or pushing branches.

Examples of actionable tasks the agent can create:
- `wrestling-pipeline/ml/experiments/embeddings/` with `notebook.ipynb`, `train.py`, `requirements.txt`, `Dockerfile.inference`.
- Minimal inference API: `wrestling-pipeline/ml/serve/` with `app.py` (FastAPI) and `Dockerfile`.

Decision heuristics:
- If task is semantic search or RAG → prefer sentence-transformers + vector DB.
- If task is image classification with small dataset → fastai transfer learning.
- If task is text classification or NER and needs SOTA → Hugging Face Transformers.

Authorization:
- The agent must prompt the user before making commits or opening PRs.
