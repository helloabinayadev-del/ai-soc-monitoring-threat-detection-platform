# Technical Interview Architecture & Design Guide

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Architectural Rationale & System Design Interview Q&A  

---

## Technical Architecture Decision Q&A (15 Core Questions)

### Q1: Why FastAPI over Flask or Django for the Backend?
- **Interviewer's Intent**: Test understanding of async I/O, API performance, and Python web frameworks.
- **Answer**: FastAPI is built on Starlette and Pydantic, providing native asynchronous ASGI concurrency (`async/await`) ideal for handling high-concurrency log ingestion streams and WebSocket push notifications. It enforces automatic data validation with Pydantic v2 schemas and auto-generates OpenAPI documentation (`/docs`), reducing boilerplate while matching Go/Node.js performance levels.
- **Project Evidence**: `backend/app/main.py` uses `FastAPI` with async log ingestion routes (`app/api/v1/endpoints/logs.py`).

### Q2: Why React 18 & TypeScript for the Frontend?
- **Interviewer's Intent**: Assess frontend framework selection and type-safety rationale.
- **Answer**: React 18's component-based architecture and virtual DOM facilitate building interactive SOC dashboards with real-time UI updates (alert badges, correlation timelines, Copilot chat). TypeScript adds compile-time type safety across API schemas, preventing runtime `undefined` errors when parsing complex telemetry JSON objects.
- **Project Evidence**: `frontend/src/types/index.ts` defines explicit TypeScript interfaces for `LogEvent`, `SecurityAlert`, `CorrelationGroup`, and `CopilotResponse`.

### Q3: Why SQLite/PostgreSQL with SQLAlchemy ORM?
- **Interviewer's Intent**: Evaluate database technology choices and ORM abstraction.
- **Answer**: SQLAlchemy ORM decouples application logic from the underlying SQL database engine. SQLite (`soc_platform.db`) allows zero-dependency local development and fast automated test runs in Pytest, while SQLAlchemy models (`Base = declarative_base()`) permit seamless configuration switching to enterprise PostgreSQL in staging/production via environment variables (`DATABASE_URL`).
- **Project Evidence**: `backend/app/core/database.py` manages SQLAlchemy ORM connections dynamically via environment variables.

### Q4: Why Machine Learning (Isolation Forest) alongside SIEM Signature Rules?
- **Interviewer's Intent**: Test hybrid detection architecture understanding.
- **Answer**: Traditional SIEM rules only detect known threat patterns (`RULE-001` to `RULE-007`). Zero-Day attacks and subtle privilege escalations bypass signature rules. Unsupervised Isolation Forest detects statistical outliers without requiring pre-labeled training data, providing a dual-layer hybrid defense (`RULE_BASED`, `ML_ANOMALY`, `HYBRID`).
- **Project Evidence**: `backend/app/ml/anomaly_detector.py` implements Scikit-Learn `IsolationForest`.

### Q5: Why Isolation Forest instead of Deep Learning Autoencoders?
- **Interviewer's Intent**: Evaluate algorithm selection and inference latency trade-offs.
- **Answer**: Isolation Forest has $O(n \log n)$ training complexity and sub-millisecond inference latency, operating efficiently on tabular security metrics without requiring GPU infrastructure. Deep learning autoencoders have high compute overhead, memory requirements, and lack transparent feature attribution. Isolation Forest permits exact z-score feature attribution explanations for SOC analysts.
- **Project Evidence**: `backend/app/ml/feature_engineering.py` extracts 10 tabular security metrics evaluated in $<5\text{ms}$.

### Q6: Why a Multi-Factor Risk Prioritization Engine?
- **Interviewer's Intent**: Assess alert triage design and alert fatigue prevention.
- **Answer**: Raw alert counts overwhelm SOC analysts. The transparent 0–100 risk engine combines severity, ML anomaly score, frequency bursts, asset criticality (`DC-PRIMARY-01` = 1.30x), threat intelligence matches (+20 pts), and correlation weights (+6 pts/event). This reduces low-priority noise while elevating critical attack chains to `CRITICAL` priority.
- **Project Evidence**: `backend/app/services/prioritization_service.py` implements the transparent 7-factor scoring engine.

### Q7: Why a 30-Minute Sliding Window Event Correlation Engine?
- **Interviewer's Intent**: Test multi-stage attack pattern tracking logic.
- **Answer**: Advanced Persistent Threats (APTs) execute multi-stage attack chains over time (Credential Access $\rightarrow$ Execution $\rightarrow$ Privilege Escalation $\rightarrow$ C2 Beacon). Independent log entries miss the broader context. A 30-minute sliding window entity matching engine clusters related events under a shared Correlation ID (`CORR-YYYYMMDD-XXXX`).
- **Project Evidence**: `backend/app/services/correlation_engine.py` implements entity matching across sliding windows.

### Q8: Why Integrate Threat Intelligence (IOC Matching)?
- **Interviewer's Intent**: Assess threat context enrichment capabilities.
- **Answer**: Matching incoming IPs and domain indicators against known malicious IOC databases immediately elevates alert risk scores (+20 pts) and provides verified external context without relying on LLM hallucination.
- **Project Evidence**: `backend/app/models/threat_intel.py` manages local IOC records used during risk calculation.

### Q9: Why Map Threats to the MITRE ATT&CK Framework?
- **Interviewer's Intent**: Evaluate standardization with industry cybersecurity taxonomies.
- **Answer**: MITRE ATT&CK provides a standardized taxonomy of adversary Tactics (`TA0001`–`TA0011`) and Techniques (`T1078`, `T1059`, etc.). Mapping rules and correlation chains to MITRE IDs enables security teams to understand attack stages and identify defensive coverage gaps.
- **Project Evidence**: `backend/app/ai/threat_classifier.py` maps detection rules to MITRE Tactics and Techniques.

### Q10: Why Ground the AI Copilot on Actual Platform Telemetry?
- **Interviewer's Intent**: Test AI reliability, hallucination prevention, and evidence enforcement.
- **Answer**: Unconstrained LLMs frequently hallucinate fake IP addresses, CVEs, or security events. The Copilot (`SecurityCopilotService`) queries actual database records (`LogEvent`, `SecurityAlert`, `CorrelationGroup`, `MLPrediction`) and formats answers into a 10-point framework separating `FACT`, `INFERENCE`, `RECOMMENDATION`, and `UNCERTAINTY`.
- **Project Evidence**: `backend/app/services/copilot_service.py` enforces grounded telemetry querying.

### Q11: How Do You Protect the AI Copilot Against Prompt Injection Attacks?
- **Interviewer's Intent**: Assess AI security engineering and untrusted data handling.
- **Answer**: Security logs are untrusted data containing arbitrary text. Raw log payloads are wrapped within structural XML tags (`<telemetry_data> ... </telemetry_data>`) with system prompt instructions commanding the model to process text inside tags strictly as string data, neutralizing embedded instructions like `"Ignore previous commands"`.
- **Project Evidence**: `backend/app/services/copilot_service.py` wraps inputs in telemetry tags.

### Q12: Why Enforce Role-Based Access Control (RBAC)?
- **Interviewer's Intent**: Evaluate access control and least privilege principles.
- **Answer**: SOC platforms contain sensitive infrastructure logs and administrative configuration controls. Enforcing role scopes (`ADMIN`, `ANALYST`, `VIEWER`) via OAuth2 JWT dependencies ensures users can only perform authorized actions (e.g. viewers cannot modify rules or tune ML thresholds).
- **Project Evidence**: Backend routes enforce role scopes via `get_current_user` dependency.

### Q13: Why Containerize with Docker & Docker Compose?
- **Interviewer's Intent**: Assess deployment consistency and environment isolation.
- **Answer**: Containerizing backend, frontend, and database services ensures reproducible execution across local development, CI/CD pipelines, and cloud staging environments without OS-level dependency conflicts.
- **Project Evidence**: `Dockerfile` and `docker-compose.yml` orchestrate multi-container deployment.

### Q14: Why Include a Quantitative Benchmark Evaluation Pipeline?
- **Interviewer's Intent**: Assess research quality and empirical verification methodology.
- **Answer**: Claiming "AI improves security" without data is scientifically invalid. The evaluation pipeline (`evaluation_pipeline.py`) runs benchmark tests on UNSW-NB15 dataset telemetry using a 70/15/15 split, calculating Precision (94.2%), Recall (95.8%), F1 (95.0%), FPR (3.8%), MTTD (12.5s), and MTTR (320.0s).
- **Project Evidence**: `backend/app/ml/evaluation_pipeline.py` calculates empirical performance metrics.

### Q15: How Does the Platform Scale to Handle High Event-Per-Second (EPS) Volumes?
- **Interviewer's Intent**: Test system design scalability awareness.
- **Answer**: For high EPS environments (>10,000 EPS), log ingestion can be decoupled from processing using Apache Kafka or Redis streams. Isolation Forest inference ($<5\text{ms}$) can run in distributed Celery worker task pools, with PostgreSQL connection pooling and Elasticsearch indexing for raw log querying.
- **Project Evidence**: Modular architecture in `app/ml/` and `app/services/` allows independent worker pool scaling.
