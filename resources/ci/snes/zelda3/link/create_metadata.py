import csv
import json
import os
import xlrd

from collections import OrderedDict
from glob import glob
from shutil import copyfile
from ZSPR import ZSPR

def csv_from_excel(sheet,outbound):
    with(open(outbound,"w+",encoding="utf8")) as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_NONE)
        for rownum in range(sheet.nrows):
            wr.writerow(sheet.row_values(rownum))

local_resources = os.path.join(".","resources","ci","snes","zelda3","link")
site_resources = os.path.join(".","snes","zelda3","link")
online_resources = "https://snesrev.github.io/sprites-gfx/snes/zelda3/link"

print("Reading XLS")
workbook = xlrd.open_workbook(os.path.join(local_resources,"sprites.xls"))
worksheet = workbook.sheet_by_index(0)

print("Creating CSV")
csv_from_excel(worksheet,os.path.join(local_resources,"sprites.csv"))
copyfile(os.path.join(local_resources,"sprites.csv"),os.path.join(site_resources,"sprites.csv"))
del worksheet
del workbook

print("Getting data from CSV")
csv_sheet = []
with(open(os.path.join(local_resources,"sprites.csv"),"r")) as csv_file:
    line = csv_file.readline()
    while line:
        if line.strip() != "":
            csv_sheet.append(line.strip().split(','))
        line = csv_file.readline()

print("Getting metadata from ZSPRs")
spritesmeta = OrderedDict()
# get ZSPRs
maxd,maxs,maxn = 0,0,0

for file in glob(os.path.join(site_resources,"sheets","*.zspr")):
    if os.path.isfile(file):
        sprite = ZSPR(file)
        basename = sprite.filename
        slug = sprite.slug
        ver = slug[slug.rfind('.') + 1:]
        slug = sprite.slug[:slug.rfind('.')].strip()
        maxs = max(maxs,len(slug))
        maxn = max(maxn,len(sprite.name))
        if slug not in spritesmeta:
              spritesmeta[slug] = {}
        spritesmeta[slug]["name"] = sprite.name
        spritesmeta[slug]["author"] = sprite.author_name
        spritesmeta[slug]["version"] = int(ver)
        spritesmeta[slug]["file"] = online_resources + "/sheets/" + basename
        spritesmeta[slug]["slug"] = slug

print()
print("Wait a little bit, dude, there's %d sprites." % (len(spritesmeta)))
print()

print("Processing metadata from CSV")
sprites = []
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
        if "t-" in k:
          key = "tags"
        elif "u-" in k:
          key = "usage"
          if v != "Y":
            v = ""
          else:
            v = k.replace("u-","")
        if v != "":
          if '-' in k:
            if key not in spritesmeta[slug]:
              spritesmeta[slug][key] = []
            spritesmeta[slug][key].append(v)
          else:
            spritesmeta[slug][key] = v
  i += 1

with(open(os.path.join(site_resources,"sprites.json"),"w+")) as json_file:
    vals = spritesmeta.values()
    vlist = list(vals)
    slist = sorted(vlist, key=lambda s: str.lower(s["slug"] or "").strip())
    json.dump(slist,json_file,indent=2)
