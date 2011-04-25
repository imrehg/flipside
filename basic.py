#!/usr/bin/env python
# -*- coding: utf-8 -*-
try: 
  from xml.etree import ElementTree
except ImportError:  
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import secrets
import string
import random

def PrintFeed(feed):
  for i, entry in enumerate(feed.entry):
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
      print '%s %s' % (entry.title.text, entry.content.text)
    elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
      print '%s %s %s' % (i, entry.title.text, entry.content.text)
      # Print this row's value for each column (the custom dictionary is
      # built from the gsx: elements in the entry.) See the description of
      # gsx elements in the protocol guide.
      print 'Contents:'
      for key in entry.custom:
        print '  %s: %s' % (key, entry.custom[key].text)
    else:
      print '%s %s' % (i, entry.title.text)

def PromptForSpreadsheet(gd_client):
  # Get the list of spreadsheets
  feed = gd_client.GetSpreadsheetsFeed()
  PrintFeed(feed)
  input = raw_input('\nSelection: ')
  return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]

def PromptForWorksheet(gd_client, key):
  # Get the list of worksheets
  feed = gd_client.GetWorksheetsFeed(key)
  PrintFeed(feed)
  input = raw_input('\nSelection: ')
  return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]

def ListGetAction(gd_client, key, wksht_id):
  # Get the list feed
  feed = gd_client.GetListFeed(key, wksht_id)
  # PrintFeed(feed)
  return feed

def updateScore(entry, good):
    out = {}
    for key in entry.custom:
        out[key] = entry.custom[key].text

    # Update total number
    try:
        out['guess'] = unicode(int(out["guess"]) + 1)
    except:
        out['guess'] = unicode(1)

    if good:
        try:
            out["goodguess"] = unicode(int(out["goodguess"]) + 1)
        except:
            out["goodguess"] = unicode(1)
        try:
            out["goodinrow"] = unicode(int(out["goodinrow"]) + 1)
        except:
            out["goodinrow"] = unicode(1)
    else:
        out["goodinrow"] = unicode(0)

    return out

def getChoice(entry):
    total = len(entry)
    gnum = random.sample(range(total), 4)
    guesses = [entry[i] for i in gnum]
    order = range(0, 4)
    random.shuffle(order)
    print bcolors.HEADER + (u"Word: %s (%s)" %(guesses[0].custom['chinese'].text, guesses[0].custom['pronounciation'].text)) + bcolors.ENDC
    print "".join([u"%d) %s  " %(i+1, guesses[order[i]].custom['english'].text) for i in range(0, 4)])
    try:
        gval = int(raw_input("? "))-1
        if (0 == order[gval]):
            right = True
        else:
            right = False
    except:
        right = False
    if right:
        print bcolors.OKGREEN + "Yeah!" + bcolors.ENDC
    else:
        print bcolors.FAIL + ("Nope, it was: %s" %(guesses[0].custom['english'].text)) + bcolors.ENDC
    print

    newscore = updateScore(guesses[0], right)
    newentry = gd_client.UpdateRow(
        guesses[0],
        newscore)
    ## Got to update our info with the latest data
    entry[gnum[0]] = newentry
    return entry, right

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = secrets.email
gd_client.password = secrets.password
gd_client.source = 'flipside'
gd_client.ProgrammaticLogin()

## Sidestep this for a bit, fix our spreadsheet/worksheet
# sheetkey = PromptForSpreadsheet(gd_client)
# workkey = PromptForWorksheet(gd_client, sheetkey)
# data = ListGetAction(gd_client, sheetkey, workkey)
data = gd_client.GetListFeed("tMQrGX97su_LcILqyWzJddQ", "od6")

entry = data.entry
total = 30
good = 0
for i in xrange(total):
    print "Question #%d" %(i+1)
    entry, right = getChoice(entry)
    if right:
        good += 1

print bcolors.HEADER + ("Finished, %d good out of %d (%.1f%%)" %(good, total, 100.0*good/total)) + bcolors.ENDC

# ### Simple application
# Get list of spreadseets
# Get list of worksheets
# Get headers
# Get all rows, organize internal data structure
# Show random element + 3 wrong answers to choose from
# Choose and update results: tries, good tries, good tries in a row (three columns)

# Base number: 16
# Every 10 the row halves it:
# 10->8, 20->4, 30->2, 40->1,
# Test class:
