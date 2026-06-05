#!/usr/bin/env python3
"""
Architecture analysis script for RisingWave monorepo.
Usage: python3 ua-arch-analyze.py <input.json> <output.json>
"""

import json
import sys
from collections import defaultdict, Counter

def main():
    if len(sys.argv) < 3:
        print("Usage: ua-arch-analyze.py <input.json> <output.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    nodes = data['fileNodes']
    import_edges = data['importEdges']
    all_edges = data['allEdges']

    # -----------------------------------------------------------------------
    # A. Directory Grouping
    # The common prefix is empty (many top-level dirs). Group by:
    #   - If starts with 'src/', group by src/<subdir>
    #   - Otherwise group by first path segment
    # -----------------------------------------------------------------------

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

    dir_groups = defaultdict(list)
    for node in nodes:
        fp = node.get('filePath', '')
        group = get_dir_group(fp)
        dir_groups[group].append(node['id'])

    # -----------------------------------------------------------------------
    # B. Node Type Grouping
    # -----------------------------------------------------------------------
    type_groups = defaultdict(list)
    for node in nodes:
        type_groups[node['type']].append(node['id'])

    # -----------------------------------------------------------------------
    # C. Import Adjacency Matrix
    # -----------------------------------------------------------------------
    fan_out = defaultdict(int)
    fan_in = defaultdict(int)
    for e in import_edges:
        fan_out[e['source']] += 1
        fan_in[e['target']] += 1

    # -----------------------------------------------------------------------
    # D. Cross-Category Dependency Analysis
    # -----------------------------------------------------------------------
    node_types = {n['id']: n['type'] for n in nodes}
    cross_cat = defaultdict(int)
    cross_cat_type = defaultdict(set)
    for e in all_edges:
        st = node_types.get(e['source'])
        tt = node_types.get(e['target'])
        et = e.get('type', '?')
        if st and tt and st != tt:
            key = (st, tt)
            cross_cat[key] += 1
            cross_cat_type[key].add(et)

    cross_cat_edges = []
    for (st, tt), count in cross_cat.items():
        cross_cat_edges.append({
            'fromType': st,
            'toType': tt,
            'edgeType': list(cross_cat_type[(st, tt)])[0],
            'count': count
        })

    # -----------------------------------------------------------------------
    # E. Inter-Group Import Frequency
    # -----------------------------------------------------------------------
    node_to_group = {}
    for group, node_ids in dir_groups.items():
        for nid in node_ids:
            node_to_group[nid] = group

    inter_group = defaultdict(int)
    for e in import_edges:
        sg = node_to_group.get(e['source'])
        tg = node_to_group.get(e['target'])
        if sg and tg and sg != tg:
            inter_group[(sg, tg)] += 1

    inter_group_list = [
        {'from': k[0], 'to': k[1], 'count': v}
        for k, v in sorted(inter_group.items(), key=lambda x: -x[1])
    ]

    # -----------------------------------------------------------------------
    # F. Intra-Group Import Density
    # -----------------------------------------------------------------------
    group_edges = defaultdict(lambda: {'internal': 0, 'total': 0})
    for e in import_edges:
        sg = node_to_group.get(e['source'])
        tg = node_to_group.get(e['target'])
        if sg:
            group_edges[sg]['total'] += 1
        if sg == tg and sg:
            group_edges[sg]['internal'] += 1

    intra_density = {}
    for g, counts in group_edges.items():
        total = counts['total']
        internal = counts['internal']
        intra_density[g] = {
            'internalEdges': internal,
            'totalEdges': total,
            'density': round(internal / total, 3) if total > 0 else 0
        }

    # -----------------------------------------------------------------------
    # G. Directory Pattern Matching
    # -----------------------------------------------------------------------
    PATTERN_MAP = {
        # RisingWave-specific crate groups
        'src/frontend': 'sql-frontend',
        'src/sqlparser': 'sql-frontend',
        'src/expr': 'expression-engine',
        'src/stream': 'stream-engine',
        'src/batch': 'batch-engine',
        'src/meta': 'meta-service',
        'src/storage': 'storage-engine',
        'src/object_store': 'storage-engine',
        'src/dml': 'storage-engine',
        'src/connector': 'connector',
        'src/jni_core': 'connector',
        'src/java_binding': 'connector',
        'java': 'connector',
        'src/compute': 'server-rpc',
        'src/prost': 'server-rpc',
        'src/rpc_client': 'server-rpc',
        'src/cmd': 'server-rpc',
        'src/cmd_all': 'server-rpc',
        'src/ctl': 'server-rpc',
        'proto': 'server-rpc',
        'src/common': 'common',
        'src/utils': 'common',
        'src/config': 'common',
        'src/error': 'common',
        'src/license': 'common',
        'src/bench': 'common',
        'src/workspace-hack': 'common',
        'lints': 'common',
        'src/risedevtool': 'devtools',
        'e2e_test': 'testing',
        'integration_tests': 'testing',
        'src/tests': 'testing',
        'src/test_runner': 'testing',
        'ci': 'ci-cd',
        '.github': 'ci-cd',
        'docker': 'infrastructure',
        'grafana': 'infrastructure',
        'scripts': 'devtools',
        'docs': 'documentation',
        'develop': 'documentation',
        '.agents': 'documentation',
        'dashboard': 'dashboard',
        'plans': 'documentation',
        'root': 'config',
    }

    pattern_matches = {}
    for group in dir_groups:
        pattern_matches[group] = PATTERN_MAP.get(group, 'unknown')

    # -----------------------------------------------------------------------
    # H. Deployment Topology
    # -----------------------------------------------------------------------
    all_paths = [n['filePath'] for n in nodes]
    has_dockerfile = any('Dockerfile' in p for p in all_paths)
    has_compose = any('docker-compose' in p for p in all_paths)
    has_k8s = any('/k8s/' in p or p.endswith('.yaml') and 'k8s' in p for p in all_paths)
    has_terraform = any(p.endswith('.tf') for p in all_paths)
    has_ci = any('.github/workflows' in p or p.endswith('.yml') and 'ci' in p for p in all_paths)
    infra_files = [n['filePath'] for n in nodes if n['type'] in ('service',) or 'Dockerfile' in n['filePath']][:20]

    deployment_topology = {
        'hasDockerfile': has_dockerfile,
        'hasCompose': has_compose,
        'hasK8s': has_k8s,
        'hasTerraform': has_terraform,
        'hasCI': has_ci,
        'infraFiles': infra_files
    }

    # -----------------------------------------------------------------------
    # I. Data Pipeline Detection
    # -----------------------------------------------------------------------
    schema_files = [n['filePath'] for n in nodes if n['filePath'].endswith('.proto') or n['filePath'].endswith('.graphql')]
    migration_files = [n['filePath'] for n in nodes if 'migration' in n['filePath'].lower() and n['filePath'].endswith('.sql')]
    data_model_files = [n['filePath'] for n in nodes if '/model/' in n['filePath'] or '/models/' in n['filePath']]
    api_handler_files = [n['filePath'] for n in nodes if '/handler' in n['filePath'] or '/service' in n['filePath']]

    data_pipeline = {
        'schemaFiles': schema_files[:10],
        'migrationFiles': migration_files[:10],
        'dataModelFiles': data_model_files[:10],
        'apiHandlerFiles': api_handler_files[:10]
    }

    # -----------------------------------------------------------------------
    # J. Documentation Coverage
    # -----------------------------------------------------------------------
    doc_groups = set(g for g, ids in dir_groups.items() if any(
        node_types.get(nid) == 'document' for nid in ids
    ))
    total_groups = len(dir_groups)
    doc_coverage = {
        'groupsWithDocs': len(doc_groups),
        'totalGroups': total_groups,
        'coverageRatio': round(len(doc_groups) / total_groups, 3) if total_groups else 0,
        'undocumentedGroups': [g for g in dir_groups if g not in doc_groups]
    }

    # -----------------------------------------------------------------------
    # K. Dependency Direction
    # -----------------------------------------------------------------------
    dep_dir_counter = defaultdict(int)
    for e in import_edges:
        sg = node_to_group.get(e['source'])
        tg = node_to_group.get(e['target'])
        if sg and tg and sg != tg:
            dep_dir_counter[(sg, tg)] += 1

    # Produce dominant direction pairs
    dep_direction = []
    seen = set()
    for (a, b), cnt_ab in dep_dir_counter.items():
        if (b, a) in seen:
            continue
        seen.add((a, b))
        cnt_ba = dep_dir_counter.get((b, a), 0)
        if cnt_ab >= cnt_ba:
            dep_direction.append({'dependent': a, 'dependsOn': b, 'edgeCount': cnt_ab})
        else:
            dep_direction.append({'dependent': b, 'dependsOn': a, 'edgeCount': cnt_ba})

    dep_direction.sort(key=lambda x: -x['edgeCount'])

    # -----------------------------------------------------------------------
    # File Stats
    # -----------------------------------------------------------------------
    files_per_group = {g: len(ids) for g, ids in dir_groups.items()}
    node_type_counts = dict(Counter(n['type'] for n in nodes))

    file_stats = {
        'totalFileNodes': len(nodes),
        'filesPerGroup': files_per_group,
        'nodeTypeCounts': node_type_counts
    }

    # -----------------------------------------------------------------------
    # Build output
    # -----------------------------------------------------------------------
    result = {
        'scriptCompleted': True,
        'directoryGroups': dict(dir_groups),
        'nodeTypeGroups': dict(type_groups),
        'crossCategoryEdges': cross_cat_edges,
        'interGroupImports': inter_group_list[:50],
        'intraGroupDensity': intra_density,
        'patternMatches': pattern_matches,
        'deploymentTopology': deployment_topology,
        'dataPipeline': data_pipeline,
        'docCoverage': doc_coverage,
        'dependencyDirection': dep_direction[:30],
        'fileStats': file_stats,
        'fileFanIn': dict(sorted(fan_in.items(), key=lambda x: -x[1])[:50]),
        'fileFanOut': dict(sorted(fan_out.items(), key=lambda x: -x[1])[:50]),
    }

    with open(sys.argv[2], 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Analysis complete. {len(nodes)} nodes in {len(dir_groups)} directory groups.")
    sys.exit(0)

if __name__ == '__main__':
    main()
