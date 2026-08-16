"""Build the Window Notes macaron as a web-ready Blender asset.

Run with:
  blender --background --python scripts/blender/create_window_notes_macaron.py

This script creates the procedural baseline under the ignored .tmp directory
and writes a GLB delivery asset. The reviewed, manually refined checkpoint is
assets/models/window-notes-macaron.blend; export from that file to preserve its
artist-authored transforms. Running this script again replaces the GLB with the
procedural baseline.
"""

from __future__ import annotations

import math
import random
import struct
import zlib
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = ROOT / ".tmp" / "blender" / "window-notes"
TEXTURE_DIR = WORK_DIR / "textures"
OUTPUT_DIR = ROOT / "assets" / "models"
BLEND_PATH = WORK_DIR / "window-notes-macaron.blend"
GLB_PATH = OUTPUT_DIR / "window-notes-macaron.glb"
WINDOW_TEXTURE_DIR = ROOT / "assets" / "textures" / "window-notes"
WINDOW_INTERIOR_TEXTURE = WINDOW_TEXTURE_DIR / "window-interior.png"

RNG = random.Random(20260815)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def write_food_albedo_png(
    path: Path,
    color: str,
    seed: int,
    *,
    profile: str,
    size: int = 512,
) -> None:
    """Write a seamless, restrained food albedo map without external dependencies."""
    base = hex_rgb(color)
    rows = bytearray()

    def value_noise(x: int, y: int, cells: int, octave_seed: int) -> float:
        grid_x = x / size * cells
        grid_y = y / size * cells
        x0 = math.floor(grid_x)
        y0 = math.floor(grid_y)
        tx = grid_x - x0
        ty = grid_y - y0
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)

        def grid_value(gx: int, gy: int) -> float:
            value = ((gx % cells) * 73856093) ^ ((gy % cells) * 19349663) ^ octave_seed
            value = (value ^ (value >> 13)) * 1274126177
            return ((value ^ (value >> 16)) & 0xFFFF) / 65535

        top = grid_value(x0, y0) * (1 - tx) + grid_value(x0 + 1, y0) * tx
        bottom = grid_value(x0, y0 + 1) * (1 - tx) + grid_value(x0 + 1, y0 + 1) * tx
        return top * (1 - ty) + bottom * ty

    for y in range(size):
        rows.append(0)
        for x in range(size):
            hashed = ((x * 73856093) ^ (y * 19349663) ^ seed) & 1023
            grain = (hashed / 1023 - 0.5)
            broad = value_noise(x, y, 7, seed * 17) - 0.5
            almond = value_noise(x, y, 47, seed * 31) - 0.5
            fine = value_noise(x, y, 181, seed * 43) - 0.5

            if profile == "shell":
                variation = broad * 12 + almond * 5 + fine * 2.2 + grain * 1.4
                # Sparse toasted almond flecks, kept subtle enough to read as food rather than stone.
                fleck = ((x * 92837111) ^ (y * 689287499) ^ (seed * 97)) & 4095
                if fleck < 9:
                    variation -= 9 * (1 - fleck / 9)
                warm_shift = broad * 1.4
            elif profile == "foot":
                variation = broad * 15 + almond * 8 + fine * 4 + grain * 2.4
                pore = ((x * 19349663) ^ (y * 83492791) ^ (seed * 131)) & 2047
                if pore < 16:
                    variation -= 15 * (1 - pore / 16)
                warm_shift = broad * 1.8
            elif profile == "window_glow":
                u = x / max(1, size - 1)
                v = y / max(1, size - 1)
                distance = math.sqrt(((u - 0.5) / 0.7) ** 2 + ((v - 0.46) / 0.82) ** 2)
                center_glow = max(0.0, 1 - distance) ** 1.45
                rabbit_halo = math.exp(-(((u - 0.5) / 0.25) ** 2 + ((v - 0.3) / 0.32) ** 2) * 1.7)
                brush_ring = math.sin(distance * 34 + broad * 5.5) * 2.2
                variation = broad * 12 + almond * 5 + fine * 1.5 + brush_ring
                variation += center_glow * 34 + rabbit_halo * 13
                warm_shift = broad * 3 + center_glow * 9 + rabbit_halo * 4
            elif profile == "cream":
                variation = broad * 5 + almond * 2.2 + fine * 0.8 + grain * 0.5
                warm_shift = broad * 1.2
            elif profile == "cream_filling":
                pressed_ripple = math.sin((y / size * 5.5 + broad * 0.22) * math.tau)
                soft_fold = math.sin((y / size * 2.4 + broad * 0.16) * math.tau)
                variation = broad * 18 + almond * 6 + fine * 1.8 + pressed_ripple * 3.6 + soft_fold * 2.2 + grain
                warm_shift = broad * 4 + pressed_ripple * 0.9 + soft_fold * 0.7
            elif profile == "painted_sugar":
                variation = broad * 9 + almond * 4 + fine * 1.5 + grain * 0.7
                warm_shift = broad * 2
            else:  # glossy fruit, honey filling, or illuminated sugar glass
                variation = broad * 18 + almond * 7 + fine * 2 + grain
                warm_shift = broad * 4.5

            # A tiny channel separation avoids a digitally grey brightness modulation.
            offsets = (variation + warm_shift, variation, variation - warm_shift * 0.45)
            rows.extend(max(0, min(255, round(channel + offset))) for channel, offset in zip(base, offsets))

    raw = bytes(rows)
    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    png = signature
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def write_roughness_png(
    path: Path,
    seed: int,
    *,
    base_roughness: float,
    variation: float,
    size: int = 512,
) -> None:
    """Write a seamless scalar roughness map as RGB for reliable glTF export."""
    rows = bytearray()

    def value_noise(x: int, y: int, cells: int, octave_seed: int) -> float:
        grid_x = x / size * cells
        grid_y = y / size * cells
        x0 = math.floor(grid_x)
        y0 = math.floor(grid_y)
        tx = grid_x - x0
        ty = grid_y - y0
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)

        def grid_value(gx: int, gy: int) -> float:
            value = ((gx % cells) * 73856093) ^ ((gy % cells) * 19349663) ^ octave_seed
            value = (value ^ (value >> 13)) * 1274126177
            return ((value ^ (value >> 16)) & 0xFFFF) / 65535

        top = grid_value(x0, y0) * (1 - tx) + grid_value(x0 + 1, y0) * tx
        bottom = grid_value(x0, y0 + 1) * (1 - tx) + grid_value(x0 + 1, y0 + 1) * tx
        return top * (1 - ty) + bottom * ty

    for y in range(size):
        rows.append(0)
        for x in range(size):
            broad = value_noise(x, y, 11, seed * 23) - 0.5
            detail = value_noise(x, y, 89, seed * 41) - 0.5
            value = base_roughness + variation * (broad * 1.35 + detail * 0.65)
            channel = max(0, min(255, round(value * 255)))
            rows.extend((channel, channel, channel))

    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    png = signature
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def write_normal_png(path: Path, seed: int, size: int = 512) -> None:
    """Write a seamless almond-flour normal map with irregular multi-scale grain."""
    def value_noise(x: int, y: int, cells: int, octave_seed: int) -> float:
        grid_x = x / size * cells
        grid_y = y / size * cells
        x0 = math.floor(grid_x)
        y0 = math.floor(grid_y)
        tx = grid_x - x0
        ty = grid_y - y0
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)

        def grid_value(gx: int, gy: int) -> float:
            value = ((gx % cells) * 73856093) ^ ((gy % cells) * 19349663) ^ octave_seed
            value = (value ^ (value >> 13)) * 1274126177
            return ((value ^ (value >> 16)) & 0xFFFF) / 65535

        top = grid_value(x0, y0) * (1 - tx) + grid_value(x0 + 1, y0) * tx
        bottom = grid_value(x0, y0 + 1) * (1 - tx) + grid_value(x0 + 1, y0 + 1) * tx
        return top * (1 - ty) + bottom * ty

    heights: list[float] = []
    for y in range(size):
        for x in range(size):
            coarse = (value_noise(x, y, 41, seed * 17) - 0.5) * 0.24
            almond = (value_noise(x, y, 113, seed * 31) - 0.5) * 0.46
            pores = (value_noise(x, y, 241, seed * 47) - 0.5) * 0.3
            heights.append(coarse + almond + pores)

    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            left = heights[y * size + (x - 1) % size]
            right = heights[y * size + (x + 1) % size]
            down = heights[((y - 1) % size) * size + x]
            up = heights[((y + 1) % size) * size + x]
            nx = (left - right) * 4.6
            ny = (down - up) * 4.6
            nz = 1.0
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            rows.extend(
                (
                    round((nx / length * 0.5 + 0.5) * 255),
                    round((ny / length * 0.5 + 0.5) * 255),
                    round((nz / length * 0.5 + 0.5) * 255),
                )
            )

    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    png = signature
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def set_input(shader: bpy.types.Node, name: str, value) -> None:
    socket = shader.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def create_material(
    name: str,
    color: str,
    *,
    roughness: float = 0.88,
    texture_seed: int | None = None,
    texture_profile: str = "shell",
    texture_size: int = 512,
    roughness_variation: float = 0.0,
    normal_seed: int | None = None,
    normal_strength: float = 0.5,
    transmission: float = 0.0,
    coat_weight: float = 0.0,
    coat_roughness: float = 0.2,
    specular_level: float = 0.22,
    alpha: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    rgb = hex_rgb(color)
    rgba = tuple(channel / 255 for channel in rgb) + (alpha,)
    set_input(shader, "Base Color", rgba)
    set_input(shader, "Roughness", roughness)
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Specular IOR Level", specular_level)
    set_input(shader, "Transmission Weight", transmission)
    set_input(shader, "Coat Weight", coat_weight)
    set_input(shader, "Coat Roughness", coat_roughness)
    set_input(shader, "IOR", 1.45)
    set_input(shader, "Alpha", alpha)
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    if texture_seed is not None:
        texture_path = TEXTURE_DIR / f"{name.lower().replace(' ', '-')}-albedo.png"
        write_food_albedo_png(
            texture_path,
            color,
            texture_seed,
            profile=texture_profile,
            size=texture_size,
        )
        image = bpy.data.images.load(str(texture_path), check_existing=True)
        image.colorspace_settings.name = "sRGB"
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image
        texture.interpolation = "Linear"
        texture.extension = "REPEAT"
        links.new(texture.outputs["Color"], shader.inputs["Base Color"])

        if roughness_variation:
            roughness_path = TEXTURE_DIR / f"{name.lower().replace(' ', '-')}-roughness.png"
            write_roughness_png(
                roughness_path,
                texture_seed + 101,
                base_roughness=roughness,
                variation=roughness_variation,
                size=texture_size,
            )
            roughness_image = bpy.data.images.load(str(roughness_path), check_existing=True)
            roughness_image.colorspace_settings.name = "Non-Color"
            roughness_texture = nodes.new("ShaderNodeTexImage")
            roughness_texture.image = roughness_image
            roughness_texture.interpolation = "Linear"
            roughness_texture.extension = "REPEAT"
            links.new(roughness_texture.outputs["Color"], shader.inputs["Roughness"])

    if normal_seed is not None:
        normal_path = TEXTURE_DIR / f"{name.lower().replace(' ', '-')}-normal.png"
        write_normal_png(normal_path, normal_seed)
        normal_image = bpy.data.images.load(str(normal_path), check_existing=True)
        normal_image.colorspace_settings.name = "Non-Color"
        normal_texture = nodes.new("ShaderNodeTexImage")
        normal_texture.image = normal_image
        normal_texture.interpolation = "Linear"
        normal_texture.extension = "REPEAT"
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.inputs["Strength"].default_value = normal_strength
        links.new(normal_texture.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])

    return material


def create_reference_image_material(name: str, image_path: Path) -> bpy.types.Material:
    """Use the approved illustration as a matte, lightly grained sugar print."""
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    set_input(shader, "Base Color", (1.0, 1.0, 1.0, 1.0))
    set_input(shader, "Roughness", 0.68)
    set_input(shader, "Specular IOR Level", 0.2)
    set_input(shader, "Coat Weight", 0.075)
    set_input(shader, "Coat Roughness", 0.42)

    image = bpy.data.images.load(str(image_path), check_existing=True)
    image.colorspace_settings.name = "sRGB"
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Linear"
    texture.extension = "CLIP"
    links.new(texture.outputs["Color"], shader.inputs["Base Color"])
    links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])

    roughness_path = TEXTURE_DIR / "rabbit-window-sugar-print-roughness.png"
    write_roughness_png(
        roughness_path,
        1187,
        base_roughness=0.68,
        variation=0.055,
        size=256,
    )
    roughness_image = bpy.data.images.load(str(roughness_path), check_existing=True)
    roughness_image.colorspace_settings.name = "Non-Color"
    roughness_texture = nodes.new("ShaderNodeTexImage")
    roughness_texture.image = roughness_image
    roughness_texture.interpolation = "Linear"
    roughness_texture.extension = "REPEAT"
    links.new(roughness_texture.outputs["Color"], shader.inputs["Roughness"])

    normal_path = TEXTURE_DIR / "rabbit-window-sugar-print-normal.png"
    write_normal_png(normal_path, 1187, size=256)
    normal_image = bpy.data.images.load(str(normal_path), check_existing=True)
    normal_image.colorspace_settings.name = "Non-Color"
    normal_texture = nodes.new("ShaderNodeTexImage")
    normal_texture.image = normal_image
    normal_texture.interpolation = "Linear"
    normal_texture.extension = "REPEAT"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.13
    links.new(normal_texture.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    return material


def smooth(object_: bpy.types.Object) -> None:
    if object_.type == "MESH":
        for polygon in object_.data.polygons:
            polygon.use_smooth = True


def apply_modifier(object_: bpy.types.Object, name: str) -> None:
    bpy.context.view_layer.objects.active = object_
    object_.select_set(True)
    bpy.ops.object.modifier_apply(modifier=name)
    object_.select_set(False)


def add_bevel(object_: bpy.types.Object, width: float, segments: int = 3) -> None:
    modifier = object_.modifiers.new("Soft handmade edge", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    apply_modifier(object_, modifier.name)


def add_displacement(object_: bpy.types.Object, strength: float, scale: float, seed: int) -> None:
    texture = bpy.data.textures.new(f"{object_.name} surface", type="CLOUDS")
    texture.noise_scale = scale
    texture.noise_depth = 2
    texture.noise_type = "SOFT_NOISE"
    texture.noise_basis = "BLENDER_ORIGINAL"
    texture.nabla = 0.025 + (seed % 5) * 0.002
    modifier = object_.modifiers.new("Almond flour surface", "DISPLACE")
    modifier.texture = texture
    modifier.strength = strength
    modifier.mid_level = 0.5
    modifier.texture_coords = "GLOBAL"
    apply_modifier(object_, modifier.name)


def cube_project_uv(object_: bpy.types.Object, cube_size: float) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = object_
    object_.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=cube_size, correct_aspect=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    object_.select_set(False)


def cubic_bezier(start: float, control_a: float, control_b: float, end: float, t: float) -> float:
    inverse = 1 - t
    return (
        inverse**3 * start
        + 3 * inverse**2 * t * control_a
        + 3 * inverse * t**2 * control_b
        + t**3 * end
    )


def shell_cap_point(t: float) -> tuple[float, float]:
    """Return the broad crown profile with its intentionally late shoulder turn."""
    normalized = min(1.0, max(0.0, t))
    radius = 1.88 * normalized
    height = 0.68 + 0.54 * math.sqrt(max(0.0, 1 - normalized**4))
    return radius, height


def top_shell_surface_z(x: float, y: float) -> float:
    """Return the baked top-shell height at a horizontal decoration position."""
    radius = math.sqrt(x * x + y * y)
    low = 0.0
    high = 1.0
    for _ in range(18):
        midpoint = (low + high) / 2
        midpoint_radius, _ = shell_cap_point(midpoint)
        if midpoint_radius < radius:
            low = midpoint
        else:
            high = midpoint
    _, height = shell_cap_point((low + high) / 2)
    return height


def create_shell(
    name: str,
    upper: bool,
    material: bpy.types.Material,
    phase: float,
) -> bpy.types.Object:
    """Build one continuous baked shell profile with a broad crown and round shoulder."""
    segments = 288
    radial_steps = 80
    shoulder_steps = 24
    joined_underside_height = 0.495
    sign = 1 if upper else -1
    vertices: list[tuple[float, float, float]] = [(0, 0, sign * shell_cap_point(0)[1])]
    faces: list[tuple[int, ...]] = []
    loops: list[list[int]] = []

    for ring in range(1, radial_steps + 1):
        t = ring / radial_steps
        radius, baked_height = shell_cap_point(t)
        loop: list[int] = []
        for index in range(segments):
            angle = index / segments * math.tau
            # Keep the silhouette handmade without interrupting the continuous
            # large-scale curve of the baked lid.
            profile_envelope = math.sin(t * math.pi)
            handmade = 1 + profile_envelope * (
                0.0055 * math.sin(angle * 3 + phase) + 0.0025 * math.sin(angle * 7 - phase)
            )
            fine_edge = 0.0015 * math.sin(angle * 23 + phase * 2) * profile_envelope
            ring_radius = radius * (handmade + fine_edge)
            surface_wobble = 0.0035 * math.sin(angle * 4 + phase) * profile_envelope
            surface_wobble += 0.0018 * math.sin(angle * 13 - phase) * profile_envelope
            loop.append(len(vertices))
            vertices.append((math.cos(angle) * ring_radius, math.sin(angle) * ring_radius, sign * (baked_height + surface_wobble)))
        loops.append(loop)

    # Preserve the concept's quick outer turn: the crown reaches the edge
    # before a short baked shoulder tucks under. Extra samples and restrained
    # displacement smooth the surface without changing that late transition.
    for step in range(1, shoulder_steps + 1):
        t = step / shoulder_steps
        radius = cubic_bezier(1.88, 1.95, 1.77, 1.62, t)
        height = cubic_bezier(0.68, 0.655, 0.5, joined_underside_height, t)
        loop = []
        for index in range(segments):
            angle = index / segments * math.tau
            envelope = math.sin(t * math.pi)
            handmade = 1 + envelope * (
                0.004 * math.sin(angle * 3 + phase) + 0.0018 * math.sin(angle * 7 - phase)
            )
            loop.append(len(vertices))
            vertices.append((math.cos(angle) * radius * handmade, math.sin(angle) * radius * handmade, sign * height))
        loops.append(loop)

    underside_center = len(vertices)
    vertices.append((0, 0, sign * joined_underside_height))

    first_loop = loops[0]
    for index in range(segments):
        faces.append((0, first_loop[index], first_loop[(index + 1) % segments]))
    for current, following in zip(loops, loops[1:]):
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append((current[index], following[index], following[next_index], current[next_index]))
    final_loop = loops[-1]
    for index in range(segments):
        faces.append((final_loop[index], underside_center, final_loop[(index + 1) % segments]))
    if not upper:
        faces = [tuple(reversed(face)) for face in faces]

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    shell = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(shell)
    add_displacement(shell, 0.0032, 0.07, round(phase * 1000))
    cube_project_uv(shell, 3.84)
    smooth(shell)
    return shell


def create_torus(
    name: str,
    major_radius: float,
    minor_radius: float,
    z: float,
    material: bpy.types.Material,
    *,
    roughness: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=128,
        minor_segments=32,
        location=(0, 0, z),
    )
    torus = bpy.context.object
    torus.name = name
    torus.data.materials.append(material)
    if roughness:
        add_displacement(torus, roughness, 0.075, int(abs(z) * 1000) + 17)
    smooth(torus)
    return torus


def create_cream_layer(
    name: str,
    z: float,
    height: float,
    material: bpy.types.Material,
    seed: int,
    *,
    upper: bool,
) -> bpy.types.Object:
    """Create one asymmetric, hand-piped cream layer with soft weight and edge variation."""
    segments = 256
    levels = 21
    local_rng = random.Random(seed)
    phase_a = local_rng.random() * math.tau
    phase_b = local_rng.random() * math.tau
    phase_c = local_rng.random() * math.tau
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []

    for level in range(levels):
        t = level / (levels - 1)
        profile_power = 0.6 if upper else 0.82
        profile = math.sin(t * math.pi) ** profile_power
        soft_center = math.sin(t * math.pi) ** 1.5
        for index in range(segments):
            angle = index / segments * math.tau
            frontness = max(0.0, -math.sin(angle))
            broad_swell = 0.062 * math.sin(angle * 4 + phase_a)
            secondary_swell = 0.028 * math.sin(angle * 9 + phase_b + t * 0.9)
            handmade = 0.012 * math.sin(angle * 17 + phase_c - t * 1.7)
            # A pressed cream filling keeps broad contact at both edges. It
            # cannot taper back to the hidden core like a free-standing torus.
            bulge = 0.15 if upper else 0.13
            radius = 1.7 + bulge * profile
            radius += profile * (broad_swell + secondary_swell + handmade)
            radius += (0.052 if upper else 0.036) * frontness**2 * profile

            local_height = height * (
                1 + 0.035 * math.sin(angle * 3 + phase_b) + 0.016 * math.sin(angle * 7 + phase_c)
            )
            center_wobble = 0.012 * math.sin(angle * 3 + phase_a)
            center_wobble += 0.006 * math.sin(angle * 8 + phase_b)
            if upper:
                # The upper cream gently drapes toward the visible front edge.
                center_wobble -= 0.024 * frontness**2
            else:
                # The lower cream is compressed by the filling above it.
                center_wobble += 0.008 * frontness**2
            surface_wobble = 0.006 * math.sin(angle * 11 + phase_c + t * 2.1) * soft_center
            z_position = z + center_wobble + (t - 0.5) * local_height + surface_wobble
            vertices.append((math.cos(angle) * radius, math.sin(angle) * radius, z_position))

    for level in range(levels - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            lower = level * segments + index
            lower_next = level * segments + next_index
            upper = (level + 1) * segments + index
            upper_next = (level + 1) * segments + next_index
            faces.append((lower, lower_next, upper_next, upper))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    band = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(band)
    add_displacement(band, 0.0035, 0.11, seed)
    cube_project_uv(band, 3.6)
    smooth(band)
    return band


def create_apricot_jam_ribbon(
    name: str,
    material: bpy.types.Material,
    seed: int,
) -> bpy.types.Object:
    """Create a recessed, glossy jam ribbon with uneven thickness and a gentle front sag."""
    segments = 256
    levels = 15
    height = 0.21
    local_rng = random.Random(seed)
    phase_a = local_rng.random() * math.tau
    phase_b = local_rng.random() * math.tau
    phase_c = local_rng.random() * math.tau
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []

    for level in range(levels):
        t = level / (levels - 1)
        profile = math.sin(t * math.pi) ** 0.68
        for index in range(segments):
            angle = index / segments * math.tau
            frontness = max(0.0, -math.sin(angle))
            broad_wave = 0.048 * math.sin(angle * 4 + phase_a)
            fine_wave = 0.02 * math.sin(angle * 11 + phase_b + t * 1.3)
            # The jam is recessed only slightly from the supporting cream; a
            # deep waist would imply the three layers are floating separately.
            radius = 1.75 + 0.12 * profile + profile * (broad_wave + fine_wave)

            local_height = height * (
                1 + 0.12 * math.sin(angle * 3 + phase_b) + 0.05 * math.sin(angle * 7 + phase_c)
            )
            center_z = -0.008 + 0.013 * math.sin(angle * 2 + phase_a)
            center_z += 0.007 * math.sin(angle * 5 + phase_c)
            center_z -= 0.018 * frontness**2
            z_position = center_z + (t - 0.5) * local_height
            vertices.append((math.cos(angle) * radius, math.sin(angle) * radius, z_position))

    for level in range(levels - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            lower = level * segments + index
            lower_next = level * segments + next_index
            upper = (level + 1) * segments + index
            upper_next = (level + 1) * segments + next_index
            faces.append((lower, lower_next, upper_next, upper))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ribbon = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ribbon)
    cube_project_uv(ribbon, 3.4)
    smooth(ribbon)
    return ribbon


def create_cylinder(
    name: str,
    radius: float,
    depth: float,
    z: float,
    material: bpy.types.Material,
    bevel: float,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=radius, depth=depth, location=(0, 0, z))
    cylinder = bpy.context.object
    cylinder.name = name
    cylinder.data.materials.append(material)
    add_bevel(cylinder, bevel, 4)
    cube_project_uv(cylinder, 3.4)
    smooth(cylinder)
    return cylinder


def create_ruffled_foot(
    name: str,
    z: float,
    material: bpy.types.Material,
    crumb_material: bpy.types.Material,
    pore_material: bpy.types.Material,
    seed: int,
) -> bpy.types.Object:
    """Create a crisp, airy pied with recessed pores and fragile baked folds."""
    local_rng = random.Random(seed)
    segments = 256
    levels = 17
    height = 0.30
    # The ruffled pied is visible at the seam, but it stays inside the smooth
    # baked shell outline. Letting it overhang around the full circumference
    # made top views read as a torn cake rather than this same macaron.
    base_radius = 1.79
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    phase_a = local_rng.random() * math.tau
    phase_b = local_rng.random() * math.tau
    phase_c = local_rng.random() * math.tau
    pore_specs = [
        (
            local_rng.uniform(0, math.tau),
            local_rng.uniform(-height * 0.38, height * 0.38),
            local_rng.uniform(0.040, 0.074),
            local_rng.uniform(0.022, 0.041),
            local_rng.uniform(0.024, 0.055),
        )
        for _ in range(72)
    ]

    for level in range(levels):
        t = level / (levels - 1)
        profile = math.sin(t * math.pi) ** 0.58
        for index in range(segments):
            angle = index / segments * math.tau
            hashed = ((index * 73856093) ^ (level * 19349663) ^ seed) & 255
            baked_grain = (hashed / 255 - 0.5) * (0.006 + 0.014 * profile)
            broad_wobble = 0.011 * math.sin(angle * 7 + phase_a)
            folded_edge = 0.012 * math.sin(angle * 41 + phase_b + t * 5.2)
            crisp_ruffle = 0.006 * math.sin(angle * 73 + phase_c - t * 7.1)
            narrow_fissure = -0.012 * max(0, math.cos(angle * 53 + phase_a)) ** 12
            radius = base_radius + 0.11 * profile + broad_wobble
            radius += profile * (folded_edge + crisp_ruffle + narrow_fissure) + baked_grain
            vertical_wobble = 0.004 * math.sin(angle * 13 + phase_b) * profile
            vertical_wobble += 0.002 * math.sin(angle * 31 + phase_a + level)
            local_z = (t - 0.5) * height + vertical_wobble
            pore_indent = 0.0
            for pore_angle, pore_z, tangent_width, vertical_width, depth in pore_specs:
                angle_distance = abs((angle - pore_angle + math.pi) % math.tau - math.pi)
                tangent_distance = angle_distance * base_radius
                distance_squared = (tangent_distance / tangent_width) ** 2 + (
                    (local_z - pore_z) / vertical_width
                ) ** 2
                if distance_squared < 1:
                    pore_indent = max(pore_indent, depth * (1 - distance_squared) ** 2)
            radius -= pore_indent
            vertices.append((math.cos(angle) * radius, math.sin(angle) * radius, z + local_z))

    for level in range(levels - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            lower = level * segments + index
            lower_next = level * segments + next_index
            upper = (level + 1) * segments + index
            upper_next = (level + 1) * segments + next_index
            faces.append((lower, lower_next, upper_next, upper))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    foot = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(foot)
    add_displacement(foot, 0.005, 0.065, seed)
    cube_project_uv(foot, 3.6)
    smooth(foot)

    # Each opening has a shallow concave dark interior. Together with the
    # matching indentation above, these remain dimensional pores when the
    # model rotates instead of becoming painted dots on a texture.
    pore_mesh = bpy.data.meshes.new(f"{name} pore cavity mesh")
    pore_cavities = bpy.data.objects.new(f"{name} airy pore cavities", pore_mesh)
    bpy.context.collection.objects.link(pore_cavities)
    pore_mesh.materials.append(pore_material)
    pore_vertices: list[tuple[float, float, float]] = []
    pore_faces: list[tuple[int, ...]] = []
    pore_sides = 12
    for pore_angle, pore_z, tangent_width, vertical_width, depth in pore_specs:
        profile_t = pore_z / height + 0.5
        profile = math.sin(max(0.0, min(1.0, profile_t)) * math.pi) ** 0.58
        broad_wobble = 0.011 * math.sin(pore_angle * 7 + phase_a)
        surface_radius = base_radius + 0.11 * profile + broad_wobble
        normal = Vector((math.cos(pore_angle), math.sin(pore_angle), 0))
        tangent = Vector((-math.sin(pore_angle), math.cos(pore_angle), 0))
        center = normal * (surface_radius - depth * 0.80) + Vector((0, 0, z + pore_z))
        center_index = len(pore_vertices)
        pore_vertices.append(tuple(center))
        inner_start = len(pore_vertices)
        outer_start = inner_start + pore_sides
        for ring_scale, radial_depth in ((0.48, depth * 0.55), (1.0, depth * 0.22)):
            for side in range(pore_sides):
                ring_angle = side / pore_sides * math.tau
                point = normal * (surface_radius - radial_depth)
                point += tangent * (math.cos(ring_angle) * tangent_width * ring_scale)
                point += Vector((0, 0, z + pore_z + math.sin(ring_angle) * vertical_width * ring_scale))
                pore_vertices.append(tuple(point))
        for side in range(pore_sides):
            following = (side + 1) % pore_sides
            pore_faces.append((center_index, inner_start + side, inner_start + following))
            pore_faces.append(
                (
                    inner_start + side,
                    outer_start + side,
                    outer_start + following,
                    inner_start + following,
                )
            )
    pore_mesh.from_pydata(pore_vertices, [], pore_faces)
    pore_mesh.update()
    smooth(pore_cavities)

    # A restrained number of embedded crumbs supports the ruffle instead of defining it.
    crumb_mesh = bpy.data.meshes.new(f"{name} crumb mesh")
    crumbs = bpy.data.objects.new(f"{name} embedded crumbs", crumb_mesh)
    bpy.context.collection.objects.link(crumbs)
    crumb_mesh.materials.append(crumb_material)
    bm = bmesh.new()
    for _ in range(56):
        angle = local_rng.uniform(0, math.tau)
        radius = local_rng.uniform(base_radius + 0.035, base_radius + 0.105)
        size = local_rng.uniform(0.008, 0.018)
        crumb_z = z + local_rng.uniform(-0.125, 0.125)
        transform = Matrix.Translation((math.cos(angle) * radius, math.sin(angle) * radius, crumb_z))
        transform @= Matrix.Diagonal((local_rng.uniform(0.7, 1.25), local_rng.uniform(0.7, 1.25), local_rng.uniform(0.6, 1.25), 1))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=size, matrix=transform)
    bm.to_mesh(crumb_mesh)
    bm.free()
    cube_project_uv(crumbs, 3.6)
    smooth(crumbs)
    return foot


def arch_points(width: float, height: float, *, pivot_left: bool = False, segments: int = 24) -> list[tuple[float, float]]:
    radius = width / 2
    center_x = radius if pivot_left else 0.0
    left = 0.0 if pivot_left else -radius
    right = width if pivot_left else radius
    center_y = height - radius
    points = [(left, 0.0), (right, 0.0), (right, center_y)]
    for index in range(1, segments + 1):
        angle = (index / segments) * math.pi
        points.append((center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius))
    return points


def arch_loop_points(width: float, height: float, *, segments: int = 32) -> list[tuple[float, float]]:
    """Return a clean closed arch loop without duplicate boundary vertices."""
    radius = width / 2
    center_y = height - radius
    points = [(-radius, 0.0), (radius, 0.0)]
    for index in range(segments + 1):
        angle = index / segments * math.pi
        points.append((math.cos(angle) * radius, center_y + math.sin(angle) * radius))
    return points


def capsule_points(width: float, height: float, segments: int = 14) -> list[tuple[float, float]]:
    radius = width / 2
    points: list[tuple[float, float]] = []
    for index in range(segments + 1):
        angle = math.pi + (index / segments) * math.pi
        points.append((math.cos(angle) * radius, radius + math.sin(angle) * radius))
    for index in range(segments + 1):
        angle = (index / segments) * math.pi
        points.append((math.cos(angle) * radius, height - radius + math.sin(angle) * radius))
    return points


def create_puffed_sugar_star(
    name: str,
    size: float,
    material: bpy.types.Material,
    phase: float,
    *,
    height: float,
    highlight_material: bpy.types.Material | None = None,
    shadow_material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Create a rounded, hand-pressed sugar star with raised irregular facets."""
    samples_per_sector = 8
    sector_count = 10
    boundary_count = samples_per_sector * sector_count
    boundary: list[tuple[float, float]] = []

    for index in range(boundary_count):
        angle = math.pi / 2 + index / boundary_count * math.tau
        lobe_wave = (1 + math.cos(5 * (angle - math.pi / 2))) / 2
        rounded_lobe = lobe_wave**1.15
        radius = size * (0.52 + 0.48 * rounded_lobe)
        radius *= 1 + 0.025 * math.sin(angle * 2 + phase) + 0.012 * math.sin(angle * 7 - phase)
        boundary.append((math.cos(angle) * radius, math.sin(angle) * radius))

    rim_height = height * 0.24
    vertices: list[tuple[float, float, float]] = [(0, 0, 0)]
    vertices.extend((x, y, 0) for x, y in boundary)
    rim_start = len(vertices)
    vertices.extend((x, y, rim_height) for x, y in boundary)

    ridge_start = len(vertices)
    for sector in range(sector_count):
        x, y = boundary[sector * samples_per_sector]
        ridge_height = height * (0.72 if sector % 2 == 0 else 0.58)
        vertices.append((x * 0.48, y * 0.48, ridge_height))

    center_index = len(vertices)
    vertices.append((0.008 * math.sin(phase), -0.006 * math.cos(phase), height))

    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []

    for index in range(boundary_count):
        next_index = (index + 1) % boundary_count
        faces.append((0, 1 + next_index, 1 + index))
        material_indices.append(0)
        faces.append((1 + index, 1 + next_index, rim_start + next_index, rim_start + index))
        material_indices.append(0)

    for sector in range(sector_count):
        sector_start = sector * samples_per_sector
        ridge = ridge_start + sector
        next_ridge = ridge_start + (sector + 1) % sector_count
        if highlight_material and sector in (0, 3, 7):
            facet_material_index = 1
        elif shadow_material and sector in (4, 8):
            facet_material_index = 2
        else:
            facet_material_index = 0

        for offset in range(samples_per_sector):
            boundary_index = (sector_start + offset) % boundary_count
            next_boundary_index = (boundary_index + 1) % boundary_count
            target_ridge = ridge if offset < samples_per_sector // 2 else next_ridge
            faces.append((rim_start + boundary_index, rim_start + next_boundary_index, target_ridge))
            material_indices.append(facet_material_index)

        midpoint = (sector_start + samples_per_sector // 2) % boundary_count
        faces.append((rim_start + midpoint, next_ridge, ridge))
        material_indices.append(facet_material_index)

        faces.append((ridge, next_ridge, center_index))
        if highlight_material and sector in (1, 5):
            material_indices.append(1)
        elif shadow_material and sector in (3, 8):
            material_indices.append(2)
        else:
            material_indices.append(0)

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    if highlight_material:
        mesh.materials.append(highlight_material)
    if shadow_material:
        mesh.materials.append(shadow_material)
    mesh.update()
    for polygon, material_index in zip(mesh.polygons, material_indices):
        polygon.material_index = material_index

    star = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(star)
    return star


def ellipse_points(width: float, height: float, segments: int = 32) -> list[tuple[float, float]]:
    return [
        (math.cos(index / segments * math.tau) * width / 2, math.sin(index / segments * math.tau) * height / 2)
        for index in range(segments)
    ]


def create_extruded_polygon(
    name: str,
    points: list[tuple[float, float]],
    depth: float,
    material: bpy.types.Material,
    bevel: float = 0.01,
    uv_cube_size: float | None = None,
) -> bpy.types.Object:
    count = len(points)
    vertices = [(x, y, -depth / 2) for x, y in points] + [(x, y, depth / 2) for x, y in points]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    object_ = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(object_)
    if bevel:
        add_bevel(object_, bevel, 3)
    if uv_cube_size:
        cube_project_uv(object_, uv_cube_size)
    smooth(object_)
    return object_


def create_extruded_arch_ring(
    name: str,
    *,
    outer_width: float,
    outer_height: float,
    inner_width: float,
    inner_height: float,
    inner_bottom: float,
    depth: float,
    material: bpy.types.Material,
    bevel: float = 0.01,
) -> bpy.types.Object:
    """Build a physically open arch frame instead of stacking solid plaques."""
    outer = arch_loop_points(outer_width, outer_height)
    inner = [(x, y + inner_bottom) for x, y in arch_loop_points(inner_width, inner_height)]
    count = len(outer)
    vertices = (
        [(x, y, -depth / 2) for x, y in outer]
        + [(x, y, -depth / 2) for x, y in inner]
        + [(x, y, depth / 2) for x, y in outer]
        + [(x, y, depth / 2) for x, y in inner]
    )
    faces: list[tuple[int, int, int, int]] = []
    outer_back = 0
    inner_back = count
    outer_front = count * 2
    inner_front = count * 3

    for index in range(count):
        next_index = (index + 1) % count
        faces.append((outer_front + index, outer_front + next_index, inner_front + next_index, inner_front + index))
        faces.append((outer_back + next_index, outer_back + index, inner_back + index, inner_back + next_index))
        faces.append((outer_back + index, outer_back + next_index, outer_front + next_index, outer_front + index))
        faces.append((inner_back + next_index, inner_back + index, inner_front + index, inner_front + next_index))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ring = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ring)
    if bevel:
        add_bevel(ring, bevel, 3)
    cube_project_uv(ring, max(outer_width, outer_height))
    smooth(ring)
    return ring


def create_textured_sugar_plaque(
    name: str,
    points: list[tuple[float, float]],
    front_material: bpy.types.Material,
    side_material: bpy.types.Material,
    *,
    depth: float,
    source_uv: tuple[float, float, float, float],
    local_bounds: tuple[float, float, float, float],
    bevel: float = 0.006,
) -> bpy.types.Object:
    """Build a thin edible plaque whose front carries the approved artwork."""
    count = len(points)
    vertices = [(x, y, -depth / 2) for x, y in points] + [(x, y, depth / 2) for x, y in points]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(side_material)
    mesh.materials.append(front_material)
    mesh.update()
    mesh.polygons[1].material_index = 1

    u_min, u_max, v_min, v_max = source_uv
    x_min, x_max, y_min, y_max = local_bounds
    uv_layer = mesh.uv_layers.new(name="Window illustration UV")
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if polygon.index == 1:
                u = u_min + ((vertex.x - x_min) / (x_max - x_min)) * (u_max - u_min)
                v = v_min + ((vertex.y - y_min) / (y_max - y_min)) * (v_max - v_min)
                uv_layer.data[loop_index].uv = (u, v)
            else:
                uv_layer.data[loop_index].uv = (0.5, 0.5)

    plaque = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(plaque)
    if bevel:
        add_bevel(plaque, bevel, 3)
    smooth(plaque)
    return plaque


def create_curve(
    name: str,
    points: list[tuple[float, float, float]],
    bevel: float,
    material: bpy.types.Material,
    *,
    cyclic: bool = False,
    bezier: bool = True,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 10
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 4
    curve_data.resolution_u = 16
    if bezier:
        spline = curve_data.splines.new("BEZIER")
        spline.bezier_points.add(len(points) - 1)
        for point, coordinate in zip(spline.bezier_points, points):
            point.co = coordinate
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
    else:
        # Dense POLY points preserve the intended syrup arc without Bezier
        # endpoint overshoot, which can otherwise form a floating loop.
        spline = curve_data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, coordinate in zip(spline.points, points):
            point.co = (*coordinate, 1.0)
    spline.use_cyclic_u = cyclic
    object_ = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(object_)
    curve_data.materials.append(material)
    return object_


def parent_local(object_: bpy.types.Object, parent: bpy.types.Object, location=(0, 0, 0)) -> None:
    object_.parent = parent
    object_.location = location


def create_window_group(materials: dict[str, bpy.types.Material]) -> bpy.types.Object:
    group = bpy.data.objects.new("Arched window sugar plaque", None)
    bpy.context.collection.objects.link(group)
    # Keep the approved placement from the composition review; only the
    # shutter's hinge relationship needs changing below.
    window_x, window_y = 0.54, 0.2
    group.location = (window_x, window_y, top_shell_surface_z(window_x, window_y) - 0.08)
    # Build the plaque basis from the canonical presentation camera: local X
    # is screen-right, local Y is screen-up, and local Z faces the camera.
    # This makes both the sill and the arch axis straight at the same time,
    # rather than correcting one edge with an in-plane spin that skews the
    # other.
    screen_right = Vector((0.5, 0.866, 0.0)).normalized()
    screen_up = Vector((-0.459, 0.265, 0.854)).normalized()
    face_normal = screen_right.cross(screen_up).normalized()
    presentation_orientation = Matrix((screen_right, screen_up, face_normal)).transposed()
    group.rotation_mode = "QUATERNION"
    group.rotation_quaternion = presentation_orientation.to_quaternion()
    group.scale = (0.98, 0.98, 0.98)

    # The reference depicts a small edible window with a real opening. Solid
    # arch plaques stacked on top of one another made the pane float in front
    # and could never read as a plausible frame.
    frame_outline = create_extruded_arch_ring(
        "Warm pencil window outline ring",
        outer_width=1.02,
        outer_height=1.12,
        inner_width=0.72,
        inner_height=0.84,
        inner_bottom=0.10,
        depth=0.045,
        material=materials["frame_shadow"],
        bevel=0.012,
    )
    parent_local(frame_outline, group, (0, 0, 0.018))

    frame = create_extruded_arch_ring(
        "Open dusky-violet sugar window frame",
        outer_width=0.98,
        outer_height=1.08,
        inner_width=0.73,
        inner_height=0.85,
        inner_bottom=0.10,
        depth=0.06,
        material=materials["frame"],
        bevel=0.022,
    )
    parent_local(frame, group, (0, 0, 0.048))

    # The pale stroke in the illustration is reflected light, not an applied
    # decoration.  A rounded physical moulding lets the scene light create
    # that highlight correctly as the viewer rotates the model.
    moulding_radius = 0.425
    moulding_center_y = 0.61
    moulding_points = [(-moulding_radius, 0.055, 0.105)]
    moulding_points.extend(
        (
            math.cos(math.pi - index / 40 * math.pi) * moulding_radius,
            moulding_center_y + math.sin(math.pi - index / 40 * math.pi) * moulding_radius,
            0.105,
        )
        for index in range(41)
    )
    moulding_points.append((moulding_radius, 0.055, 0.105))
    frame_moulding = create_curve(
        "Rounded dusky-violet sugar window moulding",
        moulding_points,
        0.052,
        materials["frame"],
        bezier=False,
    )
    frame_moulding.parent = group

    pane = create_extruded_polygon(
        "Inset warm apricot sugar-glass pane",
        arch_points(0.82, 0.94),
        0.025,
        materials["window_glow"],
        0.008,
        uv_cube_size=1.0,
    )
    parent_local(pane, group, (0, 0.08, 0.032))

    # The authored pane is the atmosphere-bearing part of this design. Keep it
    # as a flat sugar print, but inset it inside the true 3D opening so the
    # frame and sill, rather than the crop boundary, define the object.
    window_illustration = create_textured_sugar_plaque(
        "Approved rabbit window sugar plaque",
        arch_points(0.68, 0.78),
        materials["window_illustration"],
        materials["window_glow"],
        depth=0.018,
        source_uv=(0.0, 1.0, 0.0, 1.0),
        local_bounds=(-0.34, 0.34, 0.0, 0.78),
    )
    parent_local(window_illustration, group, (0, 0.13, 0.057))

    # One integrated rounded sill supports the frame and hides the lower pane
    # edge. It replaces the previous stack of three unrelated floating bars.
    sill_outline = create_extruded_polygon(
        "Integrated window sill pencil edge",
        [(-0.52, -0.06), (0.52, -0.06), (0.52, 0.12), (-0.52, 0.12)],
        0.052,
        materials["frame_shadow"],
        0.018,
        uv_cube_size=1.1,
    )
    parent_local(sill_outline, group, (0, 0, 0.072))
    sill_moulding = create_curve(
        "Rounded dusky-violet sugar sill moulding",
        [(-0.45, 0.035, 0.142), (0.45, 0.035, 0.142)],
        0.052,
        materials["frame"],
        bezier=False,
    )
    sill_moulding.parent = group

    hinge = bpy.data.objects.new("Open sugar shutter hinge", None)
    bpy.context.collection.objects.link(hinge)
    hinge.parent = group
    hinge.location = (0.42, 0.045, 0.058)
    # The reference shutter is not opened flat to 180 degrees. Folding it 36
    # degrees out of the frame plane leaves an approximately 144-degree
    # included angle and visible foreshortening from the presentation camera.
    hinge.rotation_euler.y = math.radians(36)

    for index, hinge_y in enumerate((0.25, 0.69)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.027, depth=0.13)
        hinge_pin = bpy.context.object
        hinge_pin.name = f"Edible shutter hinge pin {index + 1}"
        hinge_pin.data.materials.append(materials["wood_back"])
        hinge_pin.parent = group
        hinge_pin.location = (0.465, hinge_y, 0.075)
        hinge_pin.rotation_euler.x = math.radians(90)
        smooth(hinge_pin)

    door_back = create_extruded_polygon(
        "Finished caramel shutter back",
        arch_points(0.58, 0.95, pivot_left=True),
        0.045,
        materials["wood_back"],
        0.014,
    )
    parent_local(door_back, hinge)
    # The shutter is one moulded object: a recessed caramel field sits behind
    # a raised arched frame and two structural rails.  Four individually
    # pasted panel polygons looked like craft-paper collage from oblique views.
    door_inset = create_extruded_polygon(
        "Recessed caramel shutter field",
        arch_points(0.52, 0.87, pivot_left=True),
        0.026,
        materials["wood_dark"],
        0.012,
        uv_cube_size=0.8,
    )
    parent_local(door_inset, hinge, (0.03, 0.035, 0.047))

    door_frame = create_extruded_arch_ring(
        "Raised honey-sugar shutter frame",
        outer_width=0.50,
        outer_height=0.84,
        inner_width=0.36,
        inner_height=0.67,
        inner_bottom=0.08,
        depth=0.038,
        material=materials["wood"],
        bevel=0.018,
    )
    parent_local(door_frame, hinge, (0.28, 0.05, 0.078))

    vertical_stile = create_extruded_polygon(
        "Raised shutter centre stile",
        [(-0.034, 0.08), (0.034, 0.08), (0.034, 0.73), (-0.034, 0.73)],
        0.04,
        materials["wood"],
        0.012,
        uv_cube_size=0.65,
    )
    parent_local(vertical_stile, hinge, (0.28, 0.05, 0.087))

    horizontal_rail = create_extruded_polygon(
        "Raised shutter middle rail",
        [(-0.195, -0.038), (0.195, -0.038), (0.195, 0.038), (-0.195, 0.038)],
        0.04,
        materials["wood"],
        0.012,
        uv_cube_size=0.4,
    )
    parent_local(horizontal_rail, hinge, (0.28, 0.41, 0.088))

    return group


def create_garland(materials: dict[str, bpy.types.Material]) -> None:
    """Model the canonical five-star crescent that cups the arched window."""
    anchor = Vector((0.54, 0.20))
    screen_right = Vector((0.5, 0.866)).normalized()
    screen_up = Vector((-0.866, 0.5)).normalized()

    def from_design_plane(local_x: float, local_y: float) -> tuple[float, float]:
        point = anchor + screen_right * local_x + screen_up * local_y
        return point.x, point.y

    def ring_local(t: float) -> tuple[float, float]:
        # The 2D design is a deep, asymmetric crescent around the window, not
        # a shallow smile beneath it. The right side finishes slightly lower
        # so it clears the open shutter in three dimensions.
        local_x = -1.08 + 2.16 * t
        local_y = 0.20 - 0.76 * math.sin(t * math.pi) ** 0.86 - 0.035 * t
        return local_x, local_y

    def surface_path(local_points: list[tuple[float, float]], lift: float) -> list[tuple[float, float, float]]:
        points = []
        for local_x, local_y in local_points:
            x, y = from_design_plane(local_x, local_y)
            points.append((x, y, top_shell_surface_z(x, y) + lift))
        return points

    def smooth_branch(local_points: list[tuple[float, float]], samples_per_segment: int = 10) -> list[tuple[float, float]]:
        """Densely sample a Catmull-Rom branch so exported tubes have no broken elbows."""
        result: list[tuple[float, float]] = []
        for segment in range(len(local_points) - 1):
            p0 = Vector(local_points[max(0, segment - 1)])
            p1 = Vector(local_points[segment])
            p2 = Vector(local_points[segment + 1])
            p3 = Vector(local_points[min(len(local_points) - 1, segment + 2)])
            for sample in range(samples_per_segment):
                t = sample / samples_per_segment
                point = 0.5 * (
                    2 * p1
                    + (-p0 + p2) * t
                    + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
                    + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
                )
                result.append((point.x, point.y))
        result.append(local_points[-1])
        return result

    path_local = [ring_local(0.02 + index / 72 * 0.96) for index in range(73)]
    create_curve(
        "Five-star crescent warm pencil edge",
        surface_path(path_local, 0.026),
        0.041,
        materials["garland_outline"],
        bezier=False,
    )
    create_curve(
        "Five-star crescent vanilla sugar piping",
        surface_path(path_local, 0.043),
        0.025,
        materials["pearl"],
        bezier=False,
    )

    # Two continuous end stems rise beside the window. The smaller decorations
    # are added below as a strict alternating bud sequence, not loose beads or
    # literal leaf silhouettes.
    end_branch_controls = [
        [ring_local(0.055), (-1.08, 0.18), (-1.15, 0.39), (-1.12, 0.60), (-1.02, 0.76)],
        [ring_local(0.945), (1.06, 0.13), (1.12, 0.31), (1.08, 0.49), (0.99, 0.61)],
    ]
    end_branches: list[list[tuple[float, float]]] = []
    for index, control_points in enumerate(end_branch_controls):
        local_points = smooth_branch(control_points)
        end_branches.append(local_points)
        create_curve(
            f"Five-star crescent end stem {index + 1} edge",
            surface_path(local_points, 0.028),
            0.032,
            materials["garland_outline"],
            bezier=False,
        )
        create_curve(
            f"Five-star crescent end stem {index + 1}",
            surface_path(local_points, 0.045),
            0.019,
            materials["pearl"],
            bezier=False,
        )

    bud_index = 0

    def add_alternating_buds(
        stem_points: list[tuple[float, float]],
        fractions: list[float],
        first_side: int,
        label: str,
    ) -> None:
        nonlocal bud_index
        for sequence_index, fraction in enumerate(fractions):
            point_index = round(fraction * (len(stem_points) - 1))
            previous_index = max(0, point_index - 1)
            following_index = min(len(stem_points) - 1, point_index + 1)
            base = Vector(stem_points[point_index])
            tangent = (Vector(stem_points[following_index]) - Vector(stem_points[previous_index])).normalized()
            normal = Vector((-tangent.y, tangent.x))
            side = first_side if sequence_index % 2 == 0 else -first_side
            reach = 0.085 + 0.008 * (sequence_index % 3)
            tip = base + normal * reach * side
            branchlet = smooth_branch(
                [
                    tuple(base),
                    tuple(base + normal * reach * 0.48 * side + tangent * 0.008),
                    tuple(tip),
                ],
                samples_per_segment=6,
            )
            create_curve(
                f"Five-star crescent {label} bud stem {sequence_index + 1} edge",
                surface_path(branchlet, 0.030),
                0.020,
                materials["garland_outline"],
                bezier=False,
            )
            create_curve(
                f"Five-star crescent {label} bud stem {sequence_index + 1}",
                surface_path(branchlet, 0.046),
                0.011,
                materials["pearl"],
                bezier=False,
            )

            bud_index += 1
            x, y = from_design_plane(tip.x, tip.y)
            radius = (0.050, 0.046, 0.053)[bud_index % 3]
            surface_z = top_shell_surface_z(x, y)
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=24,
                ring_count=16,
                radius=radius + 0.009,
                location=(x, y, surface_z + radius * 0.78),
            )
            backing = bpy.context.object
            backing.name = f"Five-star crescent alternating bud {bud_index} cocoa base"
            backing.data.materials.append(materials["garland_outline"])
            smooth(backing)
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=24,
                ring_count=16,
                radius=radius,
                location=(x, y, surface_z + radius * 0.92 + 0.008),
            )
            bud = bpy.context.object
            bud.name = f"Five-star crescent alternating bud {bud_index} vanilla sphere"
            bud.data.materials.append(materials["pearl"])
            smooth(bud)

    add_alternating_buds(
        path_local,
        [0.16, 0.23, 0.38, 0.45, 0.57, 0.64, 0.77, 0.84],
        1,
        "main vine",
    )
    add_alternating_buds(
        end_branches[0],
        [0.30, 0.50, 0.70, 0.91],
        1,
        "left rise",
    )
    add_alternating_buds(
        end_branches[1],
        [0.30, 0.50, 0.70, 0.91],
        -1,
        "right rise",
    )

    stars = [
        (0.10, "green", 0.19, -0.18),
        (0.31, "pink", 0.22, 0.12),
        (0.50, "green", 0.20, -0.08),
        (0.70, "pink", 0.22, 0.16),
        (0.90, "green", 0.19, -0.12),
    ]
    for index, (t, color, size, rotation) in enumerate(stars):
        x, y = from_design_plane(*ring_local(t))
        z = top_shell_surface_z(x, y) + 0.045
        backing = create_puffed_sugar_star(
            f"Star {index + 1} pencil edge",
            size + 0.019,
            materials["garland_outline"],
            index * 0.73 + 0.2,
            height=0.035,
        )
        backing.location = (x, y, z)
        backing.rotation_euler.z = rotation
        star = create_puffed_sugar_star(
            f"Star {index + 1} sugar",
            size,
            materials[color],
            index * 0.73 + 0.2,
            height=0.078,
            highlight_material=materials[f"{color}_highlight"],
            shadow_material=materials[f"{color}_shadow"],
        )
        star.location = (x, y, z + 0.019)
        star.rotation_euler.z = rotation

        # Fine cream ridges echo the hand-painted creases in the reference;
        # the volume and colored facets underneath carry the actual form.
        for ray_index, angle in enumerate((math.radians(86), math.radians(28), math.radians(148))):
            ray_length = size * (0.68 if ray_index == 0 else 0.58)
            ray = create_curve(
                f"Star {index + 1} pressed sugar crease {ray_index + 1}",
                [
                    (x, y, z + 0.103),
                    (
                        x + math.cos(angle + rotation) * ray_length,
                        y + math.sin(angle + rotation) * ray_length,
                        z + 0.061,
                    ),
                ],
                0.008,
                materials[f"{color}_crease"],
                bezier=False,
            )

def build_model() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clear_scene()

    materials = {
        "shell": create_material(
            "Night violet shell",
            "#65405F",
            roughness=0.92,
            texture_seed=211,
            texture_profile="shell",
            roughness_variation=0.08,
            normal_seed=211,
            normal_strength=0.42,
        ),
        "foot": create_material(
            "Crisp violet foot",
            "#573650",
            roughness=0.95,
            texture_seed=731,
            texture_profile="foot",
            roughness_variation=0.07,
            normal_seed=743,
            normal_strength=0.52,
        ),
        "foot_crumb": create_material(
            "Toasted violet foot crumbs",
            "#98616E",
            roughness=0.94,
        ),
        "foot_pore": create_material(
            "Deep baked violet foot pores",
            "#2E1B2B",
            roughness=1.0,
            texture_seed=769,
            texture_profile="foot",
            texture_size=256,
            roughness_variation=0.025,
        ),
        "cream": create_material(
            "Warm white chocolate cream",
            "#F6E3BE",
            roughness=0.64,
            texture_seed=401,
            texture_profile="cream",
            texture_size=256,
            roughness_variation=0.065,
            transmission=0.025,
            coat_weight=0.12,
            coat_roughness=0.24,
            specular_level=0.3,
        ),
        "cream_upper": create_material(
            "Upper vanilla cream with pressed ripples",
            "#EACB98",
            roughness=0.67,
            texture_seed=457,
            texture_profile="cream_filling",
            texture_size=256,
            roughness_variation=0.1,
            normal_seed=457,
            normal_strength=0.16,
            coat_weight=0.1,
            coat_roughness=0.28,
            specular_level=0.28,
        ),
        "cream_lower": create_material(
            "Lower vanilla cream with warm marbling",
            "#F0D4A6",
            roughness=0.64,
            texture_seed=523,
            texture_profile="cream_filling",
            texture_size=256,
            roughness_variation=0.085,
            normal_seed=523,
            normal_strength=0.14,
            coat_weight=0.12,
            coat_roughness=0.25,
            specular_level=0.3,
        ),
        "apricot": create_material(
            "Apricot honey jam",
            "#F09A32",
            roughness=0.14,
            texture_seed=613,
            texture_profile="jam",
            texture_size=256,
            roughness_variation=0.09,
            normal_seed=613,
            normal_strength=0.08,
            transmission=0.16,
            coat_weight=0.62,
            coat_roughness=0.06,
            specular_level=0.44,
        ),
        "outline": create_material("Warm brown pencil sugar", "#302027", roughness=1.0),
        "frame": create_material(
            "Dusky violet sugar frame",
            "#74516E",
            roughness=0.82,
            texture_seed=907,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.045,
        ),
        "frame_shadow": create_material(
            "Deep violet sugar frame edge and back",
            "#62445E",
            roughness=0.9,
            texture_seed=929,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.035,
        ),
        "window_glow": create_material(
            "Warm apricot hard-candy window glow",
            "#97490F",
            roughness=0.44,
            texture_seed=821,
            texture_profile="window_glow",
            texture_size=256,
            roughness_variation=0.05,
            coat_weight=0.16,
            coat_roughness=0.18,
            specular_level=0.3,
        ),
        "window_illustration": create_reference_image_material(
            "Approved generated rabbit window sugar print",
            WINDOW_INTERIOR_TEXTURE,
        ),
        "wood": create_material(
            "Honey brown shutter",
            "#9F6037",
            roughness=0.78,
            texture_seed=1013,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.04,
        ),
        "wood_back": create_material(
            "Finished caramel shutter edge and back",
            "#815037",
            roughness=0.84,
            texture_seed=1021,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.04,
        ),
        "wood_dark": create_material(
            "Dark caramel shutter panels",
            "#693B2B",
            roughness=0.86,
            texture_seed=1031,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.035,
        ),
        # These hues are sampled from the canonical 2D candies.  Separate
        # colored creases keep the facets in the same palette instead of
        # washing every star toward white under the scene lights.
        "pink": create_material(
            "Warm coral-pink star sugar",
            "#EE8F7E",
            roughness=0.84,
            texture_seed=1201,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.045,
            normal_seed=1201,
            normal_strength=0.12,
        ),
        "green": create_material(
            "Warm olive-green star sugar",
            "#C5B853",
            roughness=0.86,
            texture_seed=1237,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.045,
            normal_seed=1237,
            normal_strength=0.12,
        ),
        "pink_highlight": create_material("Coral star raised facet", "#F6B09F", roughness=0.8),
        "pink_shadow": create_material("Coral star pressed facet", "#A76367", roughness=0.9),
        "pink_crease": create_material("Coral star icing crease", "#F8C4AC", roughness=0.76),
        "green_highlight": create_material("Olive star raised facet", "#E4D584", roughness=0.82),
        "green_shadow": create_material("Olive star pressed facet", "#8E7D35", roughness=0.91),
        "green_crease": create_material("Olive star icing crease", "#F0E1A2", roughness=0.77),
        "garland_outline": create_material("Warm cocoa garland edge", "#865B52", roughness=0.94),
        "pearl": create_material(
            "Warm vanilla pearl sugar",
            "#EBC58C",
            roughness=0.7,
            texture_seed=1289,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.035,
            normal_seed=1289,
            normal_strength=0.08,
            coat_weight=0.08,
            coat_roughness=0.3,
            specular_level=0.26,
        ),
    }

    create_shell("Upper night-violet shell", True, materials["shell"], 0.35)
    create_shell("Lower night-violet shell", False, materials["shell"], 1.25)
    create_ruffled_foot(
        "Upper crisp macaron foot",
        0.49,
        materials["foot"],
        materials["foot_crumb"],
        materials["foot_pore"],
        731,
    )
    create_ruffled_foot(
        "Lower crisp macaron foot",
        -0.5,
        materials["foot"],
        materials["foot_crumb"],
        materials["foot_pore"],
        947,
    )

    create_cylinder("White chocolate cream core", 1.3, 0.92, 0, materials["cream"], 0.13)
    create_cream_layer(
        "Upper draped vanilla cream layer",
        0.30,
        0.56,
        materials["cream_upper"],
        401,
        upper=True,
    )
    create_cream_layer(
        "Lower supporting vanilla cream layer",
        -0.29,
        0.47,
        materials["cream_lower"],
        509,
        upper=False,
    )
    create_apricot_jam_ribbon("Inset translucent apricot honey ribbon", materials["apricot"], 613)
    create_window_group(materials)
    create_garland(materials)

    root = bpy.data.objects.new("Window Notes Macaron", None)
    bpy.context.collection.objects.link(root)
    for object_ in list(bpy.context.scene.objects):
        if object_ is not root and object_.parent is None:
            object_.parent = root
    root.rotation_euler.z = math.radians(-2)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), compress=True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        export_apply=True,
        export_yup=True,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    print(f"BLEND={BLEND_PATH} ({BLEND_PATH.stat().st_size} bytes)")
    print(f"GLB={GLB_PATH} ({GLB_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    build_model()
