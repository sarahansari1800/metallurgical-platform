import streamlit as st
# st is the short form for Streamlit (Web UI).
import pandas as pd
# panda is imported here as pd to handle data library by reading database tables.

# from sqlalchemy import create_engine
# sqlalchemy here creates a connection to database in PostgreSQL for development phase. During the deployment phase, it will directly take the excel file from Github called approvedVersion.csv in CSV format.
# create_engine helps to create a connection for the database.
import io
# io helps in creating downloadable files which is needed as Excel export later by creating temporary file in the memory to generate excel files and downloading them from UI.

import re  
# re is a regular expression used for importing standard text in processing library of Python. This is not heavily used but implemented for potential pattern matching.

def format_chem_safe(text):
    text = str(text)
    # To ensure that the selected input is converted into a string despite of data missing or integer.

    # Converting simple numerals to subscripts like Fe2 → Fe₂
    subs = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

    result = ""
    i = 0
    # I is a pointer index that integrates throughout text, character by character. This helps in initialising the empty string for building the formatted results.

    while i < len(text):
        char = text[i]
        # This process one character at a time.

        # If we detect start of reference → copy everything unchanged
        if char == "[":
            end = text.find("]", i)
            if end != -1:
                result += text[i:end+1]  
                # Preserve references like [36, 45] as it is.
                i = end + 1
                continue

        # If the character is followed by number then convert it to subscript.
        if char.isalpha() and i + 1 < len(text) and text[i+1].isdigit():
            j = i + 1
            while j < len(text) and text[j].isdigit():
                j += 1

            result += char + text[i+1:j].translate(subs)
            i = j
            continue

        # Default character unchanged needed
        result += char
        i += 1

    return result

st.set_page_config(layout="wide")
# This helps in creating full width layout which is better for column and table handling interface.
st.title("Digital Platform for Valorization of Metallurgical By–Products")
# This line helps in displaying the title as the main heading in the top of the page.

# =====================================
# DATABASE STRUCTURE
# =====================================
#engine = create_engine(
#    "postgresql+psycopg2://faruqansari:userpass@localhost:5432/metallurgical_platform"
#)
# This line helps in connecting the Streamlit with PostgreSQL (metallurgical platform) using psycopg2 for development phase of the prototype. For deployment phase as mentioned it will directly take from CSV file.

@st.cache_data
def load_data():
    return pd.read_csv("approvedVersion.csv")

df = load_data()
# This reads the table present in the database into a Pandas Dataframe. Also makes the database run only once to make it robust.
cols = df.columns.tolist()
# This stores the names of the column in a list form. E.g., row[cols[0]] Industry / Process, row[cols[1]] Primary Source etc.

# =====================================
# SIDE PANEL IN THE UI
# =====================================
st.sidebar.header("Navigation Panel")
# Leads to creation of side panel bar in the UI and naming the header.

st.sidebar.markdown("### Database Overview")
# First section is created, under which static information is displaced,
st.sidebar.write("Total Number of Residues: 50")
st.sidebar.write("Total Number of Industries: 26")

industry = st.sidebar.selectbox(
    "Please Select the Industry / Material / Process",
    ["Select"] + sorted(df[cols[0]].dropna().unique())
)
# creates a dropdown functionality to select industry or material or process.
# below dropdown is depending on the above dropdown selection mentioning residue options.

if industry != "Select":
    residue_options = df[df[cols[0]] == industry][cols[2]].dropna().unique()

    residue = st.sidebar.selectbox(
        "Please Select the Byproduct",
        ["All"] + sorted(residue_options)
    )
else:
    residue = "All"

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    <div style="font-size: 12px; color: grey;">
    <i>*This prototype was developed by Sarah Ansari under the co-supervision of LUT University and VTT Finland as part of Master's thesis.</i>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================
# LANDING PAGE (INTRODUCTION PAGE)
# =====================================
if industry == "Select":
    
    st.markdown("## ⚙️ Platform Workflow")
    st.image("processFlow.png", width="stretch")

    st.markdown("## 🔬 Metallurgical Industries or Materials")
    st.image("examplesResidues.png", width="stretch")

# These conditions display the image that are present in the same folder (in this case Database).

    st.info("Select an industry or material from the navigation panel to begin.")
# The condition means if there are no selection made then keep on showing the introduction page.

# ===========================================
# MAIN DASHBOARD LOGIC PRESENT IN SIDE PANEL
# ===========================================
else:

    filtered = df[df[cols[0]] == industry]
# To filter out the information based on the selection of industry or process or material.

    if residue != "All":
        filtered = filtered[filtered[cols[2]] == residue]
# To filter out the information based on the selection of respective byproduct.


    st.divider()
# This creates the horizontal line to separate the sections.

    # =====================================
    # OVERVIEW 
    # =====================================
    st.subheader("🧭 Overview")
# this is representing the section heading.

    st.write(
        "This digital tool prototype supports decision–making for helping the user choose a suitable valorization pathway for selected metallurgical byproduct."
    )
# A short introduction note on what this UI is representing.

    if len(filtered) == 1:
        row = filtered.iloc[0]
# This selects the first matching for a single residue type and picks the first row of the filtered data.

        c1, c2, c3 = st.columns(3)
# This creates a layout with 3 columns.

        c1.markdown(f"**Industry or Material**  \n{row[cols[0]]}")
        c2.markdown(f"**Primary Source**  \n{format_chem_safe(row[cols[1]])}")
        # the condition format_chem_safe is used for converting the text into subscript if necessary.
        c3.markdown(f"**Byproduct Stream**  \n{row[cols[2]]}")
    else:
        st.info("Please select a specific material and byproduct stream from the navigation panel.")
# This info message pops up in case there is nothing selected in the side panel.

    # =====================================
    # MATCHMAKING SECTION
    # =====================================
    st.divider()
    st.subheader("🧩 Valorization Pathways Insight")
    # This section is a simple code to show briefly what can be possible valorization pathways for selected option. It is just for quick overview.

    st.caption(
        "The suggested valorization pathways represent initial screening options and are not exhaustive."
    )

    if len(filtered) > 0:

        text = (
            filtered[cols[4]].astype(str) + " " +
            filtered[cols[7]].astype(str)
        ).str.cat(sep=" ")
        # It combines the information present in column E (Valorization Pathways) and column H (End–use Applications)
        # in the excel database to search for keywords.

        words = text.lower().split()
        # Through this condition it converts all the words in the string to lowercase and splits them into individual words.

        # For instance,in order to avoid mismatching (between "co" from "composition") and improve keyword–based detection.

        suggestions = []
        # This list stores all the suggested valorization pathways based on detected metals or materials.

        # ====================================
        # MATCHMAKING BASED ON METAL KEYWORDS
        # ====================================

        if "fe" in words or "iron" in words:
            suggestions.append("Magnetic separation / Reduction / Smelting / Recycling / Pelletisation")

        if "cu" in words or "copper" in words:
            suggestions.append("Flotation / Hydrometallurgical leaching / Slag reduction / Electrorefining")

        if "zn" in words or "zinc" in words:
            suggestions.append("Waelz process / Hydrometallurgical leaching / Volatilization / Dechlorination")

        if "pb" in words or "lead" in words:
            suggestions.append("Hydrometallurgical leaching / Volatilization / Electrorefining / Stabilization")

        if "al" in words or "aluminum" in words or "aluminium" in words:
            suggestions.append("Hydrometallurgical leaching / Magnetic separation / Geopolymerization")

        if "mn" in words or "manganese" in words:
            suggestions.append("Acid leaching / Roasting / Precipitation")

        if "sn" in words or "tin" in words:
            suggestions.append("Gravity separation / Flotation / Carbothermic reduction / Acid leaching")

        if "li" in words or "lithium" in words:
            suggestions.append("Acid leaching / Smelting / Direct regeneration")

        if "co" in words or "cobalt" in words:
            suggestions.append("Acid leaching / Hydrometallurgical recovery")

        if "ni" in words or "nickel" in words:
            suggestions.append("Acid or alkali leaching / Neutralization")

        if "v" in words or "vanadium" in words:
            suggestions.append("Oxidation roasting / Selective leaching / Secondary smelting")

        if "ree" in words or "rees" in words or "rare" in words:
            suggestions.append("Acid or alkaline leaching / Roasting / Beneficiation")

        if "sc" in words or "scandium" in words:
            suggestions.append("Selective leaching")

        if "nb" in words or "ta" in words or "niobium" in words or "tantalum" in words:
            suggestions.append("Gravity separation / Acid leaching")

        if "mo" in words or "molybdenum" in words:
            suggestions.append("Oxidative roasting / Leaching")

        if "w" in words or "tungsten" in words:
            suggestions.append("Alkaline or acid leaching / Roasting")

        if "ti" in words or "titanium" in words:
            suggestions.append("Acid leaching / Thermal roasting")

        if "cr" in words or "chromium" in words:
            suggestions.append("Alkaline roasting / Reduction Cr(VI) → Cr(III) / Leaching")

        if "au" in words or "gold" in words:
            suggestions.append("Electrorefining / Leaching / Re–leaching")

        if "ag" in words or "silver" in words:
            suggestions.append("Electrorefining / Leaching")

        if "pgm" in words or "pgms" in words:
            suggestions.append("Smelting / Hydrometallurgical leaching / Electrorefining")

        if "as" in words or "arsenic" in words:
            suggestions.append("Stabilization / Leaching")

        if "cd" in words or "cadmium" in words:
            suggestions.append("Hydrometallurgical recovery / Stabilization")

        if "cl" in words or "chlorine" in words:
            suggestions.append("Dechlorination")

        if "s" in words or "sulfur" in words or "sulfide" in words:
            suggestions.append("Roasting / Stabilization / Bioleaching")

        if "cao" in words or "calcium" in words:
            suggestions.append("Carbonation / Cement applications / Stabilization")

        if "sio2" in words:
            suggestions.append("Mechanical activation / Geopolymerization")

        if "al2o3" in words:
            suggestions.append("Geopolymerization / Leaching")

        # =========================
        # OUTPUT
        # =========================
        if suggestions:
            for s in sorted(set(suggestions)):
                st.success("→ " + s)
        else:
            st.info("Further analysis required")
        # Here is the simple keyword–based decision coding system created to suggest the possible valorization options.

    # =====================================
    # CLEAN FUNCTION
    # =====================================
    def clean_text(x):
        return [i.strip() for i in str(x).replace("\n", ";").split(";") if i.strip()]
# Converts the text present in a string to bullet points.

    # =====================================
    # RESIDUE PROFILE
    # =====================================
    st.divider()
    st.subheader("🧪 Residue Profile")

    if len(filtered) == 1:

        row = filtered.iloc[0]

        left, right = st.columns(2)
# Divides the page into 2 separate sections


        # LEFT SIDE – PHYSICAL AND CHEMICAL
        with left:

            st.markdown("### ⚗️ Physicochemical Properties*")
            st.caption(
                "*The physicochemical properties are derived from literature studies and represent indicative ranges for preliminary screening purposes."
            )
            st.markdown(f"**Average Chemical Composition**  \n{format_chem_safe(row[cols[10]])}")

            st.markdown(f"**Chemical Formulae***  \n{format_chem_safe(row[cols[11]])}")
            st.caption(
                "*These represent the crystallographic phases rather than the intrinsic nature of the material or mineral's origin."
            )

            st.markdown(f"**Elemental Composition**  \n{row[cols[12]]}")
            st.markdown(f"**Physical State of Byproducts**  \n{row[cols[13]]}")
            st.markdown(f"**Production Content**  \n{row[cols[14]]}")
            st.markdown(f"**pH Indicator**  \n{format_chem_safe(row[cols[15]])}")
            st.markdown(f"**Water Content**  \n{row[cols[16]]}")


        # RIGHT SIDE – PROCESSING & APPLICATIONS
        with right:

            st.markdown("### ⚙ Processing and Applications")

            st.markdown(f"**Process Stage of Generation**  \n{row[cols[3]]}")

            st.markdown("**Valorization Pathways or Processings**")
            for i in clean_text(row[cols[4]]):
                st.markdown(f"- {format_chem_safe(i)}")

            st.markdown("**Typical Issues**")
            for i in clean_text(row[cols[5]]):
                st.markdown(f"- {i}")

            st.markdown(f"**Techno–Economic Aspects**  \n{row[cols[6]]}")

            st.markdown("**End–use Applications**")
            for i in clean_text(row[cols[7]]):
                st.markdown(f"- {format_chem_safe(i)}")

    # =====================================
    # CRM and SRM SECTION
    # =====================================
    st.divider()
    st.subheader("🔋 Critical and Strategic Materials")

    if len(filtered) == 1:
        st.success(f" Associated Critical Raw Materials (CRMs) [39]: {row[cols[8]]}")
        st.info(f"Associated Strategic Raw Materials (SRMs) [39]: {row[cols[9]]}")
# This section is for mentioning what CRMs and SRMs are present in the selected residues.

# =====================================
    # DOWNLOAD SECTION
    # =====================================
    st.divider()
    st.subheader("⬇ Download Information")

    def export_excel(data):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            data.to_excel(writer, index=False)
        return buffer.getvalue()

    if len(filtered) > 0:
        st.markdown("• Filtered Database (xlsx format)")
        st.download_button(
            label="Download",
            data=export_excel(filtered),
            file_name="filtered_database.xlsx"
        )

    # Reference file
    with open("referencesList.docx", "rb") as file:
        reference_file = file.read()

    st.markdown("• List of References (docx format)")
    st.download_button(
        label="Download",
        data=reference_file,
        file_name="referencesList.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )