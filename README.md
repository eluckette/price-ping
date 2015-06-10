# Price Ping

Price Ping allows users to search and set price notifications for Amazon products. The app is catered to users who hold off on buying products in hopes of a price decrease. Users can set a price alert on any product for one to five days. If the price of their selected product drops, they will be notified via text with a link to the product. Users are able to add multiple alerts, manage current alerts, and see their recently viewed products. 

### Technology Stack

**Backend**: 
- Python/Flask
- Python Libraries: Random, PyShorteners
- SQLite, SQLAlchemy

**Frontend**:
- Javascript, jQuery, AJAX
- HTML5/CSS3, Bootstrap

**APIs**:
- Amazon Product Advertising
- Twilio

## Overview & Features 

### Homepage

![alt home-page](https://raw.github.com/eluckette/price-ping/master/static/images/home-page.png)

**Search Bar**
- User selects category from dropdown and enters search term into text field
- Input values are used to create the API call to Amazon. 
- API response is an XML object, the server then iterates through the XML object to retreive products and product attributes to create a JSON string that is saved in the database. 

**See what others are setting alerts for**
- The server queriers the database for five random alert_id's from all users profiles. 
- AJAX get request to load trending alerts on homepage. 

### Search Results

![alt search-results](https://raw.github.com/eluckette/price-ping/master/static/images/search-results.png)

- AJAX get request to retrieve JSON string that was created on user search. 
- When new page is selected, get request to refresh page results

**Selecting a Product**

![alt alert-preferences](https://raw.github.com/eluckette/price-ping/master/static/images/alert-preferences.png)

- Each products has link to open modal window. 
- Modal window displays product, product attributes and input boxes for user to set price alert preferences
- When window is originally opened, product information and corresponding user id are saved to the alerts table in the database as an inactive alert. 
- If the user submits information in the window, the alert information is sent to the server with a post request and the inactive alert is now changed to active.
 
### My Account

![alt my-account](https://raw.github.com/eluckette/price-ping/master/static/images/my-account.png)

**Current Alerts**
- All of the users current, active alerts are shown.

**Your recently viewed items**
- This column shows the last three items the user selected, but did not set an alert for. 

## Get Price Ping Running on Your Machine

Clone or fork this repo: 

```
https://github.com/eluckette/price-ping.git
```

Create and activate a virtual environment inside your project directory: 

```
virtualenv env
source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```


Get your own secret keys for Amazon Product API and Twilio API and save them to a file <kbd>secrets.sh</kbd>. 

Source your secret keys:

```
source secrets.sh
```

Run the app:

```
python server.py
```

Navigate to localhost:5000 to search Price Ping for products and set your own alerts. 

