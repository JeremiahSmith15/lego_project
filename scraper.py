# -*- coding: utf-8 -*-
"""
Author: Jeremiah Smith
Last Updated: 8/3/2023

Description: This script defines the get_all_sests function which scrapes all set data from
the brickset website for the given 'theme'. It stores the data in a csv file called
'theme'_lego_sets.csv.

"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from math import ceil

def add_attribute(html_tag, content = 'string'):
    """
    Checks if html_tag is None and returns the content of the tag

    Parameters
    ----------
    html_tag : bs4.element.Tag
        Tag containing information
    content : str
        A string containing the attribute of the html_tag that contains the content
    Returns
    -------
    String containing the value in the html_tag or None if the html_tag is NoneType.

    """
    if html_tag is None:
        return None
    else:
        if content == 'string':
            return html_tag.string
        elif content == 'text':
            return html_tag.text
        else:
            return None
            print("ERROR in add_atttribute unexpected content type.")

def get_all_sets(theme):
   """
   Scrapes data from brickset for the given theme and stores it in theme_lego_sets.csv

   Parameters
   ----------
   theme : str
       The theme that you wish to scrape data.

   Returns
   -------
   None.

   """
   #Starting url for theme lego set information
   url = "https://brickset.com/sets/theme-" + theme + "/page-1"
    
   #Initialize dictionary containing the set information
   set_information = {"name":[], "number": [], "subtheme":[], "release_year": [], "rating": [],
                       "number_of_ratings": [], "pieces": [], "num_minifigs": [], "minifig_codes":[],  
                       "retail_price": [], "price_per_piece": [], "packaging":[], "instructions":[], 
                       "additional_images":[], "designer": [], "launch_exit":[], "current_value_new":[], 
                       "current_value_used":[], "notes": [], "related_sets": [], "community_info": []}
    
    
   #Add header to avoid 403 response
   headers = {
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
               }
    
   #Get raw html from url
   html_doc = requests.get(url, headers = headers)
   #Transform raw html to a soup
   soup = BeautifulSoup(html_doc.content, "html.parser")
   
   #Isolate number of results per page and total number of results
   results = soup.find('div', class_ = "results").string.split()
   page_count = 1
   
   max_page_count = ceil(float(results[4])/float(results[2]))
   print(max_page_count)
   while(page_count <= max_page_count):
        
       ###############################START OF PAGE SCRAPE##################################
       #Scrape all sets blocks
       article_tags = soup.find_all('article')
        
       #Loop through every set
       for tag in article_tags:
            #If a set is found
            if (tag['class'] == ['set']):
                #Get the title of the set
                set_name = tag.h1
                set_information['name'].append(add_attribute(set_name))
                
                #Pull set number
                set_information['number'].append(add_attribute(tag.div.a))
                
                #Pull subtheme 
                set_information['subtheme'].append(add_attribute(tag.find('a', class_ = 'subtheme')))
                
                #Pull release year
                set_information['release_year'].append(add_attribute(tag.find('a', class_ = 'year')))
                
                #Pull set rating
                rating = tag.find('div', class_ = 'rating')
                set_information['rating'].append(add_attribute(rating.span, 'text'))
                
                #Pull number of ratings
                set_information['number_of_ratings'].append(add_attribute(tag.find('a', class_='popuplink plain')))
                
                
                ###################Consider writing a function to do this part##############
                #Isolate piece count, number of minifigs, packaging type, etc
                meta_info = tag.find_all('div', class_ = 'col')
                
                
                def get_info_from_block(block, block_type):
                    """
                    Scrapes set information from block depending on the type of information in the 
                    block.
        
                    Parameters
                    ----------
                    block : bs4.element.Tag
                        Contains a block of set information which includes piece count, minfigs, price, etc.
                    block_type : int
                        Identifies the type of information expected in this block. It can take the value 0 or 1.
        
                    Returns
                    -------
                    A dictionary containing the information about the set
        
                    """
                    
                    #Obtain keys of available information
                    set_info_keys = block.find_all('dt')
                    
                    #Obtain values of available information
                    set_info_values = block.find_all('dd')
                    
                    if block_type == 0:
                        #Set default fields and values
                        set_info = {"pieces":0, "num_minifigs":"0", "minifig_codes":[], "retail_price":0, 
                                         "price_per_piece":0, "packaging": None, "instructions": None, "additional_images":0}
                        
                        for i in range(len(set_info_keys)):
                            #Switch statment to match the given information with the correct values
                           if set_info_keys[i].string == "Pieces":
                               set_info["pieces"] = set_info_values[i].string
                           elif set_info_keys[i].string == "Minifigs":
                               #There are two different sets of information with this label
                               if set_info_values[i].attrs == {}:
                                   set_info["num_minifigs"] = set_info_values[i].string
                               else:
                                   for code in set_info_values[i].find_all('a'):
                                       set_info["minifig_codes"].append(code.string)
                           elif set_info_keys[i].string == "RRP":
                               set_info["retail_price"] = set_info_values[i].string
                           elif set_info_keys[i].string == "PPP":
                               set_info["price_per_piece"] = set_info_values[i].string
                           elif set_info_keys[i].string == "Packaging":
                               set_info["packaging"] = set_info_values[i].string
                           elif set_info_keys[i].string == "Instructions":
                               set_info["instructions"] = set_info_values[i].string
                           elif set_info_keys[i].string == "Additional images":
                               set_info["additional_images"] = set_info_values[i].string
                           else:
                               print(set_info_keys[i].string)
                               print("ERROR in get_info_from_block unexpected type of information")
                                    
                        return set_info
                    
                    if block_type == 1:
                        #Set default fields and values
                        set_info = {"designer": None, "launch_exit":None, "current_value_new":0, "current_value_used": 0,
                                    "notes": None, "related_sets": []}
                        
                        for i in range(len(set_info_keys)):
                            #Switch statment to match the given information with the correct values
                            if set_info_keys[i].string == "Designer":
                                set_info["designer"] = set_info_values[i].string
                            elif set_info_keys[i].string == "Launch/exit":
                                 set_info["launch_exit"] = set_info_values[i].string
                            elif set_info_keys[i].string == "Value new":
                                set_info["current_value_new"] = set_info_values[i].string
                            elif set_info_keys[i].string == "Value used":
                                set_info["current_value_used"] = set_info_values[i].string
                            elif set_info_keys[i].string == "Notes":
                                set_info["notes"] = set_info_values[i].string
                            elif set_info_keys[i].string == "Related sets":
                                for set_number in set_info_values[i].find_all('a'):
                                    set_info["related_sets"].append(set_number.string)
                            else:
                                print(set_info_keys[i].string)
                                print("ERROR in get_info_from_block unexpected type of information")
                        return set_info
                    
                #Scrape key information from both blocks in meta info
                for i in range(len(meta_info)):
                    info = get_info_from_block(meta_info[i], i)
                    for key in info:
                        set_information[key].append(info[key])
                
            
                #Community Information
                set_information['community_info'].append(tag.find('dd',class_='hideingallery').string)
       
       page_count += 1
       #Go to the next page
       url = url.replace('page-' + str(page_count-1), 'page-'+ str(page_count))
      
       #Take a break to avoid a 429 error
       time.sleep(3)
       html_doc = requests.get(url, headers = headers)

       #Transform raw html to a soup
       soup = BeautifulSoup(html_doc.content, "html.parser")
       
   set_data = pd.DataFrame(set_information)
       
   set_data.to_csv(theme + "_lego_sets")
       
#get_all_sets("Star-Wars")
get_all_sets("City")
