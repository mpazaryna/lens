# Enrichment Pipeline -- Behavior Specification

**Spec:** [spec.md](spec.md)
**PRD:** [prd.md](prd.md)

## Step 0: Organize fetched and extracted content by feed — ticket: 86e0m72qm

### Feature: Feed-organized output directories

```gherkin
Feature: Feed-organized output directories
  Fetched HTML and extracted markdown are written into subdirectories
  named after the feed source, making output browsable by source.

  Scenario: Fetched HTML is organized by feed
    Given a feed named "BBC Top Stories"
    When articles from that feed are fetched
    Then HTML files are written to fetched/bbc-top-stories/

  Scenario: Extracted markdown mirrors feed structure
    Given fetched HTML exists in fetched/bbc-top-stories/
    When extraction runs
    Then markdown files are written to extracted/bbc-top-stories/

  Scenario: Feed name is sanitized for filesystem safety
    Given a feed named "Tech & Science (2026)"
    When the feed name is normalized
    Then the directory name contains only lowercase alphanumeric characters, hyphens, and underscores

  Scenario: Multiple feeds produce separate directories
    Given feeds named "BBC Top Stories" and "Hacker News"
    When articles from both feeds are fetched
    Then fetched/bbc-top-stories/ and fetched/hacker-news/ both exist
    And each contains only articles from its respective feed

  Scenario: Flat files from prior runs are still processed
    Given HTML files exist directly in fetched/ (no subdirectory)
    When extraction runs
    Then those flat files are still extracted
    And output is written to extracted/ (no subdirectory)
```

## Step 1: Per-stage provider configuration — ticket: TBD

### Feature: Per-stage provider resolution

```gherkin
Feature: Per-stage provider resolution
  Each LLM stage can use a different provider and model.
  Stage-specific config falls back to the default provider.

  Scenario: Default provider used when no stage config set
    Given LENS_PROVIDER is set to "ollama"
    And LENS_MODEL is set to "llama3.2"
    And no LENS_SUMMARIZE_PROVIDER is set
    Then the summarization provider resolves to ollama/llama3.2

  Scenario: Stage-specific provider overrides default
    Given LENS_PROVIDER is set to "ollama"
    And LENS_SUMMARIZE_PROVIDER is set to "anthropic"
    And LENS_SUMMARIZE_MODEL is set to "claude-haiku-4-5-20251001"
    Then the summarization provider resolves to anthropic/claude-haiku-4-5-20251001
    And the default provider is still ollama

  Scenario: Partial override inherits missing fields from default
    Given LENS_PROVIDER is set to "ollama"
    And LENS_MODEL is set to "llama3.2"
    And LENS_SUMMARIZE_MODEL is set to "devstral:24b"
    And no LENS_SUMMARIZE_PROVIDER is set
    Then the summarization provider resolves to ollama/devstral:24b

  Scenario: Stage-specific API key overrides default
    Given LENS_API_KEY is set to "default-key"
    And LENS_SUMMARIZE_API_KEY is set to "summarize-key"
    Then the summarization stage uses "summarize-key"
    And other stages use "default-key"

  Scenario: Independent stage configuration
    Given LENS_SUMMARIZE_PROVIDER is set to "ollama"
    And LENS_RANK_PROVIDER is set to "anthropic"
    Then summarization and ranking use different providers
```

## Step 2: `lens enrich` CLI command — ticket: TBD

### Feature: Enrichment CLI command

```gherkin
Feature: Enrichment CLI command
  The lens enrich command runs only the enrichment pipeline
  against previously collected content. Requires an API key
  for cloud providers but not for Ollama.

  Scenario: Enrich runs enrichment only
    Given articles have been collected and are at "extracted" status
    When "lens enrich" is run
    Then summarization is performed
    And collection is not re-run

  Scenario: Enrich with Ollama does not require API key
    Given LENS_PROVIDER is set to "ollama"
    And no LENS_API_KEY is set
    When "lens enrich" is run
    Then enrichment proceeds without error

  Scenario: Enrich with cloud provider requires API key
    Given LENS_PROVIDER is set to "anthropic"
    And no LENS_API_KEY is set
    When "lens enrich" is run
    Then an error is raised indicating the API key is required

  Scenario: Retry failed enrichment items
    Given some items are at "failed" status from a prior enrichment run
    When "lens enrich --retry-failed" is run
    Then failed items are reset and reprocessed

  Scenario: Enrichment output shows counts
    Given 10 articles are at "extracted" status
    When "lens enrich" is run
    Then the output includes the number of articles summarized and any errors
```

## Step 3: Enrichment orchestrator with state tracker — ticket: TBD

### Feature: State-aware enrichment

```gherkin
Feature: State-aware enrichment
  The enrichment orchestrator processes items at "extracted" status
  through summarization, tracking progress per item.

  Scenario: Process extracted items
    Given 3 items at "extracted" status in the state tracker
    When enrichment runs
    Then all 3 items are summarized
    And their status is updated to "summarized"
    And stage_times includes a "summarized" entry for each

  Scenario: Skip non-extracted items
    Given items at statuses "new", "fetched", "extracted", and "summarized"
    When enrichment runs
    Then only the "extracted" item is processed

  Scenario: Failed summarization isolates error
    Given 3 items at "extracted" status
    And the LLM provider fails on the second item
    When enrichment runs
    Then the first and third items are "summarized"
    And the second item is "failed" with an error message
    And retry_count is incremented

  Scenario: Second enrichment run is a no-op
    Given all items are at "summarized" status
    When enrichment runs again
    Then no LLM calls are made
    And all items remain at "summarized"

  Scenario: Retry failed enrichment
    Given an item at "failed" status with retry_count 1
    When enrichment runs with retry_failed=True
    Then the item is reset to "extracted"
    And reprocessed through summarization
```

## Step 4: Structured summarization output — ticket: TBD

### Feature: Structured JSON summary output

```gherkin
Feature: Structured JSON summary output
  Summarization produces structured JSON with metadata
  including feed provenance and LLM call details.

  Scenario: Summary JSON contains all required fields
    Given an article is summarized
    Then the output JSON contains:
      | field              | type   |
      | title              | string |
      | source_url         | string |
      | feed_name          | string |
      | summary_text       | string |
      | word_count         | int    |
      | provider           | string |
      | model              | string |
      | timestamp          | string |
      | processing_time_ms | float  |

  Scenario: Token counts are captured
    Given a summarization call completes
    Then the output includes input_tokens and output_tokens

  Scenario: Feed name is preserved from collection
    Given an article was collected from feed "Hacker News"
    When it is summarized
    Then the output JSON contains feed_name "Hacker News"
```

## Step 5: Enrichment logging and observability — ticket: TBD

### Feature: Per-call LLM observability

```gherkin
Feature: Per-call LLM observability
  Each LLM call logs metadata for debugging and cost tracking.

  Scenario: Summarization logs include call metadata
    Given a summarization call completes
    Then the log entry includes model, provider, tokens in/out, and latency

  Scenario: Run log captures enrichment timing
    Given an enrichment run processes 5 articles
    Then the run log contains 5 item entries with stage timing

  Scenario: Run log is written after enrichment
    Given an enrichment run completes
    Then a JSON log file exists in {data_dir}/logs/
    And the log contains enrichment-specific metadata
```

## Step 6: E2E enrichment integration test — ticket: TBD

### Feature: End-to-end enrichment against local Ollama

```gherkin
Feature: End-to-end enrichment against local Ollama
  Integration test exercises the full enrichment pipeline
  against pre-collected content using a local Ollama instance.

  Scenario: Enrich pre-collected articles
    Given extracted markdown files exist in extracted/
    And state tracker has items at "extracted" status
    And Ollama is running locally with llama3.2
    When enrichment runs with provider=ollama model=llama3.2
    Then JSON summaries are written to processed/
    And state tracker shows items at "summarized" status

  Scenario: Second enrichment run is a no-op
    Given all items are at "summarized" status from a prior run
    When enrichment runs again
    Then no LLM calls are made
    And no new files are written to processed/

  Scenario: Run log is produced
    Given enrichment completes
    Then a run log file exists in logs/
    And it contains per-item timing and token counts
```
