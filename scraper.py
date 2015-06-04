# This scraper collects all the AFL players from each of the club websites

import scraperwiki
import requests
from bs4 import BeautifulSoup
import datetime
import dateutil.parser
import re

afl = requests.get("http://www.afl.com.au/")

aflsoup = BeautifulSoup(afl.content)

aflul = aflsoup.find("ul",class_="team-logos")
afllis = aflul.find_all("li")

teams = {}
players = {}
for a in afllis:
	teams[a.a.text] = a.a.get("href")

for t in teams.keys():
	teampage = requests.get(teams[t])
	teamsoup = BeautifulSoup(teampage.content)
	nav = teamsoup.find("div",class_="nav")
	navlinks = nav.find_all("a")
	playerlink = None
	for n in navlinks:
		if t == u"North Melbourne":
			players[t] = teams[t]+"players"
		elif t == u"Geelong Cats":
			players[t] = "http://www.geelongcats.com.au/football/players/seniors"
		else:
			if "player" in n.get("href"):
				if "senior" in n.get("href"):
					players[t] = teams[t]+n.get("href")[1:]

data = []

for p in players.keys():
	playerpage = requests.get(players[p])
	playersoup = BeautifulSoup(playerpage.content)
	tbody = playersoup.find("tbody")
	thead = playersoup.find("thead")
	cats = []
	ths = thead.find_all("th")
	for th in ths:
		if th.get("class") != None:
			cats.append(th.get("class")[0])
	trs = tbody.find_all("tr")
	for tr in trs:
		player = {}
		tds = tr.find_all("td")
		for i,td in enumerate(tds):
			if i == 9:
				player['glsyear'] = td.text.strip()
			elif i == 10:
				player['glscareer'] = td.text.strip()
			else:
				player[cats[i]] = td.text.strip()
		player['club'] = p.replace(" ","-")
		player['year'] = datetime.datetime.now().year
		data.append(player)

scraperwiki.sqlite.save(unique_keys=["name","club","year"],data=data,table_name='players')
