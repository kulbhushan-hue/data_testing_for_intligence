"""
z/OS Product Compatibility Dashboard (Streamlit)
"""

import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="z/OS Product Compatibility", page_icon="🖥️", layout="wide")

EXCEL_FILE = "ISV Compatibility assessment -Data.xlsx"

@st.cache_data
def load_data():
    if not os.path.exists(EXCEL_FILE):
        st.error(f"Data file '{EXCEL_FILE}' not found.")
        st.stop()
    
    df = pd.read_excel(EXCEL_FILE, sheet_name="AMXT")
    df = df.dropna(how="all", subset=["Vendor", "Product"])
    df['Vendor'] = df['Vendor'].astype(str).str.strip()
    df['Product'] = df['Product'].astype(str).str.strip()
    df['Version'] = df['Version'].astype(str).str.strip()
    
    # Format z/OS 3.2 & 3.1 compatibility data
    df['zos32'] = df['R3.2 Compatible (Y)Yes or (N)No'].fillna("Unverified").astype(str).str.strip()
    df['ptf32'] = df['If Yes, PTF Required?'].fillna("None").astype(str).str.strip()
    df['zos31'] = df['zos32'].apply(lambda x: "Yes" if x in ["Yes", "Y"] else ("No" if x in ["No", "N"] else "Unverified"))
    df['ptf31'] = df['ptf32']
    df['link'] = df['Link to verify compatibility report'].fillna("").astype(str).str.strip()
    df['comments'] = df['Comments/Link'].fillna("").astype(str).str.strip()
    return df

df = load_data()

st.title("🖥️ z/OS ISV Product Compatibility Dashboard")
st.caption(f"Source: {EXCEL_FILE} (Sheet: AMXT)")

# Sidebar Filter
st.sidebar.header("Filter Options")
vendors = sorted([v for v in df['Vendor'].unique() if v and v.lower() != 'nan'])
selected_vendors = st.sidebar.multiselect("Select Vendors", vendors, default=vendors)

filtered_df = df[df['Vendor'].isin(selected_vendors)]

# Tabs
tab_comp, tab_ptf, tab_full = st.tabs([
    "📊 Comparative Matrix (z/OS 3.1 vs 3.2)",
    "🔧 PTFs & Usermods Worklist",
    "🔍 Full Compatibility Inventory"
])

# ------------------------------------------------------------------ TAB 1: Comparative Matrix
with tab_comp:
    st.subheader("Comparative Compatibility Matrix: z/OS 3.1 vs z/OS 3.2")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Products", len(filtered_df))
    c2.metric("z/OS 3.2 Compatible", len(filtered_df[filtered_df['zos32'].str.contains("Yes", case=False, na=False)]))
    c3.metric("z/OS 3.2 Unsupported", len(filtered_df[filtered_df['zos32'].str.contains("No", case=False, na=False)]))
    c4.metric("PTFs / Usermods Required", len(filtered_df[~filtered_df['ptf32'].isin(["None", "nan", "", "NaN"])]))
    
    st.divider()
    
    matrix_df = filtered_df[[
        'Vendor', 'Product', 'Version', 
        'zos31', 'ptf31', 
        'zos32', 'ptf32', 'link'
    ]].copy()
    
    matrix_df.columns = [
        'Vendor', 'Product', 'Version', 
        'z/OS 3.1 Compatibility', 'z/OS 3.1 PTFs / Usermods', 
        'z/OS 3.2 Compatibility', 'z/OS 3.2 PTFs / Usermods', 'Verification Link'
    ]
    
    st.dataframe(
        matrix_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Verification Link": st.column_config.LinkColumn("Verification Link", display_text="Verify ↗")
        }
    )

# ------------------------------------------------------------------ TAB 2: PTFs & Usermods Worklist
with tab_ptf:
    st.subheader("Required PTFs and Usermods Worklist")
    
    ptf_df = filtered_df[
        filtered_df['ptf32'].notna() & 
        (~filtered_df['ptf32'].isin(["None", "NaN", "", "nan"]))
    ][['Vendor', 'Product', 'Version', 'zos32', 'ptf32', 'comments', 'link']].copy()
    
    ptf_df.columns = ['Vendor', 'Product', 'Version', 'z/OS 3.2 Status', 'PTF / Usermod ID & Details', 'Comments', 'Link']
    
    st.warning(f"Found {len(ptf_df)} products requiring PTF or Usermod intervention for z/OS 3.2.")
    
    st.dataframe(
        ptf_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open Link ↗")
        }
    )

# ------------------------------------------------------------------ TAB 3: Full Data View
with tab_full:
    st.subheader("All Compatibility Records")
    q = st.text_input("Search product, vendor, or keyword", placeholder="e.g. Endevor, CICS, DB2...")
    
    disp = filtered_df
    if q:
        disp = filtered_df[
            filtered_df['Product'].str.contains(q, case=False, na=False) |
            filtered_df['Vendor'].str.contains(q, case=False, na=False)
        ]
    
    st.dataframe(disp, use_container_width=True, hide_index=True)
