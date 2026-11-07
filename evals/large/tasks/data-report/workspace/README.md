# Order exports, 2025

`data/` holds raw exports from three regional shops plus one refunds file:

- `orders_eu.csv`, `orders_us.csv`, `orders_uk.csv`: one row per exported order version. The columns are the same in all three files, but `orders_uk.csv` lists them in a different order. Fields may be quoted (customer names can contain commas).
- `refunds.csv`: `refund_id, order_id, amount, currency, refunded_at`.

Do not edit anything in `data/`.

## Deliverable

`report.py`, run as `python3 report.py [DATA_DIR] [OUT_FILE]` (defaults: `data` and `answers.json`), reads the four files in `DATA_DIR` and writes `OUT_FILE`. It must work on any export with the same layout, not only this one. Use the Python 3 standard library only. Leave the `answers.json` it produces for `data/` in the workspace root.

`answers.json` has exactly these keys:

```json
{
  "net_revenue_usd_by_quarter": {"2025-Q1": 0.0, "2025-Q2": 0.0, "2025-Q3": 0.0, "2025-Q4": 0.0},
  "unique_paying_customers": 0,
  "refund_rate": 0.0,
  "top_product": "",
  "median_order_value_usd": 0.0,
  "malformed_rows_skipped": 0,
  "duplicates_removed": 0
}
```

Money figures are rounded to 2 decimals (checked to within ±0.01). `refund_rate` is a fraction between 0 and 1 rounded to 4 decimals (checked to within ±0.0001). Counts are exact integers. Round only the final figures.

## House rules

Apply these steps in this order.

### 1. Skip malformed order rows

Read each order file as CSV. Blank lines are not rows. A data row is malformed if any of these hold:

- it has a different number of fields from the header;
- `order_id` is empty;
- `quantity` is not a whole number of at least 1;
- `unit_price` is not a plain decimal number of at least 0;
- `currency`, ignoring case and surrounding spaces, is not `EUR`, `USD` or `GBP`;
- `order_date` or `updated_at` is not a real date in one of the formats below.

Skip every malformed row and count it in `malformed_rows_skipped`. Count rows across all three files, before removing duplicates.

Accepted `order_date` formats: `2025-03-04`, `04/03/2025` (always day first, then month), `Mar 4, 2025`, and `2025-03-04T14:22:10Z`. Only the calendar date matters.

Accepted `updated_at` formats: `2025-03-05T10:00:00Z`, `2025-03-05 10:00:00` (UTC), and `2025-03-05T12:00:00+02:00` (a local time with its UTC offset).

### 2. Remove duplicates

The same `order_id` can appear several times, in one file or across files, once per exported version. Keep only the version with the latest `updated_at`, comparing actual instants (so mind the offsets). `duplicates_removed` is the number of valid rows minus the number of distinct order ids among them.

### 3. Drop cancelled orders and test accounts

Use the kept version of each order.

- Cancelled: `status` is `cancelled` or `canceled`, in any letter case.
- Test account: any one of these marks the order as a test order:
  - `is_test` is `1`, `true`, `yes` or `y`, in any letter case;
  - the email's domain is exactly `test.shopco.io`;
  - `customer_name` starts with `test-`, in any letter case (so `Tester Brandt` and `Testa, Maria` are real customers).

The orders left are the *included orders*.

### 4. Convert and apply refunds

Fixed rates: 1 EUR = 1.08 USD, 1 GBP = 1.27 USD, 1 USD = 1 USD.

- An order's gross value is `quantity × unit_price`, converted to USD at its own `currency`.
- A refund is converted to USD at the refund row's own `currency`. A `refund_id` that appears more than once is counted once. Refunds that point at an order that is not included (cancelled, test, malformed only, or unknown) are ignored.
- An order's net revenue is its gross value minus its refunds.

## Figures

- `net_revenue_usd_by_quarter`: sum of net revenue of included orders, grouped by the calendar quarter of `order_date` (not the refund date). Keys look like `2025-Q1`.
- `unique_paying_customers`: number of distinct `customer_id` values with at least one included order whose net revenue, rounded to cents, is above 0. A fully refunded order does not make its customer a paying customer.
- `refund_rate`: total refunds in USD divided by total gross value in USD, both over included orders.
- `top_product`: the `product` with the highest total net revenue over included orders.
- `median_order_value_usd`: median gross value in USD of included orders (the mean of the two middle values when the count is even).
- `malformed_rows_skipped`: see step 1.
- `duplicates_removed`: see step 2.
