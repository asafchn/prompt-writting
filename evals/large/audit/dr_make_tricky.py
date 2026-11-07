#!/usr/bin/env python3
"""Build my own small, adversarial dataset (unambiguous cases only) for data-report."""
import csv, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
H = ["order_id", "customer_id", "customer_email", "customer_name", "product", "quantity", "unit_price", "currency",
     "status", "order_date", "updated_at", "is_test"]
UKH = ["updated_at", "order_id", "status", "customer_id", "customer_name", "customer_email", "product", "currency",
       "unit_price", "quantity", "order_date", "is_test"]


def row(oid, cid, email, name, prod, q, p, cur, st, od, ua, t=""):
    return dict(zip(H, [oid, cid, email, name, prod, q, p, cur, st, od, ua, t]))


eu = [
    row("A1", "C1", "a@x.com", "Holm, Ana", "Tent", "2", "100.00", "EUR", "shipped", "2025-01-15", "2025-01-15T10:00:00Z"),
    # same id later in file, later wall clock text but EARLIER instant (+05:00) -> must NOT win
    row("A1", "C1", "a@x.com", "Holm, Ana", "Tent", "9", "100.00", "EUR", "shipped", "2025-01-15", "2025-01-15T12:00:00+05:00"),
    row("A2", "C2", "b@x.com", "Tester Brandt", "Lamp", "1", "50", "eur ", "delivered", "31/03/2025", "2025-03-31 08:00:00"),
    row("A3", "C3", "c@latest.shopco.io", "Ana Rossi", "Lamp", "3", "10.10", " GBP", "completed", "Apr 1, 2025", "2025-04-01T00:00:00Z", "no"),
    row("A4", "C4", "d@test.shopco.io", "Dee", "Tent", "1", "999.00", "USD", "completed", "2025-05-05", "2025-05-05T00:00:00Z"),
    row("A5", "C5", "e@x.com", "test-Eve", "Tent", "1", "999.00", "USD", "completed", "2025-05-05", "2025-05-05T00:00:00Z"),
    row("A6", "C6", "f@x.com", "Fay", "Tent", "1", "999.00", "USD", "completed", "2025-05-05", "2025-05-05T00:00:00Z", "Y"),
    row("A7", "C7", "g@x.com", "Gus", "Tent", "1", "999.00", "USD", "CANCELED", "2025-05-05", "2025-05-05T00:00:00Z"),
    row("A8", "C8", "h@x.com", "Hal", "Tent", "1", "10.00", "USD", "shipped", "31/02/2025", "2025-02-28T00:00:00Z"),  # bad date
    row("A9", "C9", "i@x.com", "Ivy", "Tent", "0", "10.00", "USD", "shipped", "2025-02-02", "2025-02-02T00:00:00Z"),  # qty 0
    row("A10", "C10", "j@x.com", "Jo", "Tent", "1", "-1.00", "USD", "shipped", "2025-02-02", "2025-02-02T00:00:00Z"),  # neg price
    row("A11", "C11", "k@x.com", "Kai", "Tent", "1", "1e2", "USD", "shipped", "2025-02-02", "2025-02-02T00:00:00Z"),  # not plain
    row("A12", "C12", "l@x.com", "Lu", "Tent", "1", "5.00", "JPY", "shipped", "2025-02-02", "2025-02-02T00:00:00Z"),  # bad cur
    row("A13", "C13", "m@x.com", "Mo", "Tent", "1", "5.00", "USD", "shipped", "2025-02-02", "2025-02-02T10:00:00"),  # T, no zone
    row("", "C14", "n@x.com", "Ned", "Tent", "1", "5.00", "USD", "shipped", "2025-02-02", "2025-02-02T00:00:00Z"),  # no id
    row("A15", "C15", "o@x.com", "Oz", "Rope", "4", "12.345", "USD", "shipped", "2025-12-31T23:59:59Z", "2026-01-01T00:00:00Z"),
    row("A16", "C1", "a@x.com", "Holm, Ana", "Rope", "1", "40.00", "GBP", "shipped", "Jul 4, 2025", "2025-07-04T09:00:00-04:00"),
    row("A17", "C17", "q@x.com", "Quin", "Lamp", "2", "20.00", "EUR", "shipped", "2025-08-08", "2025-08-08T00:00:00Z"),
    # A17 cancelled in a LATER version (instant later) -> excluded
    row("A17", "C17", "q@x.com", "Quin", "Lamp", "2", "20.00", "EUR", "cancelled", "2025-08-08", "2025-08-08T03:00:00+02:00"),
    row("A18", "C18", "r@x.com", "Rae", "Lamp", "1", "30.00", "USD", "shipped", "2025-09-09", "2025-09-09 00:00:00"),
]
us = [
    # A16 appears again in another file with an older instant -> loses
    row("A16", "C1", "a@x.com", "Holm, Ana", "Rope", "7", "40.00", "GBP", "shipped", "Jul 4, 2025", "2025-07-04T12:00:00Z"),
    row("A19", "C19", "s@x.com", "Sam", "Tent", "1", "200.00", "USD", "completed", "Feb 29, 2025", "2025-03-01T00:00:00Z"),  # bad date
    row("A20", "C20", "t@x.com", "Tia", "Tent", "1", "60.00", "USD", "completed", "2025-10-10", "2025-10-10T00:00:00Z"),
]
uk = [
    row("A21", "C21", "u@x.com", "Testa, Maria", "Lamp", "5", "8.00", "GBP", "shipped", "10/11/2025", "2025-11-10T00:00:00Z"),
    row("A22", "C22", "v@x.com", "Vic", "Tent", "1", "100.00", "GBP", "shipped", "2025-06-30", "2025-06-30T00:00:00Z"),
]
with open(f"{out}/orders_eu.csv", "w", newline="") as f:
    w = csv.DictWriter(f, H); w.writeheader(); [w.writerow(r) for r in eu]
    f.write("\n")  # trailing blank line
with open(f"{out}/orders_us.csv", "w", newline="") as f:
    w = csv.DictWriter(f, H); w.writeheader(); w.writerow(us[0]); f.write("\n"); [w.writerow(r) for r in us[1:]]
    f.write("A23,C23,w@x.com,Wu,Tent,1,5.00,USD,shipped,2025-02-02\n")  # too few fields
with open(f"{out}/orders_uk.csv", "w", newline="") as f:
    w = csv.DictWriter(f, UKH); w.writeheader(); [w.writerow(r) for r in uk]
with open(f"{out}/refunds.csv", "w", newline="") as f:
    f.write("refund_id,order_id,amount,currency,refunded_at\n")
    f.write("R1,A1,50.00,EUR,2025-02-01T00:00:00Z\n")
    f.write("R1,A1,50.00,EUR,2025-02-01T00:00:00Z\n")      # duplicate id
    f.write("R2,A20,60.00,USD,2026-01-05T00:00:00Z\n")     # full refund -> C20 not paying
    f.write("R3,A7,10.00,USD,2025-06-01T00:00:00Z\n")      # cancelled order -> ignored
    f.write("R4,A99,10.00,USD,2025-06-01T00:00:00Z\n")     # unknown
    f.write("R5,A22,10.00,EUR,2025-07-01T00:00:00Z\n")     # refund in EUR against GBP order
    f.write("R6,A8,1.00,USD,2025-07-01T00:00:00Z\n")       # malformed-only order -> ignored
