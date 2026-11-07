# Large-task eval: generic request vs skill-rewritten brief

Agent: claude-opus-5-5 at medium effort, Claude Code headless, max 40 turns, tools Bash,Read,Edit,Write,Glob,Grep.

| task | arm | prompt words | runs | mean score | passed | gaming | mean turns | mean minutes | mean cost $ |
|---|---|---|---|---|---|---|---|---|---|
| api-migration | generic | 79 | 15 | 1.00 | 15/15 | 0 | 7 | 1.3 | 0.33 |
| api-migration | skill | 1601 | 15 | 1.00 | 15/15 | 0 | 7 | 1.2 | 0.32 |
| bugfix-ledger | generic | 74 | 15 | 1.00 | 15/15 | 0 | 5 | 0.7 | 0.19 |
| bugfix-ledger | skill | 1251 | 15 | 1.00 | 15/15 | 0 | 5 | 0.7 | 0.18 |
| data-report | generic | 97 | 15 | 1.00 | 15/15 | 0 | 7 | 1.2 | 0.34 |
| data-report | skill | 1461 | 15 | 1.00 | 15/15 | 0 | 8 | 2.7 | 0.48 |
| incident-logs | generic | 85 | 15 | 1.00 | 15/15 | 0 | 9 | 1.1 | 0.29 |
| incident-logs | skill | 1149 | 15 | 1.00 | 15/15 | 0 | 7 | 1.5 | 0.38 |
| perf-dedupe | generic | 56 | 15 | 1.00 | 15/15 | 0 | 7 | 4.0 | 0.17 |
| perf-dedupe | skill | 1449 | 15 | 1.00 | 15/15 | 0 | 11 | 4.1 | 0.27 |

**Skill arm, cost of writing the brief (once per task, read-only exploration):** api-migration: 10 turns, $0.24, bugfix-ledger: 14 turns, $0.21, data-report: 11 turns, $0.72, incident-logs: 12 turns, $0.34, perf-dedupe: 9 turns, $0.20

**Mean score over tasks (each task weighted equally):** generic: 1.00, skill: 1.00

**Paired difference (skill - generic):** +0.000 ± 0.000 (one standard error, n=75 pairs); 95% CI roughly +0.000 to +0.000.

## Per-check pass rates

**api-migration**

| check | generic | skill |
|---|---|---|
| mod_batch | 15/15 | 15/15 |
| mod_dispatch | 15/15 | 15/15 |
| mod_feeds | 15/15 | 15/15 |
| mod_geo | 15/15 | 15/15 |
| mod_health | 15/15 | 15/15 |
| mod_news | 15/15 | 15/15 |
| mod_poller | 15/15 | 15/15 |
| mod_profile | 15/15 | 15/15 |
| mod_rates | 15/15 | 15/15 |
| mod_search | 15/15 | 15/15 |
| mod_stocks | 15/15 | 15/15 |
| mod_weather | 15/15 | 15/15 |
| no_live_oldnet_anywhere | 15/15 | 15/15 |
| report_files_changed | 15/15 | 15/15 |
| report_migrated_count | 15/15 | 15/15 |
| visible_tests_pass | 15/15 | 15/15 |

**bugfix-ledger**

| check | generic | skill |
|---|---|---|
| bug_convert_direction | 15/15 | 15/15 |
| bug_days_in_range_inclusive | 15/15 | 15/15 |
| bug_invoice_vat_on_discounted_net | 15/15 | 15/15 |
| bug_jpy_minor_units | 15/15 | 15/15 |
| bug_parse_parentheses | 15/15 | 15/15 |
| bug_vat_category_normalised | 15/15 | 15/15 |
| reg_cross_rate_and_identity | 15/15 | 15/15 |
| reg_half_up_rounding | 15/15 | 15/15 |
| reg_inclusive_periods | 15/15 | 15/15 |
| reg_per_line_vat_rounding | 15/15 | 15/15 |
| report_lists_all_bugs | 15/15 | 15/15 |
| visible_tests_pass | 15/15 | 15/15 |

**data-report**

| check | generic | skill |
|---|---|---|
| hidden_duplicates_removed | 15/15 | 15/15 |
| hidden_malformed_rows_skipped | 15/15 | 15/15 |
| hidden_median_order_value_usd | 15/15 | 15/15 |
| hidden_net_revenue_usd_by_quarter | 15/15 | 15/15 |
| hidden_refund_rate | 15/15 | 15/15 |
| hidden_top_product | 15/15 | 15/15 |
| hidden_unique_paying_customers | 15/15 | 15/15 |
| visible_duplicates_removed | 15/15 | 15/15 |
| visible_malformed_rows_skipped | 15/15 | 15/15 |
| visible_median_order_value_usd | 15/15 | 15/15 |
| visible_net_revenue_usd_by_quarter | 15/15 | 15/15 |
| visible_refund_rate | 15/15 | 15/15 |
| visible_top_product | 15/15 | 15/15 |
| visible_unique_paying_customers | 15/15 | 15/15 |

**incident-logs**

| check | generic | skill |
|---|---|---|
| failed_payment_requests | 15/15 | 15/15 |
| incident_end_utc | 15/15 | 15/15 |
| incident_start_utc | 15/15 | 15/15 |
| root_cause_change_id | 15/15 | 15/15 |
| root_cause_service | 15/15 | 15/15 |
| trigger_evidence | 15/15 | 15/15 |

**perf-dedupe**

| check | generic | skill |
|---|---|---|
| edge_different_keys | 15/15 | 15/15 |
| edge_empty_fields | 15/15 | 15/15 |
| edge_ties | 15/15 | 15/15 |
| edge_transitive | 15/15 | 15/15 |
| edge_unicode_casefold | 15/15 | 15/15 |
| large_20k_identical | 15/15 | 15/15 |
| large_20k_under_3s | 15/15 | 15/15 |
| medium_2k_identical | 15/15 | 15/15 |
| report_timings | 15/15 | 15/15 |
| visible_tests_pass | 15/15 | 15/15 |
