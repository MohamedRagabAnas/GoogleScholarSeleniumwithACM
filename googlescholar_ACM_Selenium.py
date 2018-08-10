# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import sys
import csv
from scrapyd_api import ScrapydAPI



#name = 'googlescholar'
#allowed_domains = ['scholar.google.com']
#topic='description_logic'
start_url = 'https://scholar.google.com.eg/citations?view_op=search_authors&hl=en&mauthors=label:'

chromeOptions = webdriver.ChromeOptions()
prefs={'disk-cache-size': 4096 }
chromeOptions.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome() # wen need to check Phantom js which is hidden and may be faster...
driverAcm = webdriver.Chrome() # wen need to check Phantom js which is hidden and may be faster...

ACM_BASE_URL = 'https://dl.acm.org/'
ACM_SEARCH_URL = ACM_BASE_URL + "results.cfm?within=owners.owner%3DGUIDE&srt=_score&query=persons.authors.personName:"


    
def getURL(Prev_Next_url):
    url=Prev_Next_url
    url=url.replace("\\x3d","=")
    url=url.replace("\\x26","&")
    url=url.replace("&oe=ASCII","")
    url=url.replace("window.location='","https://scholar.google.com.eg")
    url=url.replace("'","")
    return url
			
def scrapeAuthorInfo():
    authors=driver.find_elements_by_xpath('//*[@class="gsc_1usr gs_scl"]')
    
    nameslst=[]
    emailslst=[]
    citationslst=[]
    linkslst=[]
    topicslst=[]
    Affliationslst=[]
    imageslst=[]

    
    for author in authors:
        
        
        name= author.find_element_by_xpath('.//h3[@class="gsc_oai_name"]/a').get_attribute('innerHTML')
        
        link= author.find_element_by_xpath('.//h3[@class="gsc_oai_name"]/a').get_attribute('href') 
        
        image=author.find_element_by_xpath('.//span[@class="gs_rimg gsc_pp_sm gsc_1usr_photo"]/img').get_attribute('src')
        
        Afflst=[] 
        Affliation=author.find_element_by_xpath('.//*[@class="gsc_oai_aff"]').get_attribute('innerHTML')
        Afflst.append(Affliation)
        
        email=author.find_element_by_xpath('.//*[@class="gsc_oai_eml"]').get_attribute('innerHTML')
        email=str(email).replace('Verified email at ', '')
        
        citedby=author.find_element_by_xpath('.//*[@class="gsc_oai_cby"]').get_attribute('innerHTML')
        citedby=str(citedby).replace('Cited by ', '')

        topicslist=[]
        topics=author.find_elements_by_xpath('.//*[@class="gsc_oai_one_int"]')
        for topic in topics:
            topicslist.append(topic.text)



        driverAcm.get(ACM_SEARCH_URL+""+name)
        try:
            linkAcm = driverAcm.find_element_by_link_text(name)
            linkAcm.click()
            affHistElems=driverAcm.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/div/a")
            affHist=[]
            for aff in affHistElems:
                affHist.append(aff.text)
            Afflst.append(affHist)
        except:
            print ('Link to be clicked cannot be found!')

        nameslst.append(name)
        Affliationslst.append(Afflst)
        emailslst.append(email)
        citationslst.append(citedby)
        linkslst.append(link)
        topicslst.append(topicslist)
        imageslst.append(image)

    authorsDict={'Name':nameslst,'Image':imageslst,'AffiliationHistory':Affliationslst,'Email':emailslst,'Link' :linkslst,'CitedBy':citationslst,'Topics':topicslst}
    return authorsDict        


def gscholarScrape(topics='lod'):
    
    topicslst=topics.split(',')
    completeAuthorsDataframe=[]

    for topic in topicslst:
        driver.get(start_url+""+topic)    
        firstpageDict=scrapeAuthorInfo()
        firstAuthorsDataframe=pd.DataFrame.from_dict(firstpageDict,orient='index').transpose()

        completeAuthorsDataframe.append(firstAuthorsDataframe)

        Prev_Next_url=''
        Prev_Next=[]
        try:  
            Prev_Next =driver.find_element_by_xpath("//button[@type='button'][@aria-label='Next']").get_attribute('onclick')
            Prev_Next_url=str(Prev_Next)
            Prev_Next_url=getURL(Prev_Next_url)

        except Exception, e:
            pass
        else:
            pass
        finally:
            pass
        
        while (Prev_Next):
            driver.get(Prev_Next_url)    
            
            nextDict=scrapeAuthorInfo()
            nextAuthorsDataframe=pd.DataFrame.from_dict(nextDict,orient='index').transpose()
            completeAuthorsDataframe.append(nextAuthorsDataframe)
            
            try:  
                Prev_Next =driver.find_element_by_xpath("//button[@type='button'][@aria-label='Next']").get_attribute('onclick')
                Prev_Next_url=str(Prev_Next)
                Prev_Next_url=getURL(Prev_Next_url)
            except Exception, e:
                Prev_Next_url=''
            else:
                pass
            finally:
                pass

    resultedFullDF=pd.concat(completeAuthorsDataframe)

    return resultedFullDF.Image
        
def main():
    
   DF= gscholarScrape('lod')
   print DF

    
    
    
if __name__ == '__main__':
    main()
        
            			
			
