import re, requests, urllib.request, os, shutil
import pyinputplus as pyip # Used for input validation
import pandas as pd # Used for data analysis, here: eg. creating CSV file
from bs4 import BeautifulSoup # Used for web scrapping (HTML)
from datetime import datetime
from pathlib import Path

# Lists to store values of the parameters
priceList = []
yearList = []
mileageList = []
pageCounter = 1
currentDate = datetime.now().strftime('%Y-%m-%d_%H:%M')

def urlCreate(): # Setting up the URL(s)
	global vehicleBrand, model, url, pageCounter
	vehicleBrand = pyip.inputStr('Marka: ', limit=3)
	model = pyip.inputStr('Model: ')
	vehicleBrand = vehicleBrand.lower()
	model = model.lower()
	url = str('http://www.otomoto.pl/osobowe/' + vehicleBrand + '/' + model)
	print('Zbieranie danych: strona numer {}...'.format(str(pageCounter))) # An info about data collection from the first page

def loop(nextPage):
	global pageCounter
	if nextPage: # If next page exists (if list is not empty)
		for nextPageURL in nextPage:
			pageCounter += 1
			url = nextPageURL.find('a').get('href') # Overwrite the url variable with next page url
		print('Zbieranie danych: strona numer {}...'.format(str(pageCounter)))
		urlRequest(url)
		scrapData(soup) # Scrap the data from the page (including first iteration)
		nextPage = soup.findAll('li', attrs={'class':'next abs'}) #returns list
		loop(nextPage)
	saveTXT(vehicleBrand, model)
	saveCSV(vehicleBrand, model)

def urlRequest(url): #connecting to the URL and parsing HTML with saving to BeautifulSoup object
	global soup
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")

def scrapData(soup): # Extracting data from the website
	for i in soup.findAll('div', attrs={'class':'offer-item__content ds-details-container'}):
		yearSoup = i.find('li', attrs={'data-code':'year'})
		if yearSoup:
			year = re.search(r'<span>([\d{4}\s]+)</span>', str(yearSoup))
			record = str(year.group(1)) + ("\n")
			yearList.append(str(record))
		else:
			yearList.append('-')
	
		mileageSoup = i.find('li', attrs={'data-code':'mileage'})
		if mileageSoup:
			mileage = re.search(r'<span>([\w\s\w]+) km</span>', str(mileageSoup))
			record = str(mileage.group(1)) + ("\n")
			mileageList.append(str(record))	
		else:
			mileageList.append('-')
	
		priceSoup = i.find('span', attrs={'class':'offer-price__number ds-price-number'})
		if priceSoup:
			price = re.search(r'<span>([\w\s\w]+)</span>', str(priceSoup))
			record = str(price.group(1)) + ("\n")
			priceList.append(str(record))
		else:
			mileageList.append('-')

def saveTXT(vehicleBrand, model): # Saving all the data to .txt file
	global fileNameTXT
	fileNameTXT = str('otomoto_' + vehicleBrand + '_' +  model + '_' + currentDate + '_data.txt')
	allData = open(fileNameTXT, 'a')
	for i in priceList:
		allData.write(str(i))
	for i in yearList:
		allData.write(str(i))
	for i in mileageList:
		allData.write(str(i))
	allData.close()

def saveCSV(vehicleBrand, model): # Saving all the data to .csv file
	global fileNameCSV	
	fileNameCSV = str('otomoto_' + vehicleBrand + '_' +  model + '_' + currentDate + '_data.csv')
	allData = pd.DataFrame({'Rok':yearList, 'Cena':priceList, 'Przebieg':mileageList})
	allData = allData.sort_values(by=['Rok', 'Cena'])
	allData.to_csv(fileNameCSV, index=False, encoding='utf-8')

def newDir(fileNameTXT, fileNameCSV): # Moving created files to dedicated directory
	global newDirPath
	currentPath = os.getcwd()
	newDirName = str(vehicleBrand + '_' + model + '_' + currentDate + '_data')
		# Creating new folder with dedicated name
	newDirPath = str('CollectedData/' + newDirName)
	os.path.join(currentPath, newDirPath)
	newDir = os.makedirs(newDirPath)
		# Moving created .txt to new folder 
	sourcePathTXT = str(currentPath + '/' + fileNameTXT)
	destinationPathTXT = str(newDirPath + '/' + fileNameTXT)
	shutil.move(sourcePathTXT, destinationPathTXT)
		# Moving created .csv to new folder
	sourcePathCSV = str(currentPath + '/' + fileNameCSV)
	destinationPathCSV = str(newDirPath + '/' + fileNameCSV)
	shutil.move(sourcePathCSV, destinationPathCSV)

print('Aby pobrać dane z serwisu otomoto wpisz żądaną markę i model samochodu.')
urlCreate()
urlRequest(url)
scrapData(soup) # Data scrap for the first site
nextPage = soup.findAll('li', attrs={'class':'next abs'}) # Return the tag with href to the next page
loop(nextPage) # Loop initialisation
newDir(fileNameTXT, fileNameCSV)
print('Dane zostały pomyślnie pobrane. \nPobrano {0} wierszy. \nLokalizacja: {1}'.format(len(yearList), newDirPath))
