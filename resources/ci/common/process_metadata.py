# While iterating through sprite files by game, this will combine and save metadata as necessary
# This one specifically grabs from the uniform format spreadsheet
#  while the sprite-local one collects the sprite format specific data

import codecs
import csv
import importlib
import json
import os
import re
import sys
import xlrd

from collections import OrderedDict
from glob import glob
from shutil import copyfile

sys.path.append(os.path.join(os.path.dirname(__file__),'../../../'))

def csv_from_excel(sheet,outbound):
    with(open(outbound,"w",encoding="utf-8")) as csv_file:
        wr = csv.writer(csv_file)
        for rownum in range(sheet.nrows):
            wr.writerow(sheet.row_values(rownum))

def process_metadata(console,game,sprite):
  local_resources = os.path.join(".","resources","ci",console,game,sprite)
  site_resources = os.path.join(".",console,game,sprite)
  online_resources = (f"https://snesrev.github.io/sprites-gfx/{console}/{game}/{sprite}")

  csv_sheet = []

  if(os.path.isfile(os.path.join(local_resources,"sprites.xls"))):
    print("Reading XLS")
    workbook = xlrd.open_workbook(os.path.join(local_resources,"sprites.xls"))
    worksheet = workbook.sheet_by_index(0)

    print("Creating CSV")
    csv_from_excel(worksheet,os.path.join(local_resources,"sprites.csv"))
    copyfile(os.path.join(local_resources,"sprites.csv"),os.path.join(site_resources,"sprites.csv"))
    del worksheet
    del workbook

    print("Getting data from CSV")
    with(open(os.path.join(local_resources,"sprites.csv"),"r",encoding="utf-8")) as csv_file:
        rd = csv.reader(csv_file)
        for row in rd:
          if len(row) > 0:
            csv_sheet.append(row)

  spritesmeta = OrderedDict()

  # Get data from sprite specific metadata source
  metamodule = False
  maxs = 30
  maxn = 0
  try:
    metamodule = importlib.import_module(f"resources.ci.{console}.{game}.{sprite}.sprite_metadata")
  except ModuleNotFoundError:
    print("No specific metadata processing for: %s/%s/%s" % (console,game,sprite))
  if metamodule:
    (spritesmeta,maxs,maxn) = metamodule.get_local_metadata()

  num = max(len(csv_sheet) - 1,len(spritesmeta))

  print()
  msg = "Wait a little bit, dude, t" if num > 0 else "T"
  print("%shere's %d records for processing." % (msg,num))
  print()

  sprites = []
  if(len(csv_sheet) > 0):
    print("Processing metadata from CSV")
    keys = []
    i = 0
    for row in csv_sheet:
        j = 0
        for cell in row:
            if i == 0:
                keys.append(cell.lower())
            else:
                if i > len(sprites):
                    sprites.append({})
                sprites[i - 1][keys[j]] = cell
            j += 1
        i+= 1

    print("Merging metadata")
    i = 1
    n = len(sprites)
    maxd = len(str(n))
    for sprite in sprites:
      slug = ""
      for k,v in sprite.items():
        v = v.strip()
        if v != "":
          if k == "slug":
            slug = v
            if slug not in spritesmeta:
              spritesmeta[slug] = {}
              spritesmeta[slug]["file"] = online_resources + "/sheets/" + slug + ".png"
              spritesmeta[slug]["preview"] = spritesmeta[slug]["file"]
              spritesmeta[slug]["short_slug"] = slug
              spritesmeta[slug]["slug"] = slug
            print("Finalizing %*d/%*d %-*s [%-*s]" %
              (
                maxd,i,
                maxd,n,
                maxn,spritesmeta[slug]["name"] if "name" in spritesmeta[slug] else "",
                maxs,slug
              )
            )
          else:
            key = k
            subkey = ""
            if "t-" in k:
              key = "tags"
              subkey = k.replace("t-","")
            elif "u-" in k:
              key = "usage"
              if v != "Y":
                v = ""
              else:
                v = k.replace("u-","")
            # If we have a value
            if v != "":
              v = v.translate({
                0x201c : u'"',
                0x201d : u'"',
                0x2018 : u"'",
                0x2019 : u"'"
              })

              # If it's a special field
              if '-' in k:
                # If we don't have a spot for it yet
                if key not in spritesmeta[slug]:
                  # Make a spot for it
                  if subkey != "":
                    spritesmeta[slug][key] = {}
                    spritesmeta[slug][key + "flat"] = []
                  else:
                    spritesmeta[slug][key] = []
                if subkey != "":
                  if subkey not in spritesmeta[slug][key]:
                    spritesmeta[slug][key][subkey] = []
                  spritesmeta[slug][key][subkey].append(v)
                  spritesmeta[slug][key + "flat"].append(v)
                else:
                  spritesmeta[slug][key].append(v)
              else:
                spritesmeta[slug][key] = v
      i += 1

    with(open(os.path.join(site_resources,"sprites.json"),"w",encoding="utf-8")) as json_file:
      vals = spritesmeta.values()
      vlist = list(vals)
      slist = sorted(vlist, key=lambda s: str.lower(s["short_slug"] if "short_slug" in s else "").strip())
      json.dump(slist,json_file,indent=2)
    with(open(os.path.join(site_resources,"z3m3.json"),"w",encoding="utf-8")) as json_file:
      slist = []
      for sprite in spritesmeta.values():
        if "name" in sprite:
          slist.append({
            "title": sprite["name"],
            "path": sprite["slug"]
          })
      json.dump(slist,json_file,indent=2)

def do_metadata():
  with(open(os.path.join(".","meta","manifests","consoles.txt"), "r")) as consoles:
    for console in consoles:
      console = console.strip()
      paths = { "console": os.path.join(".",console) }
      with(open(os.path.join(paths["console"],"games.txt"), "r")) as games:
        for game in games:
          game = game.strip()
          paths["game"] = os.path.join(paths["console"],game)
          with(open(os.path.join(paths["game"],"manifests","manifest.json"), "r")) as manifest:
            manifest = json.load(manifest)
            for key in manifest:
              if "$schema" not in key:
                if "name" in manifest[key] and "folder name" in manifest[key]:
                  sprite = manifest[key]["folder name"]
                  paths["sprite"] = os.path.join(paths["game"],sprite)
                  print("Processing: %s/%s/%s" % (console,game,sprite))
                  process_metadata(console,game,sprite)
                  print()

if __name__ == "__main__":
  do_metadata()
