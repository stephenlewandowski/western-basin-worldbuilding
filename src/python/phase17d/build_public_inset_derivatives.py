"""Make reader annotations from retained insets without changing their geometry.

Run from anywhere. Originals and their original builders remain untouched.
Only text, accessibility metadata and the viewing frame change; six markers
refer to responsive descriptions in the Atlas. Coordinates are display units.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

CASES = [
    ('hf01', 'hf01_canopy_old_wall_section', 'Canopy and retained wall',
     '40 180 1350 565', [(150, 360), (625, 225), (880, 350),
                           (950, 495), (830, 610), (1135, 610)],
     ['Retained wall', 'Replaceable glass', 'Attachment and service rib',
      'Data and electrical services', 'Passage and maintenance', 'Property break']),
    ('hf03', 'hf03_field_seam_drainage_section', 'Field, working seam and drainage',
     '40 180 1350 550', [(155, 305), (377, 220), (575, 260),
                           (800, 220), (1235, 590), (820, 670)],
     ['Open field', 'Selective propagation', 'Machine repair and interruption',
      'Contained work and hold', 'Drainage and distinct wetland', 'Outside supply']),
    ('hf04', 'hf04_qualification_cell_section', 'Qualification cell and retained hall',
     '40 190 1350 635', [(80, 310), (590, 445), (885, 225),
                           (1270, 560), (685, 707), (1280, 690)],
     ['Retained hall', 'Cell and empty berth', 'Staffed qualification',
      'Accessible services', 'Separate material bays', 'Outside freight']),
]


def geometry(root):
    """Ordered shape attributes before the added annotation group."""
    shape_tags = {'rect', 'path', 'circle', 'ellipse', 'line', 'polygon', 'polyline'}
    return [(e.tag, dict(e.attrib)) for e in root.iter()
            if e.tag.rsplit('}', 1)[-1] in shape_tags]


def main():
    lineage = []
    for folder, stem, title, frame, positions, names in CASES:
        original = ROOT / 'assets/phase17d' / folder / f'{stem}.svg'
        raw = original.read_bytes()
        root = ET.fromstring(raw)
        before = geometry(root)
        for parent in root.iter():
            for child in list(parent):
                if child.tag == f'{{{NS}}}text':
                    parent.remove(child)
        assert geometry(root) == before, 'Retained geometry changed'
        root.set('viewBox', frame)
        root.set('height', str(round(1440 * float(frame.split()[3]) / 1350)))
        root.find(f'{{{NS}}}title').text = title + ' — six reading groups'
        root.find(f'{{{NS}}}desc').text = (
            'Qualitative composite 2075 design concept. The original geometry is retained. '
            + '; '.join(f'{i:02d}: {name}' for i, name in enumerate(names, 1))
            + '. Full descriptions follow this image. No measured geometry or performance.')
        original_lf_hash = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()
        metadata = ET.SubElement(root, f'{{{NS}}}metadata')
        metadata.text = json.dumps({'derived_from': str(original.relative_to(ROOT)).replace('\\', '/'),
                                    'original_sha256_lf': original_lf_hash,
                                    'change': 'annotation and viewing frame only'})
        markers = ET.SubElement(root, f'{{{NS}}}g', {'id': 'reader-markers'})
        for i, (x, y) in enumerate(positions, 1):
            ET.SubElement(markers, f'{{{NS}}}circle', {'cx': str(x), 'cy': str(y), 'r': '30',
                'fill': '#254b53', 'stroke': '#f4f1e9', 'stroke-width': '4'})
            label = ET.SubElement(markers, f'{{{NS}}}text', {'x': str(x), 'y': str(y + 12),
                'text-anchor': 'middle', 'style': 'font:700 35px Arial, sans-serif;fill:#fff'})
            label.text = f'{i:02d}'
        output = original.with_name(stem + '_public.svg')
        output.write_bytes(ET.tostring(root, encoding='utf-8') + b'\n')
        lineage.append({'original': str(original.relative_to(ROOT)).replace('\\', '/'),
                        'original_sha256': hashlib.sha256(raw).hexdigest(),
                        'original_sha256_lf': original_lf_hash,
                        'derivative': str(output.relative_to(ROOT)).replace('\\', '/'),
                        'derivative_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                        'retained_shapes': len(before), 'marker_count': 6})
    destination = ROOT / 'assets/phase17d/public_inset_derivatives.json'
    destination.write_text(json.dumps(lineage, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(lineage)} derivatives; all original shape attributes retained.')


if __name__ == '__main__':
    main()
