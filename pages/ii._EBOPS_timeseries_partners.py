#------------------------- IMPORT PACKAGES USED
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
#from pages.helper_functions import preproc_serviceByType_df

# setting the page title, icon and opening in wide mode
st.set_page_config(page_title = "UK_Services_Trade_Explorer", page_icon = 'star',layout="wide")

#------------------------- TITLE AND BASIC PAGE INTRO

# make a title & Intro section
st.title('UK Services Trade by Type and Partner')
st.write('---')
st.write("""This section allows you to compare services trade for a chosen type (either at the BPM 12 category level, or at limited number of the EOPS 2010 levels) across a range of selected partners. Choose which trade flow and partners you would like to compare across. You can also choose which chart types you would like to show, with the options being Stacked bar charts, stacked area charts and line charts. All three types will show absolute values, and both year-on-year and quarter-on-quarter change in £s. Line charts (which are not stacked) will additional show change in percentage terms.""" )

#------------------------- DATA LOADING

# load_preprocessed 
df = pd.read_parquet("./data/services_trade_type_country.parquet")

#-------- SELECT BOXES TO CHOOOSE OPTIONS

chosen_service = st.selectbox("Which service would you like to compare across?", df.service_code_desc.unique())
chosen_flow = st.selectbox("Which trade flow would you like to choose?", ['Exports', 'Imports'])
compare_partners = st.multiselect("Which partners would you like to compare scross", df.country.unique(), default='China')

#-------- DATA PREPROCESSING, BASED ON OPTIONS

# create a standard "long dataframe"
# first makes selection based on option boxes select options
# then melt it (melt the quarters into one column); and fix non-numeric values
df2 = (df
         # filter based on selectors
         .query('service_code_desc == @chosen_service') 
         .query('country.isin(@compare_partners)')
         .query('direction == @chosen_flow')
         .melt(id_vars=df.columns[:7], var_name='quarter') # melt
         .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)).mul(1_000_000)) # make our values numeric
      )

# create a time series chart so that can do diff and pct_change
# df2 has already been filtered for service, country and flow
df3 = df2.pivot(index='quarter',columns='country',values='value')

# create a select box for chosen type of chart
chosen_chart = st.selectbox("What type of chart would you prefer?", ["Stacked-bar", "Line-chart", "Area-chart"], index=0)

# if stacked bar create three charts
if chosen_chart == "Stacked-bar":
    # absolute values (from df2)
    fig1 = px.bar(df2, x='quarter', y='value', color='country',
                  height=600, width=1200,
                  title=f"UK services exports of {df2.service_type[1]} to {compare_partners}"
                 )
    fig1.update_layout(xaxis_title="",yaxis_title="Exports £s")
    # diff YoY values (from df3)
    fig2 = px.bar(df3.diff(4).iloc[4:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"YoY Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig2.update_layout(xaxis_title="",yaxis_title="YoY change in exports, £s")
    # diff QoQ values (from df3)
    fig3 = px.bar(df3.diff(1).iloc[1:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"QoQ Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig3.update_layout(xaxis_title="",yaxis_title="QoQ change in exports, £s")
    
    
    #st.table(df3)

elif chosen_chart == "Area-chart":
    # absolute values (from df2)
    fig1 = px.area(df2, x='quarter', y='value', color='country',
                  height=600, width=1200,
                  title=f"UK services exports of {df2.service_type[1]} to {compare_partners}"
                 )
    fig1.update_layout(xaxis_title="",yaxis_title="Exports £s")
    # diff YoY values (from df3)
    fig2 = px.area(df3.diff(4).iloc[4:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"YoY Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig2.update_layout(xaxis_title="",yaxis_title="YoY change in exports, £s")
    
    fig3 = px.area(df3.diff(1).iloc[1:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"QoQ Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig3.update_layout(xaxis_title="",yaxis_title="QoQ change in exports, £s")
    
    
elif chosen_chart == "Line-chart":
    # absolute values (from df2)
    fig1 = px.line(df2, x='quarter', y='value', color='country',
                  height=600, width=1200,
                  title=f"UK services exports of {df2.service_type[1]} to {compare_partners}"
                 )
    fig1.update_layout(xaxis_title="",yaxis_title="Exports £s")
    # diff YoY values (from df3)
    fig2 = px.line(df3.diff(4).iloc[4:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"YoY Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig2.update_layout(xaxis_title="",yaxis_title="YoY change in exports, £s")
    # % change YoY values (from df3)
    fig3 = px.line(df3.pct_change(4).mul(100).iloc[4:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"YoY Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig3.update_layout(xaxis_title="",yaxis_title="YoY change in exports, %")
    # diff QoQ values (from df3)
    fig4 = px.line(df3.diff(1).iloc[1:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"QoQ Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig4.update_layout(xaxis_title="",yaxis_title="QoQ change in exports, £s")
    # % change QoQ values (from df3)
    fig5 = px.line(df3.pct_change(1).mul(100).iloc[1:,:].reset_index(), x='quarter', y=df3.columns,
                 height=600, width=1200,
                 title=f"QoQ Change in £s in UK services exports of {df2.service_type[1]} to {compare_partners}")
    fig5.update_layout(xaxis_title="",yaxis_title="QoQ change in exports, %")
    
    
st.plotly_chart(fig1)
st.plotly_chart(fig2)
st.plotly_chart(fig3)
try: st.plotly_chart(fig4) ; st.plotly_chart(fig5)
except: pass
