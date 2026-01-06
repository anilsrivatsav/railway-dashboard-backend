import pandas as pd
from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO

def export_to_csv(data, filename):
    df = pd.DataFrame([item.__dict__ for item in data])
    csv = StringIO()
    df.to_csv(csv, index=False)
    csv.seek(0)
    return StreamingResponse(csv, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}.csv"
    })

def export_to_excel(data, filename):
    df = pd.DataFrame([item.__dict__ for item in data])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": f"attachment; filename={filename}.xlsx"
    })