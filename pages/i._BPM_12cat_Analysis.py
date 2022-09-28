
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
st.title('UK Services Trade - BPM6 Headline 12 Categories ')
st.write('---')
st.write("""This dashboard analyses the UK's services trade by services trade type and partner,
based on data from the UK's [Office for National Statistics](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeinservicesservicetypebypartnercountrynonseasonallyadjusted).
This dataset is not seasonally-adjusted. All data is published in GBP Millions. Some quarterly values are not published by the ONS
because they would be disclosive: this dashboard does not fill or interpolate these values, they are left blank so as not to mislead.""" )

#------------------------- DATA LOADING

# load_preprocessed 
df = pd.read_parquet("./data/services_trade_type_country.parquet")

# --------------------- SETTING PARAMETERS

st.write("Choose to analyse trade with one country or with a selection of partners")

# checkbox to choose one partner or a group of partners
one_partner = st.checkbox("One partner")
mul_partner = st.checkbox("A group of partners")

if (one_partner==False) & (mul_partner==False):
    st.write("Plese choose one or multiple partners")
    
elif (one_partner==True) & (mul_partner==True):
    st.write("Plese choose choose only one option")

else:
    
    # create a list of unique partners
    list_countries = list(df.country.unique())
    
    # if we have selected one partner
    if one_partner:
        # create list selectbox to choose which partner
        partner_select = st.selectbox('Which trade partner do you want to analyse?', list_countries, index=list_countries.index("China"))
        
        # create a df of only exports
        ex_df = (df
                  .query('country == @partner_select')
                  .query('direction == "Exports"')
                  .melt(id_vars= df.columns[:7], var_name="quarter")
                  .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)).mul(1_000_000))
                  )
        
        # create a df of only imports
        im_df = (df
                  .query('country == @partner_select')
                  .query('direction == "Imports"')
                  .melt(id_vars= df.columns[:7], var_name="quarter")
                  .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)).mul(1_000_000))
                  )
    
    # if examining multiple partners
    if mul_partner:
        
        # enter partners with multi select
        partner_select = st.multiselect('Which trade partners do you want to analyse?', list_countries, default=['China'])
        
        # create and export dataframe that can use
        ex_df = (df
                  .query('country.isin(@partner_select)') # only include chosen countries
                  .query('direction == "Exports"')        # exports only
                  .melt(id_vars= df.columns[:7], var_name="quarter") # melt our dataframe
                  .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)).mul(1_000_000)) # make our values numeric
                )
        
        # change categories back to strings (makes groupby faster)
        for col in ex_df.columns: 
            if ex_df[col].dtype.name == "category": # if its a category
                ex_df[col] = ex_df[col].astype('str') # convert to string
        
        # create a groupby list that excludes country
        groupby_list = list(ex_df.columns[:5]) + ['quarter']
        # groupby this list and sum values
        ex_df = (ex_df
                  .groupby(groupby_list)['value'].sum()
                  .reset_index()
                )
        
        # Now do the same for imports dataframe that can use
        im_df = (df
                  .query('country.isin(@partner_select)') # only include chosen countries
                  .query('direction == "Imports"')        # imports only
                  .melt(id_vars= df.columns[:7], var_name="quarter") # melt our dataframe
                  .assign(value = lambda x: pd.to_numeric(x.value.replace("..",np.nan)).mul(1_000_000)) # make our values numeric
                )
        
        # change categories back to strings (makes groupby faster)
        for col in im_df.columns: 
            if im_df[col].dtype.name == "category": # if its a category
                im_df[col] = im_df[col].astype('str') # convert to string
        
        # create a groupby list that excludes country
        groupby_list = list(im_df.columns[:5]) + ['quarter']
        # groupby this list and sum values
        im_df = (im_df
                  .groupby(groupby_list)['value'].sum()
                  .reset_index()
                )

# -------------- PLOTTING

    # now setup plotting
    # outdent so can run from either ex_df, im_df depending on partner setup
    
    st.write("---")
    st.write("### UK services trade with chosen partner(s)")
    st.write("**By BPM6 12 Categories type**")

# ----- IMPORTS    

    st.write("#### Exports")
    st.write(" ")
    st.write("This first chart is a stacked bar chart of all the UK's services exports to your chosen partner(s). It's useful for seeing all services exports together, and how big each type of service is as part of the whole. The chart is interactive so you can hover, zoom in or change the services which are shown (try clicking or double-clicking the service types in the chart legend).")
    
    # ----- STACKED BAR CHART
    
    # setup a dataframe for first exports plot 
    plot_ex1 = ex_df[(
        ex_df.service_type_code.astype('str') == 
        ex_df.service_type_code_12cat.astype('str') # only 12 high level categories
                    ) & (ex_df.service_type_code != '0')  # and not equal to total
                   ]
    
    fig1 = px.bar(plot_ex1, x='quarter', y='value', color='service_code_desc',
                height=600, width=1200,
                title=f"UK services exports to {partner_select} per quarter, by service type")
    fig1.update_layout(yaxis_title="Export value, £s", xaxis_title="")
    
    st.plotly_chart(fig1)
    
    # ------ NON-STACKED LINE CHARTS WITH METRIC OPTION
    
    st.write("This chart shows a line chart of services exports to your chosen partner(s), it's useful for examining the different types of services on their own. You can choose what type of metric you want to display: absolute export values, year-on-year change in export values (in either £s or % terms) and quarter-on-quarter change in export values (again, in either £s or % terms). As above, this chart is interactive.")
    st.write(" ")
    st.write("What metric would you like your line chart to show?")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: abs_ex = st.checkbox("Exports: Absolute", value=True)
    with col2: yoy_abs_ex = st.checkbox("Exports: YoY £ change")
    with col3: yoy_percent_ex = st.checkbox("Exports: YoY % change")
    with col4: qoq_abs_ex = st.checkbox("Exports: QoQ £ change")
    with col5: qoq_percent_ex = st.checkbox("Exports: QoQ % change")
    
    if abs_ex + yoy_abs_ex + yoy_percent_ex + qoq_abs_ex + qoq_percent_ex != 1:
        st.write("Please tick one box, and only one box!")
    else:
        plot_ex1_alt = plot_ex1.copy()       
        plot_ex1_alt = plot_ex1_alt.pivot(index='service_code_desc',
                                             columns='quarter',
                                             values='value').T
        cus_yaxis_string = "Export value,  £s"
                
        if yoy_abs_ex:
            plot_ex1_alt = plot_ex1_alt.diff(4).iloc[4:,:]
            cus_yaxis_string = "YoY change in export value,  £s"
        elif yoy_percent_ex:
            plot_ex1_alt = plot_ex1_alt.pct_change(4).mul(100).iloc[4:,:]
            cus_yaxis_string = "YoY change in export value,  %"
        elif qoq_abs_ex:
            plot_ex1_alt = plot_ex1_alt.diff(1).iloc[4:,:]
            cus_yaxis_string = "QoQ change in export value,  £s"
        elif qoq_percent_ex:
            plot_ex1_alt = plot_ex1_alt.pct_change(1).mul(100).iloc[4:,:]
            cus_yaxis_string = "QoQ change in export value,  £s"
    
        # keep the plot indented so only runs if we have one ticked
        fig1 = px.line(plot_ex1_alt.reset_index(), x='quarter', y=plot_ex1_alt.columns,
                    height=600, width=1200,
                    title=f"UK services exports to {partner_select} per quarter, by service type")
        fig1.update_layout(yaxis_title=cus_yaxis_string, xaxis_title="")

        st.plotly_chart(fig1)
    
    
    # ----- IMPORTS    

    st.write("#### Imports")
    st.write(" ")
    st.write("This first chart is a stacked bar chart of all the UK's services imports from your chosen partner(s). It's useful for seeing all services imports together, and how big each type of service is as part of the whole. The chart is interactive so you can hover, zoom in or change the services which are shown (try clicking or double-clicking the service types in the chart legend).") 

# ----- STACKED BAR CHART
    
    # setup a dataframe for first imports plot 
    plot_im1 = im_df[(
        im_df.service_type_code.astype('str') == 
        im_df.service_type_code_12cat.astype('str') # only 12 high level categories
                    ) & (im_df.service_type_code != '0')  # and not equal to total
                   ]
    
    fig2 = px.bar(plot_im1, x='quarter', y='value', color='service_code_desc',
                height=600, width=1200,
                title=f"UK services imports from {partner_select} per quarter, by service type")
    fig2.update_layout(yaxis_title="Import value, £s", xaxis_title="")
    
    st.plotly_chart(fig2)
    
    # ------ NON-STACKED LINE CHARTS WITH METRIC OPTION
    
    st.write("This chart shows a line chart of services imports from your chosen partner(s), it's useful for examining the different types of services on their own. You can choose what type of metric you want to display: absolute import values, year-on-year change in import values (in either £s or % terms) and quarter-on-quarter change in import values (again, in either £s or % terms). As above, this chart is interactive.")
    st.write(" ")
    st.write("What metric would you like your line chart to show?")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: abs_im = st.checkbox("Imports: Absolute", value=True)
    with col2: yoy_abs_im = st.checkbox("Imports: YoY £ change")
    with col3: yoy_percent_im = st.checkbox("Imports: YoY % change")
    with col4: qoq_abs_im = st.checkbox("Imports: QoQ £ change")
    with col5: qoq_percent_im = st.checkbox("Imports: QoQ % change")
    
    if abs_im + yoy_abs_im + yoy_percent_im + qoq_abs_im + qoq_percent_im != 1:
        st.write("Please tick one box, and only one box!")
    else:
        plot_im1_alt = plot_im1.copy()       
        plot_im1_alt = plot_im1_alt.pivot(index='service_code_desc',
                                             columns='quarter',
                                             values='value').T
        cus_yaxis_string = "Import value,  £s"
                
        if yoy_abs_im:
            plot_im1_alt = plot_im1_alt.diff(4).iloc[4:,:]
            cus_yaxis_string = "YoY change in import value,  £s"
        elif yoy_percent_im:
            plot_im1_alt = plot_im1_alt.pct_change(4).mul(100).iloc[4:,:]
            cus_yaxis_string = "YoY change in import value,  %"
        elif qoq_abs_im:
            plot_im1_alt = plot_im1_alt.diff(1).iloc[4:,:]
            cus_yaxis_string = "QoQ change in import value,  £s"
        elif qoq_percent_im:
            plot_im1_alt = plot_im1_alt.pct_change(1).mul(100).iloc[4:,:]
            cus_yaxis_string = "QoQ change in import value,  £s"
    
        # keep the plot indented so only runs if we have one ticked
        fig1 = px.line(plot_im1_alt.reset_index(), x='quarter', y=plot_im1_alt.columns,
                    height=600, width=1200,
                    title=f"UK services imports from {partner_select} per quarter, by service type")
        fig1.update_layout(yaxis_title=cus_yaxis_string, xaxis_title="")

        st.plotly_chart(fig1)
    
    
        
