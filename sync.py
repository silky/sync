#!/usr/bin/python

'''
	      sync - Light sync util
       Copyright (C)  2012  Heather

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
import time
from threading import Thread

# -------- below classes has some troubles with my IDE but nvm ---------
from configparser import ConfigParser 
from subprocess import Popen, PIPE
# ----------------------------------------------------------------------

class VCS:
  git=0
  git_git=1
  git_mercurial=2
  git_subversion=3
  git_veracity=4
  hg_hg=5

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
  
def gitgitSync(): 
  pretty(cmd("git pull origin master"))
  pretty(cmd("git fetch git master"))
  pretty(cmd("git push -f git master"))
  
def githgSync():
  pretty(cmd("hg pull"))
  pretty(cmd("hg update"))
  pretty(cmd("hg push git"))

def hghgSync():
  pretty(cmd("hg pull"))
  pretty(cmd("hg update"))
  pretty(cmd("hg push hg"))
  
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

class ThreadingSync(Thread):
  def __init__(self, vcs):
    Thread.__init__(self)
    self.vcs = vcs
  def run(self):
    if self.vcs == VCS.git:
      checkGitModifications()
      gitSync()
    elif self.vcs == VCS.git_git:
      gitgitSync()
    elif self.vcs == VCS.git_mercurial:
      githgSync()
    elif self.vcs == VCS.git_subversion:
      print ( "can't sync git from subversion yet")
    elif self.vcs == VCS.git_veracity:
      print ( "can't sync git from veracity yet")
      print ( "you can do it manually by using:")
      print ( "vv fast-export proj proj.vci")
      print ( "git fast-import < proj.vci")
    elif self.vcs == VCS.hg_hg:
      hghgSync()
      
def SyncStarter(repo):
  print("------ Repository: ", repo, "------")
  r = repo.split("-t")
  pth = (r[0]).strip()
  if len(r) < 2:
    vcs = VCS.git
  else:
    vcs = {
      'git' 		: VCS.git,
      'git git' 	: VCS.git_git,
      'git hg' 	    : VCS.git_mercurial,
      'git svn' 	: VCS.git_subversion,
      'git vv' 	    : VCS.git_veracity,
      'hg hg'       : VCS.hg_hg}[(r[1]).strip()]
  os.chdir(pth)
  thrd = ThreadingSync(vcs)
  thrd.setDaemon(True)
  thrd.start()

  succ = True
  mustend = time.time() + 100
  while time.time() < mustend:
    if thrd.is_alive(): time.sleep(0.25)  
    else: 
      print(" --> ", r, ": successful synchronized :)")
      succ = False
      break
  if succ: print(" --> ", r, ": timed out :(")
  print("______________________________________________________________________")
  
def syncrepos(repos):
  for r in repos.split("\n"):
    if r: SyncStarter(r)
print("====================================================================")
print("            sync: Global repositories synchronizer v.0.8  ")
print("====================================================================")
config = ConfigParser()
config.readfp(open('/etc/conf.d/repolist.conf'))
if os.geteuid() == 0:
  print("warning: running from root, only root repositories is syncing")
else:
  user = config.get('Repos','user')
  syncrepos(user)
  sudo = True
root = config.get('Repos','sudo')
syncrepos(root)
