"""Importer: reads data/CMMC L2 SSP.xlsx and populates assessment fields.
Expected columns:
  - requirement_id
  - assessment_objectives
  - assessment_methods
"""
import os
import pandas as pd
from sqlmodel import Session, select
from .main import engine, Control

XLSX_PATH = "/data/CMMC L2 SSP.xlsx"
COL_REQ = "requirement_id"
COL_OBJ = "assessment_objectives"
COL_MTH = "assessment_methods"

def run():
    if not os.path.exists(XLSX_PATH):
        print(f"Excel not found at {XLSX_PATH}")
        return
    df = pd.read_excel(XLSX_PATH)
    lc = {c.lower().strip(): c for c in df.columns}
    for need in (COL_REQ, COL_OBJ, COL_MTH):
        if need not in lc:
            raise SystemExit(f"Missing required column in Excel: {need}")
    with Session(engine) as s:
        for _, row in df.iterrows():
            rid = str(row[lc[COL_REQ]]).strip()
            if not rid:
                continue
            obj = None if pd.isna(row[lc[COL_OBJ]]) else str(row[lc[COL_OBJ]])
            mth = None if pd.isna(row[lc[COL_MTH]]) else str(row[lc[COL_MTH]])
            ctrl = s.exec(select(Control).where(Control.requirement_id==rid)).first()
            if not ctrl:
                ctrl = Control(requirement_id=rid, domain="Unknown", title=rid, statement="")
            ctrl.assessment_objectives = obj
            ctrl.assessment_methods = mth
            s.add(ctrl)
        s.commit()
    print("Import complete.")

if __name__ == "__main__":
    run()
