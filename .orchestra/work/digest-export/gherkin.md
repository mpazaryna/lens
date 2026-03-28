# Digest and Export -- Behavior Specification

**Spec:** [spec.md](spec.md)
**PRD:** [prd.md](prd.md)

## Step 1: Digest generator — ticket: TBD

### Feature: Per-feed markdown digest

```gherkin
Feature: Per-feed markdown digest
  The digest generator reads processed summaries and produces
  a single markdown briefing per feed, sorted by substance.

  Scenario: Generate digest for a feed
    Given processed JSON summaries exist for feed "bbc-news"
    When a digest is generated
    Then a markdown file is written to digest/bbc-news.md
    And the header includes "BBC News" and the article count

  Scenario: Articles sorted by word count descending
    Given summaries with word counts 500, 1200, and 800
    When a digest is generated
    Then the 1200-word article appears first
    And the 500-word article appears last

  Scenario: Each article includes title, URL, summary, and metadata
    Given a processed summary with title "AI Advances"
    When a digest is generated
    Then the article section includes the title as a heading
    And includes the source URL
    And includes the summary text
    And includes word count and processing time

  Scenario: Empty feed produces valid digest
    Given no processed summaries exist for feed "empty-feed"
    When a digest is generated
    Then the digest file contains the header with 0 articles

  Scenario: Failed items are excluded
    Given items at "summarized" and "failed" status
    When a digest is generated
    Then only summarized items appear in the digest

  Scenario: Digest overwrites previous version
    Given a digest file already exists for feed "bbc-news"
    When a new digest is generated
    Then the previous file is overwritten with new content

  Scenario: Multiple feeds produce separate files
    Given processed summaries for "bbc-news" and "lobsters"
    When all digests are generated
    Then digest/bbc-news.md and digest/lobsters.md both exist
```

## Step 2: `lens digest` CLI command — ticket: TBD

### Feature: Digest CLI command

```gherkin
Feature: Digest CLI command
  The lens digest command generates markdown briefings
  from existing processed data. No LLM or network required.

  Scenario: Generate all digests
    Given processed data exists for multiple feeds
    When "lens digest" is run
    Then digest files are generated for each feed
    And the output lists each file and article count

  Scenario: Custom data directory
    Given processed data exists in a custom directory
    When "lens digest --data-dir /custom/path" is run
    Then digests are generated from that directory

  Scenario: No API key required
    Given no LENS_API_KEY is set
    When "lens digest" is run
    Then digests are generated without error
```

## Step 3: Export formatter — ticket: TBD

### Feature: JSON export

```gherkin
Feature: JSON export
  Export produces a structured JSON file per feed containing
  all summaries as an array.

  Scenario: Export feed as JSON
    Given processed summaries exist for feed "lobsters"
    When JSON export runs
    Then export/lobsters.json is written
    And it contains a JSON object with feed name and articles array

  Scenario: JSON includes generation timestamp
    When JSON export runs
    Then the output includes a generated_at timestamp

  Scenario: Empty feed produces valid JSON
    Given no summaries for feed "empty"
    When JSON export runs
    Then the output contains an empty articles array
```

### Feature: Obsidian export

```gherkin
Feature: Obsidian export
  Export produces individual markdown notes with YAML frontmatter
  compatible with Obsidian import.

  Scenario: Export as Obsidian notes
    Given processed summaries exist for feed "lobsters"
    When Obsidian export runs
    Then individual markdown files are written to export/obsidian/lobsters/

  Scenario: Obsidian note has YAML frontmatter
    Given a summary with title "AI Advances" from feed "lobsters"
    When Obsidian export runs
    Then the note contains YAML frontmatter with:
      | field      | value        |
      | title      | AI Advances  |
      | feed       | lobsters     |
      | tags       | [lens, lobsters] |
    And the note body contains the summary text

  Scenario: Obsidian note filename is safe
    Given a summary with title "What's New in AI? (2026)"
    When Obsidian export runs
    Then the filename contains only safe characters
```

## Step 4: `lens export` CLI command — ticket: TBD

### Feature: Export CLI command

```gherkin
Feature: Export CLI command
  The lens export command outputs structured data in
  configurable formats.

  Scenario: Default export is JSON
    When "lens export" is run
    Then JSON files are written to export/

  Scenario: Obsidian export format
    When "lens export --format obsidian" is run
    Then Obsidian notes are written to export/obsidian/

  Scenario: Custom data directory
    When "lens export --data-dir /custom/path" is run
    Then export reads from and writes to that directory

  Scenario: No API key required
    Given no LENS_API_KEY is set
    When "lens export" is run
    Then export completes without error
```
