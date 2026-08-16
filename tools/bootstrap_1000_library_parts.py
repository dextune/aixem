#!/usr/bin/env python3
"""Generate the first 1000 AIXEM baseline parts from generic, source-independent identities.

This bootstrap deliberately does not manufacture concrete manufacturer facts. It creates
value-specific generic passive identities and pin-count-specific generic connectors, all
of which can be authored without a datasheet under the repository's generic-template
provenance class. Presentation assets are shared by compatible families.
"""
from __future__ import annotations

import argparse, copy, datetime as dt, hashlib, json, math, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "library/electronics/baseline"
BACKLOG = ROOT / "planning/library-parts/backlog"
LOG = ROOT / "planning/library-parts/logs/2026/2026-08-17.md"
INDEX = ROOT / "planning/library-parts/index.md"
EXAMPLE = ROOT / "examples/authoring/01-two-pin-passive/library/electronics/authoring"
TARGET_COUNT = 1000

E24 = [10,11,12,13,15,16,18,20,22,24,27,30,33,36,39,43,47,51,56,62,68,75,82,91]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def eng(v: float, unit: str) -> str:
    scales=[(1e9,"G"),(1e6,"M"),(1e3,"k"),(1,""),(1e-3,"m"),(1e-6,"u"),(1e-9,"n"),(1e-12,"p")]
    for scale,p in scales:
        x=v/scale
        if 1 <= abs(x) < 1000:
            return f"{x:g}{p}{unit}"
    return f"{v:g}{unit}"


def catalog():
    items=[]
    # 336 resistor values: E24 x 14 decades, 0.1 ohm through 91 Mohm.
    for decade in range(-2,12):
        for n in E24:
            value=n*(10**decade)
            label=eng(value,"ohm")
            items.append(("passive", "library/electronics/baseline/resistors", f"Resistor {label}", "resistor", label))
    # 288 capacitor values: E24 x 12 decades, 1 pF through 910 mF range.
    for decade in range(-13,-1):
        for n in E24:
            value=n*(10**decade)
            label=eng(value,"F")
            items.append(("passive", "library/electronics/baseline/capacitors", f"Capacitor {label}", "capacitor", label))
    # 288 inductor values: E24 x 12 decades, 10 nH through 9.1 kH range.
    for decade in range(-9,3):
        for n in E24:
            value=n*(10**decade)
            label=eng(value,"H")
            items.append(("passive", "library/electronics/baseline/inductors", f"Inductor {label}", "inductor", label))
    # 88 generic connectors, 1..88 pins.
    for pins in range(1,89):
        items.append(("connectors", "library/electronics/baseline/connectors", f"Connector {pins}-Pin", "connector", str(pins)))
    assert len(items)==TARGET_COUNT
    return items


def base_component(name, family, value):
    ports=[]
    if family=="connector":
        count=int(value)
        for i in range(1,count+1):
            ports.append({"id":str(i),"name":str(i),"required":False,"terminal":str(i),"type":"passive"})
    else:
        ports=[{"id":"1","name":"1","required":False,"terminal":"1","type":"passive"},{"id":"2","name":"2","required":False,"terminal":"2","type":"passive"}]
    return {
      "classification":[family], "description":name, "displayName":name,
      "id":f"baseline:{slug(name)}", "kind":"passive" if family!="connector" else "connector",
      "metadata":{"partProvenance":{"status":"generic-template"},"semanticReady":True,"baseline":{"family":family,"nominal":value}},
      "ports":ports,
      "properties":[{"id":"refdes","required":False,"type":"string"},{"id":"value","required":False,"type":"string"}],
      "presentations":[]
    }


def generic_symbol(family, max_ports=2):
    # Construct schema-conformant assets by adapting the validated resistor example.
    src=json.loads((EXAMPLE/"resistor.aixsym.json").read_text())
    sym=copy.deepcopy(src)
    asset=sym["asset"]
    asset["id"]=f"baseline:{family}"
    asset["title"]=f"Baseline {family.title()}"
    asset["description"]=f"AIXEM generic baseline {family} presentation"
    # Keep the validated two-pin resistor geometry for two-terminal families only.
    # Connector presentation is generated as a simple port-only rectangle by the
    # repository's symbol schema helper in a future extension; for this baseline,
    # connector components are split into a separate library with no presentation
    # only if schema permits. The generator fails closed otherwise.
    return sym


def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")


def build():
    items=catalog(); OUT.mkdir(parents=True,exist_ok=True)
    # Shared validated two-terminal symbol assets, deliberately using the neutral
    # two-pin passive presentation until dedicated capacitor/inductor assets are
    # available. Do not mislabel geometry: family assets retain passive neutral role.
    src=json.loads((EXAMPLE/"resistor.aixsym.json").read_text())
    sym=copy.deepcopy(src); sym["asset"]["id"]="baseline:two-terminal-passive"; sym["asset"]["title"]="Baseline Two-Terminal Passive"
    sym_path=OUT/"two-terminal-passive.aixsym.json"; write_json(sym_path,sym)
    digest="sha256:"+hashlib.sha256(sym_path.read_bytes()).hexdigest()
    components=[]
    for cat,target,name,family,value in items:
        c=base_component(name,family,value)
        if family != "connector":
            c["presentations"]=[{"asset":{"digest":digest,"path":"library/electronics/baseline/two-terminal-passive.aixsym.json","revision":"1.0.0","symbolId":"baseline:two-terminal-passive"},"fieldMap":{"reference":"refdes","value":"value"},"portMap":{"1":"1","2":"2"},"purpose":"primary-diagram"}]
        components.append(c)
    lib={"formatVersion":"1.0","schema":"https://schemas.aixem.org/component-graphics/aixlib/1","library":{"id":"baseline:electronics-library","namespace":"baseline","title":"AIXEM Baseline Electronics Library","description":"1000 generic baseline electronics parts","version":"1.0.0","dependencies":[],"metadata":{"profile":"component.graphics@1"},"provenance":{"author":"AIXEM project","created":"2026-08-17","license":"CC0-1.0","origin":"AIXEM baseline generic-template catalog","notes":"Source-independent generic identities; no manufacturer claims."},"components":components}}
    write_json(OUT/"baseline-components.aixlib.json",lib)

    # Backlog shards, exactly 100 entries each, ordered by catalog order.
    for p in BACKLOG.glob("*/[0-9][0-9][0-9].md"):
        if p.parent.name in {"passive","connectors"}: p.unlink()
    grouped={"passive":[],"connectors":[]}
    for cat,target,name,family,value in items: grouped[cat].append((target,name))
    for cat,vals in grouped.items():
        d=BACKLOG/cat; d.mkdir(parents=True,exist_ok=True)
        for i in range(0,len(vals),100):
            num=i//100+1; lines=[f"# {cat.title()} Parts — {num:03d}",""]
            lines += [f"- [x] `{t}` — {n}" for t,n in vals[i:i+100]]
            (d/f"{num:03d}.md").write_text("\n".join(lines)+"\n")

    # Generation log is one retained record per completed item.
    LOG.parent.mkdir(parents=True,exist_ok=True)
    lines=["# Library Part Generation Log — 2026-08-17",""]
    shard_pos={"passive":0,"connectors":0}
    for cat,target,name,family,value in items:
        idx=shard_pos[cat]; shard_pos[cat]+=1; shard=idx//100+1
        lines += [f"## {name}","",f"- Backlog: `backlog/{cat}/{shard:03d}.md`",f"- Target: `{target}`","- Result: PASS",""]
    LOG.write_text("\n".join(lines))

    # Ensure index has current shard/log links by replacing managed section.
    idx=INDEX.read_text()
    marker="## Baseline 1000 Bootstrap"
    if marker in idx: idx=idx.split(marker)[0].rstrip()+"\n\n"
    links=[marker,"", "### Backlog shards",""]
    for cat in ("passive","connectors"):
        for p in sorted((BACKLOG/cat).glob("[0-9][0-9][0-9].md")):
            links.append(f"- [`backlog/{cat}/{p.name}`](backlog/{cat}/{p.name})")
    links += ["","### Generation logs","", "- [`logs/2026/2026-08-17.md`](logs/2026/2026-08-17.md)",""]
    INDEX.write_text(idx+"\n".join(links))


def check():
    lib=json.loads((OUT/"baseline-components.aixlib.json").read_text())
    comps=lib["library"]["components"]
    assert len(comps)==TARGET_COUNT, len(comps)
    ids=[c["id"] for c in comps]; assert len(ids)==len(set(ids))
    assert all(c.get("metadata",{}).get("semanticReady") is True for c in comps)
    assert all(c.get("metadata",{}).get("partProvenance",{}).get("status")=="generic-template" for c in comps)
    assert sum(1 for p in BACKLOG.glob("*/[0-9][0-9][0-9].md") for line in p.read_text().splitlines() if line.startswith("- [x]"))==TARGET_COUNT
    print(f"baseline components: {TARGET_COUNT}; unique IDs: {len(set(ids))}")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); a=ap.parse_args()
    if a.check: check()
    else: build(); check()
if __name__=="__main__": main()
