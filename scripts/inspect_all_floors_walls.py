import pypdf
import json

files = [
    ('Floor 00', '00-Ground_Floor-Clean.pdf'),
    ('Floor 01', '01-First_Floor-Clean.pdf'),
    ('Floor 02', '02-Second_Floor-Clean.pdf'),
    ('Floor 03', '03-Roof_Floor-Clean.pdf'),
]

for flabel, fname in files:
    try:
        reader = pypdf.PdfReader(fname)
        att = reader.attachments
        has_vc = 'vectorcraft-editing.vectorcraft' in att if att else False
        print(f"\n=== {flabel}: {fname} (VectorCraft: {has_vc}) ===")
        if has_vc:
            data = att['vectorcraft-editing.vectorcraft'][0]
            doc = json.loads(data.decode('utf-8'))['document']
            layers = doc.get('layers', [])
            print(f"Total layers: {len(layers)}")
            wall_layers = [l for l in layers if any(w in l.get('name', '').lower() for w in ['wall', 'ผนัง', 'muro', 'перегородк'])]
            for wl in wall_layers:
                n_children = len(wl.get('kind', {}).get('children', []))
                print(f"  Wall Layer: '{wl.get('name')}' -> {n_children} children")
            # Also list other layers with > 50 children to see where walls might hide
            other_big = [l for l in layers if l not in wall_layers and len(l.get('kind', {}).get('children', [])) > 200]
            print("  Other major layers:", [f"{l.get('name')} ({len(l.get('kind', {}).get('children', []))})" for l in other_big[:8]])
    except Exception as e:
        print(f"Error reading {fname}: {e}")

