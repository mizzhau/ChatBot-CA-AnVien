import io
import json
import re
import sys
from pathlib import Path


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
CHUNKS_DIR = REPO_ROOT / "data" / "chunks"
SOURCE_REGISTRY_PATH = CHUNKS_DIR / "id_source.json"
OUTPUT_PATH = CHUNKS_DIR / "source.jsonl"


RE_H1 = re.compile(r"^# (.+)$", re.MULTILINE)

RE_CHUONG = re.compile(
    r"^## Ch\u01b0\u01a1ng\s+([IVXLCDM\d]+)[:\.\s]+(.+)$", re.MULTILINE
)

RE_DIEU = re.compile(
    r"^### (?:Điều|Dieu)\s+(\d+[a-z]?)\.\s*(.*)$", re.MULTILINE
)

RE_SECTION = re.compile(r"^(#{2,3}) (.+)$", re.MULTILINE)

RE_PHUCLUC = re.compile(r"^# PHỤ LỤC", re.MULTILINE)

RE_TRAILING_ARTIFACT = re.compile(
    r"(\s*\n(---|\*\*\*)\s*)*\s*\n## .+$", re.DOTALL
)

PORTAL_CHAR_THRESHOLD = 3000


def load_source_registry(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"[ERROR] Source registry not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def clean_content(text: str) -> str:
    text = RE_TRAILING_ARTIFACT.sub("", text)
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def detect_content_type(content: str, source_id: str) -> str:
    portal_ids = {"SRC-C-03", "SRC-DVC-BCA", "SRC-F-04"}
    if source_id in portal_ids or len(content) <= PORTAL_CHAR_THRESHOLD:
        return "portal_reference"
    if RE_DIEU.search(content):
        return "law_article"
    return "guide_section"


def extract_doc_title(content: str, registry_title: str) -> str:
    agency_words = {"QUỐC HỘI", "CHÍNH PHỦ", "BỘ CÔNG AN", "BỘ TƯ PHÁP"}
    for m in RE_H1.finditer(content):
        title = m.group(1).strip()
        if title.upper() not in agency_words:
            return title
    return registry_title


def build_chuong_map(content: str) -> list:
    result = []
    for m in RE_CHUONG.finditer(content):
        result.append((m.start(), m.group(1).strip(), m.group(2).strip()))
    return result


def find_chuong_for_offset(chuong_map: list, offset: int):
    chuong = chuong_title = None
    for pos, num, title in chuong_map:
        if pos <= offset:
            chuong, chuong_title = num, title
        else:
            break
    return chuong, chuong_title


def split_appendix(content: str):
    m = RE_PHUCLUC.search(content)
    if m:
        return content[: m.start()].rstrip(), content[m.start():]
    return content, None


def chunk_law_article(content, source_id, source_title, source_url, doc_quality="text"):
    main_body, appendix_text = split_appendix(content)
    chuong_map = build_chuong_map(main_body)

    chunks = []
    dieu_matches = list(RE_DIEU.finditer(main_body))

    for idx, m in enumerate(dieu_matches):
        dieu_num = m.group(1).strip()
        dieu_title_text = m.group(2).strip()
        start = m.start()
        end = dieu_matches[idx + 1].start() if idx + 1 < len(dieu_matches) else len(main_body)

        chuong, chuong_title = find_chuong_for_offset(chuong_map, start)
        body = clean_content(main_body[start:end])

        if chuong:
            chunk_id = f"{source_id}_C{chuong}_D{dieu_num}"
        else:
            chunk_id = f"{source_id}_D{dieu_num}"

        chunks.append({
            "chunk_id": chunk_id,
            "source_id": source_id,
            "content_type": "law_article",
            "source_title": source_title,
            "chuong": chuong,
            "chuong_title": chuong_title,
            "dieu": dieu_num,
            "dieu_title": dieu_title_text if dieu_title_text else None,
            "section_title": None,
            "content": body,
            "source_url": source_url,
            "doc_quality": doc_quality,
        })

    if appendix_text:
        parts = re.split(r"(?=^# PHỤ LỤC)", appendix_text, flags=re.MULTILINE)
        for i, part in enumerate(parts):
            part = clean_content(part)
            if not part:
                continue
            title_m = RE_H1.match(part)
            section_t = title_m.group(1).strip() if title_m else f"PHỤ LỤC {i + 1}"
            chunks.append({
                "chunk_id": f"{source_id}_PHUCLUC{i + 1}",
                "source_id": source_id,
                "content_type": "appendix",
                "source_title": source_title,
                "chuong": None,
                "chuong_title": None,
                "dieu": None,
                "dieu_title": None,
                "section_title": section_t,
                "content": part,
                "source_url": source_url,
                "doc_quality": doc_quality,
            })

    return chunks


def chunk_guide_section(content, source_id, source_title, source_url, doc_quality="text"):
    chunks = []
    section_matches = list(RE_SECTION.finditer(content))

    def make_chunk(idx, section_title, body):
        return {
            "chunk_id": f"{source_id}_S{idx + 1}",
            "source_id": source_id,
            "content_type": "guide_section",
            "source_title": source_title,
            "chuong": None,
            "chuong_title": None,
            "dieu": None,
            "dieu_title": None,
            "section_title": section_title,
            "content": clean_content(body),
            "source_url": source_url,
            "doc_quality": doc_quality,
        }

    if not section_matches:
        return [make_chunk(0, None, content)]

    pre = content[: section_matches[0].start()].strip()
    chunk_idx = 0
    if pre:
        chunks.append(make_chunk(chunk_idx, None, pre))
        chunk_idx += 1

    for i, m in enumerate(section_matches):
        title = m.group(2).strip()
        start = m.start()
        end = (
            section_matches[i + 1].start()
            if i + 1 < len(section_matches)
            else len(content)
        )
        body = clean_content(content[start:end])
        if body:
            chunks.append(make_chunk(chunk_idx, title, body))
            chunk_idx += 1

    return chunks


def chunk_portal_reference(content, source_id, source_title, source_url, doc_quality="text"):
    return [{
        "chunk_id": f"{source_id}_REF",
        "source_id": source_id,
        "content_type": "portal_reference",
        "source_title": source_title,
        "chuong": None,
        "chuong_title": None,
        "dieu": None,
        "dieu_title": None,
        "section_title": None,
        "content": clean_content(content),
        "source_url": source_url,
        "doc_quality": doc_quality,
    }]


def process_file(md_path: Path, registry: dict) -> list:
    source_id = md_path.stem

    if source_id not in registry:
        print(f"  [SKIP] {source_id} not in source registry.", file=sys.stderr)
        return []

    reg = registry[source_id]
    source_url = reg.get("url") or ""
    registry_title = reg.get("title", source_id)
    doc_quality = reg.get("doc_quality", "text")

    content = md_path.read_text(encoding="utf-8")
    # Bỏ qua comment metadata HTML nếu có (từ converter)
    content = re.sub(r"^<!--.*?-->\s*", "", content, flags=re.DOTALL)
    source_title = extract_doc_title(content, registry_title)
    ctype = detect_content_type(content, source_id)

    if ctype == "law_article":
        return chunk_law_article(content, source_id, source_title, source_url, doc_quality)
    elif ctype == "guide_section":
        return chunk_guide_section(content, source_id, source_title, source_url, doc_quality)
    else:
        return chunk_portal_reference(content, source_id, source_title, source_url, doc_quality)


def validate_chunk(chunk: dict) -> list:
    required_fields = [
        "chunk_id", "source_id", "content_type", "source_title",
        "chuong", "chuong_title", "dieu", "dieu_title",
        "section_title", "content", "source_url", "doc_quality",
    ]
    errors = []
    for field in required_fields:
        if field not in chunk:
            errors.append(f"Missing field: {field}")
    if chunk.get("content_type") not in {
        "law_article", "guide_section", "portal_reference", "appendix"
    }:
        errors.append(f"Invalid content_type: {chunk.get('content_type')}")
    if not chunk.get("content"):
        errors.append("Empty content")
    return errors


def main() -> None:
    registry = load_source_registry(SOURCE_REGISTRY_PATH)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(PROCESSED_DIR.glob("*.md"))
    if not md_files:
        sys.exit(f"[ERROR] No .md files found")

    all_chunks = []
    type_counts = {}
    validation_errors = []

    print(f"Processing {len(md_files)} files...\n")
    for md_path in md_files:
        chunks = process_file(md_path, registry)
        for chunk in chunks:
            errs = validate_chunk(chunk)
            for e in errs:
                validation_errors.append(f"{chunk.get('chunk_id', '?')}: {e}")
            ctype = chunk.get("content_type", "unknown")
            type_counts[ctype] = type_counts.get(ctype, 0) + 1
        all_chunks.extend(chunks)

        label = chunks[0]["content_type"] if chunks else "SKIP"
        print(f"  {md_path.stem:<20} -> {len(chunks):>4} chunks  [{label}]")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"Total chunks: {len(all_chunks)}")
    for ctype, count in sorted(type_counts.items()):
        print(f"  {ctype:<22} {count:>4}")

    if validation_errors:
        print(f"\n[WARN] {len(validation_errors)} validation error(s):")
        for e in validation_errors[:20]:
            print(f"  • {e}")
    else:
        print("\n[OK] All chunks passed validation.")


if __name__ == "__main__":
    main()
