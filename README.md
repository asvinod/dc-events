# DC-Events Tracker - A Web Scraping Project
# ⬇️ Public Link ⬇️
## https://docs.google.com/spreadsheets/d/e/2PACX-1vQmn0wAuW7PMCyXi7AjBuBujFL3GQmtC6YexxvRruIy11XmPT-CRkc26BdidBp_-5WkmIfZebrF3lqY/pubhtml?gid=2122857125&single=true 
# Introduction
If you're a student, researcher, or just someone interested in exploring discussions of public policy in Washington, D.C., there are hundreds of organizations, including think tanks, embassies, NGOs, and others that have many upcoming events. 
# Breakdown 
## A. Events List 
I scraped the "Top 100 Think Tanks - US" from UPenn Libraries (https://guides.library.upenn.edu/c.php?g=1035991&p=7509974), into a CSV file, events-only.csv. This is only some of the many organizations in D.C., and I will continue adding events pages to this to add more events that can be scraped and compiled into the spreadsheet. 
## B. Scraping / Cleaning
### 1. Playwright 
(https://playwright.dev/) This is a browser automation library that is deal for JavaScript heavy websites. Playwright also provides something called Stealth that hides things that sites can detect to block bots. This way a script can be automated to scrape a site without it being blocked. 
### 2. BeautifulSoup (bs4) 
This is a Python library used for parsing HTML, transforming raw HTML into a structured tree of Python objects. It removed unwanted tags and gets specific attributes, making the HTML cleaner and easier to work with. 
### 3. re 
This is a built-in Python library for regular expressions, which I use to do further cleaning of the HTML to make the prompt smaller. 
## C. Gemini 
I'm using the "gemini-2.5-flash-lite" model as it is the cheapest, and since I'm directly prompting it with the contents of the site, I don't have any need for a better model.
## D. Google Sheets API 
This is used to update a published spreadsheet that is updated weekly by a Github workflow script! 
