"""Inspect the licensed teardown glTF before composing camera views."""
import bpy
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
source = root / 'local/models3d/iphone_12_teardown/scene.gltf'
bpy.ops.import_scene.gltf(filepath=str(source))

for name in ('front_panel', 'battery', 'motherboard', 'back_cover', 'backplate', 'body'):
    matches = [o for o in bpy.data.objects if o.name == name]
    print('GROUP', name, len(matches))
    if not matches:
        continue
    root_obj = matches[0]
    children = [o for o in root_obj.children_recursive if o.type == 'MESH']
    coords = [o.matrix_world @ Vector(v) for o in children for v in o.bound_box]
    if coords:
        print('BOUNDS', [round(min(c[i] for c in coords), 4) for i in range(3)],
              [round(max(c[i] for c in coords), 4) for i in range(3)])
    for o in children:
        print('  MESH', o.name, 'verts', len(o.data.vertices),
              'mats', [m.name for m in o.data.materials])
for m in bpy.data.materials:
    print('MATERIAL', m.name, [(n.name, n.image.filepath if n.image else '') for n in m.node_tree.nodes if n.type == 'TEX_IMAGE'] if m.use_nodes else [])
