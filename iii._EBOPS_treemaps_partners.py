#------------------------- IMPORT PACKAGES USED
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# setting the page title, icon and opening in wide mode
st.set_page_config(page_title = "UK_Services_Trade_Explorer", page_icon = 'star',layout="wide")

#------------------------- TITLE AND BASIC PAGE INTRO

# make a title & Intro section
st.title('UK Services Trade - EBOPS2010 Classification across partners')
st.write('---')
st.write("""This section allows you to compare services trade for a chosen type (either at the BPM 12 category level, or at limited number of the EOPS 2010 levels) across a range of selected partners. Choose which trade flow and partners you would like to compare across. You can also choose which chart types you would like to show, with the options being Stacked bar charts, stacked area charts and line charts. All three types will show absolute values, and both year-on-year and quarter-on-quarter change in £s. Line charts (which are not stacked) will additional show change in percentage terms.""" )

#------------------------- DATA LOADING & PREPROCESSING

# load_preprocessed 
df = pd.read_parquet("./data/services_trade_type_country.parquet")

# melt the dataframe
df2 = (df
        .melt(id_vars=df.columns[:7], var_name='quarter')
        .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)))
)

# st.write(df2.value.dtype)

# select which type of service
service_select = st.selectbox("What type of services would you like to compare across the group?",
                             df2.service_code_desc.unique(),
                             index=0)

# select time
time_select = st.multiselect("What time period would you like included? Last four quarter by default?",
                             df2.quarter.unique(),
                             default = df2.quarter.unique()[-4:]
                             )

# select flow
flow_select = st.multiselect("What flow direction would you like to explore?",
                            ['Exports','Imports'])

st.write("Would you like to make a custom list of countries or use a pre-set list?")
# for choosing whether to make a list, or use a preset
# create 2x columns
col1, col2, col3 = st.columns(3)
with col1:  # for set lists
    set_list = st.checkbox("A pre-set list of countries")
with col2:  # for a custom list
    cus_list = st.checkbox("Make a custom list of countries")
with col3:
    world_list = st.checkbox("All countries.")

if cus_list + set_list + world_list == 1:
    
    if world_list == 1: 
        country_list = list(df2.country.unique())
        country_list.remove('Total EU27')
        country_list.remove('World total')
        country_list.remove('Rest of World')
         
    elif cus_list == 1:
        country_list = st.multiselect("Which countries would you like in your list?", 
                                      df2.country.unique(),
                                      default=['China','Japan','India','South Korea'])
    
    elif set_list == 1:
        chosen_set_list = st.selectbox("Which pre-set list would you like to use",
                                      ['G20', 'BRICS',"G7"])
        if chosen_set_list == "G7":
            country_list = ['United States inc Puerto Rico','Italy','Germany',
                           'France','Canada','Japan']
        
        elif chosen_set_list == "G20":
            country_list = ['United States inc Puerto Rico','Italy','Germany','France',
                           'Australia','Canada','Japan','South Korea','Saudi Arabia',
                           'India','Russia','South Africa','Turkey','Argentina',
                           'Brazil','Mexico','China','Indonesia']
        elif chosen_set_list == "BRICS":
            country_list = ['Brazil','China','India','South Africa','Russia']
    
    # now subset the dataframe by our chosen selectors
    df3 = (df2
            .query('quarter.isin(@time_select)')
            .query('country.isin(@country_list)')
            .query('service_code_desc == @service_select')
            .query('direction == @flow_select')
          )
    
    # now remove our as category dtypes
    for col in df3.columns[:7]:
        if df3[col].dtype.name == "category":
            df3[col] = df3[col].astype('str')
    
    # first drop the quarter column
    df4 = (df3
            .drop(columns='quarter')
          )
        
    # now groupby everything other than value
    df5 = (df4
            .groupby(by=list(df4.columns)[:-1])['value'].sum()
            .reset_index()
            .assign(value= lambda x: x.value.div(1000).round(2))
          )
    
    # for val in df4.value:
    #     st.write(val)
            
    
    # now plot a treemap
    fig1 = px.treemap(df5,
                     path=['country'],
                     values='value',
                     title=f"UK {flow_select} of {service_select} (to/from selected partners over chosen period), £s billons",
                     height=700, width=1200)
    
    st.plotly_chart(fig1)

# else:
#     st.write("Please select one (and only one) option.")

    
# NOT USED
    
# st.table(df2.country.unique())

# #------------------------- DATA PREPROCESSING

# # change categories back to strings (makes groupby faster)
# for col in df.columns: 
#     if df[col].dtype.name == "category": # if its a category
#         df[col] = df[col].astype('str') # convert to string
        
# df2 = (df
#         .melt(id_vars=df.columns[:7], var_name='quarter')
#         .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)))
#       )

#st.table(df2)

# fig = px.treemap(df,
#                 path = [''])