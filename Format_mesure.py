import csv
from pathlib import Path

MESURE_IN_CSV = ""

def resolve_contract_id(env):
    """
        Read de csv file and resolve the Odoo contract ids
        Parameter : env 
        Return : dict { id_csv : id_odoo } (return None if not found)
    """
    contract_col = "contrat_id" # change to ref 
    odoo_field = "id" # change to name

    with MESURE_IN_CSV.open("r", encoding="utf-8", newLine="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if contract_col not in (reader.fieldnames or []):
            raise ValueError(
                f"Column '{contract_col}' not found."
                f"Available : {reader.fieldnames}"
            )
        csv_ids = (
            str(row[contract_col]).strip()
            for row in reader
            if row.get(contract_col) and str(row[contract_col]).strip
        )

    Contract = env["gmao.contract"]
    index = {}
    for contract in Contract.search([]):
        val = getattr(contract, odoo_field)
        if val is None:
            continue
        key = str(val).strip()
        if key in index:
            print(f"Odood Duplicate : {key}")
        index[key] = contract.id

    mapping = {}
    not_found = []
    for csv_id in csv_ids:
        if csv_id in index:
            mapping[csv_id] = index[csv_id]
        else:
            mapping[csv_id] = None
            not_found.append(csv_id)

    print(f"IDs : {len(csv_ids)}")
    print(f"IDs found : {len(csv_ids) - len(not_found)}")
    print(f"IDs not found : {len(not_found)}")

    if not_found:
        print(f"Non trouvés     : {not_found[:10]}")

    return mapping

def write_mapping_report(mapping, output_path, all_csv_ids):
    """Écrit un rapport complet du mapping."""
    with Path(output_path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["contrat_id", "odoo_id", "status"])

        for csv_id in sorted(all_csv_ids):
            odoo_id = mapping.get(csv_id)
            status = "OK" if odoo_id is not None else "NOT_FOUND"
            writer.writerow([csv_id, odoo_id or "", status])

        # Ligne de résumé
        found = sum(1 for v in mapping.values() if v is not None)
        total = len(mapping)
        writer.writerow([])
        writer.writerow(["Total", total, ""])
        writer.writerow(["Found", found, ""])
        writer.writerow(["Not found", total - found, ""])


# def resolve_contract_id(env, csv_path, contract_col="contrat_id",
#                         odoo_field="name", delimiter=";", encoding="utf-8"):
#     csv_path = Path(csv_path)
#     if not csv_path.exists():
#         raise FileNotFoundError(f"CSV not found: {csv_path}")

#     # 1. Lecture CSV
#     with csv_path.open("r", encoding=encoding, newline="") as f:
#         reader = csv.DictReader(f, delimiter=delimiter)
#         if contract_col not in (reader.fieldnames or []):
#             raise ValueError(
#                 f"Column '{contract_col}' not found. "
#                 f"Available: {reader.fieldnames}"
#             )
#         csv_ids = {
#             str(row[contract_col]).strip()
#             for row in reader
#             if row.get(contract_col) and str(row[contract_col]).strip()
#         }

#     # 2. Index Odoo
#     Contract = env["gmao.contract"]
#     index = {}
#     for contract in Contract.search([]):
#         val = getattr(contract, odoo_field, None)
#         if val is None:
#             continue
#         key = str(val).strip()
#         if key in index:
#             print(f"Odoo Duplicate: {key} (ids {index[key]} and {contract.id})")
#         index[key] = contract.id

#     # 3. Matching
#     mapping = {cid: index.get(cid) for cid in csv_ids}
#     not_found = [cid for cid, oid in mapping.items() if oid is None]

#     # 4. Rapport
#     print(f"IDs          : {len(csv_ids)}")
#     print(f"IDs found    : {len(csv_ids) - len(not_found)}")
#     print(f"IDs not found: {len(not_found)}")
#     if not_found:
#         print(f"Not found    : {not_found[:10]}")

#     return mapping
