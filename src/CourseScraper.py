import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep

class CourseScraper:
    def __init__(self, links=None):
        self.courses = []
        self.courses_df = pd.DataFrame()
        
        self.course_links = links
        if (self.course_links != None):
            self.scrape_courses(self.course_links)
            
    def format_course(self, course):
        """Dict
        """
        formatted_course = {}
        attrs_keep = {
            'Course',
            'Name',
            'Minimum Fee Hours',
            'Corequisites',
            'Prerequisites',
            'Recommendations',
            'Requirements',
            'Restrictions',
            'Description',
            'Type'
        }
        
        for key in attrs_keep:
            if (key in course.keys()):
                formatted_course[key] = course[key]
            else:
                print (course['Course'], key)
            
        return formatted_course
        
    
    def add_course(self, course):
        """Dict
        """
        self.courses.append(course)
    
    def scrape_courses(self, links):
        """
        """
        n_links = len(links)
        print ("\t Scraping course pages...")

        for i in range(n_links):
            course = links[i]
            print ("\t\t{}/{}  ".format(i, n_links) + course['name'] + '...')

            try:
                course_details = self.scrape_course(course)
                self.add_course(course_details)
                ###
                sleep(0.5)
            except Exception as e:
                print ('\tFAILED', e)

            # format the details
            #course_details_clean = self.format_course(course_details)
            #self.add_course(course_details_clean)
        
        # create dataframe
        self.courses_df = pd.DataFrame(self.courses)
    
    def scrape_course(self, course):
        """
        """
        page = requests.get(course['link'])
        if (page.status_code != 200):
            print ("Error: {}".format(page.status_code))
            return
        
        soup = BeautifulSoup(page.content, 'html.parser')

        # human readable course name
        human_name = soup.find('h3').text.strip()
        
        # isolate the div with course information
        details_div = soup.find("div", {"class": "course-details"})
        
        # create an empty list for the info divs
        details = {
            'Course': course['name'],
            'Type': course['type'],
            'Name': human_name,
            'Link': course['link']
        }
        for div in details_div.find_all("div"):
            # only keep the divs containing info
            if ('aria-describedby' in div.attrs.keys()):
                
                attribute = div.text.strip()
                # info in the col to the right
                right_col = div.find_next_sibling("div")
                info = right_col.text.strip()
                
                details[attribute] = info
        
        return details