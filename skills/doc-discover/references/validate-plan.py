#!/usr/bin/env python3
"""
Validates docs/.doc-plan.json against the required schema.
Exit code 0 = valid, exit code 1 = errors found.
Zero external dependencies — uses only Python stdlib.

Usage: python3 validate-plan.py [path-to-plan.json]
  Default path: docs/.doc-plan.json
"""
import json
import sys
import os

WAVE_ASSIGNMENTS = {
    "doc-c4": 1,
    "doc-api": 2,
    "doc-data-discover": 2,
    "doc-events": 2,
    "doc-data-tables": 3,
    "doc-data-queries": 4,
    "doc-security": 5,
    "doc-devops": 5,
    "doc-testing": 5,
    "doc-data-overview": 5,
    "doc-adr": 6,
    "doc-quality": 6,
}

MAX_WAVE = 6
VALID_WAVES = set(range(1, MAX_WAVE + 1))

REQUIRED_TOP_KEYS = ["project_name", "language", "framework", "generated", "waves", "sections"]
REQUIRED_SECTION_KEYS = ["id", "title", "enabled", "wave", "output_files"]
FORBIDDEN_SECTION_KEYS = ["priority", "order", "rank"]


def validate(plan_path):
    errors = []

    # --- File exists and is valid JSON ---
    if not os.path.isfile(plan_path):
        print(f"FAIL: File not found: {plan_path}")
        return 1

    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON: {e}")
        return 1

    # --- Top-level keys ---
    for key in REQUIRED_TOP_KEYS:
        if key not in plan:
            errors.append(f"Missing top-level key: \"{key}\"")

    # --- Waves object ---
    waves = plan.get("waves")
    if waves is not None:
        if not isinstance(waves, dict):
            errors.append(f"\"waves\" must be an object, got {type(waves).__name__}")
        else:
            for wnum in range(1, MAX_WAVE + 1):
                wkey = str(wnum)
                if wkey not in waves:
                    errors.append(f"\"waves\" missing key \"{wkey}\"")
                elif not isinstance(waves[wkey], list):
                    errors.append(f"\"waves\".\"{wkey}\" must be an array")

    # --- Sections array ---
    sections = plan.get("sections")
    if sections is not None:
        if not isinstance(sections, list):
            errors.append(f"\"sections\" must be an array, got {type(sections).__name__}")
        else:
            seen_ids = set()
            for i, section in enumerate(sections):
                sid = section.get("id", f"<index {i}>")
                prefix = f"sections[{i}] (id={sid})"

                # Required keys
                for key in REQUIRED_SECTION_KEYS:
                    if key not in section:
                        errors.append(f"{prefix}: missing required key \"{key}\"")

                # Forbidden keys
                for key in FORBIDDEN_SECTION_KEYS:
                    if key in section:
                        errors.append(f"{prefix}: contains forbidden key \"{key}\" — rename to \"wave\"")

                # Wave value
                wave_val = section.get("wave")
                if wave_val is not None:
                    if not isinstance(wave_val, int) or wave_val not in VALID_WAVES:
                        errors.append(f"{prefix}: \"wave\" must be integer 1-{MAX_WAVE}, got {wave_val!r}")
                    elif sid in WAVE_ASSIGNMENTS and wave_val != WAVE_ASSIGNMENTS[sid]:
                        errors.append(
                            f"{prefix}: \"wave\" is {wave_val} but should be "
                            f"{WAVE_ASSIGNMENTS[sid]} for {sid}"
                        )

                # Enabled is boolean
                enabled = section.get("enabled")
                if enabled is not None and not isinstance(enabled, bool):
                    errors.append(f"{prefix}: \"enabled\" must be boolean, got {type(enabled).__name__}")

                # output_files is array
                of = section.get("output_files")
                if of is not None and not isinstance(of, list):
                    errors.append(f"{prefix}: \"output_files\" must be an array")

                # Track IDs
                if isinstance(sid, str):
                    seen_ids.add(sid)

            # --- Cross-check: enabled sections in waves ---
            if waves and isinstance(waves, dict):
                for section in sections:
                    sid = section.get("id")
                    enabled = section.get("enabled", False)
                    wave_val = section.get("wave")
                    if enabled and sid and wave_val:
                        wave_key = str(wave_val)
                        wave_list = waves.get(wave_key, [])
                        if sid not in wave_list:
                            errors.append(
                                f"Section \"{sid}\" is enabled with wave={wave_val} "
                                f"but not listed in waves.\"{wave_key}\""
                            )

    # --- Output ---
    if errors:
        print(f"FAIL: {len(errors)} error(s) found in {plan_path}:\n")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print(f"PASS: {plan_path} is valid")
        return 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "docs/.doc-plan.json"
    sys.exit(validate(path))
