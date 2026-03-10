"""Technology Registry — seed data and DB helpers.

Provides a comprehensive seed list of technologies spanning AI/ML, backend,
frontend, systems, databases, DevOps, mobile, and runtime/tooling domains.
All collectors read from the ``tracked_technologies`` table at runtime so the
list can grow dynamically without code changes.
"""

import logging
from sqlalchemy.orm import Session

from app.models.models import TrackedTechnology

logger = logging.getLogger(__name__)

# ── Comprehensive seed catalogue ──────────────────────────────────
# Each entry maps to one GitHub repository and one StackOverflow tag.

SEED_TECHNOLOGIES: list[dict] = [
    # ── AI / ML ───────────────────────────────────────────────────
    {"name": "LangChain", "github_repo": "langchain-ai/langchain", "so_tag": "langchain", "category": "AI",
     "description": "python ai llm orchestration openai langchain agents chains retrieval augmented generation"},
    {"name": "PyTorch", "github_repo": "pytorch/pytorch", "so_tag": "pytorch", "category": "AI",
     "description": "deep learning machine learning pytorch neural networks ai python gpu"},
    {"name": "TensorFlow", "github_repo": "tensorflow/tensorflow", "so_tag": "tensorflow", "category": "AI",
     "description": "deep learning machine learning tensorflow neural networks ai google python"},
    {"name": "Hugging Face", "github_repo": "huggingface/transformers", "so_tag": "huggingface-transformers", "category": "AI",
     "description": "ai machine learning transformers nlp hugging face models pretrained"},
    {"name": "OpenAI", "github_repo": "openai/openai-python", "so_tag": "openai-api", "category": "AI",
     "description": "ai llm gpt openai api machine learning natural language processing"},
    {"name": "Ollama", "github_repo": "ollama/ollama", "so_tag": "ollama", "category": "AI",
     "description": "local llm inference ollama open source ai models self-hosted"},
    {"name": "LlamaIndex", "github_repo": "run-llama/llama_index", "so_tag": "llama-index", "category": "AI",
     "description": "ai data framework llm rag retrieval augmented generation indexing"},
    {"name": "scikit-learn", "github_repo": "scikit-learn/scikit-learn", "so_tag": "scikit-learn", "category": "AI",
     "description": "machine learning python scikit-learn classification clustering regression"},
    {"name": "Keras", "github_repo": "keras-team/keras", "so_tag": "keras", "category": "AI",
     "description": "deep learning keras neural network api high-level python"},
    {"name": "MLflow", "github_repo": "mlflow/mlflow", "so_tag": "mlflow", "category": "AI",
     "description": "mlops machine learning lifecycle tracking experiment mlflow deployment"},
    {"name": "Stable Diffusion", "github_repo": "CompVis/stable-diffusion", "so_tag": "stable-diffusion", "category": "AI",
     "description": "generative ai image generation diffusion models stable diffusion"},
    {"name": "Qdrant", "github_repo": "qdrant/qdrant", "so_tag": "qdrant", "category": "AI",
     "description": "vector database ai embeddings similarity search qdrant rust"},
    {"name": "ChromaDB", "github_repo": "chroma-core/chroma", "so_tag": "chromadb", "category": "AI",
     "description": "vector database ai embeddings similarity search chromadb open source"},
    {"name": "Weaviate", "github_repo": "weaviate/weaviate", "so_tag": "weaviate", "category": "AI",
     "description": "vector database ai search weaviate graphql semantic"},
    {"name": "Milvus", "github_repo": "milvus-io/milvus", "so_tag": "milvus", "category": "AI",
     "description": "vector database ai embeddings similarity search milvus cloud native"},

    # ── Backend ───────────────────────────────────────────────────
    {"name": "FastAPI", "github_repo": "fastapi/fastapi", "so_tag": "fastapi", "category": "Backend",
     "description": "python web framework fastapi async rest api backend pydantic"},
    {"name": "Django", "github_repo": "django/django", "so_tag": "django", "category": "Backend",
     "description": "python web framework django backend orm admin full-stack"},
    {"name": "Flask", "github_repo": "pallets/flask", "so_tag": "flask", "category": "Backend",
     "description": "python web framework flask micro backend lightweight"},
    {"name": "Express.js", "github_repo": "expressjs/express", "so_tag": "express", "category": "Backend",
     "description": "javascript node web framework express backend rest api"},
    {"name": "NestJS", "github_repo": "nestjs/nest", "so_tag": "nestjs", "category": "Backend",
     "description": "typescript node framework nestjs backend enterprise angular-inspired"},
    {"name": "Spring Boot", "github_repo": "spring-projects/spring-boot", "so_tag": "spring-boot", "category": "Backend",
     "description": "java web framework spring boot backend enterprise microservices"},
    {"name": "Gin", "github_repo": "gin-gonic/gin", "so_tag": "go-gin", "category": "Backend",
     "description": "go web framework gin backend fast http rest api"},
    {"name": "Ruby on Rails", "github_repo": "rails/rails", "so_tag": "ruby-on-rails", "category": "Backend",
     "description": "ruby web framework rails backend full-stack mvc convention"},
    {"name": "Laravel", "github_repo": "laravel/framework", "so_tag": "laravel", "category": "Backend",
     "description": "php web framework laravel backend eloquent artisan"},
    {"name": "ASP.NET Core", "github_repo": "dotnet/aspnetcore", "so_tag": "asp.net-core", "category": "Backend",
     "description": "dotnet csharp web framework aspnet core backend microsoft"},
    {"name": "Hono", "github_repo": "honojs/hono", "so_tag": "hono", "category": "Backend",
     "description": "web framework ultrafast edge workers typescript javascript hono"},

    # ── Frontend ──────────────────────────────────────────────────
    {"name": "React", "github_repo": "facebook/react", "so_tag": "reactjs", "category": "Frontend",
     "description": "javascript frontend react ui components web spa virtual dom"},
    {"name": "Vue", "github_repo": "vuejs/core", "so_tag": "vue.js", "category": "Frontend",
     "description": "javascript frontend vue ui components web spa reactive"},
    {"name": "Angular", "github_repo": "angular/angular", "so_tag": "angular", "category": "Frontend",
     "description": "typescript frontend angular framework spa enterprise google"},
    {"name": "Svelte", "github_repo": "sveltejs/svelte", "so_tag": "svelte", "category": "Frontend",
     "description": "javascript frontend svelte compiler ui components web reactive"},
    {"name": "Next.js", "github_repo": "vercel/next.js", "so_tag": "next.js", "category": "Frontend",
     "description": "javascript react framework nextjs ssr ssg frontend web fullstack"},
    {"name": "Nuxt", "github_repo": "nuxt/nuxt", "so_tag": "nuxt.js", "category": "Frontend",
     "description": "javascript vue framework nuxt ssr ssg frontend web"},
    {"name": "Remix", "github_repo": "remix-run/remix", "so_tag": "remix", "category": "Frontend",
     "description": "react web framework remix ssr nested routes full-stack"},
    {"name": "Astro", "github_repo": "withastro/astro", "so_tag": "astro", "category": "Frontend",
     "description": "web framework astro static site islands partial hydration content"},
    {"name": "SolidJS", "github_repo": "solidjs/solid", "so_tag": "solidjs", "category": "Frontend",
     "description": "javascript frontend solidjs reactive ui fine-grained reactivity"},
    {"name": "htmx", "github_repo": "bigskysoftware/htmx", "so_tag": "htmx", "category": "Frontend",
     "description": "html hypermedia htmx ajax frontend minimal javascript"},
    {"name": "Tailwind CSS", "github_repo": "tailwindlabs/tailwindcss", "so_tag": "tailwind-css", "category": "Frontend",
     "description": "css utility-first framework tailwind styling frontend responsive"},

    # ── Systems / Languages ───────────────────────────────────────
    {"name": "Rust", "github_repo": "rust-lang/rust", "so_tag": "rust", "category": "Systems",
     "description": "systems programming rust memory safety performance backend cli wasm"},
    {"name": "Go", "github_repo": "golang/go", "so_tag": "go", "category": "Systems",
     "description": "systems programming go golang concurrency goroutines backend cloud"},
    {"name": "Zig", "github_repo": "ziglang/zig", "so_tag": "zig", "category": "Systems",
     "description": "systems programming zig low-level performance c alternative comptime"},
    {"name": "Kotlin", "github_repo": "JetBrains/kotlin", "so_tag": "kotlin", "category": "Systems",
     "description": "programming language kotlin jvm android jetbrains multiplatform"},
    {"name": "TypeScript", "github_repo": "microsoft/TypeScript", "so_tag": "typescript", "category": "Systems",
     "description": "programming language typescript javascript types static analysis microsoft"},

    # ── Databases / Data ──────────────────────────────────────────
    {"name": "PostgreSQL", "github_repo": "postgres/postgres", "so_tag": "postgresql", "category": "Database",
     "description": "database postgresql sql relational acid backend open source"},
    {"name": "MongoDB", "github_repo": "mongodb/mongo", "so_tag": "mongodb", "category": "Database",
     "description": "database mongodb nosql document store json flexible schema"},
    {"name": "Redis", "github_repo": "redis/redis", "so_tag": "redis", "category": "Database",
     "description": "database redis cache key-value in-memory data structure"},
    {"name": "Elasticsearch", "github_repo": "elastic/elasticsearch", "so_tag": "elasticsearch", "category": "Database",
     "description": "search engine elasticsearch full-text analytics distributed lucene"},
    {"name": "Supabase", "github_repo": "supabase/supabase", "so_tag": "supabase", "category": "Database",
     "description": "backend as service supabase postgresql auth storage realtime firebase alternative"},
    {"name": "Prisma", "github_repo": "prisma/prisma", "so_tag": "prisma", "category": "Database",
     "description": "orm prisma typescript database node schema migrations type-safe"},
    {"name": "Drizzle ORM", "github_repo": "drizzle-team/drizzle-orm", "so_tag": "drizzle-orm", "category": "Database",
     "description": "orm drizzle typescript sql database node lightweight type-safe"},
    {"name": "SQLAlchemy", "github_repo": "sqlalchemy/sqlalchemy", "so_tag": "sqlalchemy", "category": "Database",
     "description": "python orm database sqlalchemy sql backend toolkit"},
    {"name": "DuckDB", "github_repo": "duckdb/duckdb", "so_tag": "duckdb", "category": "Database",
     "description": "analytics database olap sql duckdb embedded columnar fast"},

    # ── DevOps / Infra ────────────────────────────────────────────
    {"name": "Docker", "github_repo": "moby/moby", "so_tag": "docker", "category": "DevOps",
     "description": "containers docker devops deployment virtualisation packaging"},
    {"name": "Kubernetes", "github_repo": "kubernetes/kubernetes", "so_tag": "kubernetes", "category": "DevOps",
     "description": "orchestration kubernetes k8s devops containers cloud scaling"},
    {"name": "Terraform", "github_repo": "hashicorp/terraform", "so_tag": "terraform", "category": "DevOps",
     "description": "infrastructure as code terraform devops cloud provisioning hcl"},
    {"name": "Ansible", "github_repo": "ansible/ansible", "so_tag": "ansible", "category": "DevOps",
     "description": "automation ansible devops configuration management provisioning"},
    {"name": "GitHub Actions", "github_repo": "actions/runner", "so_tag": "github-actions", "category": "DevOps",
     "description": "ci cd github actions devops automation pipelines workflows"},
    {"name": "ArgoCD", "github_repo": "argoproj/argo-cd", "so_tag": "argocd", "category": "DevOps",
     "description": "gitops argocd kubernetes continuous delivery deployment devops"},
    {"name": "Grafana", "github_repo": "grafana/grafana", "so_tag": "grafana", "category": "DevOps",
     "description": "monitoring visualization grafana dashboards metrics observability"},
    {"name": "Prometheus", "github_repo": "prometheus/prometheus", "so_tag": "prometheus", "category": "DevOps",
     "description": "monitoring metrics prometheus time-series alerting devops"},

    # ── Mobile ────────────────────────────────────────────────────
    {"name": "Flutter", "github_repo": "flutter/flutter", "so_tag": "flutter", "category": "Mobile",
     "description": "mobile cross-platform flutter dart ui google ios android"},
    {"name": "React Native", "github_repo": "facebook/react-native", "so_tag": "react-native", "category": "Mobile",
     "description": "mobile cross-platform react native javascript ios android facebook"},

    # ── Runtime / Tooling ─────────────────────────────────────────
    {"name": "Bun", "github_repo": "oven-sh/bun", "so_tag": "bun", "category": "Runtime",
     "description": "javascript runtime bun fast bundler backend frontend package manager"},
    {"name": "Deno", "github_repo": "denoland/deno", "so_tag": "deno", "category": "Runtime",
     "description": "javascript typescript runtime deno secure modern node alternative"},
    {"name": "Node.js", "github_repo": "nodejs/node", "so_tag": "node.js", "category": "Runtime",
     "description": "javascript runtime node server backend async event-driven"},
    {"name": "Vite", "github_repo": "vitejs/vite", "so_tag": "vite", "category": "Runtime",
     "description": "javascript build tool vite frontend bundler fast dev server hmr"},
    {"name": "Tauri", "github_repo": "tauri-apps/tauri", "so_tag": "tauri", "category": "Runtime",
     "description": "desktop app framework tauri rust webview lightweight electron alternative"},
    {"name": "Electron", "github_repo": "electron/electron", "so_tag": "electron", "category": "Runtime",
     "description": "desktop app framework electron chromium node cross-platform"},
]


def get_active_technologies(db: Session) -> list[dict[str, str]]:
    """Return all active tracked technologies from the database."""
    techs = db.query(TrackedTechnology).filter(TrackedTechnology.is_active.is_(True)).all()
    return [
        {"name": t.name, "github_repo": t.github_repo, "so_tag": t.so_tag}
        for t in techs
    ]


def get_tracked_names(db: Session) -> set[str]:
    """Return the set of all active technology names."""
    rows = (
        db.query(TrackedTechnology.name)
        .filter(TrackedTechnology.is_active.is_(True))
        .all()
    )
    return {r[0] for r in rows}


def seed_technologies(db: Session) -> int:
    """Populate the tracked_technologies table if it is empty.

    Returns the number of technologies seeded.
    """
    existing = db.query(TrackedTechnology).count()
    if existing > 0:
        logger.info("Technology registry already has %d entries — skipping seed.", existing)
        return 0

    for tech in SEED_TECHNOLOGIES:
        db.add(TrackedTechnology(**tech))
    db.commit()

    count = len(SEED_TECHNOLOGIES)
    logger.info("Seeded %d technologies into the registry.", count)
    return count
