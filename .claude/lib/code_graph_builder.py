"""Build a Python code-structure graph with in-process AST parsing."""
from __future__ import annotations

import ast
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


logger = logging.getLogger(__name__)

EXCLUDE_DIRS = {".venv", "venv", "build", "__pycache__", ".git", "node_modules", ".claude"}
MODULE_DEGREE = 20
FUNC_DEGREE = 12
FANOUT = 15
_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class CodeGraphProvider(Protocol):
    name: str

    def available(self, project_root: str) -> bool: ...

    def build(self, project_root: str) -> dict: ...


@dataclass(frozen=True)
class PythonAstProvider:
    name: str = "python-ast"

    def available(self, project_root: str) -> bool:
        return True

    def build(self, project_root: str) -> dict:
        return _build_ast_graph(project_root)


@dataclass(frozen=True)
class GraphifyStubProvider:
    name: str = "graphify"

    def available(self, project_root: str) -> bool:
        return False

    def build(self, project_root: str) -> dict:
        return {"nodes": [], "namespace": {"project": _project_name(project_root)}}


_GRAPHIFY_STUB = GraphifyStubProvider()
_PYTHON_AST = PythonAstProvider()


@dataclass
class ModuleInfo:
    path: Path
    local_id: str
    tree: ast.Module
    node: dict
    imports: list[str]
    imported_names: dict[str, str]
    functions: dict[str, dict]
    classes: dict[str, dict]
    all_exports: set[str]


def select_provider(project_root: str) -> CodeGraphProvider:
    for provider in (_GRAPHIFY_STUB, _PYTHON_AST):
        if provider.available(project_root):
            return provider
    return _PYTHON_AST


def build_code_graph(project_root: str, provider: str | None = None) -> dict:
    selected = _PYTHON_AST if provider == "python-ast" else select_provider(project_root)
    graph = selected.build(project_root)
    _persist_graph(Path(project_root), graph)
    return graph


def scan_python_files(project_root: str) -> list[Path]:
    root = Path(project_root).resolve()
    files = []
    for path in root.rglob("*.py"):
        rel_parts = path.resolve().relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        files.append(path)
    return sorted(files, key=lambda p: _rel(root, p))


def parse_module(path: str | Path, project_root: str | Path) -> dict | None:
    root = Path(project_root).resolve()
    info = _parse_module_info(Path(path), root, {})
    return None if info is None else info.node


def diagnose_structure(graph: dict) -> list[dict]:
    findings: list[dict] = []
    nodes = sorted(graph.get("nodes", []), key=lambda n: n.get("local_id", ""))
    for node in nodes:
        if _excluded_node(node):
            continue
        degree = len(node.get("edges_out", [])) + len(node.get("edges_in", []))
        if node.get("type") == "module" and degree >= MODULE_DEGREE:
            findings.append(_finding("medium", "God 노드 후보", node["local_id"], "god_node", "medium"))
        if node.get("type") in {"function", "class"} and degree >= FUNC_DEGREE:
            findings.append(_finding("medium", "God 노드 후보", node["local_id"], "god_node", "medium"))
        if node.get("type") == "module" and len(node.get("edges_out", [])) >= FANOUT:
            findings.append(_finding("medium", "과결합 모듈 후보", node["local_id"], "high_coupling", "medium"))
    findings.extend(_circular_findings(nodes))
    findings.extend(_dead_code_findings(nodes))
    return sorted(findings, key=lambda f: (_SEVERITY_ORDER.get(f["severity"], 9), f["rule_id"], f["evidence_ref"]))


def _build_ast_graph(project_root: str) -> dict:
    root = Path(project_root).resolve()
    files = scan_python_files(project_root)
    module_map = _module_name_map(root, files)
    modules: list[ModuleInfo] = []
    for path in files:
        info = _parse_module_info(path, root, module_map)
        if info is not None:
            modules.append(info)
    nodes = _assemble_nodes(modules)
    node_ids = {n["local_id"] for n in nodes}
    for info in modules:
        for target in info.imports:
            if target in node_ids:
                _add_edge(info.node, target, "import", "high")
        _add_call_edges(info, node_ids)
    _fill_edges_in(nodes)
    for node in nodes:
        node["edges_out"] = sorted(node["edges_out"], key=lambda e: (e["target_local"], e["type"]))
        node["edges_in"] = sorted(node["edges_in"], key=lambda e: (e["source_local"], e["type"]))
    return {"nodes": sorted(nodes, key=lambda n: n["local_id"]), "namespace": {"project": _project_name(project_root)}}


def _parse_module_info(path: Path, root: Path, module_map: dict[str, str]) -> ModuleInfo | None:
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        logger.warning("skip python file %s: %s", path, exc)
        return None
    local_id = _rel(root, path)
    functions, classes = _member_nodes(tree, local_id, root)
    all_exports = _extract_all(tree)
    imports, imported_names = _extract_imports(tree, module_map)
    node = _node(local_id, Path(local_id).stem, "module", root)
    node["_parsed"] = True
    return ModuleInfo(path, local_id, tree, node, imports, imported_names, functions, classes, all_exports)


def _member_nodes(tree: ast.Module, module_id: str, root: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    functions: dict[str, dict] = {}
    classes: dict[str, dict] = {}
    for item in tree.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nid = f"{module_id}:{item.name}"
            functions[item.name] = _node(nid, item.name, "function", root, decorated=bool(item.decorator_list))
        elif isinstance(item, ast.ClassDef):
            nid = f"{module_id}:{item.name}"
            classes[item.name] = _node(nid, item.name, "class", root, decorated=bool(item.decorator_list))
    return functions, classes


def _extract_imports(tree: ast.Module, module_map: dict[str, str]) -> tuple[list[str], dict[str, str]]:
    imports: set[str] = set()
    names: dict[str, str] = {}
    for node in _iter_import_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = module_map.get(alias.name)
                if target:
                    imports.add(target)
                    names[alias.asname or alias.name.split(".")[0]] = target
        elif isinstance(node, ast.ImportFrom):
            base = "." * node.level + (node.module or "")
            base = base.lstrip(".")
            base_target = module_map.get(base)
            if base_target:
                imports.add(base_target)
            for alias in node.names:
                full = f"{base}.{alias.name}" if base else alias.name
                target = module_map.get(full) or base_target
                if target:
                    imports.add(target)
                    names[alias.asname or alias.name] = target
    return sorted(imports), names


def _iter_import_nodes(tree: ast.Module) -> list[ast.AST]:
    found: list[ast.AST] = []

    def visit(node: ast.AST, skip: bool = False) -> None:
        if isinstance(node, ast.If) and _is_type_checking_test(node.test):
            for child in node.orelse:
                visit(child, skip)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom)) and not skip:
            found.append(node)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, skip)

    visit(tree)
    return found


def _is_type_checking_test(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "TYPE_CHECKING"


def _extract_all(tree: ast.Module) -> set[str]:
    exports: set[str] = set()
    for item in tree.body:
        if not isinstance(item, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in item.targets):
            continue
        if isinstance(item.value, (ast.List, ast.Tuple)):
            for elt in item.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    exports.add(elt.value)
    return exports


def _add_call_edges(info: ModuleInfo, node_ids: set[str]) -> None:
    local_targets = {**{k: v["local_id"] for k, v in info.functions.items()}, **{k: v["local_id"] for k, v in info.classes.items()}}
    local_targets.update(info.imported_names)
    for name, func_node in {**info.functions, **info.classes}.items():
        body_node = _find_def(info.tree, name)
        if body_node is None:
            continue
        for call in ast.walk(body_node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                target = local_targets.get(call.func.id)
                if target and target in node_ids and target != func_node["local_id"]:
                    _add_edge(func_node, target, "call", "low")


def _find_def(tree: ast.Module, name: str) -> ast.AST | None:
    for item in tree.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and item.name == name:
            return item
    return None


def _assemble_nodes(modules: list[ModuleInfo]) -> list[dict]:
    nodes: list[dict] = []
    for info in modules:
        nodes.append(info.node)
        for name, node in sorted(info.functions.items()):
            node["in_all"] = name in info.all_exports
            node["is_test"] = name.startswith("test_") or "/test" in info.local_id or Path(info.local_id).name.startswith("test_")
            nodes.append(node)
        for name, node in sorted(info.classes.items()):
            node["in_all"] = name in info.all_exports
            node["is_test"] = name.startswith("Test") or "/test" in info.local_id or Path(info.local_id).name.startswith("test_")
            nodes.append(node)
    return nodes


def _module_name_map(root: Path, files: list[Path]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in files:
        rel = _rel(root, path)
        parts = rel[:-3].split("/")
        dotted = ".".join(parts)
        mapping[dotted] = rel
        if parts[-1] == "__init__":
            mapping[".".join(parts[:-1])] = rel
    return mapping


def _fill_edges_in(nodes: list[dict]) -> None:
    node_map = {n["local_id"]: n for n in nodes}
    for node in nodes:
        node["edges_in"] = []
    seen: set[tuple[str, str, str]] = set()
    for node in nodes:
        for edge in node.get("edges_out", []):
            target = node_map.get(edge["target_local"])
            key = (node["local_id"], edge["target_local"], edge["type"])
            if target and key not in seen:
                seen.add(key)
                target["edges_in"].append({"source_local": node["local_id"], "type": edge["type"]})


def _add_edge(node: dict, target: str, edge_type: str, confidence: str) -> None:
    edge = {"target_local": target, "type": edge_type, "confidence": confidence}
    if edge not in node["edges_out"]:
        node["edges_out"].append(edge)


def _node(local_id: str, title: str, node_type: str, root: Path, *, decorated: bool = False) -> dict:
    return {
        "local_id": local_id,
        "title": title,
        "type": node_type,
        "domain": local_id.split("/", 1)[0] if "/" in local_id else "",
        "fqn": local_id,
        "edges_out": [],
        "edges_in": [],
        "decorated": decorated,
    }


def _circular_findings(nodes: list[dict]) -> list[dict]:
    module_ids = {n["local_id"] for n in nodes if n.get("type") == "module"}
    graph = {
        n["local_id"]: sorted(
            e["target_local"]
            for e in n.get("edges_out", [])
            if e.get("type") == "import" and e["target_local"] in module_ids
        )
        for n in nodes
        if n.get("type") == "module"
    }
    findings = []
    for component in _tarjan(graph):
        if len(component) >= 2 and not all("__init__.py" in item for item in component):
            evidence = " -> ".join(component)
            findings.append(_finding("high", "순환 의존 후보", evidence, "circular_dependency", "high"))
    return findings


def _tarjan(graph: dict[str, list[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indexes[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph.get(node, []):
            if target not in indexes:
                strongconnect(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[target])
        if lowlinks[node] == indexes[node]:
            component = []
            while True:
                item = stack.pop()
                on_stack.remove(item)
                component.append(item)
                if item == node:
                    break
            components.append(sorted(component))

    for node in sorted(graph):
        if node not in indexes:
            strongconnect(node)
    return sorted(components, key=lambda c: c[0])


def _dead_code_findings(nodes: list[dict]) -> list[dict]:
    findings = []
    for node in sorted(nodes, key=lambda n: n.get("local_id", "")):
        if node.get("type") not in {"function", "class"}:
            continue
        if _suppressed_dead_candidate(node):
            continue
        incoming_calls = [e for e in node.get("edges_in", []) if e.get("type") == "call"]
        if not incoming_calls:
            findings.append(_finding("low", "미참조 코드 후보", node["local_id"], "dead_code_candidate", "low"))
    return findings


def _suppressed_dead_candidate(node: dict) -> bool:
    name = str(node.get("title", ""))
    lid = str(node.get("local_id", ""))
    return (
        bool(node.get("decorated"))
        or bool(node.get("in_all"))
        or bool(node.get("is_test"))
        or name.startswith("__")
        or "__init__.py" in lid
    )


def _excluded_node(node: dict) -> bool:
    lid = str(node.get("local_id", ""))
    return "__init__.py" in lid or "/test" in lid or Path(lid).name.startswith("test") or "/vendor/" in lid


def _finding(severity: str, title: str, evidence_ref: str, rule_id: str, confidence: str) -> dict:
    return {
        "category": "code_structure",
        "severity": severity,
        "title": title,
        "detail": f"{evidence_ref} 에서 {title} 신호를 발견했습니다.",
        "evidence_ref": evidence_ref,
        "suggestion": "정적 AST 기반 후보입니다. 변경 전 수동 확인 후 분해 또는 정리를 검토하세요.",
        "rule_id": rule_id,
        "confidence": confidence,
    }


def _persist_graph(root: Path, graph: dict) -> None:
    out = root / ".claude" / "memory" / "graph" / "views" / "code_graph_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def _project_name(project_root: str | Path) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(project_root).resolve().name)
