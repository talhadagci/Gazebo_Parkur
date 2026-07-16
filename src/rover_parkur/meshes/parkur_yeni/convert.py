#!/usr/bin/env python3
import sys
from pathlib import Path

def parse_mtl(path):
    mats = {}
    cur = None
    for line in open(path):
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'newmtl':
            cur = parts[1]
            mats[cur] = {'Kd': (0.7, 0.7, 0.7), 'Ka': (0.2, 0.2, 0.2),
                         'Ks': (0.05, 0.05, 0.05), 'Ns': 10.0}
        elif cur:
            if parts[0] == 'Kd':
                mats[cur]['Kd'] = tuple(float(x) for x in parts[1:4])
            elif parts[0] == 'Ka':
                mats[cur]['Ka'] = tuple(float(x) for x in parts[1:4])
            elif parts[0] == 'Ks':
                mats[cur]['Ks'] = tuple(float(x) for x in parts[1:4])
            elif parts[0] == 'Ns':
                mats[cur]['Ns'] = float(parts[1])
    return mats


def convert(obj_path, dae_path):
    obj_path = Path(obj_path)
    verts, norms = [], []
    groups = {}          # material -> list[ (vi, ni) x3 ]  (fan-triangulated)
    cur_mat = 'default'
    mtl_file = None

    for line in open(obj_path):
        parts = line.split()
        if not parts:
            continue
        c = parts[0]
        if c == 'mtllib':
            mtl_file = ' '.join(parts[1:])
        elif c == 'v':
            verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif c == 'vn':
            norms.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif c == 'usemtl':
            cur_mat = parts[1]
        elif c == 'f':
            refs = []
            for r in parts[1:]:
                fields = r.split('/')
                vi = int(fields[0])
                ni = int(fields[2]) if len(fields) > 2 and fields[2] else 0
                # negatif indeks destegi
                if vi < 0:
                    vi = len(verts) + 1 + vi
                refs.append((vi - 1, ni - 1))
            tris = groups.setdefault(cur_mat, [])
            for i in range(1, len(refs) - 1):   # fan triangulation
                tris.append((refs[0], refs[i], refs[i + 1]))

    mats = {}
    if mtl_file:
        mtl_path = obj_path.parent / mtl_file
        if mtl_path.exists():
            mats = parse_mtl(mtl_path)

    def fmt(t):
        return ' '.join(f'{x:.6g}' for x in t)

    out = []
    w = out.append
    w('<?xml version="1.0" encoding="utf-8"?>')
    w('<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">')
    w('  <asset>')
    w('    <contributor><authoring_tool>obj2dae.py</authoring_tool></contributor>')
    w('    <unit name="meter" meter="1"/>')
    w('    <up_axis>Z_UP</up_axis>')
    w('  </asset>')

    # ---- effects ----
    w('  <library_effects>')
    for m in groups:
        p = mats.get(m, {'Kd': (0.7, 0.7, 0.7), 'Ka': (0.2, 0.2, 0.2),
                         'Ks': (0.05, 0.05, 0.05), 'Ns': 10.0})
        w(f'    <effect id="{m}-effect">')
        w('      <profile_COMMON><technique sid="common"><phong>')
        w(f'        <ambient><color>{fmt(p["Ka"])} 1</color></ambient>')
        w(f'        <diffuse><color>{fmt(p["Kd"])} 1</color></diffuse>')
        w(f'        <specular><color>{fmt(p["Ks"])} 1</color></specular>')
        w(f'        <shininess><float>{p["Ns"]:.6g}</float></shininess>')
        w('      </phong></technique></profile_COMMON>')
        w('    </effect>')
    w('  </library_effects>')

    # ---- materials ----
    w('  <library_materials>')
    for m in groups:
        w(f'    <material id="{m}-material" name="{m}">'
          f'<instance_effect url="#{m}-effect"/></material>')
    w('  </library_materials>')

    # ---- geometries: material basina bir mesh ----
    w('  <library_geometries>')
    for m, tris in groups.items():
        vmap, nmap = {}, {}
        gv, gn = [], []
        p_ints = []
        for tri in tris:
            for vi, ni in tri:
                if vi not in vmap:
                    vmap[vi] = len(gv)
                    gv.append(verts[vi])
                if ni >= 0 and ni not in nmap:
                    nmap[ni] = len(gn)
                    gn.append(norms[ni])
                p_ints.append(vmap[vi])
                p_ints.append(nmap[ni] if ni >= 0 else 0)
        if not gn:
            gn = [(0.0, 0.0, 1.0)]

        vflat = ' '.join(f'{c:.6f}' for v in gv for c in v)
        nflat = ' '.join(f'{c:.6f}' for n in gn for c in n)
        pflat = ' '.join(map(str, p_ints))

        w(f'    <geometry id="{m}-geom" name="{m}-geom">')
        w('      <mesh>')
        w(f'        <source id="{m}-pos">')
        w(f'          <float_array id="{m}-pos-array" count="{len(gv)*3}">{vflat}</float_array>')
        w('          <technique_common>')
        w(f'            <accessor source="#{m}-pos-array" count="{len(gv)}" stride="3">')
        w('              <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>')
        w('            </accessor>')
        w('          </technique_common>')
        w('        </source>')
        w(f'        <source id="{m}-norm">')
        w(f'          <float_array id="{m}-norm-array" count="{len(gn)*3}">{nflat}</float_array>')
        w('          <technique_common>')
        w(f'            <accessor source="#{m}-norm-array" count="{len(gn)}" stride="3">')
        w('              <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>')
        w('            </accessor>')
        w('          </technique_common>')
        w('        </source>')
        w(f'        <vertices id="{m}-verts"><input semantic="POSITION" source="#{m}-pos"/></vertices>')
        w(f'        <triangles material="{m}-sym" count="{len(tris)}">')
        w(f'          <input semantic="VERTEX" source="#{m}-verts" offset="0"/>')
        w(f'          <input semantic="NORMAL" source="#{m}-norm" offset="1"/>')
        w(f'          <p>{pflat}</p>')
        w('        </triangles>')
        w('      </mesh>')
        w('    </geometry>')
    w('  </library_geometries>')

    # ---- scene ----
    w('  <library_visual_scenes>')
    w('    <visual_scene id="Scene" name="Scene">')
    for m in groups:
        w(f'      <node id="{m}-node" name="{m}-node">')
        w(f'        <instance_geometry url="#{m}-geom">')
        w('          <bind_material><technique_common>')
        w(f'            <instance_material symbol="{m}-sym" target="#{m}-material"/>')
        w('          </technique_common></bind_material>')
        w('        </instance_geometry>')
        w('      </node>')
    w('    </visual_scene>')
    w('  </library_visual_scenes>')
    w('  <scene><instance_visual_scene url="#Scene"/></scene>')
    w('</COLLADA>')

    Path(dae_path).write_text('\n'.join(out))
    print("Done")

if __name__ == '__main__':
    convert("src/rover_parkur/meshes/parkur_yeni/tabelalar_renkli.obj", "src/rover_parkur/meshes/parkur_yeni/tabelalar_renkli.dae")
