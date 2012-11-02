#!/usr/bin/python -O

'''
	      sync - Light sync util
          Copyright (C)  2012  Ash Harley

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
'''

import os
import string
import configparser 
from subprocess import *

def command(x):
  return str(Popen(x.split(' '), stdout=PIPE).communicate()[0])

def rm_empty(L): return [l for l in L if (l and l!="")]

def pretty(msg):
  ss = msg.split("\n")
  for s in ss: 
    if not s.startswith("b"): print(s)

def gitPull(): pretty(command("git pull origin master"))
def gitFetchUpstream(): pretty(command("git fetch upstream master"))
def gitRebase(): pretty(command("git pull --rebase upstream master"))
def gitForcePush(): pretty(command("git push -f origin master"))

def gitUntracked():
  status = command("git status")
  if "# Untracked files:" in status:
    untf = status.split("# Untracked files:")[1][1:].split("\n")
    return rm_empty([x[2:] for x in untf if string.strip(x) != "#" and x.startswith("#\t")])
  else:
    return []

def gitNew():
  status = command("git status").split("\n")
  return [x[14:] for x in status if x.startswith("#\tnew file:   ")]

def gitModified():
  status = command("git status").split("\n")
  return [x[14:] for x in status if x.startswith("#\tmodified:   ")]

def checkGitModifications():
  print("Untracked:", gitUntracked())
  print("New:", gitNew())
  print("Modified:", gitModified())

def sync(repo):
  os.chdir(repo)
  checkGitModifications()
  gitPull()
  gitFetchUpstream()
  gitRebase()
  gitForcePush()

config = configparser.ConfigParser()
config.readfp(open('repolist.conf'))
repos = config.get('General','repositories')
for r in repos.split("\n"):
  if r:
    print("Repo: ", r)
    sync(r)
