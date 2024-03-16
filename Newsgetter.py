####################################################################################################################################
########################################################## Version 2.0.0 ###########################################################
####################################################################################################################################
# Import Libraries
####################################################################################################################################
import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar

from stqdm import stqdm
import pandas as pd
import io

from Scrappers import *
from Parameters import *
from Newsletters import *

####################################################################################################################################


####################################################################################################################################
# Identify search parameters and get user inputs
####################################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------------------
# Styling Page:
#-----------------------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title='Newsgetter',layout="wide")
st.title('Get Started with :blue[Newsgetter]')
st.markdown("This tool was created to streamline the creation of newsletters by leveraging Google News")
st.divider()
#-----------------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------------
# Create a session to save data:
#-----------------------------------------------------------------------------------------------------------------------------------
Session = st.session_state
#-----------------------------------------------------------------------------------------------------------------------------------

####################################################################################################################################
# Get User Inputs:
####################################################################################################################################    
with st.sidebar:
    #-------------------------------------------------------------------------------------------------------------------------------
    # Styling Page:
    #-------------------------------------------------------------------------------------------------------------------------------
    st.image('https://infomineo.com/wp-content/uploads/2023/03/Logo-2-bleus.png', width=220)
    st.divider()
    st.subheader('Search Parameters:',divider='rainbow')
    newsletter_type = st.radio('Select Type of Search',['Detailed','Quick'],horizontal=True)
    
    if newsletter_type == 'Detailed':
        #-------------------------------------------------------------------------------------------------------------------------------
        # User Inputs
        #-------------------------------------------------------------------------------------------------------------------------------
        date_range = st.date_input ('Date Range *',value=[],format="DD/MM/YYYY",help='Select start and end date for the search')
        countries = st.multiselect('Countries*',list(Google_Parameters.countries_acronyms().keys()))
        included_keywords = st_tags(label='Included Keywords *', text='Press enter to add more', maxtags = 100, key='Included Keywords')
        exclude_keywords= st_tags(label='Excluded Keywords', text='Press enter to add more', maxtags = 100, key='Excluded Keywords')
        websites= st_tags(label='Websites & Domains', text='Press enter to add more', maxtags = 100, key='Websites')
        #-------------------------------------------------------------------------------------------------------------------------------

        #-------------------------------------------------------------------------------------------------------------------------------
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox('Language',Google_Parameters.interface_langs().keys(),placeholder="Choose a language",help='Language of results')
            location = st.selectbox('Geo Location',Google_Parameters.countries().keys(),placeholder="Choose a location",help='Geographical location of search')
        #-------------------------------------------------------------------------------------------------------------------------------    
        with col2:
            term_appear = st.selectbox('Keywords Location',Google_Parameters.term_apperaing().keys(),help='Where should the keywords appear in the results?')
            quantity = st.number_input('Results Quantity',min_value=10,max_value=100,help='Number of results per country')
        #-------------------------------------------------------------------------------------------------------------------------------
    if newsletter_type == 'Quick':
        date_range = st.date_input ('Date Range *',value=[],format="DD/MM/YYYY",help='Select start and end date for the search')
        quick_newsletter = st.selectbox('Select Newsletter',Newsletters.Newsletters_Parameters().keys())
        quantity = st.number_input('Results Quantity',min_value=10,max_value=100,help='Number of results per country')
        
        countries = Newsletters.Newsletters_Parameters()[quick_newsletter]['Countries']
        included_keywords = Newsletters.Newsletters_Parameters()[quick_newsletter]['Keywords']
        exclude_keywords, websites, language, location, term_appear = '','','','',''
    #-------------------------------------------------------------------------------------------------------------------------------
    # Start Search Button
    #-------------------------------------------------------------------------------------------------------------------------------
    st.divider()
    Start_Search = st.button ('Start Searching')
    st.divider()
    st.caption('Newsgetter - v2.0.0')
    #-------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------



####################################################################################################################################
# Extract all avaiable results
####################################################################################################################################


####################################################################################################################################
# Search Google
####################################################################################################################################
if Start_Search or 'google_results' in Session.keys() :
    st.subheader('Searching Results',divider='rainbow')
    
Search_Status = False
    
if Start_Search:
    Search_Status  = True
        
if Search_Status: 
    with st.status('Search Google'):
        try:
            #-------------------------------------------------------------------------------------------------------------------------------
            # Prepare Google Search Links
            #-------------------------------------------------------------------------------------------------------------------------------
            Google_Links = []
            for country in countries:
                country_acronyms = list(set(Google_Parameters.countries_acronyms()[country]))
                Start_Date = date_range[0].strftime("%m-%d-%Y") if date_range else ""
                End_Date = date_range[1].strftime("%m-%d-%Y")  if date_range else ""
                
                Link = Scrappers.Google_Advanced_URL(query=country_acronyms,exact_words=included_keywords, none_of_words=exclude_keywords, site_or_domain=websites, results_count=quantity, term_apperaing=term_appear,
                                                    start_date=Start_Date, end_date=End_Date, country=location, search_language=language, search_type='')
                Google_Links.append({country:Link})
            #-------------------------------------------------------------------------------------------------------------------------------


            
            #-------------------------------------------------------------------------------------------------------------------------------
            # Print Google Search Links
            #-------------------------------------------------------------------------------------------------------------------------------
            num_columns = len(Google_Links)
            columns = st.columns(num_columns)
            for i, dict in enumerate(Google_Links):
                with columns[i]:
                    country = list(dict.keys())[0]
                    link = dict[country]
                    st.link_button(country,link)
            #-------------------------------------------------------------------------------------------------------------------------------
            
            
            
            #-------------------------------------------------------------------------------------------------------------------------------
            # Get Google Links Results
            #-------------------------------------------------------------------------------------------------------------------------------
            Google_Results = pd.DataFrame()
            for result in stqdm(Google_Links):
                Country = list(result.keys())[0]
                Link = result[Country]
                Link_Results = Scrappers.Google_News_Selenium(Link)
                Link_Results['Country'] = Country
                Google_Results = pd.concat([Google_Results,Link_Results],ignore_index=True)
            
            
            
            #-------------------------------------------------------------------------------------------------------------------------------
            # Format Results and add "Selection" option
            #------------------------------------------------------------------------------------------------------------------------------- 
            Google_Results['Select'] = False
            column_names = list(Google_Results.columns)
            column_names.remove('Select')
            column_order = ['Select'] + column_names
            Google_Results = Google_Results.reindex(columns=column_order)
            
            
            
            #-------------------------------------------------------------------------------------------------------------------------------
            # Save Results to Session and Reset Search Status
            #------------------------------------------------------------------------------------------------------------------------------- 
            Session['google_results'] = Google_Results
            Search_Status = False
            #-------------------------------------------------------------------------------------------------------------------------------
        
        except Exception as e:
            st.warning(e)

            
if 'google_results' in Session.keys():
    with st.expander('Google Results',True):
        st.metric('Total Reuslts',Session['google_results'].shape[0]) 
        #-------------------------------------------------------------------------------------------------------------------------------
        # Show Select-able Dataframe
        #-------------------------------------------------------------------------------------------------------------------------------
        Session['Google_Results_Selection'] = st.data_editor(Session['google_results'],column_config={
                                                            'Select':st.column_config.CheckboxColumn()},
                                                            hide_index=True)
        st.divider()
        #-------------------------------------------------------------------------------------------------------------------------------
        
        
        
        #-------------------------------------------------------------------------------------------------------------------------------
        # Start Scrapping Button
        #-------------------------------------------------------------------------------------------------------------------------------
        Start_Scapping = st.button('Start Scapping')
        #-------------------------------------------------------------------------------------------------------------------------------
        
####################################################################################################################################


####################################################################################################################################
# Scrape Results
####################################################################################################################################
if 'google_results' in Session.keys() and Start_Scapping == True:
        
        st.subheader('Scrapping Results',divider='rainbow')
        
        with st.status('Scrapping Results'):
            #---------------------------------------------------------------------------------------------------------------------------
            # Get Links from Google Results
            #---------------------------------------------------------------------------------------------------------------------------
            Google_Results_Selection = Session['Google_Results_Selection']
            Selected_Results = Google_Results_Selection[Google_Results_Selection['Select']==True]
            
            if Selected_Results.shape[0] != 0:
                Links = Selected_Results['Link']
            else:
                Links = Session['google_results']['Link']
            #---------------------------------------------------------------------------------------------------------------------------
            
            
            #---------------------------------------------------------------------------------------------------------------------------
            # Itterate over each link to scrape website and save in Scrapped_Websites_List
            #---------------------------------------------------------------------------------------------------------------------------
            Scraped_Websites_List = []
            
            for link in stqdm(Links):
                Website_dict = Scrappers.Site_Scrapper(link,included_keywords)
                Scraped_Websites_List.append(Website_dict)
            #---------------------------------------------------------------------------------------------------------------------------
            
            
            #---------------------------------------------------------------------------------------------------------------------------
            # Create a Dataframe for scrapping results and save in Session   
            #---------------------------------------------------------------------------------------------------------------------------
            Scraped_Websites_DF = pd.DataFrame(Scraped_Websites_List)
            Session['Scraped_Websites_DF'] = Scraped_Websites_DF
            #---------------------------------------------------------------------------------------------------------------------------
            
        
            #---------------------------------------------------------------------------------------------------------------------------
            # Merge Scraped Websites with Google Results and Format the findings
            #---------------------------------------------------------------------------------------------------------------------------
            Final_Results = Scrappers.Result_Formating(Google_Results_Selection,Scraped_Websites_DF,included_keywords)
            #---------------------------------------------------------------------------------------------------------------------------
            
            
            #---------------------------------------------------------------------------------------------------------------------------
            # Save Data in Session
            #---------------------------------------------------------------------------------------------------------------------------
            Session['Final_Results'] = Final_Results
            #---------------------------------------------------------------------------------------------------------------------------
            
        
            #---------------------------------------------------------------------------------------------------------------------------
            # Print Results
            #---------------------------------------------------------------------------------------------------------------------------
            colA,colB,colC = st.columns(3)
            with colA:
                st.metric('Scrapped Reuslts',Final_Results.shape[0])
            with colB:
                st.metric('Not Scraped',(Final_Results['Paragraphs'] != '').sum())
            with colC:
                st.metric('Not Scraped',(Final_Results['Paragraphs'] == '').sum())
            
            Final_Results = st.data_editor(Final_Results,column_config={"Link": st.column_config.LinkColumn("Link",display_text="Link")},hide_index=True)
            st.divider()
            #---------------------------------------------------------------------------------------------------------------------------
            
            
            ####################################################################################################################################
            # Download Results and reset search
            ####################################################################################################################################  
            if 'Final_Results' in Session.keys(): 
                
                col3,col4 = st.columns(2)
                with col3:
                    buffer = io.BytesIO()
                    Final_Results = Session['Final_Results']
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        Final_Results.to_excel(writer, sheet_name='Sheet1', index=False)

                    Donwload = st.download_button('Download Results',data=buffer,file_name="Results.xlsx",mime='textcsv')
                    Session['Download'] = True
            
                with col4:
                    Refresh = st.button('Reset Research')
                    if Refresh:
                        Session.clear()
                        st.experimental_rerun()
            #-----------------------------------------------------------------------------------------------------------------------------------            
