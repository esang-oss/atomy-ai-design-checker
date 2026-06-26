"""D3.js force-directed graph HTML renderer.

Reads graph_index.json structure and produces a standalone HTML file
with interactive D3.js v7 force-directed visualization.
"""
from __future__ import annotations

import html as html_lib
import json
from collections import deque
from pathlib import Path


# Node type -> color mapping
_TYPE_COLORS = {
    "memory": "#4A90D9",
    "glossary": "#2ECC71",
    "data_source": "#E67E22",
    "external": "#95A5A6",
    "project": "#9B59B6",
    "module": "#F1C40F",
    "function": "#1ABC9C",
    "class": "#E74C3C",
}
_DEFAULT_COLOR = "#7F8C8D"


def _filter_by_hop(graph: dict, center_node: str, hop: int) -> dict:
    """BFS hop filter — returns subgraph within hop distance from center."""
    node_map = {n["local_id"]: n for n in graph.get("nodes", [])}
    if center_node not in node_map:
        return {"nodes": [], "namespace": graph.get("namespace", {})}

    visited: set[str] = {center_node}
    queue: deque[tuple[str, int]] = deque([(center_node, 0)])

    while queue:
        nid, depth = queue.popleft()
        if depth >= hop:
            continue
        node = node_map.get(nid)
        if not node:
            continue
        for e in node.get("edges_out", []):
            target = e["target_local"]
            if target not in visited and target in node_map:
                visited.add(target)
                queue.append((target, depth + 1))
        for e in node.get("edges_in", []):
            source = e["source_local"]
            if source not in visited and source in node_map:
                visited.add(source)
                queue.append((source, depth + 1))

    filtered_nodes = []
    for n in graph.get("nodes", []):
        if n["local_id"] in visited:
            node_copy = dict(n)
            node_copy["edges_out"] = [
                e for e in n.get("edges_out", []) if e["target_local"] in visited
            ]
            node_copy["edges_in"] = [
                e for e in n.get("edges_in", []) if e["source_local"] in visited
            ]
            filtered_nodes.append(node_copy)

    return {"nodes": filtered_nodes, "namespace": graph.get("namespace", {})}


def _build_d3_data(graph: dict) -> dict:
    """Convert graph_index nodes to D3.js compatible nodes + links."""
    nodes = []
    links = []
    seen_edges: set[tuple[str, str, str]] = set()

    for n in graph.get("nodes", []):
        nodes.append({
            "id": n["local_id"],
            "title": n.get("title", n["local_id"]),
            "type": n.get("type", "memory"),
            "fqn": n.get("fqn", ""),
            "domain": n.get("domain", ""),
            "color": _TYPE_COLORS.get(n.get("type", ""), _DEFAULT_COLOR),
        })
        for e in n.get("edges_out", []):
            key = (n["local_id"], e["target_local"], e["type"])
            if key not in seen_edges:
                seen_edges.add(key)
                links.append({
                    "source": n["local_id"],
                    "target": e["target_local"],
                    "type": e.get("type", "related_to"),
                })

    return {"nodes": nodes, "links": links}


def render_html(
    graph: dict,
    output_path: str,
    *,
    center_node: str | None = None,
    hop: int = 2,
) -> Path:
    """Render graph to standalone D3.js HTML file.

    Args:
        graph: graph_index.json dict (with nodes, namespace, etc.)
        output_path: Path to write HTML file.
        center_node: If set, filter to N-hop neighborhood.
        hop: Hop distance for local view (default 2).

    Returns:
        Path to the written HTML file.
    """
    out = Path(output_path)

    if center_node is not None:
        graph = _filter_by_hop(graph, center_node, hop)

    d3_data = _build_d3_data(graph)
    # Escape "</" so an attacker-controlled string value (e.g. a node title containing
    # "</script>") cannot break out of the embedded <script> data block. JSON escaping
    # alone does not touch "/", so the literal closing tag would otherwise survive.
    data_json = json.dumps(d3_data, ensure_ascii=False).replace("</", "<\\/")
    namespace = graph.get("namespace", {})
    project = html_lib.escape(str(namespace.get("project", "unknown")))
    title = f"Knowledge Graph — {project}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; overflow: hidden; }}
  svg {{ width: 100vw; height: 100vh; }}
  .link {{ stroke: #555; stroke-opacity: 0.6; stroke-width: 1.5px; }}
  .link-label {{ font-size: 9px; fill: #888; pointer-events: none; }}
  .node-label {{ font-size: 11px; fill: #ddd; pointer-events: none; text-anchor: middle; }}
  .tooltip {{ position: absolute; background: #16213e; border: 1px solid #0f3460; padding: 8px 12px; border-radius: 6px; font-size: 12px; pointer-events: none; opacity: 0; transition: opacity 0.2s; }}
  .legend {{ position: fixed; top: 16px; right: 16px; background: rgba(22,33,62,0.9); padding: 12px; border-radius: 8px; font-size: 12px; }}
  .legend-item {{ display: flex; align-items: center; margin: 4px 0; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}
  .empty-msg {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 18px; color: #888; }}
</style>
</head>
<body>
<div class="tooltip" id="tooltip"></div>
<div class="legend">
  <div class="legend-item"><span class="legend-dot" style="background:#4A90D9"></span>Memory</div>
  <div class="legend-item"><span class="legend-dot" style="background:#2ECC71"></span>Glossary</div>
  <div class="legend-item"><span class="legend-dot" style="background:#E67E22"></span>Data Source</div>
  <div class="legend-item"><span class="legend-dot" style="background:#9B59B6"></span>Project</div>
  <div class="legend-item"><span class="legend-dot" style="background:#95A5A6"></span>External</div>
  <div class="legend-item"><span class="legend-dot" style="background:#F1C40F"></span>Module</div>
  <div class="legend-item"><span class="legend-dot" style="background:#1ABC9C"></span>Function</div>
  <div class="legend-item"><span class="legend-dot" style="background:#E74C3C"></span>Class</div>
</div>
<svg id="graph"></svg>
<script>
const data = {data_json};

// Escape dynamic node fields before they reach innerHTML (.html()) sinks.
function esc(s) {{
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}}

if (data.nodes.length === 0) {{
  document.body.innerHTML += '<div class="empty-msg">No nodes in graph</div>';
}} else {{
  const svg = d3.select("#graph");
  const width = window.innerWidth;
  const height = window.innerHeight;
  const tooltip = d3.select("#tooltip");

  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(30));

  const g = svg.append("g");

  // Zoom
  svg.call(d3.zoom().scaleExtent([0.1, 4]).on("zoom", (e) => g.attr("transform", e.transform)));

  // Links
  const link = g.append("g").selectAll("line")
    .data(data.links).join("line").attr("class", "link");

  // Link labels
  const linkLabel = g.append("g").selectAll("text")
    .data(data.links).join("text").attr("class", "link-label")
    .text(d => d.type);

  // Nodes
  const node = g.append("g").selectAll("circle")
    .data(data.nodes).join("circle")
    .attr("r", 8)
    .attr("fill", d => d.color)
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .call(d3.drag()
      .on("start", (e, d) => {{ if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
      .on("drag", (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
      .on("end", (e, d) => {{ if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }})
    )
    .on("mouseover", (e, d) => {{
      tooltip.style("opacity", 1)
        .html(`<strong>${{esc(d.title)}}</strong><br/>FQN: ${{esc(d.fqn)}}<br/>Type: ${{esc(d.type)}}<br/>Domain: ${{esc(d.domain) || "—"}}`);
    }})
    .on("mousemove", (e) => {{
      tooltip.style("left", (e.pageX + 12) + "px").style("top", (e.pageY - 12) + "px");
    }})
    .on("mouseout", () => tooltip.style("opacity", 0));

  // Labels
  const label = g.append("g").selectAll("text")
    .data(data.nodes).join("text").attr("class", "node-label")
    .text(d => d.title);

  simulation.on("tick", () => {{
    link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
    linkLabel.attr("x", d => (d.source.x + d.target.x) / 2)
             .attr("y", d => (d.source.y + d.target.y) / 2);
    node.attr("cx", d => d.x).attr("cy", d => d.y);
    label.attr("x", d => d.x).attr("y", d => d.y - 14);
  }});
}}
</script>
</body>
</html>"""

    out.write_text(html, encoding="utf-8")
    return out
