#!/usr/bin/env python3
"""
Layer assignment script for RisingWave monorepo.
Uses analysis results to produce final layers.json
"""

import json
import sys

def get_dir_group(file_path):
    parts = file_path.split('/')
    if not parts:
        return 'root'
    if parts[0] == 'src' and len(parts) >= 2:
        return 'src/' + parts[1]
    if parts[0] in ('', '.'):
        return 'root'
    if len(parts) == 1:
        return 'root'
    return parts[0]

def main():
    with open('/Users/eric.rodriguez/src/data/risingwave/.understand-anything/tmp/ua-arch-input.json') as f:
        data = json.load(f)

    nodes = data['fileNodes']

    # Build group -> node_ids map
    from collections import defaultdict
    dir_groups = defaultdict(list)
    for node in nodes:
        fp = node.get('filePath', '')
        group = get_dir_group(fp)
        dir_groups[group].append(node['id'])

    # -----------------------------------------------------------------------
    # Layer definitions: maps layer_id -> list of directory groups
    # -----------------------------------------------------------------------
    LAYER_GROUPS = {
        'layer:sql-frontend': [
            'src/frontend',
            'src/sqlparser',
        ],
        'layer:expression-engine': [
            'src/expr',
        ],
        'layer:stream-engine': [
            'src/stream',
        ],
        'layer:batch-engine': [
            'src/batch',
        ],
        'layer:meta-service': [
            'src/meta',
        ],
        'layer:storage-engine': [
            'src/storage',
            'src/object_store',
            'src/dml',
        ],
        'layer:connector': [
            'src/connector',
            'src/jni_core',
            'src/java_binding',
            'java',
        ],
        'layer:server-rpc': [
            'src/compute',
            'proto',
            'src/prost',
            'src/rpc_client',
            'src/cmd',
            'src/cmd_all',
            'src/ctl',
        ],
        'layer:common': [
            'src/common',
            'src/utils',
            'src/config',
            'src/error',
            'src/bench',
            'src/workspace-hack',
            'lints',
        ],
        # All remaining groups go into testing-ops
        'layer:testing-ops': [],
    }

    # Collect all assigned groups
    assigned_groups = set()
    for groups in LAYER_GROUPS.values():
        for g in groups:
            assigned_groups.add(g)

    # Everything else goes into testing-ops
    for g in dir_groups:
        if g not in assigned_groups:
            LAYER_GROUPS['layer:testing-ops'].append(g)

    # Build node_ids for each layer
    layer_nodes = defaultdict(list)
    for layer_id, groups in LAYER_GROUPS.items():
        for g in groups:
            layer_nodes[layer_id].extend(dir_groups.get(g, []))

    # Verify all nodes are assigned
    assigned_count = sum(len(v) for v in layer_nodes.values())
    total = len(nodes)
    print(f"Total nodes: {total}, Assigned: {assigned_count}")
    assert assigned_count == total, f"MISMATCH: {assigned_count} != {total}"

    # Build layer descriptors
    LAYER_META = {
        'layer:sql-frontend': {
            'name': 'SQL Frontend',
            'description': 'SQL parsing, query planning, optimization, and scheduling — the entry point for all SQL queries in RisingWave, encompassing the binder, planner, optimizer, and the standalone SQL parser crate.',
        },
        'layer:expression-engine': {
            'name': 'Expression Engine',
            'description': 'Scalar and aggregate expression evaluation used across both streaming and batch execution, including built-in functions, type coercion, and expression compilation.',
        },
        'layer:stream-engine': {
            'name': 'Stream Processing Engine',
            'description': 'Streaming execution runtime responsible for dataflow graph execution, operator executors, barrier protocol, watermarks, and stateful stream-processing logic.',
        },
        'layer:batch-engine': {
            'name': 'Batch Processing Engine',
            'description': 'Batch query execution engine handling ad-hoc queries against materialized views, including distributed batch planning, exchange operators, and local task execution.',
        },
        'layer:meta-service': {
            'name': 'Meta Service',
            'description': 'Cluster-wide metadata management, catalog storage, barrier coordination, actor scheduling, and SeaORM-backed persistence for all distributed system state.',
        },
        'layer:storage-engine': {
            'name': 'Storage Engine',
            'description': 'Cloud-native Hummock LSM-tree storage engine, object-store abstraction over S3/GCS/HDFS, and the DML subsystem for INSERT/UPDATE/DELETE operations.',
        },
        'layer:connector': {
            'name': 'Connector Layer',
            'description': 'Source and sink connectors for external systems (Kafka, Pulsar, Kinesis, CDC, Iceberg, and more), JNI bridge to the Java connector node, and the Java-side connector runtime.',
        },
        'layer:server-rpc': {
            'name': 'Server & RPC Infrastructure',
            'description': 'Binary entry points (compute node, all-in-one), gRPC service definitions in Protobuf, generated Prost bindings, RPC client wrappers, and the internal diagnostic control (ctl) CLI.',
        },
        'layer:common': {
            'name': 'Common & Shared Utilities',
            'description': 'Cross-cutting shared libraries including core data types, array representations, session config, hash utilities, error codes, async runtime helpers, and workspace dependency management.',
        },
        'layer:testing-ops': {
            'name': 'Testing, Operations & Developer Tools',
            'description': 'End-to-end SQLLogicTest suites, simulation and integration test harnesses, CI pipeline scripts, Docker/Grafana configurations, the risedev developer tool, documentation, and project configuration files.',
        },
    }

    # Output JSON array
    output = []
    for layer_id, meta in LAYER_META.items():
        node_ids = layer_nodes[layer_id]
        if node_ids:
            output.append({
                'id': layer_id,
                'name': meta['name'],
                'description': meta['description'],
                'nodeIds': node_ids,
            })

    # Print summary
    for layer in output:
        print(f"  {layer['id']}: {len(layer['nodeIds'])} nodes")
    print(f"Total layers: {len(output)}")
    print(f"Grand total nodes: {sum(len(l['nodeIds']) for l in output)}")

    out_path = '/Users/eric.rodriguez/src/data/risingwave/.understand-anything/intermediate/layers.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Written to {out_path}")

if __name__ == '__main__':
    main()
