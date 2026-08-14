#!/usr/bin/env python3
"""Parse canonical document metadata and print a deterministic summary."""
from __future__ import annotations
import json
from aixem_docs import load_documents

docs = load_documents()
print(json.dumps({
    "documents": len(docs),
    "normative": sum(d.meta.get("status") == "normative" for d in docs),
    "requirements": sum(len(d.requirements) for d in docs),
    "domains": sorted({str(d.meta.get("domain")) for d in docs}),
}, indent=2, sort_keys=True))
