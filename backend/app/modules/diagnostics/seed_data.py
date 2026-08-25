"""Curated diagnostic questions across all 7 backend engineering skills."""

from typing import Any, Dict, List

SEEDED_DIAGNOSTIC_QUESTIONS: List[Dict[str, Any]] = [
    # 1. SQL Fundamentals
    {
        "id": "dq_sql_1",
        "skill_id": "sql_fundamentals",
        "question_text": "In a relational database query engine, what is the primary purpose of the Cost-Based Optimizer (CBO)?",
        "difficulty": "medium",
        "difficulty_weight": 1.0,
        "options_json": [
            {
                "id": "A",
                "text": "To validate SQL syntax and check whether referenced tables and columns exist.",
            },
            {
                "id": "B",
                "text": "To evaluate multiple physical execution plans using table statistics (selectivity, cardinality, page counts) and pick the cheapest plan.",
            },
            {
                "id": "C",
                "text": "To rewrite nested subqueries into stored procedures automatically.",
            },
            {
                "id": "D",
                "text": "To enforce ACID durability by writing changes to the Write-Ahead Log (WAL).",
            },
        ],
        "correct_option_id": "B",
        "explanation": "The Cost-Based Optimizer (CBO) compares alternative physical access paths (e.g. index scan vs sequential scan, hash join vs merge join) using table statistics to estimate I/O and CPU cost, selecting the lowest-cost execution plan.",
        "order_index": 1,
    },
    {
        "id": "dq_sql_2",
        "skill_id": "sql_fundamentals",
        "question_text": "When joining two large tables (10M rows each) without indexes on the join key, which physical join algorithm is most commonly chosen by modern database engines?",
        "difficulty": "medium",
        "difficulty_weight": 1.1,
        "options_json": [
            {
                "id": "A",
                "text": "Nested Loop Join",
            },
            {
                "id": "B",
                "text": "Hash Join",
            },
            {
                "id": "C",
                "text": "Index Nested Loop Join",
            },
            {
                "id": "D",
                "text": "Cartesian Product Scan",
            },
        ],
        "correct_option_id": "B",
        "explanation": "For large unsorted tables without indexes, a Hash Join builds an in-memory hash table on the smaller relation and probes it in $O(M+N)$ time, avoiding the $O(M \\times N)$ cost of a standard Nested Loop Join.",
        "order_index": 2,
    },
    # 2. Database Indexing
    {
        "id": "dq_idx_1",
        "skill_id": "database_indexing",
        "question_text": "Given a table `orders` with a composite B+ Tree index on `(tenant_id, status, created_at)`, which of the following queries CANNOT use this index effectively?",
        "difficulty": "hard",
        "difficulty_weight": 1.3,
        "options_json": [
            {
                "id": "A",
                "text": "SELECT * FROM orders WHERE tenant_id = 't_123' AND status = 'COMPLETED';",
            },
            {
                "id": "B",
                "text": "SELECT * FROM orders WHERE tenant_id = 't_123' ORDER BY created_at;",
            },
            {
                "id": "C",
                "text": "SELECT * FROM orders WHERE status = 'PENDING' AND created_at > '2026-01-01';",
            },
            {
                "id": "D",
                "text": "SELECT * FROM orders WHERE tenant_id = 't_123' AND status = 'PENDING' AND created_at > '2026-01-01';",
            },
        ],
        "correct_option_id": "C",
        "explanation": "Composite B+ Tree indexes follow the leftmost prefix rule. A query filtering only on `status` and `created_at` omits the leading column `tenant_id`, preventing the B+ Tree from navigating down the tree hierarchy.",
        "order_index": 3,
    },
    {
        "id": "dq_idx_2",
        "skill_id": "database_indexing",
        "question_text": "Why does adding multiple secondary indexes on a high-throughput write-heavy table degrade overall application performance?",
        "difficulty": "medium",
        "difficulty_weight": 1.2,
        "options_json": [
            {
                "id": "A",
                "text": "Secondary indexes increase read latency on primary key lookups.",
            },
            {
                "id": "B",
                "text": "Every INSERT/UPDATE/DELETE requires synchronous tree modifications, page splits, and additional WAL writes across all secondary indexes.",
            },
            {
                "id": "C",
                "text": "Database locks the entire table whenever any index is read.",
            },
            {
                "id": "D",
                "text": "Secondary indexes force queries to bypass the query cache.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "Secondary indexes create write amplification: every write operation to the primary table requires corresponding B+ Tree balance operations and WAL entries across every defined secondary index.",
        "order_index": 4,
    },
    # 3. Transactions & Concurrency
    {
        "id": "dq_tx_1",
        "skill_id": "transactions",
        "question_text": "How does the Write-Ahead Logging (WAL) protocol guarantee Durability while maintaining high transaction throughput?",
        "difficulty": "hard",
        "difficulty_weight": 1.3,
        "options_json": [
            {
                "id": "A",
                "text": "By writing modified database data pages to disk synchronously on every transaction commit.",
            },
            {
                "id": "B",
                "text": "By sequentially appending transaction change records to an append-only log on disk before flushing dirty data pages asynchronously.",
            },
            {
                "id": "C",
                "text": "By keeping all committed transactions only in memory across multiple replica nodes.",
            },
            {
                "id": "D",
                "text": "By executing transactions only in single-threaded mode to avoid disk conflicts.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "WAL enforces that log records describing a change are flushed to sequential, append-only disk storage BEFORE dirty buffer pool pages are written to random disk locations. This allows fast sequential commits and crash recovery.",
        "order_index": 5,
    },
    {
        "id": "dq_tx_2",
        "skill_id": "transactions",
        "question_text": "In SQL isolation levels, which phenomenon is prevented by 'Repeatable Read' that is allowed in 'Read Committed'?",
        "difficulty": "medium",
        "difficulty_weight": 1.2,
        "options_json": [
            {
                "id": "A",
                "text": "Dirty Read (reading uncommitted changes from another concurrent transaction).",
            },
            {
                "id": "B",
                "text": "Non-Repeatable / Fuzzy Read (reading different values for the same row within the same transaction).",
            },
            {
                "id": "C",
                "text": "Write Skew (concurrent transactions modifying distinct rows violating a cross-row invariant).",
            },
            {
                "id": "D",
                "text": "Deadlock generation.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "Read Committed prevents Dirty Reads. Repeatable Read additionally guarantees that if transaction T1 reads row R, subsequent reads of row R within T1 will yield the exact same data, preventing Non-Repeatable (Fuzzy) Reads.",
        "order_index": 6,
    },
    # 4. Caching
    {
        "id": "dq_cache_1",
        "skill_id": "caching",
        "question_text": "What is a 'Cache Stampede' (Thundering Herd problem) and what is the best strategy to mitigate it?",
        "difficulty": "medium",
        "difficulty_weight": 1.2,
        "options_json": [
            {
                "id": "A",
                "text": "When Redis runs out of memory; mitigate by increasing maxmemory.",
            },
            {
                "id": "B",
                "text": "When a popular cache key expires and thousands of concurrent requests simultaneously hit the database; mitigate using distributed mutex locks or probabilistic early recomputation (XFetch).",
            },
            {
                "id": "C",
                "text": "When cache eviction deletes keys in FIFO order; mitigate by switching to LFU.",
            },
            {
                "id": "D",
                "text": "When cache keys contain oversized JSON payloads; mitigate by using Protobuf.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "A cache stampede occurs when a hot key expires and numerous concurrent worker threads miss the cache simultaneously, swamping the backing database. Distributed locking or early background refresh mitigates this.",
        "order_index": 7,
    },
    {
        "id": "dq_cache_2",
        "skill_id": "caching",
        "question_text": "In a Cache-Aside (Lazy Loading) architecture, what is the recommended procedure when updating data?",
        "difficulty": "easy",
        "difficulty_weight": 1.0,
        "options_json": [
            {
                "id": "A",
                "text": "Update the database first, then invalidate (delete) the cached key in Redis.",
            },
            {
                "id": "B",
                "text": "Update the cache first, then asynchronously write to the database whenever possible.",
            },
            {
                "id": "C",
                "text": "Delete the database record and wait for the cache to expire.",
            },
            {
                "id": "D",
                "text": "Overwrite both the database and cache simultaneously in a single distributed 2PC transaction.",
            },
        ],
        "correct_option_id": "A",
        "explanation": "In Cache-Aside, mutating operations write to the primary database and subsequently delete/evict the cache key. Next read request experiences a cache miss and repopulates the cache with fresh data.",
        "order_index": 8,
    },
    # 5. Distributed Systems
    {
        "id": "dq_dist_1",
        "skill_id": "distributed_systems",
        "question_text": "According to the CAP theorem, when a network partition (P) occurs between data centers, what fundamental trade-off must a distributed system make?",
        "difficulty": "medium",
        "difficulty_weight": 1.2,
        "options_json": [
            {
                "id": "A",
                "text": "Trade-off between encryption strength and latency.",
            },
            {
                "id": "B",
                "text": "Trade-off between Consistency (refusing requests or returning errors to avoid stale data) and Availability (answering all requests even if data is stale).",
            },
            {
                "id": "C",
                "text": "Trade-off between CPU utilization and RAM capacity.",
            },
            {
                "id": "D",
                "text": "Trade-off between relational schemas and document stores.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "Partitions over physical networks are inevitable. Under partition, a system must either prioritize linearizable Consistency (CP) by rejecting conflicting writes, or prioritize Availability (AP) by continuing to accept requests at the cost of stale reads.",
        "order_index": 9,
    },
    {
        "id": "dq_dist_2",
        "skill_id": "distributed_systems",
        "question_text": "In a distributed storage system with $N=5$ replicas, if a write quorum requires $W=3$ ACKs, what is the minimum read quorum $R$ needed to guarantee strong consistency (reading the latest write)?",
        "difficulty": "hard",
        "difficulty_weight": 1.4,
        "options_json": [
            {
                "id": "A",
                "text": "R = 1",
            },
            {
                "id": "B",
                "text": "R = 2",
            },
            {
                "id": "C",
                "text": "R = 3",
            },
            {
                "id": "D",
                "text": "R = 5",
            },
        ],
        "correct_option_id": "C",
        "explanation": "Strict quorum consistency requires $R + W > N$. With $N=5$ and $W=3$, we need $R + 3 > 5 \\implies R > 2 \\implies R = 3$. This guarantees that the read set overlaps with the write set on at least one replica node.",
        "order_index": 10,
    },
    # 6. Messaging & Queues
    {
        "id": "dq_msg_1",
        "skill_id": "messaging_queues",
        "question_text": "Why must message queue consumers in distributed architectures be implemented to be 'Idempotent'?",
        "difficulty": "easy",
        "difficulty_weight": 1.0,
        "options_json": [
            {
                "id": "A",
                "text": "Because message brokers frequently lose messages on node failure.",
            },
            {
                "id": "B",
                "text": "Because standard message delivery guarantees are 'at-least-once', meaning network retries can deliver duplicate messages.",
            },
            {
                "id": "C",
                "text": "Because queues only process messages alphabetically.",
            },
            {
                "id": "D",
                "text": "To prevent queues from consuming too much memory.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "Due to network timeouts and unacknowledged delivery retries, distributed message systems guarantee at-least-once delivery. Idempotent consumers guarantee that processing the same message duplicate yields identical state.",
        "order_index": 11,
    },
    {
        "id": "dq_msg_2",
        "skill_id": "messaging_queues",
        "question_text": "What is the primary function of a Dead Letter Queue (DLQ) in an asynchronous message processing pipeline?",
        "difficulty": "easy",
        "difficulty_weight": 1.0,
        "options_json": [
            {
                "id": "A",
                "text": "To store successfully completed messages for audit logging.",
            },
            {
                "id": "B",
                "text": "To isolate 'poison pill' messages that repeatedly fail processing after max retry attempts without blocking the main processing queue.",
            },
            {
                "id": "C",
                "text": "To compress binary payloads before sending over TCP.",
            },
            {
                "id": "D",
                "text": "To route messages to secondary consumers in round-robin fashion.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "A DLQ catches malformed or unprocessable messages after exhausting retry policies, preventing infinite crash loops (poison pills) from halting the consumption pipeline for healthy messages.",
        "order_index": 12,
    },
    # 7. System Design
    {
        "id": "dq_sd_1",
        "skill_id": "system_design",
        "question_text": "When designing an API rate limiter to protect backend services from sudden bursts while supporting a steady sustained request rate, which algorithm is most standard?",
        "difficulty": "medium",
        "difficulty_weight": 1.2,
        "options_json": [
            {
                "id": "A",
                "text": "Token Bucket",
            },
            {
                "id": "B",
                "text": "Round Robin DNS",
            },
            {
                "id": "C",
                "text": "Consistent Hashing Ring",
            },
            {
                "id": "D",
                "text": "Merkle Tree Verification",
            },
        ],
        "correct_option_id": "A",
        "explanation": "The Token Bucket algorithm accumulates tokens at a constant refill rate up to bucket capacity, accommodating defined temporary traffic bursts while strictly enforcing long-term sustained rate limits.",
        "order_index": 13,
    },
    {
        "id": "dq_sd_2",
        "skill_id": "system_design",
        "question_text": "When sharding a large database by a shard key, what is the 'Hotspot Partition' problem and how can it be mitigated?",
        "difficulty": "hard",
        "difficulty_weight": 1.4,
        "options_json": [
            {
                "id": "A",
                "text": "CPU overheating in physical server racks; mitigate with better cooling.",
            },
            {
                "id": "B",
                "text": "When an uneven distribution of traffic/data concentrates heavily on a single shard key (e.g. celebrity user or active tenant); mitigate by salting the shard key or isolated dedicated shards.",
            },
            {
                "id": "C",
                "text": "When index tree depths exceed 4 levels; mitigate by rebuilding indexes.",
            },
            {
                "id": "D",
                "text": "When replication lags behind WAL logs; mitigate with synchronous replicas.",
            },
        ],
        "correct_option_id": "B",
        "explanation": "Hotspots occur when high-frequency entities (e.g. large tenant or viral account) overwhelm a single partition. Key salting (appending random hash suffix) or dedicated multi-shard routing distributes the load.",
        "order_index": 14,
    },
]

