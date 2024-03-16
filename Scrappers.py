import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import unquote
from Webtrench import TextScrapper
import pandas as pd
from Parameters import Google_Parameters

class Scrappers():
    ###############################################################################################################################################################################################################
    ######################################################################################### Google Functions ####################################################################################################
    ###############################################################################################################################################################################################################
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Function 1 : Google Advanced URL Builder
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Google_Advanced_URL(query, exact_words='', none_of_words='', site_or_domain='', results_count='', term_apperaing='',
                            start_date='', end_date='', country='', search_language='', search_type=''):

        # Building Main Query
        QUERY = '(' + '+OR+'.join(['"' + word.replace(" ","+") + '"' for word in query]) + ')' if type(query) is list else '("' + query.replace(" ","+") + '")'
        EXACT_WORDS = '+OR+'.join(['"' + word + '"' for word in exact_words]) if exact_words else ''
        NONE_OF_WORDS = '+'.join(['-' + word for word in none_of_words]) if none_of_words else ''
        SITE_OR_DOMAIN = '+OR+'.join(['+site:' + site for site in site_or_domain])  if site_or_domain else ''
        
        FULL_QUERY = QUERY + '+AND+' + '(' + EXACT_WORDS + ')' + NONE_OF_WORDS + SITE_OR_DOMAIN
        
        RESULTS_COUNTS = f"&num={int(results_count)}" if results_count else ''
        DATE = f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}" if start_date or end_date else ''
        
        SEARCH_TYPE = Google_Parameters.search_type()[search_type] if search_type else Google_Parameters.search_type()['News']
        LANGUGAGE = Google_Parameters.interface_langs()[search_language] if search_language else Google_Parameters.interface_langs()['English']
        COUNTRY = Google_Parameters.countries()[country] if country else ''
        TERM_APPERAING = Google_Parameters.term_apperaing()[term_apperaing] if term_apperaing else ''

        
        
        Url = f"https://www.google.com/search?q={FULL_QUERY}{RESULTS_COUNTS}{DATE}{COUNTRY}{LANGUGAGE}{TERM_APPERAING}{SEARCH_TYPE}".replace(" ","+")
    
        # Return URL
        return Url
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Function 2 : Google_News_Requests
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Google_News_Requests(URL):
        response = requests.get(URL)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.content,'html.parser')

        Results = [a for a in soup.find_all("a", href=True) if 'data-ved' in a.attrs]
        Final_Results = []

        # Extarct From Google News
        for result in Results:
            Headline = result.find('h3').text
            Date = result.find(class_="r0bn4c rQMQod").text
            Link = unquote(result.attrs['href'].split("/url?q=")[1].split('&sa')[0])

            page = {"Headline":Headline,
                    "Date":Date,
                    "Link":Link}
            
            Final_Results.append(page)
        return Final_Results
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Function 2 : Google_News_Requests
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Google_News_Selenium(URL):  
        # Prepare and Start Driver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(URL)
        
        # Get Available Articles
        Results = driver.find_elements(By.CLASS_NAME ,'WlydOe')
        
        
        # Get Extract articles
        Articles = []
        for result in Results:
            Publisher = result.text.split('\n')[0]
            Headline = result.text.split('\n')[1]
            Short_Description = result.text.split('\n')[2]
            Date = result.text.split('\n')[-1]
            Link = result.get_attribute('href')
            
            article = {
                    "Headline":Headline,
                    "Short Description":Short_Description,
                    "Date":Date,
                    "Publisher":Publisher,
                    "Link":Link}
            Articles.append(article)
        
        
        # Return Results as a Dataframe
        Articles = pd.DataFrame(Articles)
        driver.close()
        
        return Articles
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    



    ###############################################################################################################################################################################################################
    ######################################################################################### Scrapping Functions #################################################################################################
    ###############################################################################################################################################################################################################
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Function 3 : Website Scrapper
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Site_Scrapper(Url,Keywords=''):
        try:
            try:
                try:
                    #--------------------------------------------------------------------------------
                    # Step 1: Get Website content using WebTrench
                    #--------------------------------------------------------------------------------
                    Paragraphs = TextScrapper.paragraph_from_url(Url)
                    Paragraphs = ([p.text.strip() for p in Paragraphs])
                    
                except:
                        #--------------------------------------------------------------------------------
                        # Step 1: Get Website content using Requests
                        #--------------------------------------------------------------------------------
                        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"} 
                        response = requests.get(Url, headers=headers, timeout=60)
                        response.encoding = response.apparent_encoding
                        soup = BeautifulSoup(response.text,'html5lib')
                        
                        #--------------------------------------------------------------------------------
                        # Step 2: Get and clean Paragraphs
                        #--------------------------------------------------------------------------------
                        Paragraphs = [paragraph.text.strip() for paragraph in soup.find_all('p') if len(paragraph.text.strip()) > 1]
                        
                        
                        if len(Paragraphs) <=1:
                            #--------------------------------------------------------------------------------
                            # Step 1: Get Website content using Requests Using Selenium
                            #--------------------------------------------------------------------------------
                            chrome_options = Options()
                            chrome_options.add_argument("--headless")
                            driver = webdriver.Chrome(options=chrome_options)
                            driver.get(Url)
            
                            #--------------------------------------------------------------------------------
                            # Step 2: Get and clean Paragraphs
                            #--------------------------------------------------------------------------------
                            Paragraphs = [paragraph.text.strip() for paragraph in driver.find_elements(By.TAG_NAME, "p") if len(paragraph.text.strip())>1]
                            driver.close()
            
            except Exception as e:
                Paragraphs = ""
                print(f"Problem in Webscraping \nLink:{Url} \nError{e}")
            #--------------------------------------------------------------------------------
            # Step 3: Get Most Relevant Paragraphs
            #--------------------------------------------------------------------------------
            Most_Relevant_Paragraphs = "\n\n".join({paragraph for paragraph in Paragraphs if any(keyword.lower() in paragraph.lower() for keyword in Keywords)})

            #--------------------------------------------------------------------------------
            # Step 4: Keyword Analysis
            #--------------------------------------------------------------------------------
            if Keywords:
                Keywords_Analysis = "\n".join([" • " + keyword.title() + " : " + str(Most_Relevant_Paragraphs.lower().count(keyword.lower())) for keyword in Keywords])
                Keywords_Totals = sum(Most_Relevant_Paragraphs.lower().count(keyword.lower()) for keyword in Keywords)
            else:
                Keywords_Analysis = 'N/A'
                Keywords_Totals = 0

            #--------------------------------------------------------------------------------
            # Step 5: Create Dict Entry
            #--------------------------------------------------------------------------------
            page = {
                    "Paragraphs":"\n\n".join(Paragraphs),
                    "Most Relevant Paragraphs":Most_Relevant_Paragraphs,
                    "Keywords Analysis":Keywords_Analysis,
                    "Keywords Total":Keywords_Totals,
                    "Link":Url}
        except:
            page = {
                    "Paragraphs":"N/A",
                    "Most Relevant Paragraphs":"N/A",
                    "Keywords Analysis":"N/A",
                    "Keywords Total":"N/A",
                    "Link":Url}
            
        return page    
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    
    ###############################################################################################################################################################################################################
    ######################################################################################### Suppport Functions ##################################################################################################
    ############################################################################################################################################################################################################### 
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Function 4 : Results Formating
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Result_Formating(Google_Results,Scrapping_Results,Keywords=''):
        # Merge Dataframes
        Final_Results = pd.merge(Google_Results,Scrapping_Results,on='Link')
        
        # Drop Duplicates and Empty Columns
        Final_Results = Final_Results.drop_duplicates(subset='Link').dropna(axis=1, how='all')
        
        # Calculate Relevancy Score
        try:
            Final_Results['Keywords Total'] = pd.to_numeric(Final_Results['Keywords Total'], errors='coerce')
            Total_Keywords = Final_Results['Keywords Total'].sum()
            Final_Results['Relevancy Score'] = Final_Results['Keywords Total'] / Total_Keywords
        except:
            Total_Keywords = 0
            Final_Results['Relevancy Score'] = 0
            
        #Rearrange collumns
        if len(Keywords) != 0:
            try:
                Final_Results = Final_Results[['Country', 'Headline', "Short Description", 'Date', 'Paragraphs', 'Most Relevant Paragraphs', 'Keywords Analysis', 'Keywords Total', 'Relevancy Score', 'Link']]
            except:
                Final_Results = Final_Results[['Country', 'Headline', "Short Description", 'Paragraphs', 'Most Relevant Paragraphs', 'Keywords Analysis', 'Keywords Total', 'Relevancy Score', 'Link']]
            # Sort by Keywords Total
            Final_Results = Final_Results.sort_values(by='Relevancy Score',ascending=False)
            Final_Results = Final_Results.reset_index(drop=True)
        
        else:
            try:
                Final_Results = Final_Results[['Country', 'Headline', "Short Description", 'Date', 'Paragraphs', 'Link']]
            except:
                Final_Results = Final_Results[['Country', 'Headline', "Short Description", 'Paragraphs', 'Link']]
    

        return Final_Results
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
