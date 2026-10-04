import { connectionCharts, connectionKinds, type ConnectionChart, type ConnectionEdge, type ConnectionNode } from './connection-data';

const nodeWidth = 230, nodeHeight = 168;
const esc = (value: string) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const source = (file: string) => `https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/${file}`;

/** Connect card boundaries. These coordinates encode layout only. */
export function connectionGeometry(from: ConnectionNode, to: ConnectionNode, offset = 0): { path: string; x: number; y: number } {
  const dx = to.x - from.x, dy = to.y - from.y;
  let x1: number, y1: number, x2: number, y2: number, path: string;
  if (Math.abs(dx) >= nodeWidth + 30) {
    const direction = Math.sign(dx);
    x1 = from.x + (direction > 0 ? nodeWidth : 0); y1 = from.y + nodeHeight / 2 + offset;
    x2 = to.x + (direction > 0 ? 0 : nodeWidth); y2 = to.y + nodeHeight / 2 + offset;
    const bend = Math.max(55, Math.abs(x2 - x1) * .42);
    path = `M${x1},${y1} C${x1 + direction * bend},${y1} ${x2 - direction * bend},${y2} ${x2},${y2}`;
  } else {
    const direction = Math.sign(dy) || 1;
    x1 = from.x + nodeWidth / 2 + offset; y1 = from.y + (direction > 0 ? nodeHeight : 0);
    x2 = to.x + nodeWidth / 2 + offset; y2 = to.y + (direction > 0 ? 0 : nodeHeight);
    // Cross-lane routes run alongside the cards rather than through their centers.
    const lane = Math.min(from.x, to.x) - 35 - Math.abs(offset);
    path = `M${x1},${y1} C${lane},${y1 + direction * 35} ${lane},${y2 - direction * 35} ${x2},${y2}`;
  }
  return { path, x: (x1 + x2) / 2, y: (y1 + y2) / 2 };
}

function board(chart: ConnectionChart, instance: string): string {
  const width = Math.max(...chart.nodes.map(node => node.x)) + nodeWidth + 65;
  const height = Math.max(...chart.nodes.map(node => node.y)) + nodeHeight + 60;
  const kinds = [...new Set(chart.edges.map(edge => edge.kind))];
  return `<div class="connection-tools"><div class="connection-zoom" aria-label="Diagram scale"><button type="button" data-zoom="out" aria-label="Zoom out">−</button><output data-scale>100%</output><button type="button" data-zoom="in" aria-label="Zoom in">+</button><button type="button" data-reset>Reset view</button></div><label>Find a part <select data-find><option value="">Choose a card…</option>${chart.nodes.map(node => `<option value="${node.id}">${esc(node.title)}</option>`).join('')}</select></label></div>
    <p class="connection-instruction" id="${instance}-help">Scroll or swipe across the chart. Drag empty space with a mouse. Select a card to trace its connections; use Tab or the menus to explore by keyboard.</p>
    <div class="connection-filters" aria-label="Highlight a connection kind"><button type="button" data-kind="all" aria-pressed="true">All connections</button>${kinds.map(kind => `<button type="button" data-kind="${kind}" class="kind-${kind}" aria-pressed="false"><span aria-hidden="true"></span>${connectionKinds[kind]}</button>`).join('')}</div>
    <div class="connection-viewport" style="--chart-height:${height + 2}px" tabindex="0" role="region" aria-label="Scrollable ${esc(chart.title)} chart" aria-describedby="${instance}-help"><div class="connection-surface" style="width:${width}px;height:${height}px"><div class="connection-board" style="width:${width}px;height:${height}px" data-width="${width}" data-height="${height}">
    <svg class="connection-lines" width="${width}" height="${height}" aria-hidden="true"><defs>${kinds.map(kind => `<marker id="${instance}-${kind}" class="kind-${kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" /></marker>`).join('')}</defs>${chart.edges.map((edge, i) => { const geometry = connectionGeometry(chart.nodes.find(node => node.id === edge.from)!, chart.nodes.find(node => node.id === edge.to)!, (i % 3 - 1) * 10); return `<path data-line="${i}" class="connection-line kind-${edge.kind}" d="${geometry.path}" ${edge.kind === 'membership' ? '' : `marker-end="url(#${instance}-${edge.kind})"`}/><path data-line-hit="${i}" class="connection-hit" d="${geometry.path}"><title>${esc(chart.nodes.find(node => node.id === edge.from)!.title)} → ${esc(chart.nodes.find(node => node.id === edge.to)!.title)} / ${esc(edge.label)} / ${connectionKinds[edge.kind]}</title></path>`; }).join('')}</svg>
    ${chart.nodes.map(node => `<button type="button" class="connection-node" data-node="${node.id}" style="left:${node.x}px;top:${node.y}px;width:${nodeWidth}px;height:${nodeHeight}px" aria-pressed="false"><strong>${esc(node.title)}</strong><span>${esc(node.subtitle)}</span></button>`).join('')}
    </div></div></div>
    <div class="connection-reading"><div data-detail aria-live="polite"><p class="eyebrow">TRACE A CONNECTION</p><h4>Select a card or line</h4><p>Names stay readable at their natural size. Scroll to follow the network, or find a part with the menu above.</p></div><label class="connection-edge-menu">Inspect a connection<select data-edge><option value="">Choose a connection…</option>${chart.edges.map((edge, i) => `<option value="${i}">${esc(chart.nodes.find(node => node.id === edge.from)!.title)} ${edge.kind === 'membership' ? '—' : '→'} ${esc(chart.nodes.find(node => node.id === edge.to)!.title)} / ${esc(edge.label)}</option>`).join('')}</select></label></div>
    <p class="connection-limit">${esc(chart.limit)} <a href="${source(chart.source)}">Chart source ↗</a></p>`;
}

export function connectionExplorer(key: keyof typeof connectionCharts, instance = `study-${key}`): string {
  const charts = connectionCharts[key];
  return `<section class="connection-explorer" id="${instance}-connections" data-connections="${key}" data-instance="${instance}" aria-label="Interactive connection charts"><div class="connection-heading"><p class="eyebrow accent">EXPLORE THE CONNECTIONS</p><h2>Follow the connections.</h2></div><div class="connection-tabs" aria-label="Choose a connection chart">${charts.map((chart, i) => `<button type="button" data-chart="${chart.id}" aria-pressed="${i === 0}">${chart.title}</button>`).join('')}</div><div data-chart-content><div class="connection-caption"><h3>${charts[0].title}</h3><p>${charts[0].intro}</p></div>${board(charts[0], instance)}</div></section>`;
}

export function mountConnectionCharts(): void {
  document.querySelectorAll<HTMLElement>('[data-connections]').forEach(explorer => {
    const charts = connectionCharts[explorer.dataset.connections as keyof typeof connectionCharts];
    let chart = charts[0], scale = 1;
    const instance = explorer.dataset.instance!;
    const content = explorer.querySelector<HTMLElement>('[data-chart-content]')!;
    const bind = () => {
      const viewport = content.querySelector<HTMLElement>('.connection-viewport')!;
      const stage = content.querySelector<HTMLElement>('.connection-board')!;
      const surface = content.querySelector<HTMLElement>('.connection-surface')!;
      const detail = content.querySelector<HTMLElement>('[data-detail]')!;
      const find = content.querySelector<HTMLSelectElement>('[data-find]')!;
      const edgeMenu = content.querySelector<HTMLSelectElement>('[data-edge]')!;
      const mark = (indices: number[]) => {
        content.querySelectorAll<SVGPathElement>('[data-line]').forEach(line => {
          line.classList.toggle('is-highlighted', indices.includes(Number(line.dataset.line)));
          line.classList.toggle('is-muted', indices.length > 0 && !indices.includes(Number(line.dataset.line)));
        });
      };
      const clearNodes = () => content.querySelectorAll<HTMLButtonElement>('[data-node]').forEach(button => button.setAttribute('aria-pressed', 'false'));
      const resetKinds = () => content.querySelectorAll<HTMLButtonElement>('[data-kind]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.kind === 'all')));
      const edgeReading = (edge: ConnectionEdge) => `<span class="connection-kind kind-${edge.kind}">${connectionKinds[edge.kind]}</span><h4>${esc(chart.nodes.find(node => node.id === edge.from)!.title)} ${edge.kind === 'membership' ? '—' : '→'} ${esc(chart.nodes.find(node => node.id === edge.to)!.title)}</h4><p><strong>${esc(edge.label)}</strong>${edge.detail ? ` · ${esc(edge.detail)}` : ''}</p>`;
      const selectEdge = (index: number) => {
        const edge = chart.edges[index]; if (!edge) return;
        clearNodes(); resetKinds(); find.value = ''; edgeMenu.value = String(index); mark([index]);
        detail.innerHTML = edgeReading(edge) + `<div class="connection-neighbors"><button type="button" data-go="${edge.from}">Find ${esc(chart.nodes.find(node => node.id === edge.from)!.title)}</button><button type="button" data-go="${edge.to}">Find ${esc(chart.nodes.find(node => node.id === edge.to)!.title)}</button></div>`;
        detail.querySelectorAll<HTMLButtonElement>('[data-go]').forEach(button => button.addEventListener('click', () => selectNode(button.dataset.go!, true)));
      };
      const selectNode = (id: string, center: boolean) => {
        const node = chart.nodes.find(node => node.id === id); if (!node) return;
        clearNodes(); resetKinds(); find.value = id; edgeMenu.value = '';
        content.querySelector<HTMLButtonElement>(`[data-node="${id}"]`)!.setAttribute('aria-pressed', 'true');
        const indices = chart.edges.flatMap((edge, i) => edge.from === id || edge.to === id ? [i] : []); mark(indices);
        detail.innerHTML = `<p class="eyebrow">SELECTED PART</p><h4>${esc(node.title)}</h4><p>${esc(node.detail)}</p><div class="connection-neighbors">${indices.map(i => { const edge = chart.edges[i], other = chart.nodes.find(n => n.id === (edge.from === id ? edge.to : edge.from))!; return `<button type="button" data-follow="${i}"><span>${edge.kind === 'membership' ? '—' : edge.from === id ? '→' : '←'} ${esc(other.title)}</span><small>${esc(edge.label)} · ${connectionKinds[edge.kind]}</small></button>`; }).join('')}</div>`;
        detail.querySelectorAll<HTMLButtonElement>('[data-follow]').forEach(button => button.addEventListener('click', () => selectEdge(Number(button.dataset.follow))));
        if (center) viewport.scrollTo({ left: (node.x + nodeWidth / 2) * scale - viewport.clientWidth / 2, top: (node.y + nodeHeight / 2) * scale - viewport.clientHeight / 2 });
      };
      content.querySelectorAll<HTMLButtonElement>('[data-node]').forEach(button => button.addEventListener('click', () => selectNode(button.dataset.node!, false)));
      content.querySelectorAll<SVGPathElement>('[data-line], [data-line-hit]').forEach(line => line.addEventListener('click', () => selectEdge(Number(line.dataset.lineHit ?? line.dataset.line))));
      find.addEventListener('change', () => selectNode(find.value, true));
      edgeMenu.addEventListener('change', () => { if (edgeMenu.value !== '') selectEdge(Number(edgeMenu.value)); });
      content.querySelectorAll<HTMLButtonElement>('[data-kind]').forEach(button => button.addEventListener('click', () => {
        clearNodes(); find.value = ''; edgeMenu.value = '';
        content.querySelectorAll<HTMLButtonElement>('[data-kind]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
        const kind = button.dataset.kind;
        const indices = chart.edges.flatMap((edge, i) => edge.kind === kind ? [i] : []); mark(indices);
        detail.innerHTML = `<p class="eyebrow">CONNECTION KIND</p><h4>${esc(button.textContent!.trim())}</h4><p>${kind === 'all' ? 'All connections are visible. Select a card or line to read it.' : `${indices.length} connections highlighted. Physical movement, records, requirements and possibilities have different meanings; line width gives no quantity.`}</p>`;
      }));
      const zoom = (next: number) => {
        const centerX = (viewport.scrollLeft + viewport.clientWidth / 2) / scale;
        const centerY = (viewport.scrollTop + viewport.clientHeight / 2) / scale;
        scale = Math.max(.75, Math.min(1.5, next));
        stage.style.transform = `scale(${scale})`;
        surface.style.width = `${Number(stage.dataset.width) * scale}px`; surface.style.height = `${Number(stage.dataset.height) * scale}px`;
        content.querySelector('output')!.textContent = `${Math.round(scale * 100)}%`;
        content.querySelector<HTMLButtonElement>('[data-zoom="out"]')!.disabled = scale === .75;
        content.querySelector<HTMLButtonElement>('[data-zoom="in"]')!.disabled = scale === 1.5;
        viewport.scrollTo(centerX * scale - viewport.clientWidth / 2, centerY * scale - viewport.clientHeight / 2);
      };
      content.querySelectorAll<HTMLButtonElement>('[data-zoom]').forEach(button => button.addEventListener('click', () => zoom(scale + (button.dataset.zoom === 'in' ? .25 : -.25))));
      content.querySelector<HTMLButtonElement>('[data-reset]')!.addEventListener('click', () => { zoom(1); viewport.scrollTo(0, 0); clearNodes(); resetKinds(); find.value = ''; edgeMenu.value = ''; mark([]); detail.innerHTML = '<h4>All connections</h4><p>Select a card or line to trace its connections.</p>'; });
      // Native touch scrolling stays available. Mouse dragging only starts on empty space.
      let drag: { x: number; y: number; left: number; top: number } | null = null;
      viewport.addEventListener('pointerdown', event => {
        if (event.pointerType !== 'mouse' || event.button !== 0 || (event.target as Element).closest('button, [data-line], [data-line-hit]')) return;
        drag = { x: event.clientX, y: event.clientY, left: viewport.scrollLeft, top: viewport.scrollTop };
        viewport.setPointerCapture(event.pointerId); viewport.classList.add('is-dragging'); event.preventDefault();
      });
      viewport.addEventListener('pointermove', event => { if (drag) viewport.scrollTo(drag.left - event.clientX + drag.x, drag.top - event.clientY + drag.y); });
      const stopDrag = () => { drag = null; viewport.classList.remove('is-dragging'); };
      viewport.addEventListener('pointerup', stopDrag); viewport.addEventListener('pointercancel', stopDrag); viewport.addEventListener('lostpointercapture', stopDrag);
    };
    explorer.querySelectorAll<HTMLButtonElement>('[data-chart]').forEach(button => button.addEventListener('click', () => {
      chart = charts.find(chart => chart.id === button.dataset.chart)!; scale = 1;
      explorer.querySelectorAll<HTMLButtonElement>('[data-chart]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      content.innerHTML = `<div class="connection-caption"><h3>${chart.title}</h3><p>${chart.intro}</p></div>${board(chart, instance)}`; bind();
    }));
    bind();
  });
}
