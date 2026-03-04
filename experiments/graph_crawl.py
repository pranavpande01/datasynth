import argparse
import asyncio
import json
from typing import Dict, Any, Set, Tuple

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy


def normalize_url(url: str) -> str:
    # Basic normalization to reduce duplicates
    return url.split("#", 1)[0].rstrip("/")


async def crawl_graph(
    seeds,
    max_depth: int,
    max_pages: int,
    follow_external: bool,
    include_content: bool,
    out_path: str,
):
    strategy = BFSDeepCrawlStrategy(
        max_depth=max_depth,
        include_external=follow_external,
        max_pages=max_pages if max_pages > 0 else None,
    )

    config = CrawlerRunConfig(
        deep_crawl_strategy=strategy,
        stream=True,
        verbose=True,
        only_text=True,
    )

    nodes: Dict[str, Dict[str, Any]] = {}
    edges: Set[Tuple[str, str, str]] = set()
    edge_list = []

    async with AsyncWebCrawler() as crawler:
        for seed in seeds:
            async for result in await crawler.arun(seed, config=config):
                if not result.success:
                    continue

                src = normalize_url(result.url)

                node = nodes.get(src, {"url": src, "discovered_only": False})
                node["discovered_only"] = False
                node["depth"] = result.metadata.get("depth", 0)
                node["title"] = getattr(result, "title", None) or result.metadata.get("title")
                if include_content:
                    node["markdown"] = result.markdown
                nodes[src] = node

                for link_type in ("internal", "external"):
                    for link in result.links.get(link_type, []):
                        href = link.get("href")
                        if not href:
                            continue
                        dst = normalize_url(href)

                        if dst not in nodes:
                            nodes[dst] = {
                                "url": dst,
                                "discovered_only": True,
                                "base_domain": link.get("base_domain"),
                            }

                        edge_key = (src, dst, link_type)
                        if edge_key not in edges:
                            edges.add(edge_key)
                            edge_list.append(
                                {
                                    "source": src,
                                    "target": dst,
                                    "type": link_type,
                                    "text": link.get("text"),
                                    "title": link.get("title"),
                                }
                            )

    graph = {"nodes": list(nodes.values()), "edges": edge_list}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", action="append", required=True, help="Seed URL (repeatable)")
    p.add_argument("--max-depth", type=int, default=2)
    p.add_argument("--max-pages", type=int, default=100)
    p.add_argument("--follow-external", action="store_true")
    p.add_argument("--include-content", action="store_true")
    p.add_argument("--out", default="experiments/graph.json")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        crawl_graph(
            seeds=args.seed,
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            follow_external=args.follow_external,
            include_content=args.include_content,
            out_path=args.out,
        )
    )
