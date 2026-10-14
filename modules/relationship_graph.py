import json

def generate_cytoscape_graph(case_id, db):
    """
    Generates Cytoscape.js compatible graph data (nodes & edges)
    representing the structured relationship network of the case.
    """
    case = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not case:
        return {'elements': {'nodes': [], 'edges': []}}

    evidence_files = db.execute(
        "SELECT * FROM evidence_files WHERE case_id = ?", (case_id,)
    ).fetchall()

    entities = db.execute("""
        SELECT e.*, ef.original_filename
        FROM entities e
        JOIN evidence_files ef ON e.evidence_id = ef.id
        WHERE e.case_id = ?
    """, (case_id,)).fetchall()

    events = db.execute(
        "SELECT * FROM events WHERE case_id = ?", (case_id,)
    ).fetchall()

    nodes = []
    edges = []
    node_ids = set()

    # 1. Central Case Node
    case_node_id = f"case_{case['id']}"
    nodes.append({
        'data': {
            'id': case_node_id,
            'label': f"Case {case['case_id']}",
            'type': 'case',
            'sub_type': case['category'],
            'color': '#2563eb', # Blue
            'size': 65,
            'category': 'Case Root',
            'details': {
                'title': case['title'],
                'category': case['category'],
                'loss_amount': f"₹{case['loss_amount']:,.2f}",
                'incident_date': case['incident_date'],
                'status': case['status']
            }
        }
    })
    node_ids.add(case_node_id)

    # 2. Evidence File Nodes
    for ef in evidence_files:
        f_node_id = f"file_{ef['id']}"
        nodes.append({
            'data': {
                'id': f_node_id,
                'label': ef['original_filename'][:20] + ('...' if len(ef['original_filename']) > 20 else ''),
                'full_name': ef['original_filename'],
                'type': 'file',
                'sub_type': ef['file_type'].upper(),
                'color': '#0284c7', # Sky Blue
                'size': 50,
                'category': 'Evidence File',
                'details': {
                    'original_filename': ef['original_filename'],
                    'size_bytes': f"{ef['file_size']:,} bytes",
                    'sha256': ef['sha256_hash'],
                    'mime_type': ef['mime_type'],
                    'upload_time': str(ef['upload_time'])
                }
            }
        })
        node_ids.add(f_node_id)

        # Edge from Case to Evidence File
        edges.append({
            'data': {
                'id': f"edge_case_file_{ef['id']}",
                'source': case_node_id,
                'target': f_node_id,
                'label': 'INCLUDES',
                'line_color': '#94a3b8'
            }
        })

    # 3. Entity Nodes & File->Entity Edges
    # Color mapping for entity types
    color_map = {
        'UPI_ID': '#10b981',      # Emerald Green
        'PHONE': '#06b6d4',       # Cyan
        'TXN_REF': '#8b5cf6',     # Purple
        'AMOUNT': '#f59e0b',      # Amber
        'EMAIL': '#14b8a6',       # Teal
        'URL_DOMAIN': '#ef4444',  # Red / Warning
        'SUSPECT_PERSON': '#ec4899', # Pink
        'SUSPECT_ORG': '#6366f1',
    }

    # Deduplicate entities across files by (type, normalized_value)
    unique_entities = {}
    for ent in entities:
        key = (ent['entity_type'], ent['normalized_value'])
        if key not in unique_entities:
            unique_entities[key] = {
                'entity_id': ent['id'],
                'type': ent['entity_type'],
                'display_val': ent['entity_value'],
                'normalized': ent['normalized_value'],
                'files': [],
                'context': ent['context']
            }
        unique_entities[key]['files'].append({
            'evidence_id': ent['evidence_id'],
            'filename': ent['original_filename']
        })

    for key, ent_data in unique_entities.items():
        etype, norm_val = key
        ent_node_id = f"ent_{etype}_{abs(hash(norm_val))}"
        
        node_color = color_map.get(etype, '#64748b')
        is_shared = len(ent_data['files']) > 1

        nodes.append({
            'data': {
                'id': ent_node_id,
                'label': ent_data['display_val'][:22] + ('...' if len(ent_data['display_val']) > 22 else ''),
                'full_value': ent_data['display_val'],
                'type': 'entity',
                'sub_type': etype,
                'color': node_color,
                'size': 44 if is_shared else 36,
                'category': f"Entity: {etype.replace('_', ' ')}",
                'is_shared': is_shared,
                'shared_count': len(ent_data['files']),
                'details': {
                    'entity_type': etype,
                    'extracted_value': ent_data['display_val'],
                    'normalized': ent_data['normalized'],
                    'source_files': [f['filename'] for f in ent_data['files']],
                    'context': ent_data['context']
                }
            }
        })
        node_ids.add(ent_node_id)

        # Edges from Evidence Files to this Entity
        for file_ref in ent_data['files']:
            f_node_id = f"file_{file_ref['evidence_id']}"
            if f_node_id in node_ids:
                edges.append({
                    'data': {
                        'id': f"edge_{f_node_id}_{ent_node_id}",
                        'source': f_node_id,
                        'target': ent_node_id,
                        'label': 'CONTAINS',
                        'line_color': node_color
                    }
                })

    # 4. Incident Event Nodes
    for ev in events:
        if ev['is_uncertain'] and ev['confidence'] < 0.6:
            continue
        ev_node_id = f"event_{ev['id']}"
        nodes.append({
            'data': {
                'id': ev_node_id,
                'label': ev['title'][:20],
                'full_title': ev['title'],
                'type': 'event',
                'sub_type': ev['event_type'],
                'color': '#ea580c', # Dark Orange
                'size': 38,
                'category': 'Timeline Event',
                'details': {
                    'date': ev['event_date'],
                    'time': ev['event_time'],
                    'type': ev['event_type'],
                    'description': ev['description'],
                    'verification': ev['verification_status']
                }
            }
        })
        node_ids.add(ev_node_id)

        if ev['evidence_id']:
            f_node_id = f"file_{ev['evidence_id']}"
            if f_node_id in node_ids:
                edges.append({
                    'data': {
                        'id': f"edge_ev_{ev_node_id}_{f_node_id}",
                        'source': f_node_id,
                        'target': ev_node_id,
                        'label': 'EVIDENCE_OF',
                        'line_color': '#ea580c'
                    }
                })

    return {
        'elements': {
            'nodes': nodes,
            'edges': edges
        },
        'stats': {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'unique_entities': len(unique_entities),
            'evidence_count': len(evidence_files)
        }
    }
