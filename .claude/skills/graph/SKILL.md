---
name: graph
description: /graph — Knowledge Graph 커맨드
metadata:
  short-description: /graph — Knowledge Graph 커맨드
---

<!--
generated-by: atomy-toolkit codex-adapter
source: _global-toolkit/core/graph.yaml
generated-at: 2026-06-02T06:24:10.457748+00:00
transformations: ['frontmatter_codex']
-->

# /graph — Knowledge Graph 커맨드

인자: $ARGUMENTS

---

## 서브커맨드 라우팅

`$ARGUMENTS`를 파싱하여 아래 서브커맨드를 실행하세요. 인자가 비어있으면 **상태 요약**을 실행합니다.

---

### (기본) 상태 요약

인자 없이 `/graph` 호출 시:

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_builder, graph_client

result = graph_builder.build('.', 0)  # session_number=0: 수동 빌드(세션 불명)
if result is None:
    print("Graph not initialized. Run `/graph init` first.")
else:
    idx = graph_client.load_graph_index('.')
    nodes = idx.get('nodes', [])  # graph_index.json 의 nodes 는 list
    edges_count = sum(len(n.get('edges_out', [])) for n in nodes)
    orphans = [n['local_id'] for n in nodes if not n.get('edges_out') and not n.get('edges_in')]
    print(f"Nodes: {len(nodes)} | Edges: {edges_count} | Orphans: {len(orphans)}")
    print("Subcommands: /graph timeline (초보자용 프로젝트 흐름) · /graph build · /graph stats · /graph viz")
```

---

### `/graph build`

수동으로 graph_index.json을 재빌드합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_builder
result = graph_builder.build('.', 0)  # session_number=0: 수동 빌드(세션 불명)
print(f"Build complete: {result.nodes_total} nodes, {result.edges_total} edges, {len(result.warnings)} warnings")
```

---

### `/graph timeline [output_path]`

프로젝트 운영 이력을 시간순 서사 HTML로 렌더링합니다. `/timeline` 은 이 서브커맨드의 별칭입니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
from pathlib import Path
import timeline_builder, timeline_renderer

args = "$ARGUMENTS".split()
output_arg = args[1] if len(args) > 1 else None
model = timeline_builder.build_timeline('.')
if model is None:
    print("아직 타임라인을 만들 기록이 없습니다. 확인한 소스:")
    print("  ✗ docs/context.md")
    print("  ✗ .claude/memory/")
    print("  ✗ memtemple")
    print("  ✗ docs/plan.md")
    print("다음 행동: `/rpi`와 `/handoff` 한 사이클을 마치면 타임라인이 생깁니다.")
else:
    out = Path(output_arg) if output_arg else Path('.claude/memory/graph/views/timeline.html')
    timeline_renderer.render_timeline_html(model, str(out), '.')
    uri = out.resolve().as_uri()
    print(f"타임라인 생성: {uri}")
    print(f"  열기 힌트 — Windows: start {out} · macOS: open {out} · Linux: xdg-open {out}")
    print(f"  coverage: {model.coverage.mode} ({model.coverage.context_blocks} cycles)")
```

---

### `/graph diagnose [output_path]`

프로젝트를 진단해 청소거리·다음 할 일·운영 효율 제안을 냅니다. `/diagnose` 는 이 서브커맨드의 별칭입니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
from pathlib import Path
import diagnose_builder, diagnose_narrator, timeline_builder, timeline_renderer

args = "$ARGUMENTS".split()
output_arg = args[1] if len(args) > 1 else None
model = diagnose_builder.build_diagnosis('.')
narrated = diagnose_narrator.narrate(model)
out = Path(output_arg) if output_arg else Path('.claude/memory/graph/views/timeline.html')

if model.counts["total"] == 0:
    print("진단 신호 없음 — 깨끗합니다 ✅ (" + model.coverage_note + ")")
else:
    timeline = timeline_builder.build_timeline('.')
    if timeline is None:
        print("타임라인 소스가 없어 HTML 패널을 만들 수 없습니다.")
    else:
        timeline_renderer.render_timeline_html(timeline, str(out), '.', diagnosis=(model, narrated))
        print(f"engine={narrated['engine']} · 청소 {model.counts['cleanup']} · 다음 {model.counts['next_action']} · 효율 {model.counts['efficiency']}")
        for finding in narrated["ordered"][:5]:
            print(f"  [{finding.severity}] {finding.title} — {finding.evidence_ref}")
        print(f"열기: {out.resolve().as_uri()}  (Windows: start {out} · macOS: open {out} · Linux: xdg-open {out})")
```

---

### `/graph code [output_path]`

Python 코드 구조를 AST 기반 Knowledge Graph로 만들고 HTML로 렌더링합니다. `/code-map`은 이 서브커맨드의 별칭입니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
from pathlib import Path
import code_graph_builder, graph_renderer

args = "$ARGUMENTS".split()
output_arg = args[1] if len(args) > 1 else None

graph = code_graph_builder.build_code_graph('.')
findings = code_graph_builder.diagnose_structure(graph)
out = Path(output_arg) if output_arg else Path('.claude/memory/graph/views/code_graph.html')
graph_renderer.render_html(graph, str(out))

print(f"Code graph: {len(graph.get('nodes', []))} nodes")
for finding in findings[:8]:
    print(f"  [{finding['severity']}] {finding['rule_id']} - {finding['evidence_ref']}")
print(f"Open: {out.resolve().as_uri()}")
print(f"  Windows: start {out} | macOS: open {out} | Linux: xdg-open {out}")
```

---

### `/code-map [output_path]`

`/graph code [output_path]`와 동일하게 실행합니다.

---

### `/graph show {id}`

노드 상세 + 1-hop 이웃을 표시합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
node = graph_client.find_node(idx, '<id>')
if node:
    result = graph_client.get_neighbors(idx, '<id>', hop=1)  # 반환: GraphQueryResult
    # result.center_node / result.neighbors 를 마크다운으로 출력
```

---

### `/graph explore {id}`

2-hop 탐색 결과를 표시합니다. (Phase K6에서 HTML 시각화 추가 예정)

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
result = graph_client.get_neighbors(idx, '<id>', hop=2)  # 반환: GraphQueryResult
# result.neighbors 를 계층적으로 출력
```

---

### `/graph link {src} {tgt} [type]`

수동으로 엣지를 추가합니다. 소스 메모리 파일의 `links` frontmatter에 항목을 추가합니다.

1. `graph_client.find_node(idx, src)` 로 소스 노드 확인
2. 소스 파일의 frontmatter `links`에 `{target: tgt, type: type}` 추가
3. `/graph build` 로 재빌드

기본 edge type: `related_to`

---

### `/graph unlink {src} {tgt}`

소스 파일의 frontmatter `links`에서 해당 타겟 제거 후 재빌드.

---

### `/graph path {src} {tgt}`

두 노드 간 최단 경로를 탐색합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
path = graph_client.find_path(idx, '<src>', '<tgt>')  # 반환: list[dict] | None
if path:
    print(" -> ".join(n['local_id'] for n in path))
else:
    print("No path found.")
```

---

### `/graph glossary {term}`

용어를 검색하거나, 없으면 새 glossary 파일 생성을 제안합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
results = graph_client.find_by_term(idx, '<term>')
if results:
    # 용어 정의와 관련 노드 출력
else:
    # .claude/memory/graph/glossary/{term-slug}.md 생성 제안
```

---

### `/graph domain {name}`

특정 도메인에 속한 노드만 필터링하여 서브그래프를 표시합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
nodes = [n for n in idx.get('nodes', []) if n.get('domain') == '<name>']  # nodes 는 list
# 도메인 서브그래프 출력 (또는 graph_client.get_domain_subgraph(idx, '<name>') 사용)
```

---

### `/graph orphans`

연결이 없는 고아 노드를 나열하고 연결 제안을 합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
orphans = graph_client.get_orphan_nodes(idx)
# 고아 노드 목록 + 잠재적 연결 후보 제안
```

---

### `/graph viz`

전체 그래프를 D3.js force-directed HTML로 렌더링합니다. (Phase K6에서 구현)

현재: "Phase K6에서 구현 예정. `/graph explore {id}`로 부분 탐색 가능." 메시지 출력.

---

### `/graph init`

기존 ASMR 메모리에서 Knowledge Graph를 최초 구축합니다.

1. `.claude/memory/graph/` 디렉토리 확인/생성
2. `graph_meta.yaml` 존재 확인
3. `graph_builder.build('.', 0)` 실행 (session_number=0: 수동 빌드)
4. 결과 보고

---

### `/graph stats`

상세 통계를 출력합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
nodes = idx.get('nodes', [])  # nodes 는 list
# 노드 타입별 수, 엣지 타입별 수, 도메인별 분포, 고아 비율 등 (idx['stats'] 에 집계 존재)
```

---

### `/graph sources`

등록된 data_source 목록과 상태를 확인합니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
import data_source_resolver
sources = data_source_resolver.load_sources('.')
for s in sources:
    privacy = s.get('privacy_level', 'public')
    print(f"  {s['id']} — {s.get('name', '?')} [{privacy}]")
if not sources:
    print("No data sources registered. Add YAML files to .claude/memory/graph/sources/")
```
