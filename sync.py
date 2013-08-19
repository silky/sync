#!/usr/bin/python

'''
              sync - Light sync util
          Copyright (C)  2012-2013  Heather

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

#Python 2x / 3x compatibility
try:  from configparser import ConfigParser 
except ImportError: 
    from ConfigParser import ConfigParser 

from subprocess import Popen, PIPE
# ----------------------------------------------------------------------

class VCS:
    git=0
    git_git=1
    git_mercurial=2
    git_subversion=3
    hg_hg=5

sudo = False

def command(x):
    return str(Popen(x.split(' '), stdout=PIPE).communicate()[0])
def rm_empty(L): return [l for l in L if (l and l!="")]
def pretty(msg):
    ss = msg.split("\n")
    for s in ss: 
        if not s.startswith("b"): print(s)
def cmd(q):
    if sudo: return command("".join(["sudo ", q]))
    else:    return command(q)
def sh(s): pretty(cmd(s))

def gitSync(branch): 
    sh("git rebase --abort")
    sh("".join(["git pull origin ", branch]))
    sh("".join(["git fetch upstream ", branch]))
    sh("".join(["git pull --rebase upstream ", branch]))
    sh("".join(["git push -f origin ", branch]))

def gitPU(branch): 
    sh("".join(["git pull origin ", branch]))
    sh("git commit -am submodule")
    sh("".join(["git push -f origin ", branch]))

def gitgitSync(): 
    sh("git pull origin master")
    sh("git fetch git master")
    sh("git push -f git master")

def githgSync():
    sh("hg pull")
    sh("hg update")
    sh("hg push git")

def hghgSync():
    sh("hg pull")
    sh("hg update")
    sh("hg push hg")

def gitNew():
    status = command("git status").split("\n")
    return [x[14:] for x in status if x.startswith("#\tnew file:   ")]

def gitModified():
    status = command("git status").split("\n")
    return [x[14:] for x in status if x.startswith("#\tmodified:   ")]

def checkGitModifications():
    print("New:", gitNew())
    print("Modified:", gitModified())

class ParentUpdate(Thread):
    def __init__(self, vcs, branch):
        Thread.__init__(self)
        self.vcs = vcs
        self.branch = branch
    def run(self):
        if self.vcs == VCS.git:
            checkGitModifications()
            gitPU(self.branch)

class ThreadingSync(Thread):
    def __init__(self, vcs, branch):
        Thread.__init__(self)
        self.vcs = vcs
        self.branch = branch
    def run(self):
        if self.vcs == VCS.git:
            checkGitModifications()
            gitSync(self.branch)
        elif self.vcs == VCS.git_git:
            gitgitSync()
        elif self.vcs == VCS.git_mercurial:
            githgSync()
        elif self.vcs == VCS.git_subversion:
            print ( "can't sync git from subversion yet")
        elif self.vcs == VCS.hg_hg:
            hghgSync()

def SyncStarter(repo):
    vcs = VCS.git
    haveparent = False
    branch = 'master'
    parent = ''

    r = repo.split(" -t")
    pth  = ((r[0]).split(" "))[0]

    print("------ Repository: ", pth, "------")

    if len(r) > 1:
        svcs = ((r[1]).split(" "))[1]
        vcs = { 
            'git'       : VCS.git,
            'git git'   : VCS.git_git,
            'git hg'    : VCS.git_mercurial,
            'git svn'   : VCS.git_subversion,
            'hg hg'     : VCS.hg_hg}[svcs]

    t = repo.split(" -b")   # <----- Branch
    if len(t) > 1:
        branch = ((t[1]).split(" ")[1])
    sbm = repo.split(" -p") # <----- Submodule Parents
    if len(sbm) > 1:
        haveparent = True
        parent = ((sbm[1]).split(" ")[1])

    os.chdir(pth)
    thrd = ThreadingSync(vcs,branch)
    thrd.setDaemon(True)
    thrd.start()

    succ = True
    mustend = time.time() + 120
    while time.time() < mustend:
        if thrd.is_alive(): time.sleep(0.25)  
        else: 
            print(" --> ", pth, ": successful synchronized :)")
            if haveparent:
                print(">>>>>>>>> Parent update: ", parent)
                os.chdir( parent.strip() )
                thrdp = ParentUpdate(vcs,branch)
                thrdp.setDaemon(True)
                thrdp.start()
                succp = True
                mustendp = time.time() + 120
                while time.time() < mustendp:
                    if thrdp.is_alive(): time.sleep(0.25)  
                    else: 
                        print(" --> ", parent, ": successful synchronized :)")
                        succp = False
                        break
                if succp: print(" --> ", parent, ": timed out :(")
            succ = False
            break
    if succ: print(" --> ", r, ": timed out :(")
    print("______________________________________________________________________")

def syncrepos(repos): 
    for r in repos.split("\n"): 
        if r: SyncStarter(r)

def sync(oz): 
    if oz == 'nt':
        config.readfp(open('../repolist.conf'))
        syncrepos( config.get('Repos','user') )
    else:
        config.readfp(open('/etc/conf.d/repolist.conf'))
        if os.geteuid() == 0:
            print("warning: running from root, only root repositories is syncing")
        else:
            user = config.get('Repos','user')
            syncrepos(user)
            sudo = True
        root = config.get('Repos','sudo')
        syncrepos(root)

print("=====================================================================================")
print("                     sync: Global repositories synchronizer v.1.8  ")
print("=====================================================================================")

config = ConfigParser()
sync(os.name)