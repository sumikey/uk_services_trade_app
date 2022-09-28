# ------------------------ IMPORTS
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------ SET CONFIG

# setting the page title, icon and opening in wide mode
st.set_page_config(page_title = "UK_Services_Trade_Explorer", page_icon = 'star',layout="wide")

st.write("# UK Services Trade by Mode of Supply")
st.write("ONS trade by mode of supply, includes experimental data")
st.write("---")

df = (pd.read_parquet("./data/mos/services_mode_supply.parquet"))
df['trade_val'] = df['2020 estimate'].mul(1_000_000)

# select flow
flow_select = st.selectbox("Which flow would you like to select?", df.Direction.unique())
# filter df on this basis
df2 = df.query('Direction == @flow_select')

# select partners
partner_select = st.multiselect("Which partner(s) would you like to select", df2.Country.unique())
df3 = df2.query('Country.isin(@partner_select)')

# which modes
modes_select = st.multiselect("Which modes would you like to include?", df.Mode.unique())
df4 = df3.query('Mode.isin(@modes_select)')

if len(df4['Service account'].unique()) != 1:
    service_select = st.selectbox("Which service would you like to select", df4['Service account'].unique())
    df4 = df[df4['Service account'] == service_select]
    
df4 = df4.sort_values(by=['Mode','trade_val'], ascending=[True, True])

fig = px.bar(df4, x='Mode', y='trade_val', color='Country', barmode='group',
             height=500, width=750,
             title=f"UK {flow_select} by mode with {partner_select} in 2020, £s")
fig.update_layout(xaxis_title='', yaxis_title='Trade Value in 2020, £s')

st.plotly_chart(fig)

