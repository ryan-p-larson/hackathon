import requests
from bs4 import BeautifulSoup

class DepartmentScraper:
    def __init__(self):
        """
        """
        self.academicUnitID = None
        self.search_pages = []
        self.class_pages = []
        
    def create_search_page(self, page_num):
        """
        """
        search = "https://myui.uiowa.edu/my-ui/courses/by-department.page?page={}&q.academicUnitId={}&showResults=1".format(page_num, self.academicUnitID)
        return search
    
    def enqueue_search_page(self, url):
        """
        """
        self.search_pages.append(url)
    
    def get_search_pages(self, soup):
        """
        """
        
        # Every department has at least one class
        first_page = self.create_search_page(1)
        self.enqueue_search_page(first_page)
    
        # check if it has a pagination tag
        paging = soup.find("ul", {"class" : "pagination"})
        if (paging == None):
            # we're good!
            return
            
        # extract only the links
        page_links = paging.find_all('a')
        
        # These are the buttons
        for i in page_links:
            if ('title' in i.attrs):
                i_title = i.attrs['title']
                # only get buttons we need
                if (i_title.startswith('Go to page ')):
                    i_url = self.create_search_page(i.text)
                    self.enqueue_search_page(i_url)
        
        return
    

    def get_page_rows(self, soup):
        """
        """
        table = soup.find(id='search-result')
        table_body = table.find_next('tbody')
        table_rows = table_body.find_all('tr')

        return table_rows
    
    def get_row_info(self, row):
        """
        """
        # each td has a separate piece of info
        cols = row.find_all('td')

        # but the top is the most important
        row_title = cols[0]

        # <a>, has multiple info for us
        row_a = row_title.find("a", { "class" : "text-underline" })
        course_name = row_a.text
        course_link = 'https://myui.uiowa.edu' + row_a.attrs['href']


        good_types = {'Discussion', 'Lecture', 'Lab', 'Independent Study'}

        # Type of class
        try:
            course_type = row_title.find_next("em").text
            if (course_type not in good_types):
                course_type = None

        except:
            course_type = None
            
        course_info = {
            'name': course_name,
            'link': course_link,
            'type': course_type
        }
        

        # dont add discussions
        if (course_type != 'Discussion'): 
            self.class_pages.append(course_info)

        return 
    
    def scrape_page(self, url):
        # Request and check page
        page = requests.get(url)
        if (page.status_code != 200):
            print ("Couldn't request page, Err: {}".format(page.status_code))

        # Create soup for our functions
        soup = BeautifulSoup(page.content, 'html.parser')

        # get the raw course rows from page
        rows = self.get_page_rows(soup)

        # format each row to get the class url and type
        for row in rows:
            # this will format and add it
            self.get_row_info(row)

        return
        
    
    def start_scrape(self, academicUnitID):
        """
        """
        # set college
        self.academicUnitID = academicUnitID
        
        # Request and check page
        page_url = self.create_search_page(1)
        page = requests.get(page_url)
        
        if (page.status_code != 200):
            print ("Couldn't request page, Err: {}".format(page.status_code))

        # Create soup for our traversal
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Instantiate scraping queue
        self.get_search_pages(soup)
        
        # now that self has a list of pages
        for page in self.search_pages:
            # scrape each page
            self.scrape_page(page)
        
        
        return 
        
        