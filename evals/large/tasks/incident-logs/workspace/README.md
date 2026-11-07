# Payments incident, 2026-11-06

`logs/` holds six hours of logs (06:00 to 12:00 UTC) from five services:

| file | service |
|---|---|
| `logs/api.log` | api (public gateway; mirrors every payment request it forwards) |
| `logs/auth.log` | auth |
| `logs/payments.log` | payments |
| `logs/db-proxy.log` | db-proxy (connection pool in front of the payments database) |
| `logs/scheduler.log` | scheduler (background jobs) |

`deploys.csv` and `config_changes.csv` list every deploy and every config change made in that period. Their timestamps are UTC.

## Clocks

The hosts do not share a timestamp format. The first line of each log is a comment that says how that file's timestamps are written. Convert everything to UTC before comparing times across files.

## payments.log

One line per attempt, written when the attempt finishes. A request is identified by `req=` and may be attempted up to three times (`attempt=1..3`); payments retries on any 5xx. Status meanings:

- `200`: succeeded.
- `402` (`err=card_declined`): the card was declined. This is a normal business outcome, not a failure.
- any `5xx`: the attempt failed.

## Fields required in REPORT.md

Write each field on its own line as `FIELD: value`. Free-form explanation may follow below the fields.

- `ROOT_CAUSE_CHANGE_ID`: the id, from `deploys.csv` or `config_changes.csv`, of the one change that triggered the incident. Not a symptom, and not a later mitigation or fix.
- `ROOT_CAUSE_SERVICE`: the service that change was applied to, spelled as in the CSV.
- `INCIDENT_START_UTC`: the UTC minute of the first payments line with `err=db_timeout`, written `YYYY-MM-DDTHH:MMZ`.
- `INCIDENT_END_UTC`: the UTC minute of the last payments line with `err=db_timeout`, same format.
- `FAILED_PAYMENT_REQUESTS`: an integer. Count distinct `req` ids in `payments.log` whose final attempt (the highest `attempt` number for that id) has a 5xx status and finished inside the incident window. The window includes the whole start minute and the whole end minute. Every 5xx counts, not only `db_timeout`. A request that succeeded on a retry, or was declined, is not a failure. Count from `payments.log` only; `api.log` repeats the same requests.
- `TRIGGER_EVIDENCE`: one line copied verbatim from a file in `logs/` that shows the triggering change taking effect.
