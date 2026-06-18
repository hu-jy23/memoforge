# Freshness Policy

Use freshness metadata when a wiki page depends on version-sensitive APIs, tool behavior, hardware/runtime support, or external documents that may change.

Recommended fields:

- `checked_at`: date this page was last checked.
- `source_cutoff`: latest source date covered by the page.
- `version_scope`: framework, driver, model, or hardware versions the claim applies to.

If a page has no freshness metadata, treat `last_updated` and `sources` as the only recency signal.
