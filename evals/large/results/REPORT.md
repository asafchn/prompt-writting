# Large-task eval: generic request vs skill-rewritten brief

Agent: claude-opus-5-5 at medium effort, Claude Code headless, max 40 turns, tools Bash,Read,Edit,Write,Glob,Grep.

| task | arm | prompt words | runs | mean score | passed | gaming | mean turns | mean minutes | mean cost $ |
|---|---|---|---|---|---|---|---|---|---|
| api-migration | generic | 79 | 1 | 1.00 | 1/1 | 0 | 8 | 1.4 | 0.34 |
| api-migration | skill | 1601 | 2 | 0.94 | 0/2 | 0 | 6 | 1.0 | 0.31 |
| bugfix-ledger | generic | 74 | 2 | 1.00 | 2/2 | 0 | 5 | 0.6 | 0.18 |
| bugfix-ledger | skill | 1251 | 1 | 1.00 | 1/1 | 0 | 5 | 0.6 | 0.20 |
| data-report | generic | 97 | 6 | 1.00 | 6/6 | 0 | 7 | 1.4 | 0.34 |
| data-report | skill | 1461 | 6 | 1.00 | 6/6 | 0 | 7 | 4.0 | 0.50 |
| incident-logs | generic | 85 | 6 | 1.00 | 6/6 | 0 | 10 | 1.3 | 0.30 |
| incident-logs | skill | 1149 | 6 | 1.00 | 6/6 | 0 | 7 | 1.6 | 0.39 |

**Mean score over tasks (each task weighted equally):** generic: 1.00, skill: 0.98

**Paired difference (skill - generic):** -0.004 ± 0.004 (one standard error, n=14 pairs); 95% CI roughly -0.013 to +0.004.

## Per-check pass rates

**api-migration**

| check | generic | skill |
|---|---|---|
| mod_batch | 1/1 | 2/2 |
| mod_dispatch | 1/1 | 2/2 |
| mod_feeds | 1/1 | 2/2 |
| mod_geo | 1/1 | 2/2 |
| mod_health | 1/1 | 2/2 |
| mod_news | 1/1 | 2/2 |
| mod_poller | 1/1 | 2/2 |
| mod_profile | 1/1 | 2/2 |
| mod_rates | 1/1 | 2/2 |
| mod_search | 1/1 | 2/2 |
| mod_stocks | 1/1 | 2/2 |
| mod_weather | 1/1 | 2/2 |
| no_live_oldnet_anywhere | 1/1 | 2/2 |
| report_files_changed | 1/1 | 0/2 |
| report_migrated_count | 1/1 | 2/2 |
| visible_tests_pass | 1/1 | 2/2 |

**bugfix-ledger**

| check | generic | skill |
|---|---|---|
| bug_convert_direction | 2/2 | 1/1 |
| bug_days_in_range_inclusive | 2/2 | 1/1 |
| bug_invoice_vat_on_discounted_net | 2/2 | 1/1 |
| bug_jpy_minor_units | 2/2 | 1/1 |
| bug_parse_parentheses | 2/2 | 1/1 |
| bug_vat_category_normalised | 2/2 | 1/1 |
| reg_cross_rate_and_identity | 2/2 | 1/1 |
| reg_half_up_rounding | 2/2 | 1/1 |
| reg_inclusive_periods | 2/2 | 1/1 |
| reg_per_line_vat_rounding | 2/2 | 1/1 |
| report_lists_all_bugs | 2/2 | 1/1 |
| visible_tests_pass | 2/2 | 1/1 |

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
