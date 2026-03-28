# Core Pipeline (Collection) -- Behavior Specification

**Spec:** [spec.md](spec.md)
**PRD:** [prd.md](prd.md)

## Step 1: Configurable data directory and OPML path — ticket: 86e0m6pd3

### Feature: Data directory resolution

```gherkin
Feature: Data directory resolution
  The pipeline resolves its data directory through a precedence chain:
  CLI flag > environment variable > default (~/.lens).
  A development fallback uses data/ when it exists in the project root.

  Scenario: Default data directory
    Given no LENS_DATA_DIR environment variable is set
    And no --data-dir CLI flag is provided
    Then the data directory resolves to ~/.lens

  Scenario: Environment variable overrides default
    Given LENS_DATA_DIR is set to /tmp/lens-data
    And no --data-dir CLI flag is provided
    Then the data directory resolves to /tmp/lens-data

  Scenario: CLI flag overrides environment variable
    Given LENS_DATA_DIR is set to /tmp/lens-data
    And the --data-dir CLI flag is set to /opt/lens
    Then the data directory resolves to /opt/lens

  Scenario: Development fallback
    Given no LENS_DATA_DIR environment variable is set
    And no --data-dir CLI flag is provided
    And a data/ directory exists in the project root
    Then the data directory resolves to data/

  Scenario: Derived paths resolve from configured root
    Given the data directory resolves to /tmp/lens-data
    Then feeds_dir is /tmp/lens-data/feeds
    And fetched_dir is /tmp/lens-data/fetched
    And extracted_dir is /tmp/lens-data/extracted
    And processed_dir is /tmp/lens-data/processed
    And ranked_dir is /tmp/lens-data/ranked
```

### Feature: OPML source path resolution

```gherkin
Feature: OPML source path resolution
  The OPML feed source path is configurable, defaulting to
  {data_dir}/feeds.opml.

  Scenario: Default OPML path
    Given the data directory resolves to ~/.lens
    And no LENS_OPML_PATH environment variable is set
    Then the OPML path resolves to ~/.lens/feeds.opml

  Scenario: Environment variable overrides default
    Given LENS_OPML_PATH is set to /etc/lens/my-feeds.opml
    Then the OPML path resolves to /etc/lens/my-feeds.opml

  Scenario: CLI flag overrides environment variable
    Given LENS_OPML_PATH is set to /etc/lens/my-feeds.opml
    And the --opml CLI flag is set to /tmp/test.opml
    Then the OPML path resolves to /tmp/test.opml
```

## Step 2: Feed state tracker — ticket: 86e0m6pd5

### Feature: Item identification

```gherkin
Feature: Item identification
  Feed items are identified by a URL-safe hash of their URL,
  ensuring stable deduplication across runs.

  Scenario: Stable item ID from URL
    Given a feed item with URL "https://example.com/article-1"
    When an item ID is generated
    Then the ID is the same every time for the same URL
    And the ID contains only URL-safe characters

  Scenario: Different URLs produce different IDs
    Given a feed item with URL "https://example.com/article-1"
    And a feed item with URL "https://example.com/article-2"
    When item IDs are generated for both
    Then the two IDs are different
```

### Feature: Item discovery

```gherkin
Feature: Item discovery
  When feeds are parsed, new items are added to the state tracker
  with status "new". Already-known items are skipped.

  Scenario: Discover new items
    Given an empty state tracker
    When 3 feed items are discovered
    Then the state tracker contains 3 items
    And all items have status "new"
    And all items have a discovered_at timestamp

  Scenario: Skip already-known items
    Given a state tracker with item "https://example.com/a" at status "fetched"
    When feed items are discovered including "https://example.com/a"
    Then item "https://example.com/a" remains at status "fetched"
    And its discovered_at timestamp is unchanged
```

### Feature: State transitions

```gherkin
Feature: State transitions
  Items progress through stages: new -> fetched -> extracted -> summarized.
  Each transition records timing. Failed items record error details.

  Scenario: Advance item to next status
    Given an item at status "new"
    When the item transitions to "fetched" with stage_time 1.2
    Then the item status is "fetched"
    And stage_times contains fetched: 1.2
    And updated_at is refreshed

  Scenario: Mark item as failed
    Given an item at status "new"
    When the item transitions to "failed" with error "Connection refused"
    Then the item status is "failed"
    And the error field is "Connection refused"
    And retry_count is 1

  Scenario: Increment retry count on repeated failure
    Given an item at status "failed" with retry_count 2
    When the item is retried and fails again with error "Timeout"
    Then retry_count is 3
    And the error field is "Timeout"

  Scenario: Reject invalid transition
    Given an item at status "new"
    When the item attempts to transition to "summarized"
    Then the transition is rejected with an error
    And the item remains at status "new"
```

### Feature: Query items by status

```gherkin
Feature: Query items by status
  The state tracker can filter items by their current status
  to determine which items need processing at each stage.

  Scenario: Filter items at a specific status
    Given a state tracker with:
      | url                          | status    |
      | https://example.com/a        | new       |
      | https://example.com/b        | fetched   |
      | https://example.com/c        | new       |
      | https://example.com/d        | failed    |
    When querying for items at status "new"
    Then 2 items are returned
    And all returned items have status "new"
```

### Feature: State persistence

```gherkin
Feature: State persistence
  State is saved to and loaded from disk as JSON. Writes are atomic
  to prevent corruption on crash.

  Scenario: Save and load roundtrip
    Given a state tracker with 3 items at various statuses
    When the state is saved to disk and loaded back
    Then all items, statuses, timestamps, and stage_times are preserved

  Scenario: Atomic write
    Given a state tracker with data
    When the state is saved
    Then a temporary file is written first
    And the temporary file is renamed to the target path

  Scenario: Load from nonexistent path
    Given no state file exists at the target path
    When state is loaded
    Then an empty state tracker is returned

  Scenario: State data is immutable
    Given a loaded state tracker
    When attempting to mutate an item's fields directly
    Then an AttributeError is raised
```

### Feature: Seen ledger migration

```gherkin
Feature: Seen ledger migration
  Existing seen.json files from the old binary ledger are migrated
  to the new state tracker format.

  Scenario: Migrate seen ledger entries
    Given a seen.json with entries:
      | url                    | processedAt          | title     |
      | https://example.com/a  | 2026-01-01T00:00:00Z | Article A |
      | https://example.com/b  | 2026-01-02T00:00:00Z | Article B |
    When the seen ledger is migrated
    Then the state tracker contains 2 items
    And all items have status "summarized"
    And titles are preserved from the original entries
```
