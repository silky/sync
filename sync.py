#!/usr/bin/python

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

class VCS:
  git_git=1
  git_mercurial=2
  git_subversion=3
  git_veracity=4

def command(x):
  return str(Popen(x.split(' '), stdout=PIPE).communicate()[0])
def rm_empty(L): return [l for l in L if (l and l!="")]
def pretty(msg):
  ss = msg.split("\n")
  for s in ss: 
    if not s.startswith("b"): print(s)
sudo = False
def cmd(q):
  if sudo:
    return command("".join(["sudo ", q]))
  else:
    return command(q)

def gitSync(): 
  pretty(cmd("git pull origin master"))
  pretty(cmd("git fetch upstream master"))
  pretty(cmd("git pull --rebase upstream master"))
  pretty(cmd("git push -f origin master"))
  
def githgSync():
  pretty(cmd("hg pull master"))
  pretty(cmd("hg pull upstream master"))
  pretty(cmd("hg update"))
  pretty(cmd("hg push master"))

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
  r = repo.split("-t")
  path = (r[0]).strip()
  if len(r) < 2:
    vcs = VCS.git_git
  else:
    vcs = {
      'git git' 	: VCS.git_git,
      'git hg' 		: VCS.git_mercurial,
      'git svn' 	: VCS.git_subversion,
      'git vv' 		: VCS.git_veracity}[(r[1]).strip()]
  os.chdir(path)
  if vcs == VCS.git_git:
    checkGitModifications()
    gitSync()
  elif vcs == VCS.git_mercurial:
    githgSync();
  elif vcs == VCS.git_subversion:
    print ( "can't sync git from subversion yet")
  elif vcs == VCS.git_veracity:
    print ( "can't sync git from veracity yet")
  
def syncrepos(repos):
  for r in repos.split("\n"):
    if r:
      print("Repo: ", r)
      sync(r)
print("================================================")
print("  sync: Global repositories synchronizer v.0.1  ")
print("================================================")
config = configparser.ConfigParser()
config.readfp(open('/etc/conf.d/repolist.conf'))
if os.geteuid() == 0:
  print("warning: running from root, only root repositories is syncing")
else:
  user = config.get('Repos','user')
  syncrepos(user)
  sudo = True
root = config.get('Repos','sudo')
syncrepos(root)
