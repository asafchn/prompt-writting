# Large-task eval: generic request vs skill-rewritten brief

Agent: claude-opus-5-5 at medium effort, Claude Code headless, max 40 turns, tools Bash,Read,Edit,Write,Glob,Grep.

| task | arm | prompt words | runs | mean score | passed | gaming | mean turns | mean minutes | mean cost $ |
|---|---|---|---|---|---|---|---|---|---|
| api-migration | generic | 79 | 6 | 0.99 | 5/6 | 0 | 7 | 1.3 | 0.32 |
| api-migration | skill | 1601 | 6 | 0.94 | 0/6 | 0 | 7 | 1.1 | 0.32 |
| bugfix-ledger | generic | 74 | 6 | 1.00 | 6/6 | 0 | 5 | 0.6 | 0.18 |
| bugfix-ledger | skill | 1251 | 6 | 1.00 | 6/6 | 0 | 5 | 0.6 | 0.18 |
| data-report | generic | 97 | 6 | 1.00 | 6/6 | 0 | 7 | 1.4 | 0.34 |
| data-report | skill | 1461 | 6 | 1.00 | 6/6 | 0 | 7 | 4.0 | 0.50 |
| incident-logs | generic | 85 | 6 | 1.00 | 6/6 | 0 | 10 | 1.3 | 0.30 |
| incident-logs | skill | 1149 | 6 | 1.00 | 6/6 | 0 | 7 | 1.6 | 0.39 |
| perf-dedupe | generic | 56 | 6 | 1.00 | 6/6 | 0 | 7 | 4.8 | 0.16 |
| perf-dedupe | skill | 1449 | 6 | 1.00 | 6/6 | 0 | 10 | 2.0 | 0.26 |

**Skill arm, cost of writing the brief (once per task, read-only exploration):** api-migration: 10 turns, $0.24, bugfix-ledger: 14 turns, $0.21, data-report: 11 turns, $0.72, incident-logs: 12 turns, $0.34, perf-dedupe: 9 turns, $0.20

**Mean score over tasks (each task weighted equally):** generic: 1.00, skill: 0.99

**Paired difference (skill - generic):** -0.010 ± 0.004 (one standard error, n=30 pairs); 95% CI roughly -0.019 to -0.002.

## Per-check pass rates

**api-migration**

| check | generic | skill |
|---|---|---|
| mod_batch | 6/6 | 6/6 |
| mod_dispatch | 6/6 | 6/6 |
| mod_feeds | 6/6 | 6/6 |
| mod_geo | 6/6 | 6/6 |
| mod_health | 6/6 | 6/6 |
| mod_news | 6/6 | 6/6 |
| mod_poller | 6/6 | 6/6 |
| mod_profile | 6/6 | 6/6 |
| mod_rates | 6/6 | 6/6 |
| mod_search | 6/6 | 6/6 |
| mod_stocks | 6/6 | 6/6 |
| mod_weather | 6/6 | 6/6 |
| no_live_oldnet_anywhere | 6/6 | 6/6 |
| report_files_changed | 5/6 | 0/6 |
| report_migrated_count | 6/6 | 6/6 |
| visible_tests_pass | 6/6 | 6/6 |

**bugfix-ledger**

| check | generic | skill |
|---|---|---|
| bug_convert_direction | 6/6 | 6/6 |
| bug_days_in_range_inclusive | 6/6 | 6/6 |
| bug_invoice_vat_on_discounted_net | 6/6 | 6/6 |
| bug_jpy_minor_units | 6/6 | 6/6 |
| bug_parse_parentheses | 6/6 | 6/6 |
| bug_vat_category_normalised | 6/6 | 6/6 |
| reg_cross_rate_and_identity | 6/6 | 6/6 |
| reg_half_up_rounding | 6/6 | 6/6 |
| reg_inclusive_periods | 6/6 | 6/6 |
| reg_per_line_vat_rounding | 6/6 | 6/6 |
| report_lists_all_bugs | 6/6 | 6/6 |
| visible_tests_pass | 6/6 | 6/6 |

**data-report**

| check | generic | skill |
|---|---|---|
| hidden_duplicates_removed | 6/6 | 6/6 |
| hidden_malformed_rows_skipped | 6/6 | 6/6 |
| hidden_median_order_value_usd | 6/6 | 6/6 |
| hidden_net_revenue_usd_by_quarter | 6/6 | 6/6 |
| hidden_refund_rate | 6/6 | 6/6 |
| hidden_top_product | 6/6 | 6/6 |
| hidden_unique_paying_customers | 6/6 | 6/6 |
| visible_duplicates_removed | 6/6 | 6/6 |
| visible_malformed_rows_skipped | 6/6 | 6/6 |
| visible_median_order_value_usd | 6/6 | 6/6 |
| visible_net_revenue_usd_by_quarter | 6/6 | 6/6 |
| visible_refund_rate | 6/6 | 6/6 |
| visible_top_product | 6/6 | 6/6 |
| visible_unique_paying_customers | 6/6 | 6/6 |

**incident-logs**

| check | generic | skill |
|---|---|---|
| failed_payment_requests | 6/6 | 6/6 |
| incident_end_utc | 6/6 | 6/6 |
| incident_start_utc | 6/6 | 6/6 |
| root_cause_change_id | 6/6 | 6/6 |
| root_cause_service | 6/6 | 6/6 |
| trigger_evidence | 6/6 | 6/6 |

**perf-dedupe**

| check | generic | skill |
|---|---|---|
| edge_different_keys | 6/6 | 6/6 |
| edge_empty_fields | 6/6 | 6/6 |
| edge_ties | 6/6 | 6/6 |
| edge_transitive | 6/6 | 6/6 |
| edge_unicode_casefold | 6/6 | 6/6 |
| large_20k_identical | 6/6 | 6/6 |
| large_20k_under_3s | 6/6 | 6/6 |
| medium_2k_identical | 6/6 | 6/6 |
| report_timings | 6/6 | 6/6 |
| visible_tests_pass | 6/6 | 6/6 |
