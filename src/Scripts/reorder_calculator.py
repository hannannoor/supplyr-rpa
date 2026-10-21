"""
============================================================
 Supplyr RPA Project - Reorder Calculator (Part B)
 Student: Mohammed Hannan Noor (XXXXXXXX)
------------------------------------------------------------
 Called by UiPath via Python Scope + Invoke Python Method.

 UiPath passes TWO CSV strings:
   1. lowstock_csv  - the low-stock products (from dt_LowStock)
   2. suppliers_csv - all supplier options (from dt_AllSuppliers)

 The script calculates the reorder priority, matches suppliers
 to each product, picks the best supplier, calculates the
 estimated reorder cost, and returns a JSON string that UiPath
 deserializes into dt_Reorders.

 PRIORITY RULE (same formula as the UiPath detection step):
   HIGH   - current stock is 0, or <= 25% of minimum
   MEDIUM - current stock is <= 60% of minimum
   LOW    - anything else below minimum

 SUPPLIER SELECTION (tiered - best tier wins):
   Tier 1: has a valid email AND can fulfil the full quantity
   Tier 2: has a valid email but cannot fulfil in full
   Tier 3: can fulfil but has no usable email
   Tier 4: anything else that is a real supplier record
   Within a tier: cheapest supplier_price, then fastest delivery.

 STATUS (drives what UiPath does next):
   READY  - safe to generate a Word PO and send via Outlook
   REVIEW - something is wrong; skip ordering, log for staff
============================================================
"""

import csv
import io
import json


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _parse_csv(csv_text):
    """Turn a CSV string (with header row) into a list of dicts."""
    if not csv_text or not csv_text.strip():
        return []
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    rows = []
    for row in reader:
        clean = {}
        for k, v in row.items():
            if k is None:          # ragged row - extra columns
                continue
            clean[k.strip()] = v.strip() if isinstance(v, str) else ""
        rows.append(clean)
    return rows


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _to_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def _is_number(value):
    """True only if the value can be read as a number."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _has_valid_email(supplier):
    """Basic check that an email is usable before Outlook tries to send."""
    email = (supplier.get("SupplierEmail") or "").strip()
    return "@" in email and "." in email.split("@")[-1]


def _is_real_supplier(supplier):
    """A LEFT JOIN miss gives a row with no supplier name at all."""
    return bool((supplier.get("SupplierName") or "").strip())


# ------------------------------------------------------------
# Business logic
# ------------------------------------------------------------

def calculate_priority(current_stock, minimum_stock):
    """
    Reorder priority based on how far below minimum the stock has fallen.
    Mirrors the UiPath detection formula so both stages agree.
    """
    curr = _to_int(current_stock, -1)
    minm = _to_int(minimum_stock, -1)

    if curr < 0 or minm <= 0:
        return "UNKNOWN"
    if curr == 0 or curr <= minm * 0.25:
        return "HIGH"
    if curr <= minm * 0.6:
        return "MEDIUM"
    return "LOW"


def choose_best_supplier(suppliers, reorder_qty):
    """
    Pick the best supplier for one product.
    Returns (best_supplier_dict_or_None, note_string).
    """
    if not suppliers:
        return None, "NO SUPPLIER FOUND - no supplier linked to this product"

    # Drop rows where the supplier record itself is broken (LEFT JOIN miss)
    real = [s for s in suppliers if _is_real_supplier(s)]
    if not real:
        return None, "NO SUPPLIER FOUND - supplier record missing or deleted"

    def sort_key(s):
        return (_to_float(s.get("SupplierPrice"), 999999.0),
                _to_int(s.get("DeliveryDays"), 999))

    emailable = [s for s in real if _has_valid_email(s)]
    fulfilling = [s for s in real
                  if _to_int(s.get("AvailableQty")) >= reorder_qty]

    # Tier 1 - has email and can fulfil in full
    tier1 = [s for s in emailable if s in fulfilling]
    if tier1:
        return sorted(tier1, key=sort_key)[0], ""

    # Tier 2 - has email but cannot fulfil in full
    if emailable:
        best = sorted(emailable, key=sort_key)[0]
        available = _to_int(best.get("AvailableQty"))
        return best, ("PARTIAL FULFILMENT - supplier can only supply %d of %d units"
                      % (available, reorder_qty))

    # Tier 3 / 4 - no usable email anywhere, cannot be emailed
    pool = fulfilling if fulfilling else real
    best = sorted(pool, key=sort_key)[0]
    return best, ("NO SUPPLIER EMAIL - cannot send purchase order to %s"
                  % best.get("SupplierName", "supplier"))


def process_reorders(lowstock_csv, suppliers_csv):
    """
    Main entry point called from UiPath.
    Returns a JSON string: a list of reorder decisions.
    """
    products = _parse_csv(lowstock_csv)
    suppliers = _parse_csv(suppliers_csv)

    # Group suppliers by ProductID for quick lookup
    suppliers_by_product = {}
    for s in suppliers:
        pid = (s.get("ProductID") or "").strip()
        suppliers_by_product.setdefault(pid, []).append(s)

    results = []
    for p in products:
        pid = (p.get("ProductID") or "").strip()
        name = p.get("ProductName", "")
        current_stock = p.get("CurrentStock", "")
        minimum_stock = p.get("MinimumStock", "")
        raw_qty = p.get("ReorderQty", "")

        notes = []

        # --- Priority is calculated here, not passed through ---
        priority = calculate_priority(current_stock, minimum_stock)
        if priority == "UNKNOWN":
            notes.append("INVALID STOCK DATA - cannot determine priority")

        # --- Validate the reorder quantity before ordering anything ---
        if not _is_number(raw_qty):
            reorder_qty = 0
            notes.append("INVALID REORDER QTY - '%s' is not a number" % raw_qty)
        else:
            reorder_qty = _to_int(raw_qty)
            if reorder_qty <= 0:
                notes.append("INVALID REORDER QTY - must be greater than zero")

        best, supplier_note = choose_best_supplier(
            suppliers_by_product.get(pid, []), reorder_qty)
        if supplier_note:
            notes.append(supplier_note)

        if best is None:
            results.append({
                "ProductID": pid,
                "ProductName": name,
                # Integer fields are emitted as text on purpose. Newtonsoft maps
                # JSON integers to Int64, which UiPath's Filter Data Table
                # activity does not support.
                "CurrentStock": str(_to_int(current_stock)),
                "MinimumStock": str(_to_int(minimum_stock)),
                "ReorderQty": str(reorder_qty),
                "Priority": priority,
                "ChosenSupplier": "",
                "SupplierEmail": "",
                "SupplierPrice": 0.0,
                "EstimatedCost": 0.0,
                "UnitPriceText": "$0.00",
                "LineTotalText": "$0.00",
                "DeliveryDays": "",
                "Status": "REVIEW",
                "Note": " | ".join(notes)
            })
            continue

        supplier_price = _to_float(best.get("SupplierPrice"))
        if supplier_price <= 0:
            notes.append("INVALID SUPPLIER PRICE - cannot calculate cost")

        estimated_cost = round(supplier_price * reorder_qty, 2)

        # Only fully clean records are safe to auto-order
        status = "READY" if not notes else "REVIEW"

        results.append({
            "ProductID": pid,
            "ProductName": name,
            # Emitted as text - see note in the no-supplier branch above.
            "CurrentStock": str(_to_int(current_stock)),
            "MinimumStock": str(_to_int(minimum_stock)),
            "ReorderQty": str(reorder_qty),
            "Priority": priority,
            "ChosenSupplier": best.get("SupplierName", ""),
            "SupplierEmail": (best.get("SupplierEmail") or "").strip(),
            "SupplierPrice": supplier_price,
            "EstimatedCost": estimated_cost,
            # Pre-formatted currency text for the Word purchase order table.
            # Kept separate from the numeric fields so Excel can still total them.
            "UnitPriceText": "${:,.2f}".format(supplier_price),
            "LineTotalText": "${:,.2f}".format(estimated_cost),
            "DeliveryDays": best.get("DeliveryDays", ""),
            "Status": status,
            "Note": " | ".join(notes)
        })

    return json.dumps(results)


# ------------------------------------------------------------
# Self-test - runs only when executed directly.
# ------------------------------------------------------------
if __name__ == "__main__":
    lowstock = (
        "ProductID,ProductName,CurrentStock,MinimumStock,ReorderQty,UnitPrice,Priority\n"
        "101,Instant Noodles (carton),12,40,60,8.50,MEDIUM\n"
        "102,Canned Tuna (24 tin),5,30,50,15.00,HIGH\n"
        "104,Biscuits Assorted (box),0,20,35,9.40,HIGH\n"
        "105,Broken Qty Item,3,20,ABC,4.00,HIGH\n"
        "999,Ghost Item,1,10,20,5.00,HIGH\n"
    )
    suppliers = (
        "ProductID,SupplierName,SupplierEmail,SupplierPrice,AvailableQty,DeliveryDays\n"
        "101,PrimeSnacks,sales@primesnacks.example.com,8.50,300,5\n"
        "101,DailyGoods,reorder@dailygoods.example.com,7.80,800,2\n"
        "101,MegaBulk,orders@megabulk.example.com,9.20,1000,1\n"
        "102,DailyGoods,reorder@dailygoods.example.com,15.00,800,2\n"
        "102,IslandFresh,supply@islandfresh.example.com,14.20,40,3\n"
        "104,ValueMart,,9.40,400,4\n"
        "104,BudgetWhole,,10.00,350,6\n"
        "105,PrimeSnacks,sales@primesnacks.example.com,4.00,500,3\n"
        "999,,,,,\n"
    )

    output = process_reorders(lowstock, suppliers)
    print("Raw JSON output:\n", output, "\n")
    print("Readable:")
    for r in json.loads(output):
        print("  [%-6s] %-26s -> %-12s $%s x %s = $%-9s (%s)"
              % (r["Status"], r["ProductName"], r["ChosenSupplier"] or "-",
                 r["SupplierPrice"], r["ReorderQty"], r["EstimatedCost"],
                 r["Priority"]))
        if r["Note"]:
            print("           note: %s" % r["Note"])
