# jungle-scraper
A scraper for welcometothejungle.com which collects, for companies of less than 50 employees, relevant information and tracks it over time. 

# How to run it? 
First download all of the packages in the requirements.txt file by running in the command line:

pip install -r requirements.txt

Download the chromedriver executable from: https://chromedriver.storage.googleapis.com/index.html?path=75.0.3770.90/ And put it in your 'Applications' folder - if you use a Mac. All of the other packages should already be in the python Standard Library. 

Then run the python file: 

python jungle_scraper.py

At some point, it will ask you for the date: just type it in the command line in the DD-MM format. 

# The 'database.csv' file
That's the file that tracks all of the data of the companies. So, to take previous data into account, make a new folder containing the jungle_scraper.py file and the most recent database.csv file, and the database.csv file will be overwritten/updated with the new data. 

If you have any questions or concerns: 
contact me at: jaya.bonelli@gmail.com
