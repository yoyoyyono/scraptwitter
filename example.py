import sys,getopt,datetime,codecs
import scraptwitter

username = str(input("Username: "))
password = str(input("Password: "))

targetUser = str(input("Profile to scrap: "))

s = scraptwitter.Scraper.Scraper.twitterSession(username, password)

criteria = scraptwitter.TimelineCriteria.TimelineCriteria().setUsername(targetUser)

tweets = scraptwitter.Scraper.Scraper.getTimeline(s, criteria)





outputFileName= "test.csv"

outputFile = codecs.open(outputFileName, "w+", "utf-8")

outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink')

for t in tweets:
    outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink)))
outputFile.flush()
print('More %d saved on file...\n' % len(tweets))
outputFile.close()
