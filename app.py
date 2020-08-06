from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

class Data:
  def __init__(self, title, year, rating, votes, metascore):
    self.title = title
    self.year = year
    self.rating = rating
    self.votes = votes
    self.metascore = metascore

  def to_dict(self):
    return {
        'Title': self.title,
        'Year': self.year,
        'Rating': self.rating,
        'Votes': self.votes,
        'Metascore': self.metascore
    }

def scrap(url):
    #This is fuction for scrapping
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                'Cache-Control': 'no-cache'}   

    url_get = requests.get(url,headers=headers)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find("div",{"class":"lister-list"}) 
    tr = table.find_all("div",{"class":"lister-item mode-advanced"}) 
    temp = [] #initiating a tuple

    for i in range(0, len(tr)):
         
        row = tr[i]
        #use the key to take information here
        # title class
        titleH3=row.find("h3",{"class":"lister-item-header"})
        title=titleH3.find("a").text
        year=titleH3.find("span",{"class":"lister-item-year text-muted unbold"}).text

        rating=0
        metascore=0
        ratingTag = row.find("div",{"class":"ratings-bar"})
        if ratingTag is not None:
            ratingsBarTag = ratingTag.find("strong")
            if ratingsBarTag is not None:
                rating = ratingsBarTag.text
            
            metascoreTag = ratingTag.find("span",{"class":"metascore"})
            if metascoreTag is not None:
                metascore = metascoreTag.text.strip()
        
        votes=0
        votesTag = row.find("p",{"class":"sort-num_votes-visible"})
        if votesTag is not None:
            votesText = votesTag.find("span",{"class":"text-muted"}).text
            if votesText == 'Votes:':
                votes = votesTag.find("span",{"name":"nv"})['data-value']

        d= Data(title,year,rating,votes,metascore)
        temp.append(d) #append the needed information 
    
    
    df= pd.DataFrame.from_records([d.to_dict() for d in temp])   #data wranggling -  try to change the data type to right data type
    if (df.size>0) :
        df['Rating'] = df['Rating'].astype('float64')
        df['Votes'] = df['Votes'].astype('int64')
        df['Metascore'] = df['Metascore'].astype('int64')
   #end of data wranggling
    nextUrlTag = soup.find("div",{"class":"desc"}).find("a",{"class":"lister-page-next next-page"}) 
    nextUrl=''
    if nextUrlTag is not None:
        nextUrl=nextUrlTag['href']
    return [df,nextUrl]

@app.route("/")
def index():
    returnData = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
    df=returnData[0] #insert url here
    result=''
    pageCount=0
    nextUrl = returnData[1]
    while ((nextUrl != '') and (pageCount < 1)):
        print(nextUrl)
        returnData2 = scrap('https://www.imdb.com'+nextUrl)
        df2 = returnData2[0]
        nextUrl = returnData2[1]
        pageCount=pageCount+1
        if df2.size>0:
            df = df.append(df2, ignore_index=True)

    # df = pd.read_pickle("./cached_dataframe200.pkl")
    # df['Metascore'] = df['Metascore'].astype('int64')
    print(df.dtypes)
    

    # This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib


    fig = plt.figure(figsize=(5,5),dpi=300)
    df.set_index('Title')['Rating'].sort_values(ascending=False).head(7).plot.bar()
    
    #Do not change this part
    plt.savefig('plot2',bbox_inches="tight") 
    plt.tight_layout()
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result2 = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    fig = plt.figure(figsize=(5,5),dpi=300)
    df.set_index('Title')['Votes'].sort_values(ascending=False).head(7).plot.bar()
    
    #Do not change this part
    plt.savefig('plot2',bbox_inches="tight") 
    plt.tight_layout()
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result3 = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    fig = plt.figure(figsize=(5,5),dpi=300)
    df.set_index('Title')['Metascore'].sort_values(ascending=False).head(7).plot.bar()
    
    #Do not change this part
    plt.savefig('plot2',bbox_inches="tight") 
    plt.tight_layout()
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result4 = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    # df.to_pickle('cached_dataframe200.pkl')
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result, result2=result2, result3=result3, result4=result4)


if __name__ == "__main__": 
    app.run()
