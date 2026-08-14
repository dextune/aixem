# Grid Controller and Sensor Interface

This directory is a complete, vendor-neutral AIXEM schematic example. It separates semantic connectivity, component libraries, symbol graphics, explicit layout, project locks, rendered output, and validation evidence.

## Build

```bash
python implementation/schematic/render_project.py \
  examples/electronics-grid-controller/project.aixproj.json
```

The renderer validates the project and writes an engineering workbench, a standalone SVG, a resolved scene, a render manifest, and machine-readable evidence.
