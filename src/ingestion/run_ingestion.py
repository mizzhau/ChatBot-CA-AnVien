import io
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.ingestion.source_mapping import NEW_SOURCES, SKIP_FILES
from src.ingestion.converter import convert_file

NEW_DOCS_DIR = REPO_ROOT / "new_docs"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
SOURCE_REGISTRY_PATH = REPO_ROOT / "data" / "chunks" / "id_source.json"


def update_source_registry(new_entries: dict[str, dict]) -> None:
    """Thêm các source entry mới vào id_source.json."""
    if SOURCE_REGISTRY_PATH.exists():
        with open(SOURCE_REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    else:
        registry = {}

    added = 0
    for source_id, entry in new_entries.items():
        if source_id not in registry:
            registry[source_id] = entry
            added += 1
        else:
            # Cập nhật nếu đã tồn tại
            registry[source_id].update(entry)

    with open(SOURCE_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"\n  → Đã cập nhật id_source.json: {added} entry mới, "
          f"{len(registry)} entry tổng cộng.")


def main() -> None:
    print("=" * 65)
    print("  DOCUMENT INGESTION — new_docs/ → data/processed/")
    print("=" * 65)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── Thống kê ──
    total = len(NEW_SOURCES)
    skipped_dedup = len(SKIP_FILES)
    print(f"\n  Tổng file cần xử lý : {total}")
    print(f"  File bỏ qua (dedup) : {skipped_dedup}")
    print(f"  Thư mục nguồn       : {NEW_DOCS_DIR}")
    print(f"  Thư mục đích        : {PROCESSED_DIR}")

    # ── Hiển thị danh sách skip ──
    if SKIP_FILES:
        print(f"\n  Danh sách file bỏ qua:")
        for fname, reason in SKIP_FILES.items():
            print(f"    ✗ {fname}")
            print(f"      └─ {reason}")

    # ── Xử lý từng file ──
    print(f"\n{'─' * 65}")
    print("  Bắt đầu chuyển đổi...\n")

    success = 0
    failed = 0
    skipped = 0
    registry_entries: dict[str, dict] = {}

    for rel_path, meta in NEW_SOURCES.items():
        source_id = meta["source_id"]
        input_path = NEW_DOCS_DIR / rel_path

        # Kiểm tra file tồn tại
        if not input_path.exists():
            print(f"  [MISS] {rel_path}")
            print(f"         → File không tồn tại: {input_path}")
            failed += 1
            continue

        # Kiểm tra đã xử lý chưa
        output_path = PROCESSED_DIR / f"{source_id}.md"
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"  [EXIST] {source_id:.<20} ← {rel_path}  ({size_kb:.0f} KB)")
            skipped += 1
            # Vẫn thêm vào registry
            registry_entries[source_id] = {
                "title": meta["title"],
                "url": meta.get("url", ""),
                "scope": meta.get("scope", ""),
                "doc_quality": meta.get("doc_quality", "text"),
            }
            continue

        # Convert
        print(f"  [{source_id}] {rel_path}")
        result = convert_file(input_path, PROCESSED_DIR, source_id)

        if result and result.exists():
            size_kb = result.stat().st_size / 1024
            print(f"         → ✓ {result.name}  ({size_kb:.1f} KB)")
            success += 1
        else:
            print(f"         → ✗ Chuyển đổi thất bại")
            failed += 1
            continue

        # Chuẩn bị registry entry
        registry_entries[source_id] = {
            "title": meta["title"],
            "url": meta.get("url", ""),
            "scope": meta.get("scope", ""),
            "doc_quality": meta.get("doc_quality", "text"),
        }

    # ── Cập nhật id_source.json ──
    print(f"\n{'─' * 65}")
    print("  Cập nhật source registry...")
    update_source_registry(registry_entries)

    # ── Tổng kết ──
    print(f"\n{'=' * 65}")
    print(f"  KẾT QUẢ INGESTION")
    print(f"{'=' * 65}")
    print(f"  ✓ Thành công  : {success}")
    print(f"  ⊘ Đã tồn tại  : {skipped}")
    print(f"  ✗ Thất bại     : {failed}")
    print(f"  ✗ Bỏ qua dedup: {skipped_dedup}")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
