TASK. Your current directory is a project folder holding `README.md` and a `data/` folder with four raw CSV exports from 2025: `orders_eu.csv` (about 760 rows), `orders_us.csv` (about 680), `orders_uk.csv` (about 410) and `refunds.csv` (about 160). The three order files have the same 12 columns (`order_id, customer_id, customer_email, customer_name, product, quantity, unit_price, currency, status, order_date, updated_at, is_test`), but `orders_uk.csv` puts them in a different order. Refunds have the columns `refund_id, order_id, amount, currency, refunded_at`. Your job is to write `report.py`, a Python 3 standard-library-only script run as `python3 report.py [DATA_DIR] [OUT_FILE]`, with defaults `data` and `answers.json`. It must apply the house rules in `README.md` exactly and write seven figures to JSON. Then run it once so the `answers.json` it produces for `data/` sits in the project root. The script will be rerun on future exports with the same layout, so every figure must be computed from the files. Read `README.md` in full before writing any code. It is the specification, and this brief only adds what it leaves open.

HOW IT WILL BE MEASURED. A checker runs `python3 report.py` (and possibly `python3 report.py OTHER_DIR OUT.json` on a different export with the same layout). It then compares the JSON to reference values computed under the README rules. The JSON must have exactly these top-level keys: `net_revenue_usd_by_quarter` (an object keyed `"2025-Q1"` … `"2025-Q4"`), `unique_paying_customers`, `refund_rate`, `top_product`, `median_order_value_usd`, `malformed_rows_skipped`, `duplicates_removed`. Money figures are rounded to 2 decimals and checked to ±0.01. `refund_rate` is a 0–1 fraction rounded to 4 decimals and checked to ±0.0001. The three counts must match exactly. `top_product` must match exactly. Rates are fixed: 1 EUR = 1.08 USD, 1 GBP = 1.27 USD, 1 USD = 1 USD. Round only the final figures, never intermediate values. The one exception is the README's "net revenue rounded to cents is above 0" test for paying customers. You don't see the reference values or the second export.

WHAT COUNTS. You need a general implementation of the README pipeline, in the README's order: skip malformed rows, then dedupe by latest `updated_at` instant, then drop cancelled and test orders, then convert currency and apply refunds, then compute the figures. Here is an example of the care expected. `updated_at` values like `2025-07-24T04:36:00+05:00`, `2025-07-24 04:36:00` and `2025-07-24T04:36:00Z` must all become timezone-aware UTC datetimes before you compare them. The naive form counts as UTC. If you compare them as strings, or drop the offset, the wrong version of some orders wins. These don't count: hard-coding any figure, row number or order id; special-casing this export's contents; tuning rules until the numbers "look right"; reading the files with fixed column positions (read headers by name, because the UK file is reordered). These traps are present in the data:
- currencies like `EUR ` and `eur`;
- `is_test` values `TRUE`, `Y`, `1`, `no`, `0` and blank;
- names like `TEST-Ivo Costa` and `test-Dara Jansen` (test accounts) next to `Testa, Maria` (a real customer);
- the email domain `latest.shopco.io` (not a test domain);
- quoted names with commas;
- impossible dates such as `30/02/2025`, `2025-02-30T10:00:00Z` and `2025-13-04`;
- quantities `-1` and `two`, and a unit price `abc`;
- a row with an extra field, and an empty `order_id`;
- the same order spread across files, with different statuses or quantities per version;
- `updated_at` values in 2026;
- repeated `refund_id`s;
- refunds pointing at unknown ids (`ORD-900001`…), or at cancelled or test orders;
- refunds dated in 2026, which still count against their order;
- refunds equal to or larger than the order's gross value.

WHAT YOU HAVE.
1. The project folder, which is your working directory. `README.md` and `data/` are read-only: never modify, rename or add files under `data/`. You write `report.py` and `answers.json` in the root. Put any scratch fixtures or helper scripts in a separate folder such as `scratch/`, and delete it before you finish.
2. Tools: Bash, Read, Edit, Write, Glob, Grep. Python 3 with the standard library only (`csv`, `datetime`, `decimal`, `json`, `re`, `statistics`, `sys`, `os`). No third-party packages and no internet.
3. A budget of 40 turns in total, with no one to answer questions. A full run of the script takes well under a second, so running it is cheap, but turns are not. A reasonable split: 4 turns reading the README and sampling the data, 8 writing the script, 15 testing and fixing, and the rest for a final clean run and your report.

HOW TO WORK.
1. Read `README.md`, the header of each file, and some sample rows. Grep for the trap patterns listed above so you know what the parser has to handle.
2. Write the parsing with explicit validators, one per rule.
   - Quantity must match `^\d+$` with a value of at least 1.
   - Unit price must be a plain decimal, matching `^\d+(\.\d+)?$`, so no sign, exponent or thousands separator.
   - Currency is checked after `strip().upper()`.
   - `order_date` accepts exactly the four README formats, and day-first for slashes. Only its calendar date is used, so for `...T14:22:10Z` take the date as written.
   - `updated_at` accepts exactly the three README formats.
   - Use `datetime.strptime` or `fromisoformat` with format checks, so impossible dates are rejected rather than rolled over.
   - Compute money with `Decimal` or with floats rounded only at the end. Either passes at ±0.01.
   - Skip blank lines, meaning rows where every field is empty. They are not rows and are not malformed.
   - Fix field count only through the parsed row length versus the header.
   - Read the three order files listed in the README (`orders_eu.csv`, `orders_uk.csv`, `orders_us.csv`) in sorted filename order.
3. Settle the README's gaps with these decisions, and keep to them:
   - **Strict whitespace.** Whitespace stripping and case-folding apply only where the README says so (currency, status, `is_test`, the `test-` prefix). Other fields are validated as given. Report how many rows that strictness rejected.
   - **Email domain.** The domain is the text after the last `@`, compared case-insensitively to exactly `test.shopco.io`. Subdomains don't match.
   - **Ties.** If two valid versions of an order have the same `updated_at` instant, keep the one read last. Report how many ties occurred.
   - **Bad refund rows.** Skip refund rows with an unparseable amount or an unknown currency. They don't count toward `malformed_rows_skipped`. Report how many there were.
   - **Dedupe refunds** on `refund_id` (keep the first occurrence) before matching them to orders.
   - **No capping.** Don't cap refunds at gross. An order's net revenue may go negative.
   - **Quarter keys.** Always emit `2025-Q1` to `2025-Q4`, as 0.0 if empty. Add a `YYYY-Qn` key for any other year that has included orders.
   - **Product ties.** If two products tie for `top_product`, pick the alphabetically first.
4. Test against a hand-made fixture directory in `scratch/` with about 15 rows. Write the expected answers before you run the script, and cover:
   - one row per malformed rule;
   - a blank line;
   - a quoted comma name;
   - a reordered-column file;
   - a three-version duplicate where the offset decides the winner;
   - each test-account mark plus the `Tester`/`Testa` false positives;
   - a duplicated refund id;
   - a refund to an unknown order;
   - a fully refunded customer;
   - an even count for the median.

   Fix the script until it matches, then run it on `data/`.
5. Sanity-check the real output. Have a temporary debug flag print row counts at each pipeline stage: total, malformed, valid, distinct, cancelled, test, included. Also print refunds matched versus ignored. Every count must add up: valid rows minus distinct ids equals `duplicates_removed`. Check that the refund rate is plausible (well under 0.5). Remove the flag, or make it opt-in, before you finish.
6. Keep a short `scratch/NOTES.md` of the decisions and stage counts so you don't redo work. Finish with a clean `python3 report.py` run from the root and a `cat answers.json`.

RULES. Not allowed: (a) modifying anything in `data/` or `README.md`; (b) third-party packages or network access; (c) hard-coded figures, ids, row numbers or file-specific branches; (d) leaving `scratch/` or other helper files behind; (e) changing the output keys or adding extra top-level keys. Allowed: helper functions, a `main()` guard, an opt-in debug flag, comments explaining rule interpretations, and any stdlib module.

HOW THE SESSION RUNS. You are done when `report.py` and a freshly generated `answers.json` are in the project root, the fixture test passes, and the scratch files are removed, or when the 40 turns run out. In that case, make sure the latest working script and its `answers.json` are in place first. Your final message must contain:
- the contents of `answers.json`;
- the stage counts from step 5;
- each interpretation decision from step 3, with how many rows it affected;
- anything in the data that the README didn't cover, and how you handled it.
