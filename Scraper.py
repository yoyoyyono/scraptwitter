import requests,json,re,datetime,sys
from bs4 import BeautifulSoup
from urllib.parse import quote
from pyquery import PyQuery
from . import Tweet

class Scraper:

    def __init__(self):
        pass

    @staticmethod
    def twitterSession(username, password):
        s = requests.Session()
        resp = s.get("https://twitter.com/login")
        soup = BeautifulSoup(resp.text,"lxml")

        token = soup.select_one("[name='authenticity_token']")['value']

        payload={
        'session[username_or_email]':username,
        'session[password]':password,
        'authenticity_token':token,
        'ui_metrics':'{"rf":{"c6fc1daac14ef08ff96ef7aa26f8642a197bfaad9c65746a6592d55075ef01af":3,"a77e6e7ab2880be27e81075edd6cac9c0b749cc266e1cea17ffc9670a9698252":-1,"ad3dbab6c68043a1127defab5b7d37e45d17f56a6997186b3a08a27544b606e8":252,"ac2624a3b325d64286579b4a61dd242539a755a5a7fa508c44eb1c373257d569":-125},"s":"fTQyo6c8mP7d6L8Og_iS8ulzPObBOzl3Jxa2jRwmtbOBJSk4v8ClmBbF9njbZHRLZx0mTAUPsImZ4OnbZV95f-2gD6-03SZZ8buYdTDkwV-xItDu5lBVCQ_EAiv3F5EuTpVl7F52FTIykWowpNIzowvh_bhCM0_6ReTGj6990294mIKUFM_mPHCyZxkIUAtC3dVeYPXff92alrVFdrncrO8VnJHOlm9gnSwTLcbHvvpvC0rvtwapSbTja-cGxhxBdekFhcoFo8edCBiMB9pip-VoquZ-ddbQEbpuzE7xBhyk759yQyN4NmRFwdIjjedWYtFyOiy_XtGLp6zKvMjF8QAAAWE468LY"}',
        'scribe_log':'',
        'redirect_after_login':'',
        'authenticity_token':token,
        'remember_me':1
        }
        headers={
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'content-type':'application/x-www-form-urlencoded',
        'origin':'https://twitter.com',
        'referer':'https://twitter.com/login',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        s.post("https://twitter.com/sessions",data=payload,headers=headers)
        return s

    @staticmethod
    def getTimeline(twitterSession, TimelineCriteria, receiveBuffer=None, bufferLength=100):
        refreshCursor = ''
        results = []
        resultsAux = []
        active = True
        first = True
        n=1
        while active:
            json = Scraper.getJson(twitterSession, TimelineCriteria, refreshCursor, cookies=twitterSession.cookies, first=first)
            if len(json['items_html'].strip()) == 0:
                break           
            scrapedTweets = PyQuery(json['items_html'])
            scrapedTweets.remove('div.withheld-tweet')
            tweets = scrapedTweets('div.js-stream-tweet')
            first = False
            
            if len(tweets) == 0:
                break
            
            for tweetHTML in tweets:
                tweetPQ = PyQuery(tweetHTML)
                tweet = Tweet.Tweet()
                
                usernameTweet = tweetPQ("span:first.username.u-dir b").text()
                txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
                retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
                favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
                dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))
                id = tweetPQ.attr("data-tweet-id")
                permalink = tweetPQ.attr("data-permalink-path")
                
                geo = ''
                geoSpan = tweetPQ('span.Tweet-geo')
                if len(geoSpan) > 0:
                    geo = geoSpan.attr('title')
                
                tweet.id = id
                tweet.permalink = 'https://twitter.com' + permalink
                tweet.username = usernameTweet
                tweet.text = txt
                tweet.date = datetime.datetime.fromtimestamp(dateSec)
                tweet.retweets = retweets
                tweet.favorites = favorites
                tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
                tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
                tweet.geo = geo
                
                results.append(tweet)
                resultsAux.append(tweet)
                
                if receiveBuffer and len(resultsAux) >= bufferLength:
                    receiveBuffer(resultsAux)
                    resultsAux = []
                
                if TimelineCriteria.maxTweets > 0 and len(results) >= TimelineCriteria.maxTweets:
                    active = False
                    breakpoint

            refreshCursor = str(id)
                        
    
        if receiveBuffer and len(resultsAux) > 0:
            receiveBuffer(resultsAux)
        
        return results

    @staticmethod
    def getJson(twitterSession, TimelineCriteria, refreshCursor, cookies, first):
        url = "https://twitter.com/i/profiles/show/%s/timeline/with_replies?"
        urlGetData = TimelineCriteria.username
        url = url % (quote(urlGetData))
        if first==False:
            url = url+"include_available_features=1&include_entities=1&max_position="+str(refreshCursor)+"&reset_error_state=false"
        headers={
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'content-type':'application/x-www-form-urlencoded',
            'origin':'https://twitter.com',
            'referer':'https://twitter.com/login',
            'upgrade-insecure-requests':'1',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        resp = twitterSession.request('GET', url, cookies=cookies, headers=headers)
        try:
            jsonData = resp.json()
        except:
            print("You entered an incorrect username or password. Try again.")

        return jsonData
        
