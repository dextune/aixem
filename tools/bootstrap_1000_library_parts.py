#!/usr/bin/env python3
"""Stage, verify, and close a deterministic 1000-part AIXEM generic baseline library."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "planning/library-parts"
BACKLOG = WORKSPACE / "backlog"
INDEX = WORKSPACE / "index.md"
LOG = WORKSPACE / "logs/2026/2026-08-17.md"
TEMPLATE = ROOT / "examples/authoring/01-two-pin-passive/library/electronics/authoring/resistor.aixsym.json"
TARGET_COUNT = 1000
DATE = "2026-08-17"
E24 = (10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91)


@dataclass(frozen=True)
class Part:
    category: str
    target: str
    family: str
    display_name: str
    value: str
    kind: str
    port_profile: str


@dataclass(frozen=True)
class Family:
    key: str
    category: str
    target: str
    kind: str
    port_profile: str
    values: tuple[str, ...]
    name_prefix: str


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def decimal_text(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def engineering(value: Decimal, unit: str) -> str:
    scales = (
        (Decimal("1e9"), "G"), (Decimal("1e6"), "M"), (Decimal("1e3"), "k"),
        (Decimal("1"), ""), (Decimal("1e-3"), "m"), (Decimal("1e-6"), "u"),
        (Decimal("1e-9"), "n"), (Decimal("1e-12"), "p"),
    )
    for scale, prefix in scales:
        scaled = value / scale
        if Decimal(1) <= abs(scaled) < Decimal(1000):
            return f"{decimal_text(scaled)}{prefix}{unit}"
    return f"{decimal_text(value)}{unit}"


def e24_values(start_exponent: int, count: int, unit: str) -> tuple[str, ...]:
    values: list[str] = []
    exponent = start_exponent
    while len(values) < count:
        for base in E24:
            values.append(engineering(Decimal(base) * (Decimal(10) ** exponent), unit))
            if len(values) == count:
                break
        exponent += 1
    if len(values) != len(set(values)):
        raise AssertionError(f"duplicate generated {unit} values")
    return tuple(values)


def families() -> tuple[Family, ...]:
    zener_values = (
        "2.4V","2.7V","3.0V","3.3V","3.6V","3.9V","4.3V","4.7V","5.1V","5.6V",
        "6.2V","6.8V","7.5V","8.2V","9.1V","10V","11V","12V","13V","15V",
        "16V","18V","20V","22V","24V","27V","30V","33V","36V","39V",
        "43V","47V","51V","56V","62V","68V","75V","82V","91V","100V",
        "110V","120V","130V","150V","160V","180V","200V","220V","240V","270V",
    )
    rectifier_values = tuple(
        f"{voltage}V {current}A"
        for voltage in (50,100,200,400,600,800,1000,1200)
        for current in ("0.5","1","1.5","2","3","4","5","6","8","10")
    )
    mos_values = tuple(
        f"{voltage}V {current}A"
        for voltage in (20,30,40,50,60,80,100,120,150,200)
        for current in (1,5,10)
    )
    switch_values = tuple(
        f"{current}A {voltage}V"
        for voltage in (5,12,24,48,120)
        for current in ("0.1","0.25","0.5","1","2","3")
    )
    return (
        Family("resistor","passive","library/electronics/passive/resistor","passive","two",e24_values(-2,250,"ohm"),"Resistor"),
        Family("capacitor","passive","library/electronics/passive/capacitor","passive","two",e24_values(-13,200,"F"),"Capacitor"),
        Family("inductor","passive","library/electronics/passive/inductor","passive","two",e24_values(-8,100,"H"),"Inductor"),
        Family("fuse","passive","library/electronics/protection/fuse","passive","two",tuple(f"{i/10:g}A" for i in range(1,51)),"Fuse"),
        Family("thermistor-ntc","passive","library/electronics/passive/thermistor","passive","two",tuple(f"{value}@25C" for value in e24_values(1,50,"ohm")),"NTC Thermistor"),
        Family("varistor","passive","library/electronics/protection/varistor","passive","two",tuple(f"{18 + 3*i}V" for i in range(30)),"MOV Varistor"),
        Family("rectifier-diode","diodes","library/electronics/diode/rectifier","diode","diode",rectifier_values,"Rectifier Diode"),
        Family("zener-diode","diodes","library/electronics/diode/zener","diode","diode",zener_values,"Zener Diode"),
        Family("led","diodes","library/electronics/diode/led","diode","diode",tuple(f"{400 + 10*i}nm" for i in range(40)),"LED"),
        Family("bjt-npn","transistors","library/electronics/transistor/bjt/npn","transistor","bjt",tuple(f"hFE-{20 + 10*i}" for i in range(30)),"NPN BJT"),
        Family("bjt-pnp","transistors","library/electronics/transistor/bjt/pnp","transistor","bjt",tuple(f"hFE-{20 + 10*i}" for i in range(30)),"PNP BJT"),
        Family("mosfet-n-channel","transistors","library/electronics/transistor/mosfet/n-channel","transistor","mosfet",mos_values,"N-Channel MOSFET"),
        Family("mosfet-p-channel","transistors","library/electronics/transistor/mosfet/p-channel","transistor","mosfet",mos_values,"P-Channel MOSFET"),
        Family("spst-switch","electromechanical","library/electronics/electromechanical/switch/spst","switch","two",switch_values,"SPST Switch"),
    )


def catalog() -> tuple[Part, ...]:
    result: list[Part] = []
    for family in families():
        for value in family.values:
            result.append(Part(family.category, family.target, family.key, f"{family.name_prefix} {value}", value, family.kind, family.port_profile))
    if len(result) != TARGET_COUNT:
        raise AssertionError(f"catalog count {len(result)} != {TARGET_COUNT}")
    names = [item.display_name.casefold() for item in result]
    if len(names) != len(set(names)):
        raise AssertionError("catalog display names are not unique")
    return tuple(result)


def pin_semantics(tag: str, polarity: str = "unspecified") -> dict:
    return {"profile":"aixem-pin-semantics-1","signalClass":"analog","functionalTags":[tag],"polarity":polarity,"capabilities":[]}


def component_ports(profile: str) -> tuple[list[dict], dict[str, str]]:
    if profile == "diode":
        return ([
            {"id":"a","name":"Anode","terminal":"a","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("anode","positive")}},
            {"id":"k","name":"Cathode","terminal":"k","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("cathode","negative")}},
        ], {"a":"1","k":"2"})
    if profile == "bjt":
        return ([
            {"id":"c","name":"Collector","terminal":"c","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("collector")}},
            {"id":"b","name":"Base","terminal":"b","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("base")}},
            {"id":"e","name":"Emitter","terminal":"e","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("emitter")}},
        ], {"c":"1","b":"2","e":"3"})
    if profile == "mosfet":
        return ([
            {"id":"d","name":"Drain","terminal":"d","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("drain")}},
            {"id":"g","name":"Gate","terminal":"g","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("gate")}},
            {"id":"s","name":"Source","terminal":"s","required":False,"type":"passive","metadata":{"pinSemantics":pin_semantics("source")}},
        ], {"d":"1","g":"2","s":"3"})
    return ([
        {"id":"1","name":"1","terminal":"1","required":False,"type":"passive"},
        {"id":"2","name":"2","terminal":"2","required":False,"type":"passive"},
    ], {"1":"1","2":"2"})


def line(identifier: str, x1: float, y1: float, x2: float, y2: float, *, role: str = "detail", style: str = "line", metadata: dict | None = None) -> dict:
    result = {"id":identifier,"layer":"body","role":role,"style":style,"type":"line","x1":x1,"y1":y1,"x2":x2,"y2":y2}
    if metadata:
        result["metadata"] = metadata
    return result


def rect(identifier: str, x: float, y: float, width: float, height: float) -> dict:
    return {"id":identifier,"layer":"body","role":"body","style":"body","type":"rect","x":x,"y":y,"width":width,"height":height}


def fields() -> list[dict]:
    return [
        {"anchor":"middle","baseline":"middle","field":"reference","id":"field-reference","layer":"fields","role":"reference-field","style":"field","type":"text","x":0,"y":-10},
        {"anchor":"middle","baseline":"middle","field":"value","id":"field-value","layer":"fields","role":"value-field","style":"value","type":"text","x":0,"y":10},
    ]


def two_terminal_graphics(key: str) -> list[dict]:
    graphics = [
        line("lead-1",-15,0,-10,0,role="pin-lead",metadata={"port":"1","portEndpoint":"start"}),
        line("lead-2",10,0,15,0,role="pin-lead",metadata={"port":"2","portEndpoint":"end"}),
    ]
    if key == "resistor":
        graphics += [rect("body",-10,-3.75,20,7.5)]
    elif key == "capacitor":
        graphics += [line("inner-1",-10,0,-2.5,0),line("plate-1",-2.5,-6,-2.5,6),line("plate-2",2.5,-6,2.5,6),line("inner-2",2.5,0,10,0)]
    elif key == "inductor":
        points = [(-10,0),(-8,-4),(-6,4),(-4,-4),(-2,4),(0,-4),(2,4),(4,-4),(6,4),(8,-4),(10,0)]
        graphics += [line(f"coil-{i}",*points[i],*points[i+1]) for i in range(len(points)-1)]
    elif key == "fuse":
        graphics += [rect("fuse-body",-8,-2.5,16,5),line("inner-1",-10,0,-8,0),line("inner-2",8,0,10,0)]
    elif key == "thermistor-ntc":
        graphics += [rect("body",-10,-3.75,20,7.5),line("temperature-slash",-7,6,7,-6,style="detail")]
    elif key == "varistor":
        graphics += [rect("body",-10,-3.75,20,7.5),line("varistor-slash",-7,6,7,-6,style="detail"),line("varistor-mark",-4,6,10,-6,style="detail")]
    elif key in {"rectifier-diode","zener-diode","led"}:
        graphics += [line("diode-top",-6,-6,4,0),line("diode-bottom",-6,6,4,0),line("diode-back",-6,-6,-6,6),line("diode-in",-10,0,-6,0),line("diode-out",4,0,6,0)]
        if key == "zener-diode":
            graphics += [line("cathode-main",6,-5,6,5),line("cathode-top",6,-5,9,-7),line("cathode-bottom",6,5,3,7),line("to-lead",6,0,10,0)]
        else:
            graphics += [line("cathode",6,-6,6,6),line("to-lead",6,0,10,0)]
        if key == "led":
            graphics += [line("light-1",0,-7,5,-12,style="detail"),line("light-1-tip-a",5,-12,3.5,-11.5,style="detail"),line("light-1-tip-b",5,-12,4.5,-10.5,style="detail"),line("light-2",4,-5,9,-10,style="detail"),line("light-2-tip-a",9,-10,7.5,-9.5,style="detail"),line("light-2-tip-b",9,-10,8.5,-8.5,style="detail")]
    elif key == "spst-switch":
        graphics += [line("contact-left",-10,0,-6,0),line("contact-right",6,0,10,0),line("blade",-6,0,5,-5),line("stationary",6,-2,6,2,style="detail")]
    else:
        raise ValueError(f"unknown two-terminal symbol family {key}")
    return graphics + fields()


def three_terminal_graphics(key: str) -> list[dict]:
    graphics = [
        line("lead-1",5,-5,15,-5,role="pin-lead",metadata={"port":"1","portEndpoint":"end"}),
        line("lead-2",-15,0,-5,0,role="pin-lead",metadata={"port":"2","portEndpoint":"start"}),
        line("lead-3",5,5,15,5,role="pin-lead",metadata={"port":"3","portEndpoint":"end"}),
    ]
    if key in {"bjt-npn","bjt-pnp"}:
        graphics += [line("base",-5,-6,-5,6),line("collector",-5,-3,5,-5),line("emitter",-5,3,5,5)]
        if key == "bjt-npn":
            graphics += [line("arrow-a",4.5,5,1.5,2.5,style="detail"),line("arrow-b",4.5,5,1.0,5.5,style="detail")]
        else:
            graphics += [line("arrow-a",-1,3.8,2.3,2.2,style="detail"),line("arrow-b",-1,3.8,0.5,6.8,style="detail")]
    elif key in {"mosfet-n-channel","mosfet-p-channel"}:
        graphics += [line("gate",-5,-6,-5,6),line("channel",-1,-5,-1,5),line("drain-inner",-1,-5,5,-5),line("source-inner",-1,5,5,5)]
        if key == "mosfet-n-channel":
            graphics += [line("arrow-a",-0.5,0,2.5,0,style="detail"),line("arrow-b",2.5,0,0.8,-1.3,style="detail"),line("arrow-c",2.5,0,0.8,1.3,style="detail")]
        else:
            graphics += [line("arrow-a",2.5,0,-0.5,0,style="detail"),line("arrow-b",-0.5,0,1.2,-1.3,style="detail"),line("arrow-c",-0.5,0,1.2,1.3,style="detail")]
    else:
        raise ValueError(f"unknown three-terminal symbol family {key}")
    return graphics + fields()


def make_symbol(family: Family) -> dict:
    doc = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    symbol = doc["symbol"]
    symbol["id"] = f"baseline:{family.key}"
    symbol["title"] = f"Baseline {family.name_prefix}"
    symbol["description"] = f"AIXEM generic baseline {family.name_prefix} schematic symbol."
    symbol["metadata"] = {"recipe":f"baseline-{family.key}"}
    symbol["provenance"] = {"author":"AIXEM project","created":DATE,"license":"CC0-1.0","notes":f"Generic baseline {family.name_prefix} presentation.","origin":"AIXEM generic baseline bootstrap"}
    symbol["parameters"] = {}
    symbol["bounds"] = {"x":-20,"y":-15,"width":40,"height":30}
    if family.port_profile in {"bjt","mosfet"}:
        symbol["graphics"] = three_terminal_graphics(family.key)
        symbol["ports"] = [
            {"id":"1","kind":"electrical","labelVisible":False,"name":"1","number":"1","numberVisible":False,"orientation":0,"snapRadius":1.25,"x":15,"y":-5},
            {"id":"2","kind":"electrical","labelVisible":False,"name":"2","number":"2","numberVisible":False,"orientation":180,"snapRadius":1.25,"x":-15,"y":0},
            {"id":"3","kind":"electrical","labelVisible":False,"name":"3","number":"3","numberVisible":False,"orientation":0,"snapRadius":1.25,"x":15,"y":5},
        ]
    else:
        symbol["graphics"] = two_terminal_graphics(family.key)
        symbol["ports"] = [
            {"id":"1","kind":"electrical","labelVisible":False,"name":"1","number":"1","numberVisible":False,"orientation":180,"snapRadius":1.25,"x":-15,"y":0},
            {"id":"2","kind":"electrical","labelVisible":False,"name":"2","number":"2","numberVisible":False,"orientation":0,"snapRadius":1.25,"x":15,"y":0},
        ]
    symbol["requiredFeatures"] = []
    return doc


def make_component(part: Part, symbol_rel: str, symbol_id: str, digest: str) -> dict:
    ports, port_map = component_ports(part.port_profile)
    return {
        "classification":[part.family],"description":f"Generic {part.display_name} baseline component.","displayName":part.display_name,"id":f"baseline:{slug(part.display_name)}","kind":part.kind,
        "metadata":{"partProvenance":{"status":"generic-template"},"semanticReady":True},
        "ports":ports,
        "presentations":[{"asset":{"digest":digest,"path":symbol_rel,"revision":"1.0.0","symbolId":symbol_id},"fieldMap":{"reference":"refdes","value":"value"},"portMap":port_map,"purpose":"primary-diagram"}],
        "properties":[{"id":"refdes","required":False,"type":"string"},{"id":"value","required":False,"type":"string","default":part.value}],
    }


def library_document(family: Family, components: list[dict]) -> dict:
    return {"formatVersion":"1.0","schema":"https://schemas.aixem.org/component-graphics/aixlib/1","library":{
        "id":f"baseline:{family.key}-library","namespace":"baseline","title":f"AIXEM Baseline {family.name_prefix} Library","description":f"Generic baseline {family.name_prefix} components.","version":"1.0.0","dependencies":[],"metadata":{"profile":"component.graphics@1"},
        "provenance":{"author":"AIXEM project","created":DATE,"license":"CC0-1.0","origin":"AIXEM generic baseline bootstrap","notes":"Source-independent generic-template identities; no manufacturer claims."},"components":components}}


def reset_managed_output() -> None:
    for family in families():
        target = ROOT / family.target
        if target.exists():
            shutil.rmtree(target)
    root_keep = ROOT / "library/electronics/.gitkeep"
    if root_keep.exists():
        root_keep.unlink()
    for category in ("passive","diodes","transistors","electromechanical"):
        folder = BACKLOG / category
        if folder.exists():
            for path in folder.glob("[0-9][0-9][0-9].md"):
                path.unlink()
    if LOG.exists():
        LOG.unlink()
        for folder in (LOG.parent, LOG.parent.parent):
            try:
                folder.rmdir()
            except OSError:
                pass


def write_production() -> None:
    grouped: dict[str,list[Part]] = {}
    for part in catalog():
        grouped.setdefault(part.family, []).append(part)
    for family in families():
        target = ROOT / family.target
        target.mkdir(parents=True, exist_ok=True)
        symbol_doc = make_symbol(family)
        symbol_path = target / f"{family.key}.aixsym.json"
        write_json(symbol_path, symbol_doc)
        digest = "sha256:" + hashlib.sha256(symbol_path.read_bytes()).hexdigest()
        symbol_rel = symbol_path.relative_to(ROOT).as_posix()
        symbol_id = symbol_doc["symbol"]["id"]
        components = [make_component(part,symbol_rel,symbol_id,digest) for part in grouped[family.key]]
        write_json(target / f"{family.key}-values.aixlib.json", library_document(family,components))


def shard_plan() -> dict[str,list[list[Part]]]:
    grouped: dict[str,list[Part]] = {}
    for part in catalog():
        grouped.setdefault(part.category, []).append(part)
    return {category:[items[i:i+100] for i in range(0,len(items),100)] for category,items in grouped.items()}


def write_shards(done: bool) -> None:
    mark = "x" if done else " "
    for category, shards in shard_plan().items():
        folder = BACKLOG / category
        folder.mkdir(parents=True, exist_ok=True)
        for number, items in enumerate(shards,1):
            lines = [f"# {category.title()} Parts - {number:03d}",""]
            lines += [f"- [{mark}] `{part.target}` — {part.display_name}" for part in items]
            (folder / f"{number:03d}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def index_text(closed: bool) -> str:
    active = shard_plan()
    order = (("Passive","passive"),("Diodes","diodes"),("Transistors","transistors"),("Analog","analog"),("Logic","logic"),("Connectors","connectors"),("Microcontrollers","microcontrollers"),("FPGA","fpga"),("Electromechanical","electromechanical"))
    lines = ["# Library Part Backlog Index","","This index is the discovery and priority owner for the operational library-part queue. See [README.md](README.md) for execution rules.","","## Backlog Shards","","Process shards in this listed order unless the caller explicitly narrows the category or shard.","","| Category | Shard |","|---|---|"]
    for label,category in order:
        if category in active:
            for number in range(1,len(active[category])+1):
                lines.append(f"| {label} | [{category}/{number:03d}.md](backlog/{category}/{number:03d}.md) |")
        else:
            lines.append(f"| {label} | [{category}/001.md](backlog/{category}/001.md) |")
    lines += ["","## Generation Logs",""]
    lines.append(f"- [`logs/2026/{DATE}.md`](logs/2026/{DATE}.md)" if closed else "No generation logs have been created yet. Add each real `logs/YYYY/YYYY-MM-DD.md` file here in the same change that creates it.")
    lines += ["","## Review Logs","","No review logs have been created yet. Add each real `reviews/YYYY/YYYY-MM-DD.md` file here in the same change that creates it.","","## Generated Reports","","No generated progress report is retained initially. Use `python tools/library_backlog.py progress` for the current derived summary.",""]
    return "\n".join(lines)


def backlog_locations() -> dict[tuple[str,str],str]:
    result: dict[tuple[str,str],str] = {}
    for category,shards in shard_plan().items():
        for number,items in enumerate(shards,1):
            for part in items:
                result[(part.target,part.display_name)] = f"backlog/{category}/{number:03d}.md"
    return result


def write_log() -> None:
    locations = backlog_locations()
    lines = [f"# Library Part Generation Log — {DATE}",""]
    for part in catalog():
        lines += [f"## {part.display_name}","",f"- Backlog: `{locations[(part.target,part.display_name)]}`",f"- Target: `{part.target}`","- Result: PASS",""]
    LOG.parent.mkdir(parents=True,exist_ok=True)
    LOG.write_text("\n".join(lines),encoding="utf-8")


def all_library_components() -> tuple[list[dict],list[Path]]:
    components: list[dict] = []
    libraries: list[Path] = []
    for path in sorted((ROOT/"library").rglob("*.aixlib.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        libraries.append(path)
        components += document["library"]["components"]
    return components,libraries


def expected_pairs() -> set[tuple[str,str]]:
    return {(part.target,part.display_name) for part in catalog()}


def parse_backlog_state() -> tuple[set[tuple[str,str]],int,int]:
    pairs: set[tuple[str,str]] = set()
    checked = unchecked = 0
    item_re = re.compile(r"^- \[(?P<state>[ x])\] `(?P<target>[^`]+)` — (?P<name>.+)$")
    for path in sorted(BACKLOG.rglob("[0-9][0-9][0-9].md")):
        for raw in path.read_text(encoding="utf-8").splitlines():
            match = item_re.fullmatch(raw)
            if not match:
                continue
            pairs.add((match.group("target"),match.group("name")))
            if match.group("state") == "x": checked += 1
            else: unchecked += 1
    return pairs,checked,unchecked


def verify_component_assets(components: list[dict]) -> None:
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for component in components:
        component_id = component["id"]
        name_key = component["displayName"].casefold()
        if component_id in seen_ids or name_key in seen_names:
            raise AssertionError(f"duplicate component identity {component_id}")
        seen_ids.add(component_id); seen_names.add(name_key)
        metadata = component.get("metadata",{})
        if metadata.get("semanticReady") is not True or metadata.get("partProvenance") != {"status":"generic-template"}:
            raise AssertionError(f"{component_id}: invalid generic-template semantic state")
        properties = {item["id"]:item for item in component.get("properties",[])}
        if not properties.get("value",{}).get("default"):
            raise AssertionError(f"{component_id}: missing semantic value default")
        presentations = component.get("presentations",[])
        if len(presentations) != 1:
            raise AssertionError(f"{component_id}: expected exactly one presentation")
        presentation = presentations[0]; asset = presentation["asset"]
        symbol_path = ROOT / asset["path"]
        if not symbol_path.is_file():
            raise AssertionError(f"{component_id}: missing symbol {asset['path']}")
        digest = "sha256:" + hashlib.sha256(symbol_path.read_bytes()).hexdigest()
        if asset["digest"] != digest:
            raise AssertionError(f"{component_id}: stale symbol digest")
        symbol = json.loads(symbol_path.read_text(encoding="utf-8"))["symbol"]
        if asset["symbolId"] != symbol["id"] or asset["revision"] != symbol["revision"]:
            raise AssertionError(f"{component_id}: symbol identity/revision mismatch")
        component_ports = {port["id"] for port in component["ports"]}; symbol_ports = {port["id"] for port in symbol["ports"]}; port_map = presentation["portMap"]
        if set(port_map) != component_ports or not set(port_map.values()).issubset(symbol_ports):
            raise AssertionError(f"{component_id}: incomplete presentation portMap")


def verify_log() -> int:
    return LOG.read_text(encoding="utf-8").count("- Result: PASS") if LOG.is_file() else 0


def verify(state: str) -> None:
    components,libraries = all_library_components()
    if len(components) != TARGET_COUNT: raise AssertionError(f"production component count {len(components)} != {TARGET_COUNT}")
    if len(libraries) != len(families()): raise AssertionError(f"library file count {len(libraries)} != {len(families())}")
    symbol_count = len(list((ROOT/"library").rglob("*.aixsym.json")))
    if symbol_count != len(families()): raise AssertionError(f"symbol file count {symbol_count} != {len(families())}")
    verify_component_assets(components)
    pairs,checked,unchecked = parse_backlog_state()
    if pairs != expected_pairs():
        raise AssertionError(f"backlog/catalog mismatch: {len(pairs)} items")
    pass_count = verify_log()
    if state == "staged":
        if checked != 0 or unchecked != TARGET_COUNT or pass_count != 0: raise AssertionError(f"staged state invalid checked={checked} unchecked={unchecked} pass={pass_count}")
    elif state == "closed":
        if checked != TARGET_COUNT or unchecked != 0 or pass_count != TARGET_COUNT: raise AssertionError(f"closed state invalid checked={checked} unchecked={unchecked} pass={pass_count}")
    else:
        raise ValueError(state)
    print(json.dumps({"state":state,"components":len(components),"libraries":len(libraries),"symbols":symbol_count,"backlogItems":len(pairs),"checked":checked,"generationPass":pass_count},sort_keys=True))


def stage() -> None:
    reset_managed_output(); write_production(); write_shards(False); INDEX.write_text(index_text(False),encoding="utf-8"); verify("staged")


def close() -> None:
    verify("staged"); write_log(); write_shards(True); INDEX.write_text(index_text(True),encoding="utf-8"); verify("closed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command",required=True); sub.add_parser("stage"); vp = sub.add_parser("verify"); vp.add_argument("--state",choices=("staged","closed"),required=True); sub.add_parser("close"); args = parser.parse_args()
    if args.command == "stage": stage()
    elif args.command == "verify": verify(args.state)
    else: close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
