#------------------------- IMPORT PACKAGES USED
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import pickle

# setting the page title, icon and opening in wide mode
st.set_page_config(page_title = "UK_Services_Trade_Explorer", page_icon = 'star',layout="wide")

# ------------------------ IMPORT DATA AND PICKLE FILES

# make a title & Intro section
st.title('Outwards Foreign Affiliates Statistics (FATS)')
st.write('---')
st.write("""This section shows foreign affiliates statistics published by Eurostat. These statistics allow you to explore the revenues and employees (as well as the number of companies) of the overseas affiliates of European companies. You can explore the affiliates across different markets, for different reporter (including the UK) and across different sectors. By default, the charts will show total services at the industry but this can be changed -- you can also explore non-services industries. The charts are full interactive.""")

# read in our data file
df = pd.read_parquet("./data/fats/cats_fats_df.parquet")

# create a melted version for easier plotting
mdf = (df
        .melt(id_vars = df.columns[:5], var_name='year')
        .assign(year = lambda x: x.year.astype('int'))
      )

# create a list of names for reading our pickle files
dict_list_names = ['geo_dict', 'rev_geo_dict', 'indic_dict', 'rev_indic_dict',
                  'part_dict', 'rev_part_dict','nace_dict','rev_nace_dict']

# reading in our pickle files
dict_collector_list = [] # create a list to collect loop variables
for name in dict_list_names: # use our list of names
    file = open(f"./data/fats/{name}.txt", "rb")  # open the 'named' file
    dictob = pickle.load(file)  # load it into a loop variable dictob
    file.close() # close our file 
    dict_collector_list.append(dictob) # append our dictob to a list

# unpack our collector list into 8 separate dictionaries
geo_dict, rev_geo_dict, indic_dict, rev_indic_dict, part_dict, rev_part_dict, nace_dict, rev_nace_dict = dict_collector_list
    
# --------

st.write("How would you like to analyse?")

# --- ONE REPORTER MUL MARKETS, SINGLE INDUSTRY

one_reporter_mul_markets = st.checkbox("Examine one reporter across multiple markets for a single industry")

if one_reporter_mul_markets:
    
    # use our dictionaries to make choices
    indic_select = st.selectbox("Which indicator?", rev_indic_dict.keys(), index=2)
    markets_select = st.multiselect("Which markets?", rev_part_dict.keys(), default=['China except Hong Kong', 'Hong Kong'])
    reporter_select = st.selectbox("Which reporter?", rev_geo_dict.keys(), list(rev_geo_dict.keys()).index('United Kingdom'))
    industry_select = st.selectbox("Which industry?", rev_nace_dict.keys(), 
                                   list(rev_nace_dict.keys()).index('Services (except public administration, defense, compulsory social security, activities of households as employers and extra-territorial organisations and bodies)'))
    
    # now "reverse" these choices to get codes
    indic_ = rev_indic_dict[indic_select]
    markets_ = [rev_part_dict[x] for x in markets_select]
    reporter_ = rev_geo_dict[reporter_select]
    industry_ = rev_nace_dict[industry_select]
    
    plot_df = (mdf
                .query('nace_r2 == @industry_')
                .query('indic_bp == @indic_')
                .query('geo == @reporter_')
                .query('partner.isin(@markets_)')
              )
    
    # if we're using turnover times it by 1 million
    if indic_ == "TUR":
        plot_df = plot_df.assign(value = plot_df.value.mul(1_000_000))
    
    title_string = f"{indic_select} of {reporter_select} affiliates in {markets_select} in {industry_select}"
    
    fig = px.line(plot_df, x='year', y='value', color='partner',
                  height=700, width=1200,
                 title=title_string)
    st.plotly_chart(fig)

# --- MUL reporters one market, SINGLE INDUSTRY

mul_reporter_one_market = st.checkbox("Examine multiple reporters within one market for a given industry")

if mul_reporter_one_market:
    
    # use our dictionaries to make choices
    indic_select = st.selectbox("Which indicator?", rev_indic_dict.keys(), index=2)
    markets_select = st.selectbox("Which market?", rev_part_dict.keys(), list(rev_part_dict.keys()).index('China except Hong Kong'))
    reporter_select = st.multiselect("Which reporters?", rev_geo_dict.keys(), default=['United Kingdom','France'])
    industry_select = st.selectbox("Which industry?", rev_nace_dict.keys(),
                                   list(rev_nace_dict.keys()).index('Services (except public administration, defense, compulsory social security, activities of households as employers and extra-territorial organisations and bodies)'))
    
    # now "reverse" these choices to get codes
    indic_ = rev_indic_dict[indic_select]
    markets_ = rev_part_dict[markets_select]
    reporter_ = [rev_geo_dict[x] for x in reporter_select]
    industry_ = rev_nace_dict[industry_select]
    
    plot_df = (mdf
                .query('nace_r2 == @industry_')
                .query('indic_bp == @indic_')
                .query('geo.isin(@reporter_)')
                .query('partner == @markets_')
              )
    
    # if we're using turnover times it by 1 million
    if indic_ == "TUR":
        plot_df = plot_df.assign(value = plot_df.value.mul(1_000_000))

    title_string = f"{indic_select} of {reporter_select} affiliates in {markets_select} in {industry_select}"
    
    fig = px.line(plot_df, x='year', y='value', color='geo',
                  height=700, width=1200,
                 title=title_string)
    st.plotly_chart(fig)
    
# --- ONE REPORTER ONE MARKET, MULTIPLE INDUSTRIES

one_reporter_one_market_mul_industries = st.checkbox("Examine multiple industries for a single reporter in a single market")

if one_reporter_one_market_mul_industries:
    
    # use our dictionaries to make choices
    indic_select = st.selectbox("Which indicator?", rev_indic_dict.keys(), index=2)
    markets_select = st.selectbox("Which market?", rev_part_dict.keys(), list(rev_part_dict.keys()).index('China except Hong Kong'))
    reporter_select = st.selectbox("Which reporter?", rev_geo_dict.keys(), list(rev_geo_dict.keys()).index('United Kingdom'))
    industry_select = st.multiselect("Which industry?", rev_nace_dict.keys(),
                                   default= ['Services (except public administration, defense, compulsory social security, activities of households as employers and extra-territorial organisations and bodies)'])
    
    # now "reverse" these choices to get codes
    indic_ = rev_indic_dict[indic_select]
    markets_ = rev_part_dict[markets_select]
    reporter_ = rev_geo_dict[reporter_select]
    industry_ = [rev_nace_dict[x] for x in industry_select]
    
    plot_df = (mdf
                .query('nace_r2.isin(@industry_)')
                .query('indic_bp == @indic_')
                .query('geo == @reporter_')
                .query('partner == @markets_')
              )
    
    # if we're using turnover times it by 1 million
    if indic_ == "TUR":
        plot_df = plot_df.assign(value = plot_df.value.mul(1_000_000))

    title_string = f"{indic_select} of {reporter_select} affiliates in {markets_select} in {industry_select}"
    
    fig = px.line(plot_df, x='year', y='value', color='nace_r2',
                  height=700, width=1200,
                 title=title_string)
    st.plotly_chart(fig)
    
    
