"""Run the memory store's search from the command line.

    python -m app.run --subject "A. Muller" "How do I register a new address?"
"""

from __future__ import annotations

import argparse
import time

from .memory import MemoryStore


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("query")
    args = ap.parse_args()

    store = MemoryStore.load()
    start = time.perf_counter()
    hits = store.search(args.subject, args.query, k=args.k)
    elapsed = time.perf_counter() - start
    for n, hit in enumerate(hits, start=1):
        print(f"  {n}. {hit.splitlines()[0][:100]}")
    print(f"memory.search subject={args.subject!r} k={args.k} "
          f"{elapsed:.2f}s -> {len(hits)} hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
