#!/usr/bin/env python3
"""
Python-Live: Simple Python Dependency Visualizer
Usage: python tools/dependency_viewer.py [path/to/file.py]
Opens interactive HTML graph in browser showing file connections.
"""
import re
import os
import sys
import json
import webbrowser
from pathlib import Path
from dataclasses import dataclass
from typing import Set, Dict, List


@dataclass
class FileNode:
    path: str
    name: str
    imports: List[str]


def parse_imports(file_path: Path) -> List[str]:
    """Extract import statements from a Python file."""
    imports = []
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return imports
    
    # Pattern: from x.y.z import ...
    from_pattern = r'^from\s+([\w.]+)\s+import'
    # Pattern: import x.y.z
    import_pattern = r'^import\s+([\w.]+)'
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue
            
        match = re.match(from_pattern, line)
        if match:
            imports.append(match.group(1))
            continue
            
        match = re.match(import_pattern, line)
        if match:
            imports.append(match.group(1))
    
    return imports


def resolve_module_to_file(module: str, project_root: Path) -> Path | None:
    """Convert module path (Domain.modules.X) to file path."""
    # Try src/ prefix first
    rel_path = module.replace('.', '/')
    
    candidates = [
        project_root / 'src' / f'{rel_path}.py',
        project_root / 'src' / rel_path / '__init__.py',
        project_root / f'{rel_path}.py',
        project_root / rel_path / '__init__.py',
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_project_root(start_path: Path) -> Path:
    """Find project root by looking for markers."""
    current = start_path if start_path.is_dir() else start_path.parent
    
    while current != current.parent:
        markers = ['pyproject.toml', 'setup.py', 'requirements.txt', '.git']
        if any((current / m).exists() for m in markers):
            return current
        current = current.parent
    
    return start_path.parent


def build_dependency_graph(start_file: Path, max_depth: int = 3) -> Dict:
    """Build dependency graph starting from a file."""
    project_root = find_project_root(start_file)
    
    nodes: Dict[str, FileNode] = {}
    edges: List[Dict] = []
    visited: Set[str] = set()
    
    def process_file(file_path: Path, depth: int):
        if depth > max_depth:
            return
        
        rel_path = str(file_path.relative_to(project_root))
        if rel_path in visited:
            return
        visited.add(rel_path)
        
        imports = parse_imports(file_path)
        node = FileNode(
            path=rel_path,
            name=file_path.stem,
            imports=imports
        )
        nodes[rel_path] = node
        
        for imp in imports:
            target = resolve_module_to_file(imp, project_root)
            if target and target.exists():
                target_rel = str(target.relative_to(project_root))
                edges.append({
                    'source': rel_path,
                    'target': target_rel,
                    'module': imp
                })
                process_file(target, depth + 1)
    
    process_file(start_file, 0)
    
    return {
        'nodes': [{'id': k, 'name': v.name, 'imports': len(v.imports)} 
                  for k, v in nodes.items()],
        'edges': edges,
        'root': str(start_file.relative_to(project_root))
    }


HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>Python-Live: {filename}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ margin: 0; background: #1a1a2e; font-family: system-ui; }}
        svg {{ width: 100vw; height: 100vh; }}
        .node {{ cursor: pointer; }}
        .node circle {{ fill: #4a90d9; stroke: #16213e; stroke-width: 2; }}
        .node.root circle {{ fill: #e94560; }}
        .node text {{ fill: #eee; font-size: 12px; }}
        .link {{ stroke: #4a90d9; stroke-opacity: 0.6; stroke-width: 1.5; }}
        .link:hover {{ stroke: #e94560; stroke-width: 3; }}
        #info {{ position: fixed; top: 10px; left: 10px; background: #16213e; 
                 color: #eee; padding: 15px; border-radius: 8px; max-width: 300px; }}
        h3 {{ margin: 0 0 10px 0; color: #e94560; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>🐍 Python-Live</h3>
        <p><strong>File:</strong> {filename}</p>
        <p><strong>Connections:</strong> {edge_count}</p>
        <p><em>Drag nodes to rearrange</em></p>
    </div>
    <svg></svg>
    <script>
        const data = {graph_data};
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("svg");
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.edges)
            .join("line")
            .attr("class", "link");
        
        const node = svg.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", d => d.id === data.root ? "node root" : "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", d => 10 + d.imports * 2);
        
        node.append("text")
            .attr("dx", 15)
            .attr("dy", 4)
            .text(d => d.name);
        
        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
    </script>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python dependency_viewer.py <path/to/file.py>")
        print("Example: python tools/dependency_viewer.py src/Domain/core/engine.py")
        sys.exit(1)
    
    file_path = Path(sys.argv[1]).resolve()
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"🔍 Analyzing: {file_path.name}")
    graph = build_dependency_graph(file_path)
    
    print(f"📊 Found {len(graph['nodes'])} files, {len(graph['edges'])} connections")
    
    # Generate HTML
    html = HTML_TEMPLATE.format(
        filename=file_path.name,
        edge_count=len(graph['edges']),
        graph_data=json.dumps(graph)
    )
    
    output_path = Path('dependency_graph.html')
    output_path.write_text(html)
    
    print(f"✅ Generated: {output_path.absolute()}")
    webbrowser.open(f'file://{output_path.absolute()}')


if __name__ == '__main__':
    main()
