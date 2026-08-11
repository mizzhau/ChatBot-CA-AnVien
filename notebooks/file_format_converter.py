import json
import csv
import io
from pathlib import Path


def read_records(path: str) -> list[dict]:
    p = Path(path)
    suffix = p.suffix.lower()

    with open(p, encoding="utf-8") as f:
        if suffix == ".jsonl":
            return [json.loads(line) for line in f if line.strip()]
        if suffix == ".json":
            data = json.load(f)
            return data if isinstance(data, list) else [data]
        if suffix == ".csv":
            return list(csv.DictReader(f))

    raise ValueError(f"Unsupported input format: {suffix}")


def to_json(records: list[dict]) -> str:
    return json.dumps(records, ensure_ascii=False, indent=2)


def to_jsonl(records: list[dict]) -> str:
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)


def to_csv(records: list[dict]) -> str:
    if not records:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue()


def to_markdown(records: list[dict]) -> str:
    if not records:
        return ""
    headers = list(records[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for r in records:
        row = [str(r.get(h, "")).replace("\n", " ") for h in headers]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


FORMATTERS = {
    "json": to_json,
    "jsonl": to_jsonl,
    "csv": to_csv,
    "markdown": to_markdown,
}


def convert_and_print(path: str, target_format: str) -> str:
    target_format = target_format.lower().lstrip(".")
    if target_format not in FORMATTERS:
        raise ValueError(f"target_format must be one of {list(FORMATTERS)}")

    records = read_records(path)
    output = FORMATTERS[target_format](records)
    print(output)
    return output


if __name__ == "__main__":
    sample_path = "/mnt/user-data/outputs/kb_chunks.jsonl"
    convert_and_print(sample_path, "json")
