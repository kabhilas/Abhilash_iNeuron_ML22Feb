from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import pymongo
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

reviewScrapper_APP = Flask(__name__)

@reviewScrapper_APP.route('/', methods=['GET'])
@cross_origin()
def  homePage():
    return render_template('index.html')

@reviewScrapper_APP.route('/review', methods=['POST'])
@cross_origin()
def reviews():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['demoDB']
            reviews = db[searchString].find({})
            if reviews.count() > 0:
                return render_template('results.html', reviews=reviews)
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage, "html.parser")
                bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
                del bigboxes[0:3]
                box = bigboxes[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prodRes.encoding = 'utf-8'
                prod_html = bs(prodRes.text, "html.parser")

                commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})

                table = db[searchString]
                reviews = []
                for commentbox in commentboxes:
                    try:
                        # name.encode(encoding='utf-8')
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = 'No Name'

                    try:
                        # rating.encode(encoding='utf-8')
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        # commentHead.encode(encoding='utf-8')
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        # custComment.encode(encoding='utf-8')
                        custComment = comtag[0].div.text
                    except Exception as e:
                        print("Exception while creating dictionary: ", e)

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}

                    x = table.insert_one(mydict)
                    reviews.append(mydict)
                return render_template('results.html', reviews=reviews)

        except:
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    reviewScrapper_APP.run(port=8000, debug=True)








