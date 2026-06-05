#!/usr/bin/env node
'use strict';

const fs = require('fs');

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  console.error('Usage: node ua-tour-analyze.js <input.json> <output.json>');
  process.exit(1);
}

let input;
try {
  input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
} catch (e) {
  console.error('Failed to read input:', e.message);
  process.exit(1);
}

const { nodes, edges, layers } = input;

// Build node map
const nodeMap = new Map();
for (const n of nodes) {
  nodeMap.set(n.id, n);
}

// Build adjacency structures
const fanIn = new Map();   // id -> count of edges pointing TO it
const fanOut = new Map();  // id -> count of edges pointing FROM it
const forwardAdj = new Map(); // id -> Set of targets (for BFS)

for (const n of nodes) {
  fanIn.set(n.id, 0);
  fanOut.set(n.id, 0);
  forwardAdj.set(n.id, new Set());
}

for (const e of edges) {
  if (!nodeMap.has(e.source) || !nodeMap.has(e.target)) continue;
  fanIn.set(e.target, (fanIn.get(e.target) || 0) + 1);
  fanOut.set(e.source, (fanOut.get(e.source) || 0) + 1);
  if (e.type === 'imports' || e.type === 'calls' || e.type === 'depends_on') {
    forwardAdj.get(e.source).add(e.target);
  }
}

// A. Fan-In Ranking (top 20)
const fanInRanking = [...nodeMap.keys()]
  .map(id => ({ id, fanIn: fanIn.get(id) || 0, name: nodeMap.get(id).name }))
  .sort((a, b) => b.fanIn - a.fanIn)
  .slice(0, 20);

// B. Fan-Out Ranking (top 20)
const fanOutRanking = [...nodeMap.keys()]
  .map(id => ({ id, fanOut: fanOut.get(id) || 0, name: nodeMap.get(id).name }))
  .sort((a, b) => b.fanOut - a.fanOut)
  .slice(0, 20);

// C. Entry Point Candidates
const totalNodes = nodes.length;
const fanOutValues = [...fanOut.values()].sort((a, b) => a - b);
const fanInValues = [...fanIn.values()].sort((a, b) => a - b);
const top10pctFanOut = fanOutValues[Math.floor(totalNodes * 0.9)];
const bottom25pctFanIn = fanInValues[Math.floor(totalNodes * 0.25)];

const entryPointNames = new Set([
  'index.ts','index.js','main.ts','main.js','app.ts','app.js',
  'server.ts','server.js','mod.rs','main.go','main.py','main.rs',
  'manage.py','app.py','wsgi.py','asgi.py','run.py','__main__.py',
  'Application.java','Main.java','Program.cs','config.ru','index.php',
  'App.swift','Application.kt','main.cpp','main.c','lib.rs'
]);

const scores = new Map();
for (const n of nodes) {
  let score = 0;
  const fp = n.filePath || '';
  const depth = fp.split('/').length - 1;

  if (n.type === 'document') {
    if (n.name === 'README.md' && depth === 0) score += 5;
    else if (n.name.endsWith('.md') && depth === 0) score += 2;
  } else if (n.type === 'file') {
    if (entryPointNames.has(n.name)) score += 3;
    if (depth <= 2) score += 1;
    if ((fanOut.get(n.id) || 0) >= top10pctFanOut) score += 1;
    if ((fanIn.get(n.id) || 0) <= bottom25pctFanIn) score += 1;
  }

  // Bonus for the known entry point
  if (fp === 'src/cmd_all/src/lib.rs') score += 5;

  scores.set(n.id, score);
}

const entryPointCandidates = [...scores.entries()]
  .filter(([, s]) => s > 0)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 5)
  .map(([id, score]) => ({
    id,
    score,
    name: nodeMap.get(id).name,
    summary: nodeMap.get(id).summary || ''
  }));

// D. BFS from top code entry point
// Find top code entry point (skip documents)
const topCodeEntry = entryPointCandidates.find(c => {
  const n = nodeMap.get(c.id);
  return n && n.type === 'file';
});

const bfsStart = topCodeEntry ? topCodeEntry.id : 'file:src/cmd_all/src/lib.rs';
const bfsOrder = [];
const depthMap = {};
const visited = new Set();
const queue = [[bfsStart, 0]];
visited.add(bfsStart);

while (queue.length > 0) {
  const [current, depth] = queue.shift();
  bfsOrder.push(current);
  depthMap[current] = depth;

  if (depth >= 4) continue; // limit BFS depth to keep results manageable

  const neighbors = forwardAdj.get(current) || new Set();
  for (const neighbor of neighbors) {
    if (!visited.has(neighbor)) {
      visited.add(neighbor);
      queue.push([neighbor, depth + 1]);
    }
  }
}

const byDepth = {};
for (const [id, d] of Object.entries(depthMap)) {
  if (!byDepth[d]) byDepth[d] = [];
  byDepth[d].push(id);
}

const bfsTraversal = { startNode: bfsStart, order: bfsOrder, depthMap, byDepth };

// E. Non-Code File Inventory
const nonCodeFiles = { documentation: [], infrastructure: [], data: [], config: [] };
const infraTypes = new Set(['service','pipeline','resource']);
const dataTypes = new Set(['table','schema','endpoint']);

for (const n of nodes) {
  if (n.type === 'document') {
    nonCodeFiles.documentation.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  } else if (infraTypes.has(n.type)) {
    nonCodeFiles.infrastructure.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  } else if (dataTypes.has(n.type)) {
    nonCodeFiles.data.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  } else if (n.type === 'config') {
    nonCodeFiles.config.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  }
}

// F. Tightly Coupled Clusters
// Find bidirectional edges
const edgeSet = new Set();
const bidirPairs = [];

for (const e of edges) {
  if (e.type === 'imports' || e.type === 'calls' || e.type === 'depends_on') {
    edgeSet.add(`${e.source}|||${e.target}`);
  }
}

for (const e of edges) {
  if (e.type === 'imports' || e.type === 'calls' || e.type === 'depends_on') {
    if (edgeSet.has(`${e.target}|||${e.source}`) && e.source < e.target) {
      bidirPairs.push([e.source, e.target]);
    }
  }
}

// Build clusters from bidirectional pairs
const clusterMap = new Map();
for (const [a, b] of bidirPairs) {
  let found = null;
  for (const [key, cluster] of clusterMap) {
    if (cluster.has(a) || cluster.has(b)) {
      found = key;
      break;
    }
  }
  if (found) {
    clusterMap.get(found).add(a);
    clusterMap.get(found).add(b);
  } else {
    const s = new Set([a, b]);
    clusterMap.set(a + '|||' + b, s);
  }
}

// Score clusters by total mutual edges
const clusters = [...clusterMap.values()]
  .filter(c => c.size >= 2 && c.size <= 8)
  .map(c => {
    const members = [...c];
    let edgeCount = 0;
    for (const m of members) {
      for (const m2 of members) {
        if (m !== m2 && edgeSet.has(`${m}|||${m2}`)) edgeCount++;
      }
    }
    return { nodes: members, edgeCount };
  })
  .sort((a, b) => b.edgeCount - a.edgeCount)
  .slice(0, 10);

// G. Layers
const layerInfo = {
  count: layers.length,
  list: layers.map(l => ({ id: l.id, name: l.name, description: l.description }))
};

// H. Node Summary Index
const nodeSummaryIndex = {};
for (const n of nodes) {
  nodeSummaryIndex[n.id] = { name: n.name, type: n.type, summary: n.summary || '' };
}

const result = {
  scriptCompleted: true,
  entryPointCandidates,
  fanInRanking,
  fanOutRanking,
  bfsTraversal,
  nonCodeFiles,
  clusters,
  layers: layerInfo,
  nodeSummaryIndex,
  totalNodes: nodes.length,
  totalEdges: edges.length
};

try {
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.log(`Results written to ${outputPath}`);
  console.log(`Total nodes: ${nodes.length}, Total edges: ${edges.length}`);
  console.log(`Entry points found: ${entryPointCandidates.length}`);
  console.log(`BFS nodes visited: ${bfsOrder.length}`);
  console.log(`Clusters found: ${clusters.length}`);
} catch (e) {
  console.error('Failed to write output:', e.message);
  process.exit(1);
}
