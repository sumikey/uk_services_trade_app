# ------------------------ IMPORTS
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------ SET CONFIG

# setting the page title, icon and opening in wide mode
st.set_page_config(page_title = "UK_Services_Trade_Explorer", page_icon = 'star',layout="wide")

st.write("# China's Services Trade on a per country basis")
st.write("OECD-WTO Balanced Trade in Services Dataset [BaTiS](https://www.oecd.org/sdd/its/balanced-trade-statistics.htm)")
st.write("---")

# read in our dataframe
df = pd.read_parquet('./data/batis/batis_china_ts.parquet')

# ----------CREATE 2x NEW FRAMES

# select only rows with countries (i.e. with aggregates removed)
df_co = df[ df.type_Partner == 'c']

# create a selectbox to choose what services we look at
services_selection = st.selectbox('What services would you like to look for?', df_co.service.unique())

# subset our dataframe by our desired selection 
df_co_ser = df_co[ df_co.service == services_selection]

# -------- PLOTTING CHINA's GLOBAL EXPORTS & IMPORTS WITH THIS DATA

# using groupby to create a df we can ploy
plot_df = df_co_ser.groupby(['Year','Flow'])['Balanced_value'].sum().unstack()
# create our plotly figure
fig = px.line(plot_df,
             x=plot_df.index, y = plot_df.columns,
             width=1000, height=650,
             title = f"China's annual trade in {services_selection} with the world, USD",
             )
# update layout - axis titles and font-size
fig.update_layout(
                xaxis_title = "",
                yaxis_title = "Value USD",
                font=dict(size=21)
                )
# display figure with streamlit
st.plotly_chart(fig)

# ---- choose flow and countries to compare

flow_choice = st.selectbox("Which flow direction would you like to choose?", df_co_ser.Flow.unique())
partner_choice = st.multiselect("Which partners would you like to compare", df_co_ser.partner.unique(), default=['United Kingdom','Germany','France'])

plot_df = (df_co_ser
              .query('Flow == @flow_choice')
              .query('partner.isin(@partner_choice)')
          )

# create our plotly figure
fig = px.line(plot_df,
             x='Year', y = 'Balanced_value', color='partner',
             width=1000, height=650,
             title = f"China's annual trade in {services_selection} with selected partners, USD",
             )

st.plotly_chart(fig)