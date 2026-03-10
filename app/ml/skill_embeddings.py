"""Skill / technology vector embeddings using TF-IDF.

Converts technology names plus short ecosystem descriptions into TF-IDF
vectors, then exposes cosine-similarity helpers that the recommender uses
to measure how "close" a user's skill profile is to each candidate technology.
"""

import logging

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Each technology is described with a short bag-of-words document that
# captures its domain, use-cases and related concepts.  This acts as
# the "corpus" for TF-IDF vectorisation.
TECHNOLOGY_DESCRIPTIONS: dict[str, str] = {
    # AI / ML
    "LangChain": "python ai llm orchestration openai langchain agents chains retrieval augmented generation",
    "OpenAI": "ai llm gpt openai api machine learning natural language processing",
    "ChromaDB": "vector database ai embeddings similarity search chromadb",
    "Qdrant": "vector database ai embeddings similarity search qdrant rust",
    "Hugging Face": "ai machine learning transformers nlp hugging face models",
    "PyTorch": "deep learning machine learning pytorch neural networks ai python",
    "Tiktoken": "tokenizer openai tiktoken encoding bpe ai",
    "DuckDB": "analytics database olap sql duckdb embedded",
    "CUDA": "gpu computing nvidia cuda parallel deep learning",
    "LangGraph": "ai orchestration agents langchain langgraph graph workflows",
    "TensorFlow": "deep learning machine learning tensorflow neural networks ai google python",
    "Keras": "deep learning keras neural network api high-level python",
    "scikit-learn": "machine learning python scikit-learn classification clustering regression",
    "MLflow": "mlops machine learning lifecycle tracking experiment mlflow deployment",
    "Ollama": "local llm inference ollama open source ai models self-hosted",
    "LlamaIndex": "ai data framework llm rag retrieval augmented generation indexing",
    "Stable Diffusion": "generative ai image generation diffusion models stable diffusion",
    "Weaviate": "vector database ai search weaviate graphql semantic",
    "Milvus": "vector database ai embeddings similarity search milvus cloud native",
    # Backend
    "FastAPI": "python web framework fastapi async rest api backend pydantic",
    "Pydantic": "python data validation pydantic schemas typing backend",
    "Uvicorn": "python asgi server uvicorn async web",
    "Starlette": "python asgi web framework starlette async",
    "SQLAlchemy": "python orm database sqlalchemy sql backend",
    "Django": "python web framework django backend orm admin",
    "Celery": "python task queue celery async distributed backend",
    "PostgreSQL": "database postgresql sql relational backend",
    "Flask": "python web framework flask micro backend",
    "Jinja2": "python template engine jinja2 web",
    "Werkzeug": "python wsgi utilities werkzeug web",
    "Express.js": "javascript node web framework express backend rest api",
    "NestJS": "typescript node framework nestjs backend enterprise angular-inspired",
    "Spring Boot": "java web framework spring boot backend enterprise microservices",
    "Gin": "go web framework gin backend fast http rest api",
    "Ruby on Rails": "ruby web framework rails backend full-stack mvc convention",
    "Laravel": "php web framework laravel backend eloquent artisan",
    "ASP.NET Core": "dotnet csharp web framework aspnet core backend microsoft",
    "Hono": "web framework ultrafast edge workers typescript javascript hono",
    # Systems
    "Rust": "systems programming rust memory safety performance backend cli",
    "Tokio": "rust async runtime tokio networking",
    "Serde": "rust serialization serde json",
    "Actix": "rust web framework actix backend",
    "Hyper": "rust http hyper networking",
    "Go": "systems programming go golang concurrency goroutines backend cloud",
    "Zig": "systems programming zig low-level performance c alternative comptime",
    "Kotlin": "programming language kotlin jvm android jetbrains multiplatform",
    "TypeScript": "programming language typescript javascript types static analysis microsoft",
    # Frontend
    "React": "javascript frontend react ui components web spa",
    "Next.js": "javascript react framework nextjs ssr frontend web",
    "Redux": "javascript state management redux react frontend",
    "Vue": "javascript frontend vue ui components web spa",
    "Nuxt": "javascript vue framework nuxt ssr frontend web",
    "Vite": "javascript build tool vite frontend bundler fast",
    "Bun": "javascript runtime bun fast bundler backend frontend",
    "Elysia": "typescript web framework elysia bun backend",
    "Vercel": "cloud platform vercel hosting frontend deployment",
    "Angular": "typescript frontend angular framework spa enterprise google",
    "Svelte": "javascript frontend svelte compiler ui components web reactive",
    "Remix": "react web framework remix ssr nested routes full-stack",
    "Astro": "web framework astro static site islands partial hydration content",
    "SolidJS": "javascript frontend solidjs reactive ui fine-grained reactivity",
    "htmx": "html hypermedia htmx ajax frontend minimal javascript",
    "Tailwind CSS": "css utility-first framework tailwind styling frontend responsive",
    # Databases
    "MongoDB": "database mongodb nosql document store json flexible schema",
    "Redis": "database redis cache key-value in-memory data structure",
    "Elasticsearch": "search engine elasticsearch full-text analytics distributed lucene",
    "Supabase": "backend as service supabase postgresql auth storage realtime",
    "Prisma": "orm prisma typescript database node schema migrations type-safe",
    "Drizzle ORM": "orm drizzle typescript sql database node lightweight type-safe",
    # DevOps
    "Docker": "containers docker devops deployment virtualisation",
    "Kubernetes": "orchestration kubernetes k8s devops containers cloud",
    "Helm": "kubernetes package manager helm devops charts",
    "Terraform": "infrastructure as code terraform devops cloud provisioning",
    "AWS": "cloud provider aws devops infrastructure",
    "Pulumi": "infrastructure as code pulumi devops cloud",
    "GitHub Actions": "ci cd github actions devops automation pipelines",
    "Ansible": "automation ansible devops configuration management provisioning",
    "ArgoCD": "gitops argocd kubernetes continuous delivery deployment devops",
    "Grafana": "monitoring visualization grafana dashboards metrics observability",
    "Prometheus": "monitoring metrics prometheus time-series alerting devops",
    # Mobile
    "Flutter": "mobile cross-platform flutter dart ui google ios android",
    "React Native": "mobile cross-platform react native javascript ios android",
    # Runtime / Tooling
    "Deno": "javascript typescript runtime deno secure modern node alternative",
    "Node.js": "javascript runtime node server backend async event-driven",
    "Tauri": "desktop app framework tauri rust webview lightweight electron alternative",
    "Electron": "desktop app framework electron chromium node cross-platform",
}


class SkillEmbedder:
    """Build TF-IDF embeddings for technologies and compute similarities."""

    def __init__(self) -> None:
        self._tech_names: list[str] = sorted(TECHNOLOGY_DESCRIPTIONS.keys())
        corpus = [TECHNOLOGY_DESCRIPTIONS[t] for t in self._tech_names]

        self._vectorizer = TfidfVectorizer()
        self._tech_matrix = self._vectorizer.fit_transform(corpus)

        logger.info("SkillEmbedder initialised with %d technologies.", len(self._tech_names))

    @property
    def technology_names(self) -> list[str]:
        return list(self._tech_names)

    def skill_similarity(self, user_skills: list[str]) -> dict[str, float]:
        """Return cosine similarity of a user skill profile to every technology.

        ``user_skills`` is a list of technology / keyword strings the user
        already knows (e.g. ``["Python", "FastAPI", "Docker"]``).  These
        are joined into a single pseudo-document and compared against the
        technology corpus.
        """
        if not user_skills:
            return {t: 0.0 for t in self._tech_names}

        # Build a pseudo-document from user skills, enriching with their
        # descriptions when available so the TF-IDF vector is richer.
        parts: list[str] = []
        for skill in user_skills:
            parts.append(skill.lower())
            # If the skill matches a known tech, fold in its description
            for tech, desc in TECHNOLOGY_DESCRIPTIONS.items():
                if skill.lower() == tech.lower():
                    parts.append(desc)
                    break

        user_doc = " ".join(parts)
        user_vec = self._vectorizer.transform([user_doc])

        sims = cosine_similarity(user_vec, self._tech_matrix).flatten()

        return {
            self._tech_names[i]: round(float(sims[i]), 6)
            for i in range(len(self._tech_names))
        }
