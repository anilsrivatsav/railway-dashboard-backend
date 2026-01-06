import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

BASE_URL = "http://127.0.0.1:8000"

# --- Helper functions ---
def sync_all():
    resp = requests.post(
        f"{BASE_URL}/sync/all",
        params={"sheet_id": "1JSlf6FOZMlSrb2wiAcb0LTk2BZYDPzvC98gNLfUDR-0"},
    )
    return resp.json() if resp.status_code == 200 else {"error": resp.text}

def health_check():
    resp = requests.get(f"{BASE_URL}/health/sheet")
    return resp.json() if resp.status_code == 200 else {"error": resp.text}

def list_items(endpoint):
    resp = requests.get(f"{BASE_URL}/{endpoint}/")
    return resp.json() if resp.status_code == 200 else []

def delete_item(endpoint, item_id):
    return requests.delete(f"{BASE_URL}/{endpoint}/{item_id}")

def update_item(endpoint, item_id, data):
    return requests.put(f"{BASE_URL}/{endpoint}/{item_id}", json=data)

def create_item(endpoint, data):
    return requests.post(f"{BASE_URL}/{endpoint}/", json=data)

def get_report(path, params=None):
    resp = requests.get(f"{BASE_URL}{path}", params=params or {})
    return resp.json() if resp.status_code == 200 else {"error": resp.text}

def generate_pdf(df, title="Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align="C")

    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)

    # Data rows
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# --- Main app ---
def main():
    st.set_page_config(page_title="Railway Dashboard", layout="wide")
    st.title("🚆 Railway Management Dashboard")

    with st.sidebar:
        st.header("📋 Navigation")
        menu = [
            "Stations", "Units", "Earnings",
            "🩺 Health Check", "🔄 Sync All",
            "📈 Reports"
        ]
        choice = st.radio("", menu)

    st.markdown(
        "<style>div.block-container{padding-top:1rem;}</style>",
        unsafe_allow_html=True
    )

    # Sync & Health
    if choice == "🔄 Sync All":
        st.subheader("🔄 Sync All Data")
        if st.button("Run Sync All"):
            result = sync_all()
            st.success("Sync completed!")
            st.json(result)

    elif choice == "🩺 Health Check":
        st.subheader("💡 Google Sheet Health Check")
        if st.button("Run Health Check"):
            result = health_check()
            st.json(result)

    # CRUD pages
    elif choice in ("Stations", "Units", "Earnings"):
        endpoint = choice.lower()
        st.subheader(f"📊 {choice} Table")
        items = list_items(endpoint)

        if items:
            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"No {choice} data found.")

    # Reports page
    elif choice == "📈 Reports":
        st.subheader("📈 Advanced Analytics & Reports")

        report_type = st.selectbox("Select Report Type", [
            "Revenue Trend",
            "Top N Units",
            "Pending Payments",
            "Upcoming Contract Expiry",
            "Summary by Zone",
            "Summary by Categorization",
            "Summary by Payment Head",
            "Custom Report"
        ])

        station_filter = st.text_input("Station Code (optional)")
        zone_filter = st.text_input("Zone (optional)")
        categorization = st.text_input("Categorization (optional)")
        period = st.selectbox("Period", ["Monthly", "Quarterly", "Yearly", "Custom"])
        top_n = st.number_input("Top N (if applicable)", min_value=1, max_value=100, value=10)
        start_date = st.date_input("Start Date (if custom period)")
        end_date = st.date_input("End Date (if custom period)")
        payment_status = st.selectbox("Payment Status", ["All", "Paid", "Unpaid", "Overdue", "Upcoming"])
        chart_type = st.selectbox("Chart Type", ["Table", "Bar", "Line", "Pie"])

        if st.button("Run Report"):
            params = {
                "station": station_filter,
                "zone": zone_filter,
                "categorization": categorization,
                "period": period.lower(),
                "top_n": top_n,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "payment_status": payment_status.lower()
            }
            data = get_report("/reports/advanced", params)
            if "error" in data:
                st.error(data["error"])
                return

            df = pd.DataFrame(data)
            if df.empty:
                st.warning("No data returned for selected filters.")
                return

            st.success(f"✅ {len(df)} records retrieved.")

            # Charting section
            if chart_type == "Table":
                st.dataframe(df, use_container_width=True)
            elif chart_type == "Bar":
                st.plotly_chart(px.bar(df, x=df.columns[0], y=df.columns[1]), use_container_width=True)
            elif chart_type == "Line":
                st.plotly_chart(px.line(df, x=df.columns[0], y=df.columns[1]), use_container_width=True)
            elif chart_type == "Pie":
                st.plotly_chart(px.pie(df, names=df.columns[0], values=df.columns[1]), use_container_width=True)

            # Download buttons
            csv_data = df.to_csv(index=False).encode("utf-8")
            excel_data = BytesIO()
            df.to_excel(excel_data, index=False)
            excel_data.seek(0)
            pdf_data = generate_pdf(df, title=report_type)

            st.download_button("📥 Download CSV", csv_data, file_name="report.csv", mime="text/csv")
            st.download_button("📥 Download Excel", excel_data, file_name="report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.download_button("📥 Download PDF", pdf_data, file_name="report.pdf", mime="application/pdf")


if __name__ == "__main__":
    main()