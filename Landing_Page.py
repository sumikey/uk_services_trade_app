# ------------------------ IMPORTS
import streamlit as st

# ------------------------ SET CONFIG

# setting the page title, icon and opening in wide mode
st.set_page_config(page_title = "UK_Services_Trade_Explorer", page_icon = 'star',layout="wide")

# ----------------

st.write("# A mini web-app for exploring UK services trade")
st.write("---")

st.write("""
### Contents

*Includes*
- UK Services Trade by Type (ONS)
- FATS Data (Eurostat, ONS)
  
  
*In Future*
- Services Trade (OECD-WTO BaTiS)
- UK Services trade by Modes of Supply (ONS)
- Total Trade by goods and services (IMF)

""")
