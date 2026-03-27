"""CLI entry point for the lens-py pipeline."""

from __future__ import annotations

import asyncio

import click

from lens_py.agents.pipeline import PipelineAgent
from lens_py.config import load_config


@click.group()
def cli() -> None:
    """Lens-py: Content-aware feed aggregator with AI-powered processing."""
    pass


@cli.command()
@click.option("--concurrency", default=5, help="Max concurrent operations per phase.")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files.")
@click.option("--category", default=None, help="Filter feeds by OPML category.")
@click.option("--verbose", is_flag=True, help="Enable verbose output.")
def run(concurrency: int, overwrite: bool, category: str | None, verbose: bool) -> None:
    """Run the full pipeline: feeds -> fetch -> extract -> summarize -> rank."""
    config = load_config()

    if not config.anthropic_api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set. See .env.example", err=True)
        raise SystemExit(1)

    click.echo("Lens-py Pipeline")
    click.echo("================")
    click.echo(f"Data directory: {config.data_dir}")
    click.echo(f"Model: {config.model}")
    click.echo("")

    agent = PipelineAgent(config)
    result = asyncio.run(agent.run(
        concurrency=concurrency,
        overwrite=overwrite,
        category_filter=category,
    ))

    click.echo("")
    click.echo("Pipeline complete!")
    click.echo(f"   Feeds found: {result.feeds_found}")
    click.echo(f"   Articles fetched: {result.articles_fetched}")
    click.echo(f"   Articles extracted: {result.articles_extracted}")
    click.echo(f"   Articles summarized: {result.articles_summarized}")
    click.echo(f"   Articles ranked: {result.articles_ranked}")
    click.echo(f"   Errors: {len(result.errors)}")
    click.echo(f"   Elapsed: {result.elapsed_seconds:.1f}s")

    if result.errors and verbose:
        click.echo("\nErrors:")
        for err in result.errors:
            click.echo(f"   - {err}")


@cli.command()
def extract() -> None:
    """Run only the extraction phase (HTML -> clean text, no LLM)."""
    config = load_config()

    from lens_py.extraction import extract_articles

    results = extract_articles(
        config.fetched_dir,
        config.extracted_dir,
        overwrite=True,
    )

    success = sum(1 for _, r in results if not isinstance(r, Exception))
    failed = sum(1 for _, r in results if isinstance(r, Exception))

    click.echo(f"Extraction complete: {success} succeeded, {failed} failed")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
