"""
Lightweight NDJSON manifest validator for embedding/training manifests.

Usage (example):
  D:/Projects/impressioncore/.venv310/Scripts/python.exe src/dev_tools/manifest_validator.py \
    --manifest src/memlog/dataset_to_embedding_training_manifest.ndjson \
    --output-report src/memlog/validator_report.json \
    --validated-out src/memlog/dataset_to_embedding_training_manifest.validated.ndjson

The validator performs safe, low-memory checks (os.path.exists, numpy.load with mmap_mode='r', shape/dtype checks)
and writes a JSON report and an optionally filtered NDJSON containing only passing records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from typing import Any

try:
    import jsonschema
except Exception:
    jsonschema = None

try:
    import numpy as np
except Exception:
    np = None  # We'll error later if numpy is required


def sha1_for_file(path: str, max_bytes: int | None = None) -> str:
    h = hashlib.sha1()
    read_bytes = 0
    with open(path, "rb") as f:
        while True:
            if max_bytes is not None:
                to_read = min(65536, max_bytes - read_bytes)
                if to_read <= 0:
                    break
            else:
                to_read = 65536
            chunk = f.read(to_read)
            if not chunk:
                break
            h.update(chunk)
            read_bytes += len(chunk)
    return h.hexdigest()


def safe_numpy_probe(path: str) -> tuple[tuple[int, ...] | None, str | None, str | None]:
    """Try to mmap-open a numpy .npy file and return (shape, dtype, error)
    Returns (shape_tuple or None, dtype_str or None, error_message or None)
    """
    if np is None:
        return None, None, "numpy not available"
    try:
        arr = np.load(path, mmap_mode="r")
    except Exception as e:
        return None, None, f"numpy.load error: {e}"
    try:
        shape = tuple(arr.shape)
        dtype = str(arr.dtype)
        return shape, dtype, None
    except Exception as e:
        return None, None, f"probe error: {e}"


def validate_record(rec: dict[str, Any], workspace_root: str, checksum_max_bytes: int) -> tuple[list[str], list[str]]:
    """Validate a single manifest record. Returns (warnings, errors)"""
    warnings: list[str] = []
    errors: list[str] = []

    # common path keys
    path_keys = ["path", "filepath", "file_path", "file", "dataset"]
    file_path = None
    for k in path_keys:
        if k in rec:
            file_path = rec[k]
            break
    if not file_path:
        errors.append("missing required file path (keys: path/filepath/file_path)")
        return warnings, errors

    # Resolve relative to workspace if not absolute
    if not os.path.isabs(file_path):
        file_path = os.path.join(workspace_root, file_path)

    if not os.path.exists(file_path):
        errors.append(f"file does not exist: {file_path}")
        return warnings, errors

    # optional expected dtype/dim/rows
    expected_dtype = rec.get("dtype") or rec.get("type")
    expected_dim = None
    if "dim" in rec:
        expected_dim = int(rec["dim"])
    elif "shape" in rec:
        # accept shape list or tuple
        try:
            shape = rec["shape"]
            if isinstance(shape, list | tuple) and len(shape) >= 1:
                expected_dim = int(shape[-1])
        except Exception:
            pass

    # probe only for .npy/.npz files to avoid loading text/audio/etc
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    shape = None
    dtype = None
    if ext in (".npy", ".npz"):
        shape, dtype, err = safe_numpy_probe(file_path)
        if err:
            errors.append(err)
            return warnings, errors
    else:
        # Non-numpy files are allowed; warn that we cannot validate shape/dtype
        warnings.append(f"non-numpy file extension '{ext}': skipping shape/dtype probe")

    # dtype check
    if expected_dtype and dtype:
        # normalize strings
        if expected_dtype.lower() not in str(dtype).lower():
            warnings.append(f"dtype mismatch: file={dtype} manifest={expected_dtype}")

    # dimensionality check (only for probed numpy files)
    if expected_dim is not None and shape is not None:
        # interpret shape: if 1D, dim == shape[0]; if 2D, dim == shape[1]
        file_dim = None
        if len(shape) == 1:
            file_dim = shape[0]
        elif len(shape) >= 2:
            file_dim = shape[1]
        if file_dim is not None and int(file_dim) != int(expected_dim):
            errors.append(f"dimension mismatch: file_dim={file_dim} manifest_dim={expected_dim}")

    # row/range checks
    rows_key = None
    for k in ("rows", "row_count", "nrows", "rows_count"):
        if k in rec:
            rows_key = k
            break
    if rows_key and shape is not None:
        try:
            nrows = int(rec[rows_key])
            if len(shape) >= 1 and int(shape[0]) < nrows:
                errors.append(f"rows out of bounds: file_rows={shape[0]} manifest_rows={nrows}")
        except Exception:
            warnings.append(f"invalid rows value for key {rows_key}")

    # checksum validation (only if present)
    if "checksum" in rec and rec.get("checksum"):
        ch = rec.get("checksum")
        try:
            fsize = os.path.getsize(file_path)
            if fsize <= checksum_max_bytes:
                got = sha1_for_file(file_path)
                if got != ch:
                    errors.append("checksum mismatch")
            else:
                warnings.append(f"file too large for full checksum check ({fsize} bytes), skipped")
        except Exception as e:
            warnings.append(f"checksum check failed: {e}")

    return warnings, errors


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate an NDJSON manifest for embeddings/training")
    p.add_argument("--manifest", required=True, help="Path to NDJSON manifest")
    p.add_argument("--output-report", default="src/memlog/validator_report.json", help="JSON report output path")
    p.add_argument("--validated-out", default=None, help="If set, write passing records to this NDJSON file")
    p.add_argument("--schema", default="src/dev_tools/manifest_schema.json", help="Optional JSON Schema to validate against")
    p.add_argument("--checksum-max-bytes", type=int, default=50 * 1024 * 1024, help="Max file size for full checksum check (bytes)")
    p.add_argument("--workspace-root", default=os.getcwd(), help="Workspace root to resolve relative paths")
    args = p.parse_args(argv)

    manifest = args.manifest
    report: dict[str, Any] = {
        "manifest": manifest,
        "validated_out": args.validated_out,
        "counts": {"total": 0, "passed": 0, "warn": 0, "failed": 0},
        "errors": [],
        "warnings": [],
        "sample_failures": [],
    }

    if not os.path.exists(manifest):
        print(f"Manifest not found: {manifest}")
        report["errors"].append({"fatal": True, "message": f"manifest not found: {manifest}"})
        with open(args.output_report, "w", encoding="utf-8") as of:
            json.dump(report, of, indent=2)
        return 2

    schema = None
    if args.schema and os.path.exists(args.schema):
        try:
            with open(args.schema, encoding="utf-8") as sf:
                schema = json.load(sf)
        except Exception as e:
            print(f"Failed to load schema {args.schema}: {e}")
            schema = None
    elif args.schema and not os.path.exists(args.schema):
        print(f"Schema file not found: {args.schema} (continuing without schema)")

    validated_fp = None
    if args.validated_out:
        validated_fp = open(args.validated_out, "w", encoding="utf-8")

    with open(manifest, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            report["counts"]["total"] += 1
            try:
                rec = json.loads(line)
            except Exception as e:
                report["counts"]["failed"] += 1
                msg = {"line": i, "error": f"invalid json: {e}", "raw": line[:200]}
                report["errors"].append(msg)
                report["sample_failures"].append(msg)
                continue

            # schema validation if available
            if schema is not None and jsonschema is not None:
                try:
                    jsonschema.validate(instance=rec, schema=schema)
                except Exception as e:
                    report["counts"]["failed"] += 1
                    msg = {"line": i, "error": f"schema validation error: {e}", "record_sample": {k: rec.get(k) for k in ("path", "dataset") if k in rec}}
                    report["errors"].append(msg)
                    if len(report["sample_failures"]) < 20:
                        report["sample_failures"].append(msg)
                    continue
            elif schema is not None and jsonschema is None:
                # warn that schema exists but jsonschema is not installed
                report["warnings"].append({"line": i, "warning": "schema present but 'jsonschema' package not installed; skipping schema validation"})

            warnings, errors = validate_record(rec, args.workspace_root, args.checksum_max_bytes)
            if warnings:
                report["counts"]["warn"] += len(warnings)
                for w in warnings:
                    report["warnings"].append({"line": i, "warning": w})
            if errors:
                report["counts"]["failed"] += 1
                msg = {"line": i, "errors": errors, "record_sample": {k: rec.get(k) for k in ("path", "dataset", "dataset_id") if k in rec}}
                report["errors"].append(msg)
                if len(report["sample_failures"]) < 20:
                    report["sample_failures"].append(msg)
                continue

            # passed
            report["counts"]["passed"] += 1
            if validated_fp:
                validated_fp.write(json.dumps(rec) + "\n")

    if validated_fp:
        validated_fp.close()

    # write report
    os.makedirs(os.path.dirname(args.output_report) or ".", exist_ok=True)
    with open(args.output_report, "w", encoding="utf-8") as of:
        json.dump(report, of, indent=2)

    # print concise summary
    print("Validation summary:")
    print(json.dumps(report["counts"], indent=2))
    if report["counts"]["failed"] > 0:
        print(f"Errors: {len(report['errors'])} (report: {args.output_report})")
        return 3
    print(f"Warnings: {len(report['warnings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
