"""Render the licensed teardown phone as transparent scene-4 PNG frames.

blender -b -t 4 -P film/scene4/blender_scene.py -- still
blender -b -t 4 -P film/scene4/blender_scene.py -- sequence
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MACHINE = json.loads((ROOT / "machine.local.json").read_text())
RENDERS = Path(MACHINE["renders_dir"]) / "scene4" / "blender"
TIMELINE = json.loads((HERE / "timeline.json").read_text())
BEATS = TIMELINE["beats"]
FPS = 30
SHOTS = {
    "lift": (.7, 1.4),
    "spin": (1.4, BEATS["open"][0]),
    "processor": (BEATS["open"][0], BEATS["close"][0]),
    "close": (BEATS["close"][0], BEATS["pair"][0]),
    "pair": (BEATS["pair"][0], TIMELINE["duration"]),
}
STILLS = {"lift": 1.1, "spin": 2.7, "processor": 7.1, "close": 13.4, "pair": 16.1}


def smooth(v):
    v = max(0.0, min(1.0, v))
    return v * v * (3 - 2 * v)


def material(name, color, metallic=0, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    if emission:
        shader = nodes.new("ShaderNodeEmission")
        shader.inputs["Strength"].default_value = 1.1
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(ROOT / "local/private-in/F0046/home.png"))
        m.node_tree.links.new(tex.outputs["Color"], shader.inputs["Color"])
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = (*color, 1)
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = .32 if metallic else .57
    m.node_tree.links.new(shader.outputs[0], out.inputs["Surface"])
    return m


def setup_model():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / "local/models3d/iphone_12_teardown/scene.gltf"))
    body = bpy.data.objects.get("body")
    if body is None:
        raise RuntimeError("teardown model has no body hierarchy")
    source_meshes = list({o.as_pointer(): o for root_name in ("body", "front_panel", "back_cover")
                          for o in bpy.data.objects[root_name].children_recursive if o.type == "MESH"}.values())
    if not source_meshes:
        raise RuntimeError("teardown body has no meshes")
    # Remove every source texture, including any baked logo or wordmark. The
    # front display gets only the private iTantra screenshot.
    graphite = material("graphite", (.055, .078, .105), .63)
    metal = material("graphite metal", (.16, .22, .27), .8)
    board = material("board", (.085, .15, .17), .2)
    battery = material("battery", (.24, .28, .32), .13)
    screen = material("iTantra display", (1, 1, 1), emission=True)
    palette = {"mat_metal": metal, "mat_parts": board, "mat_plastic_parts": graphite,
               "mat_color_body": graphite, "mat_color_housing": metal,
               "mat_color_plastic": graphite, "mat_glass": graphite,
               "mat_screen": screen, "mat_screen_plastic": graphite}
    # Native axes: X depth/front, Y width, Z height. Rotate into film axes.
    axes = Matrix(((0, 1, 0, 0), (0, 0, 1, -.073), (1, 0, 0, 0), (0, 0, 0, 1)))
    axes = Matrix.Diagonal((40, 40, 40, 1)) @ axes
    groups = {}
    for side in ("A", "B"):
        root = bpy.data.objects.new(f"phone_{side}", None)
        bpy.context.collection.objects.link(root)
        groups[side] = {"root": root}
        for layer in ("screen", "board", "battery", "back", "frame"):
            group = bpy.data.objects.new(f"{side}_{layer}", None)
            bpy.context.collection.objects.link(group)
            group.parent = root
            groups[side][layer] = group
    for original in source_meshes:
        name = original.name.lower()
        if name.startswith("back_cover") or "back_cam" in name or "apple" in name or "logo" in name or "wordmark" in name:
            continue
        if name == "front_panel_mat_glass_0":
            continue
        if name.startswith("front_panel") or name.startswith("earspeaker"):
            layer = "screen"
        elif name.startswith("motherboard") or name.startswith("cover_"):
            layer = "board"
        elif name.startswith("battery"):
            layer = "battery"
        elif name.startswith("back_cover") or name.startswith("backplate") or name.startswith("wireless_charge"):
            layer = "back"
        else:
            layer = "frame"
        for side in ("A", "B"):
            obj = original.copy()
            obj.data = original.data
            bpy.context.collection.objects.link(obj)
            obj.parent = groups[side][layer]
            obj.matrix_world = axes @ original.matrix_world
            for slot in obj.material_slots:
                old = slot.material.name if slot.material else ""
                slot.material = palette.get(old, graphite)
            obj.name = f"{side}_{original.name}"
    for original in list(bpy.data.objects):
        if original.type == "MESH" and not original.name.startswith(("A_", "B_")):
            bpy.data.objects.remove(original, do_unlink=True)
    # The imported display sits below an opaque front panel. A thin local
    # screenshot surface keeps the genuine housing and a readable app screen.
    mesh = bpy.data.meshes.new("display surface")
    mesh.from_pydata([(-1.26, -2.73, .19), (1.26, -2.73, .19),
                      (1.26, 2.73, .19), (-1.26, 2.73, .19)], [], [(0, 1, 2, 3)])
    mesh.update()
    uv = mesh.uv_layers.new()
    for loop, xy in zip(mesh.polygons[0].loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[loop].uv = xy
    mesh.materials.append(screen)
    for side in ("A", "B"):
        obj = bpy.data.objects.new(f"{side}_iTantra_screen", mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = groups[side]["screen"]
    # The backplate has camera cutouts even after its camera meshes are gone.
    # Cover them on its inner side so no shot reveals their silhouette.
    back_mesh = bpy.data.meshes.new("clean graphite back")
    corners = ((1.13, 2.64, 0), (-1.13, 2.64, 90),
               (-1.13, -2.64, 180), (1.13, -2.64, 270))
    outline = [(cx + .22 * math.cos(math.radians(angle + step * 15)),
                cy + .22 * math.sin(math.radians(angle + step * 15)), -.06)
               for cx, cy, angle in corners for step in range(7)]
    back_mesh.from_pydata(outline, [], [tuple(range(len(outline)))])
    back_mesh.update()
    back_mesh.materials.append(graphite)
    for side in ("A", "B"):
        obj = bpy.data.objects.new(f"{side}_clean_back", back_mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = groups[side]["back"]
    return groups


def setup_stage():
    camera_data = bpy.data.cameras.new("front camera")
    camera = bpy.data.objects.new("front camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0, 0, 20)
    camera.rotation_euler = (0, 0, 0)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 17.777778
    bpy.context.scene.camera = camera
    for name, color, energy, location, size in (
        ("key", (0.64, .83, 1), 2200, (-6, 7, 8), 6),
        ("rim", (.27, .59, 1), 2400, (6, 4, -2), 4),
        ("fill", (1, 1, 1), 1400, (2, -5, 9), 5),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0, 0, 0)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.world.color = (.015, .025, .04)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"


def pose(groups, t):
    lift = smooth((t - .72) / .65)
    opening = smooth((t - BEATS["open"][0]) / (BEATS["open"][1] - BEATS["open"][0]))
    closing = smooth((t - BEATS["close"][0]) / max(.001, BEATS["close"][1] - BEATS["close"][0]))
    spread = opening * (1 - closing)
    pair = smooth((t - BEATS["pair"][0]) / .75)
    a = groups["A"]
    a["root"].location = (-2.7 + .5 * lift - 1.25 * pair, -.2 + .75 * (1 - lift), 0)
    a["root"].rotation_euler = (math.radians(-5), .18 + .18 * math.sin(max(0, t - 1.4) * .38), -1.13 * (1 - lift) - .12 * lift)
    a["root"].scale = (.25 + .75 * lift,) * 3
    for layer, offset in {"screen": -2.15, "board": -.18, "battery": .9, "back": 1.75, "frame": 0}.items():
        a[layer].location = (offset * spread, 0, (.23 if layer == "screen" else 0) * spread)
    for obj in a["back"].children:
        obj.hide_render = spread < .6
    b = groups["B"]
    b["root"].hide_render = pair < .01
    b["root"].location = (8.5 - 4.4 * pair, -.28, 0)
    b["root"].rotation_euler = (-.06, -.22 + .06 * math.sin(t * .45), .08)
    b["root"].scale = (.84 * pair,) * 3
    for obj in b["back"].children:
        obj.hide_render = True


def render_at(groups, t, path):
    pose(groups, t)
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print("SCENE4_RENDER", path.name, round(t, 3), flush=True)


def main():
    mode = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "still"
    if mode not in ("still", "sequence"):
        raise ValueError("mode must be still or sequence")
    groups = setup_model()
    setup_stage()
    if mode == "still":
        out = ROOT / "results/F0052/preview"
        selected = sys.argv[sys.argv.index("--") + 2] if len(sys.argv) > sys.argv.index("--") + 2 else None
        for shot, t in STILLS.items():
            if selected and shot != selected:
                continue
            render_at(groups, t, out / f"{shot}.png")
    else:
        selected = sys.argv[sys.argv.index("--") + 2] if len(sys.argv) > sys.argv.index("--") + 2 else None
        for shot, (start, end) in SHOTS.items():
            if selected and shot != selected:
                continue
            for frame in range(math.ceil(start * FPS), math.ceil(end * FPS)):
                render_at(groups, frame / FPS, RENDERS / shot / f"{frame:06d}.png")


if __name__ == "__main__":
    main()
