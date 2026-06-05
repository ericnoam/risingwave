# RISINGWAVE ONBOARDING GUIDE


## Project Overview

```
┌─────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Field       │ Value                                                                                                  │
├─────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Name        │ risingwave                                                                                             │
├─────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Description │ A Postgres-compatible streaming database and event streaming platform for agentic AI, written in Rust. │
├─────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Languages   │ Rust (primary), Protobuf, Python, SQL, Java, Shell, YAML, TOML, TypeScript, Markdown                   │
└─────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

RisingWave replaces the traditional Debezium + Kafka + Flink + serving-DB stack with a single system. It continuously ingests data from databases, event streams, and webhooks, processes it incrementally via materialized views, and serves fresh results at low latency — all behind a standard PostgreSQL wire protocol.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


## Architecture Layers

The codebase is organized into 10 architectural layers:

### 1. SQL Frontend (src/frontend/)
SQL parsing, query planning, optimization, and scheduling. The entry point for all SQL queries, encompassing the binder, planner, optimizer, and the standalone SQL parser crate (src/sqlparser/).

Key files:
```
┌─────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────┐
│ File                                        │ Role                                                                                  │
├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ src/sqlparser/src/parser.rs                 │ Hand-written recursive descent SQL parser producing ASTs                              │
├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ src/frontend/src/binder/mod.rs              │ Resolves AST against catalog — type-checks and name-resolves                          │
├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ src/frontend/src/handler/mod.rs             │ Dispatcher routing each statement (DDL/DML/SELECT/EXPLAIN) to its handler             │
├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ src/frontend/src/optimizer/plan_node/mod.rs │ Hub of the optimizer — defines all logical/batch/stream plan node types (fan-in: 235) │
├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ src/frontend/src/optimizer/rule/mod.rs      │ Registers hundreds of rewrite rules (predicate pushdown, join reordering, etc.)       │
├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ src/frontend/src/optimizer/mod.rs           │ Optimizer entry point — drives logical→physical plan transformation                   │
└─────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────┘
```
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 2. Expression Engine (src/expr/)
Scalar and aggregate expression evaluation used across both streaming and batch execution paths, including built-in functions, type coercion, and expression compilation.

Key files:
┌─────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┐
│ File                            │ Role                                                                          │
├─────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ src/expr/impl/src/scalar/mod.rs │ Registry of all built-in scalar functions via #[function] macro (fan-out: 89) │
└─────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 3. Stream Processing Engine (src/stream/)
Streaming execution runtime responsible for dataflow graph execution, operator executors, the barrier protocol, watermarks, and stateful stream-processing logic.

Key files:
```
┌────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────┐
│ File                                       │ Role                                                                       │
├────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ src/stream/src/executor/mod.rs             │ Defines the Executor trait and re-exports all executor types (fan-in: 113) │
├────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ src/stream/src/from_proto/mod.rs           │ Deserializes stream_plan.proto into live Rust executor objects             │
├────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ src/stream/src/task/barrier_manager/mod.rs │ Coordinates barrier collection on each compute node                        │
├────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ src/stream/src/common/table/state_table.rs │ Relational state table interface wrapping raw Hummock access (fan-in: 63)  │
├────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ src/stream/src/lib.rs                      │ Stream crate root                                                          │
└────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 4. Batch Processing Engine (src/batch/)
Batch query execution for ad-hoc queries against materialized views, including distributed batch planning, exchange operators, and local task execution.

Key files:
```
┌────────────────┬─────────────────────────────────────────────────────────────────────────┐
│ File           │ Role                                                                    │
├────────────────┼─────────────────────────────────────────────────────────────────────────┤
│ src/batch/src/ │ Batch executor implementations (hash join, sort, aggregate, scan, etc.) │
└────────────────┴─────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 5. Meta Service (src/meta/)
Cluster-wide metadata management, catalog storage, barrier coordination, actor scheduling, and SeaORM-backed persistence for all distributed system state.

Key files:
```
┌──────────────────────────────────┬───────────────────────────────────────────────────────────────────────┐
│ File                             │ Role                                                                  │
├──────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
│ src/meta/src/manager/metadata.rs │ Authoritative state for catalog objects and streaming graph topology  │
├──────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
│ src/meta/src/manager/mod.rs      │ Orchestrates all sub-managers (barrier, Hummock, connectors)          │
├──────────────────────────────────┼───────────────────────────────────────────────────────────────────────┤
│ src/meta/src/barrier/mod.rs      │ Injects Barrier control messages into source actors for checkpointing │
└──────────────────────────────────┴───────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 6. Storage Engine (src/storage/)
Cloud-native Hummock LSM-tree storage engine, object-store abstraction over S3/GCS/HDFS, and the DML subsystem for INSERT/UPDATE/DELETE.

Key files:
```
┌────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────┐
│ File                                       │ Role                                                                                     │
├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
│ src/storage/src/hummock/mod.rs             │ Hummock crate root — exposes HummockStorage implementing the state-store trait (fan-in:  │
│                                            │ 70)                                                                                      │
├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
│ src/storage/hummock_sdk/src/version.rs     │ HummockVersion — immutable snapshot of the entire LSM tree                               │
├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
│ src/storage/src/hummock/compactor/mod.rs   │ Compaction task orchestration (read SSTables → merge → write → report)                   │
├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
│ src/storage/src/hummock/event_handler/mod. │ Event-driven interface between storage and compaction                                    │
│ rs                                         │                                                                                          │
└────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 7. Connector Layer (src/connector/)
Source and sink connectors for external systems (Kafka, Pulsar, Kinesis, CDC, Iceberg), JNI bridge to the Java connector node, and the Java-side connector runtime.

Key files:
```
┌─────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ File                            │ Role                                                                   │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ src/connector/src/source/mod.rs │ SplitEnumerator and SplitReader traits for all sources (fan-in: 97)    │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ src/connector/src/sink/mod.rs   │ Sink trait and all sink implementations (fan-out: 37)                  │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ src/connector/src/parser/mod.rs │ Format parsers — Avro, Protobuf, JSON, CSV, Debezium CDC (fan-out: 26) │
└─────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 8. Server & RPC Infrastructure (src/utils/pgwire/, src/cmd_all/, proto/)
Binary entry points, gRPC service definitions in Protobuf, generated Prost bindings, RPC client wrappers, and the ctl diagnostic CLI.

Key files:
```
┌─────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
│ File                                │ Role                                                             │
├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ src/utils/pgwire/src/pg_server.rs   │ SessionManager and Session traits + TCP/TLS accept loop          │
├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ src/utils/pgwire/src/pg_protocol.rs │ Full PostgreSQL wire protocol state machine                      │
├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ src/cmd_all/src/lib.rs              │ All-in-one binary re-exporting all three launch modes            │
├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ proto/stream_plan.proto             │ Wire encoding for the full streaming execution plan (1550 lines) │
├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ proto/data.proto                    │ DataChunk, StreamChunk, Datum — data wire format                 │
├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ proto/meta.proto                    │ 50 RPCs for the meta service                                     │
└─────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 9. Common & Shared Utilities (src/common/)
Cross-cutting shared libraries including core data types, array representations, session config, hash utilities, error codes, and async runtime helpers.

Key files:
```
┌─────────────────────────────┬─────────────────────────────────────────────────────────────────────┐
│ File                        │ Role                                                                │
├─────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ src/common/src/types/mod.rs │ DataType enum, Datum / ScalarImpl value representation (fan-in: 61) │
├─────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ src/common/src/array/mod.rs │ Columnar ArrayImpl variants for vectorized processing               │
└─────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

### 10. Testing, Operations & Developer Tools (e2e_test/, ci/, docker/)
End-to-end SQLLogicTest suites, simulation and integration test harnesses, CI pipeline scripts, Docker/Grafana configurations, the risedev developer tool, and project configuration.

Key files:
```
┌───────────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│ File                      │ Role                                                                        │
├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ e2e_test/                 │ SQLLogicTest (.slt) test suites for all SQL features                        │
├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ docker/Dockerfile         │ Multi-stage production build (Rust + Java → minimal Ubuntu runtime)         │
├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ docker/docker-compose.yml │ Standalone cluster: meta, frontend, compute, compactor as separate services │
├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ risedev.yml               │ Developer environment profiles                                              │
└───────────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


## Key Concepts
```
┌──────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Concept                  │ Description                                                                                                │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Materialized Views       │ Core abstraction — incrementally maintained query results, always up-to-date                               │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Streaming Plan vs.       │ Same logical plan nodes; optimizer produces two physical variants depending on the statement type          │
│ Batch Plan               │                                                                                                            │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Actor Model              │ Each stream operator runs as an independent actor processing StreamChunk messages over async channels      │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Barrier Protocol         │ Epoch-based Chandy-Lamport snapshot mechanism — ensures exactly-once semantics and consistency after       │
│                          │ failures                                                                                                   │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Split-Based Parallelism  │ Sources are parallelized by assigning splits (e.g., Kafka partitions) to workers; enables independent      │
│                          │ source and operator scaling                                                                                │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Hummock                  │ Cloud-native LSM-tree storage with SSTables written to S3 — compute nodes are stateless                    │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ #[function] macro        │ Proc-macro for registering built-in functions with automatic type dispatch and vectorization               │
├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Postgres Wire Protocol   │ RisingWave is compatible at the protocol level, not just SQL dialect — any Postgres client connects        │
│                          │ natively                                                                                                   │
└──────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


## Guided Tour (15 Steps)

Follow these steps in order to build a mental model of the system:
```
┌──────┬────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Step │ Title                  │ What to Read                                                                                           │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1    │ Project Overview       │ README.md — core value proposition and architecture overview                                           │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2    │ Codebase Structure &   │ src/README.md, src/cmd_all/src/lib.rs, src/cmd_all/src/README.md                                       │
│      │ Binary Entry           │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3    │ Postgres Wire          │ src/utils/pgwire/src/pg_server.rs, src/utils/pgwire/src/pg_protocol.rs                                 │
│      │ Protocol Gateway       │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4    │ SQL Parsing & Query    │ src/sqlparser/src/parser.rs, src/frontend/src/binder/mod.rs, src/frontend/src/handler/mod.rs           │
│      │ Binding                │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 5    │ Core Type System &     │ src/common/src/types/mod.rs, src/common/src/array/mod.rs                                               │
│      │ Column Arrays          │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 6    │ Expression Engine      │ src/expr/impl/src/scalar/mod.rs                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 7    │ Query Optimizer: Plan  │ src/frontend/src/optimizer/plan_node/mod.rs, src/frontend/src/optimizer/rule/mod.rs,                   │
│      │ Nodes & Rules          │ src/frontend/src/optimizer/mod.rs                                                                      │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 8    │ gRPC Protobuf          │ proto/stream_plan.proto, proto/data.proto, proto/meta.proto                                            │
│      │ Contracts              │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 9    │ Stream Executors &     │ src/stream/src/executor/mod.rs, src/stream/src/from_proto/mod.rs, src/stream/src/lib.rs                │
│      │ the Actor Model        │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10   │ Barrier Protocol &     │ src/stream/src/task/barrier_manager/mod.rs, src/meta/src/barrier/mod.rs,                               │
│      │ Checkpointing          │ docs/dev/src/design/checkpoint.md                                                                      │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 11   │ Hummock: Cloud-Native  │ src/storage/src/hummock/mod.rs, src/storage/hummock_sdk/src/version.rs,                                │
│      │ State Store            │ src/stream/src/common/table/state_table.rs, docs/dev/src/design/state-store-overview.md                │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 12   │ Hummock Compaction     │ src/storage/src/hummock/compactor/mod.rs, src/storage/src/hummock/event_handler/mod.rs                 │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 13   │ Connector Layer:       │ src/connector/src/source/mod.rs, src/connector/src/sink/mod.rs, src/connector/src/parser/mod.rs        │
│      │ Sources & Sinks        │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 14   │ Meta Service: Cluster  │ src/meta/src/manager/metadata.rs, src/meta/src/manager/mod.rs                                          │
│      │ Brain                  │                                                                                                        │
├──────┼────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 15   │ Containerization &     │ docker/Dockerfile, docker/docker-compose.yml                                                           │
│      │ Deployment             │                                                                                                        │
└──────┴────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


## Complexity Hotspots

These areas have high complexity and should be approached carefully:
```
┌─────────────────┬────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────┐
│ Area            │ Files                                          │ Why It's Complex                                                   │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Optimizer Plan  │ src/frontend/src/optimizer/plan_node/mod.rs    │ Hub of the entire optimizer — every logical, batch, and stream     │
│ Nodes           │ (fan-in: 235, fan-out: 152)                    │ plan node type passes through here                                 │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Optimizer Rules │ src/frontend/src/optimizer/rule/mod.rs         │ Hundreds of rewrite rules interact non-trivially; rule ordering    │
│                 │ (fan-out: 87)                                  │ matters                                                            │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Stream          │ src/stream/src/executor/mod.rs (fan-in: 113)   │ Central registry for all executor types — changes here ripple      │
│ Executor Hub    │                                                │ across the entire streaming engine                                 │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Connector       │ src/connector/src/source/mod.rs (fan-in: 97)   │ Aggregates all source implementations; split assignment logic is   │
│ Source Hub      │                                                │ subtle                                                             │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ CDC Parsers     │ src/connector/src/parser/ (Debezium, MySQL,    │ CDC schema-change handling, multi-format dispatch, and             │
│                 │ PostgreSQL, SQL Server)                        │ correctness guarantees across DB dialects                          │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Avro /          │ src/connector/src/parser/avro/,                │ Schema registry integration, Glue catalog resolution, schema       │
│ Protobuf        │ src/connector/src/parser/protobuf/             │ evolution                                                          │
│ Parsers         │                                                │                                                                    │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Hummock Version │ src/storage/hummock_sdk/src/version.rs         │ Global immutable LSM tree view — versioning invariants are         │
│                 │                                                │ critical for consistency                                           │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ State Table     │ src/stream/src/common/table/state_table.rs     │ Relational abstraction over raw key-value storage; correctness is  │
│                 │ (fan-in: 63)                                   │ critical for every stateful executor                               │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Barrier Manager │ src/meta/src/barrier/mod.rs                    │ Distributed consistency protocol — incorrect barrier ordering      │
│                 │                                                │ breaks exactly-once guarantees                                     │
├─────────────────┼────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Iceberg Catalog │ src/connector/src/connector_common/iceberg/    │ JNI bridge + multiple catalog backends (JNI, REST,                 │
│                 │                                                │ storage-backed) with intricate config resolution                   │
└─────────────────┴────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────┘
```
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


## Quick Start for Local Development

# Build
./risedev b

# Check (clippy + style)
./risedev c

# Start a local instance (background)
./risedev d

# Run a query
./risedev psql -c "SELECT version();"

# Run e2e tests
./risedev slt './e2e_test/basic/**/*.slt'

# Stop
./risedev k
