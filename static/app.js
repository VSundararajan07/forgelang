const sourceEl = document.getElementById('source');
const maxVerticesEl = document.getElementById('max-vertices');
const vertexValueEl = document.getElementById('vertex-value');
const maxGraphsEl = document.getElementById('max-graphs');
const checkButton = document.getElementById('check-button');
const buttonLabel = document.getElementById('button-label');
const resultsSection = document.getElementById('results');
const errorBox = document.getElementById('error-box');
const resultContent = document.getElementById('result-content');
const toast = document.getElementById('toast');
let toastTimeout;

maxVerticesEl.addEventListener('input', () => { vertexValueEl.textContent = maxVerticesEl.value; });

document.getElementById('load-example').addEventListener('click', () => {
  sourceEl.value = `conjecture "Tree Characterization":\n    V(G in SimpleGraphs:\n        tree(G) <=> (connected(G) & edges(G) == vertices(G) - 1)\n    )`;
  sourceEl.focus();
  showToast('Tree characterization loaded into editor.');
});

document.querySelectorAll('.example-card').forEach(card => {
  card.addEventListener('click', async () => {
    try {
      const response = await fetch('/api/examples');
      const examples = await response.json();
      const example = examples.find(item => item.filename === card.dataset.example);
      if (!example) throw new Error('Example file was not found.');
      sourceEl.value = example.source;
      sourceEl.focus();
      window.scrollTo({top: 0, behavior: 'smooth'});
      showToast(`${example.name} loaded into editor.`);
    } catch (error) { showToast(error.message || 'Could not load example.'); }
  });
});

checkButton.addEventListener('click', runCheck);

async function runCheck() {
  resultsSection.hidden = false;
  errorBox.hidden = true;
  resultContent.hidden = true;
  document.getElementById('graph-panel').hidden = true;
  document.getElementById('result-title').textContent = 'Checking your conjecture…';
  document.getElementById('result-status').textContent = 'RUNNING';
  document.getElementById('result-status').classList.remove('bad');
  checkButton.disabled = true;
  buttonLabel.textContent = 'Searching graphs…';
  resultsSection.scrollIntoView({behavior: 'smooth', block: 'start'});
  try {
    const response = await fetch('/api/check', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({source: sourceEl.value, max_vertices: Number(maxVerticesEl.value), max_graphs: Number(maxGraphsEl.value)})
    });
    const data = await response.json();
    if (!response.ok || data.status === 'INVALID_FORMULA' || data.status === 'INVALID_SETTINGS') {
      showError(data.error || data.message || 'The conjecture could not be checked.');
      return;
    }
    renderResults(data);
  } catch (error) {
    showError(`Could not contact the ForgeLang server. Make sure the Python web app is running.\n\n${error.message || ''}`);
  } finally {
    checkButton.disabled = false;
    buttonLabel.textContent = 'Check conjecture';
  }
}

function showError(message) {
  document.getElementById('result-title').textContent = 'Could not check conjecture';
  const status = document.getElementById('result-status');
  status.textContent = 'NEEDS ATTENTION'; status.classList.add('bad');
  errorBox.textContent = message; errorBox.hidden = false; resultContent.hidden = true;
}

function renderResults(data) {
  errorBox.hidden = true; resultContent.hidden = false;
  document.getElementById('result-title').textContent = data.conjecture_name || 'Search results';
  const status = document.getElementById('result-status');
  status.classList.toggle('bad', data.status !== 'COUNTEREXAMPLE_FOUND');
  status.textContent = data.status === 'COUNTEREXAMPLE_FOUND' ? 'COUNTEREXAMPLE FOUND' : 'NO COUNTEREXAMPLE FOUND';
  document.getElementById('result-message').textContent = data.message;
  document.getElementById('stat-examined').textContent = Number(data.graphs_examined || 0).toLocaleString();
  document.getElementById('stat-time').textContent = Number(data.elapsed_seconds || 0).toFixed(4);
  document.getElementById('stat-bound').textContent = `≤ ${data.max_vertices}`;
  const certificateLine = document.getElementById('certificate-line');
  if (data.certificate) { certificateLine.textContent = `Certificate saved locally: ${data.certificate}`; certificateLine.hidden = false; }
  else { certificateLine.hidden = true; }
  const graphPanel = document.getElementById('graph-panel');
  if (data.graph) {
    graphPanel.hidden = false;
    document.getElementById('graph-heading').textContent = `${data.graph.n} vertices · ${data.graph.edges.length} edges`;
    drawGraph(data.graph);
    document.getElementById('graph-details').textContent = `Edges: ${JSON.stringify(data.graph.edges)}   Degrees: (${data.graph.degrees.join(', ')})`;
  }
}

function drawGraph(graph) {
  const svg = document.getElementById('graph-svg');
  svg.replaceChildren();
  const ns = 'http://www.w3.org/2000/svg';
  const n = graph.n;
  if (!n) return;
  const cx = 210, cy = 145, radius = n === 1 ? 0 : Math.min(105, 32 + n * 12);
  const points = Array.from({length: n}, (_, i) => {
    const angle = -Math.PI / 2 + 2 * Math.PI * i / n;
    return {x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle), id: i};
  });
  const edgeSet = new Set(graph.edges.map(e => `${e[0]}-${e[1]}`));
  graph.edges.forEach(([u,v]) => {
    const line = document.createElementNS(ns, 'line');
    line.setAttribute('x1', points[u].x); line.setAttribute('y1', points[u].y);
    line.setAttribute('x2', points[v].x); line.setAttribute('y2', points[v].y);
    line.setAttribute('stroke', '#53677c'); line.setAttribute('stroke-width', '2.2');
    svg.appendChild(line);
  });
  points.forEach(point => {
    const group = document.createElementNS(ns, 'g');
    const circle = document.createElementNS(ns, 'circle');
    circle.setAttribute('cx', point.x); circle.setAttribute('cy', point.y); circle.setAttribute('r', '17');
    circle.setAttribute('fill', '#b8f36b'); circle.setAttribute('stroke', '#e0ffbd'); circle.setAttribute('stroke-width', '1.5');
    const label = document.createElementNS(ns, 'text');
    label.setAttribute('x', point.x); label.setAttribute('y', point.y + 4);
    label.setAttribute('text-anchor', 'middle'); label.setAttribute('font-family', 'DM Mono, monospace');
    label.setAttribute('font-size', '12'); label.setAttribute('font-weight', '500'); label.setAttribute('fill', '#142011');
    label.textContent = point.id;
    const degree = document.createElementNS(ns, 'text');
    degree.setAttribute('x', point.x); degree.setAttribute('y', point.y + 31);
    degree.setAttribute('text-anchor', 'middle'); degree.setAttribute('font-family', 'DM Mono, monospace');
    degree.setAttribute('font-size', '9'); degree.setAttribute('fill', '#94a7bb');
    degree.textContent = `deg ${graph.degrees[point.id]}`;
    group.append(circle, label, degree); svg.appendChild(group);
  });
}

function showToast(message) {
  toast.textContent = message; toast.hidden = false;
  clearTimeout(toastTimeout); toastTimeout = setTimeout(() => { toast.hidden = true; }, 2400);
}
