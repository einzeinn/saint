"""Load a DataHub MCE JSON datapack without the metadata-file source parser."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from datahub.configuration.common import OperationalError
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.com.linkedin.pegasus2avro.mxe import MetadataChangeEvent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path, help="Path to a DataHub MCE JSON datapack")
    args = parser.parse_args()

    gms_url = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
    token = os.getenv("DATAHUB_GMS_TOKEN") or os.getenv("DATAHUB_TOKEN")
    if not token:
        raise SystemExit("Set DATAHUB_GMS_TOKEN or DATAHUB_TOKEN before loading the pack.")

    records = json.loads(args.pack.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("The datapack must contain a JSON list of MCE records.")

    emitter = DatahubRestEmitter(gms_server=gms_url, token=token)
    emitted = 0
    skipped = 0
    for index, record in enumerate(records):
        try:
            if "proposedSnapshot" in record:
                event = MetadataChangeEvent.from_obj(record)
                emitter.emit_mce(event)
            elif "aspect" in record:
                proposal = MetadataChangeProposalWrapper.from_obj(record)
                emitter.emit_mcp(proposal)
            else:
                raise ValueError("unknown DataHub event shape")
        except (TypeError, ValueError, KeyError) as exc:
            skipped += 1
            print(f"Skipped malformed record at index {index}: {exc}")
            continue
        except OperationalError as exc:
            # The server rejected this specific record (e.g. an aspect the
            # connected GMS version doesn't recognize, a transient network
            # error). Skip it and keep going instead of losing progress on
            # every remaining record in the file.
            skipped += 1
            print(f"Skipped record at index {index} rejected by server: {exc}")
            continue
        emitted += 1

    print(f"Loaded {emitted} metadata events into {gms_url}; skipped {skipped} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
