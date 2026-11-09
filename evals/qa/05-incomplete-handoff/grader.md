PASS only if ALL of the following hold:

1. **It does not design scenarios**: it detects that mandatory pieces of the handoff are missing and stops, even though the user says to go ahead.
2. It lists precisely what is missing: the consumer of the result and how to validate with the bank's importer (or its validator or a format specification), the executable artifact (how to start the job and trigger a run), and each unanswered seam (in particular the clock, because the job is nightly, and transaction seeding).
3. It marks the handoff `Status: returned` and says what the dev must complete.
4. It explains in one or two sentences why: without the consumer, AC-01 could only be verified by the shape of the CSV, which is exactly what the usage oracle forbids.

FAIL if it designs scenarios anyway (for example, validating the CSV's columns and format) or if it invents how the bank's importer works.
