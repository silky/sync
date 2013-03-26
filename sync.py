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
    if sudo: return command("".join(["sudo ", q]))
    else:    return command(q)

def gitSync(branch): 
    pretty(cmd("".join(["git pull origin ", branch])))
    pretty(cmd("".join(["git fetch upstream ", branch])))
    pretty(cmd("".join(["git pull --rebase upstream ", branch])))
    pretty(cmd("".join(["git push -f origin ", branch])))

def gitPU(branch): 
    pretty(cmd("".join(["git pull origin ", branch])))
    pretty(cmd("".join(["git commit -am \"submodule update\"", branch])))
    pretty(cmd("".join(["git push -f origin ", branch])))

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
        self.parent = parent
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
    print("------ Repository: ", repo, "------")
    haveparent = False
    r = repo.split("-t")
    pth = (r[0]).strip()
    if len(r) < 2:
        vcs = VCS.git
        branch = 'master'
    else:
        t = ((r[1]).strip()).split("-b")
        if len(t) < 2:
            branch = 'master'
        else:
            branch = (t[1]).strip()
        sbm = ((t[1]).strip()).split("-p")
        if len(sbm) < 2:
            haveparent = False
        else:
            haveparent = True
            parent = (sbm[1]).strip()
        vcs = {
            'git'       : VCS.git,
            'git git'   : VCS.git_git,
            'git hg' 	: VCS.git_mercurial,
            'git svn'   : VCS.git_subversion,
            'hg hg'     : VCS.hg_hg}[(t[0]).strip()]
    os.chdir(pth)
    thrd = ThreadingSync(vcs,branch)
    thrd.setDaemon(True)
    thrd.start()

    succ = True
    mustend = time.time() + 120
    while time.time() < mustend:
        if thrd.is_alive(): time.sleep(0.25)  
        else: 
            print(" --> ", r, ": successful synchronized :)")
            if haveparent:
                print("------ Parent update: ", parent, "------")
                os.chdir( parent.strip() )
                thrdp = ParentUpdate(vcs,branch,parent)
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

print("====================================================================")
print("            sync: Global repositories synchronizer v.1.1  ")
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
