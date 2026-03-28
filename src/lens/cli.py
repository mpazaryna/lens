"""CLI entry point for the lens-py pipeline."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import click

from lens.config import load_config
from lens.errors import ConfigError
from lens.pipeline import run_pipeline
from lens.providers import create_provider


def _configure_logging(level_name: str) -> None:
    """Configure the root lens logger from a level name."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("lens").setLevel(level)


@click.group()
def cli() -> None:
    """Lens-py: Content-aware feed aggregator with AI-powered processing."""
    pass


@cli.command()
@click.option("--concurrency", default=5, help="Max concurrent operations per phase.")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files.")
@click.option("--category", default=None, help="Filter feeds by OPML category.")
@click.option("--verbose", is_flag=True, help="Enable verbose output.")
@click.option("--data-dir", default=None, type=click.Path(path_type=Path), help="Data directory.")
@click.option("--opml", default=None, type=click.Path(path_type=Path), help="OPML file path.")
def run(
    concurrency: int,
    overwrite: bool,
    category: str | None,
    verbose: bool,
    data_dir: Path | None,
    opml: Path | None,
) -> None:
    """Run the full pipeline: feeds -> fetch -> extract -> summarize -> rank."""
    config = load_config(data_dir_override=data_dir, opml_override=opml)
    _configure_logging("debug" if verbose else config.log_level)

    if config.provider != "ollama" and not config.api_key:
        raise ConfigError(
            f"LENS_API_KEY not set (required for {config.provider}). See .env.example"
        )

    click.echo("Lens Pipeline")
    click.echo("=============")
    click.echo(f"Data directory: {config.data_dir}")
    click.echo(f"Provider: {config.provider}")
    click.echo(f"Model: {config.model}")
    click.echo("")

    provider = create_provider(
        provider=config.provider,
        model=config.model,
        api_key=config.api_key,
        base_url=config.base_url,
    )
    result = asyncio.run(
        run_pipeline(
            config=config,
            provider=provider,
            concurrency=concurrency,
            overwrite=overwrite,
            category_filter=category,
        )
    )

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
@click.option("--data-dir", default=None, type=click.Path(path_type=Path), help="Data directory.")
def extract(data_dir: Path | None) -> None:
    """Run only the extraction phase (HTML -> clean text, no LLM)."""
    config = load_config(data_dir_override=data_dir)
    _configure_logging(config.log_level)

    from lens.collect.extractor import extract_articles

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
