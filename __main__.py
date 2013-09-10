#!/usr/bin/env python

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
fst = True

#statistics
total = 0
success = 0
error = 0

def command(x, shll):
    return str(Popen(x.split(' '), stdout=PIPE, shell = shll).communicate()[0])
def pretty(msg):
    ss = msg.split("\n")
    for s in ss: 
        if not s.startswith("b"): print(s)
def cmd(q, shll):
    if sudo: return command("".join(["sudo ", q]), shll)
    else:    return command(q, shll)
def sh(s, shll): pretty(cmd(s,shll))

def gitSync(branch, upstreambranch, shell):
    sh("".join(["git checkout ", branch]), shell)
    sh("git rebase --abort", shell)
    sh("".join(["git pull origin ", branch]), shell)
    sh("".join(["git fetch upstream ", upstreambranch]), shell)
    sh("".join(["git pull --rebase upstream ", upstreambranch]), shell)
    sh("".join(["git push -f origin ", branch]), shell)

def gitPU(branch, shell):
    sh("".join(["git pull origin ", branch]), shell)
    sh("git commit -am submodule", shell)
    sh("".join(["git push -f origin ", branch]), shell)

def gitgitSync(shell):
    sh("git pull origin master", shell)
    sh("git fetch git master", shell)
    sh("git push -f git master", shell)

def githgSync(shell):
    sh("hg pull", shell)
    sh("hg update", shell)
    sh("hg push git", shell)

def hghgSync(shell):
    sh("hg pull", shell)
    sh("hg update", shell)
    sh("hg push hg", shell)

def gitNew(shell):
    status = command("git status", shell).split("\n")
    return [x[14:] for x in status if x.startswith("#\tnew file:   ")]

def gitModified(shell):
    status = command("git status", shell).split("\n")
    return [x[14:] for x in status if x.startswith("#\tmodified:   ")]

def checkGitModifications(shell):
    print("New: %s" % gitNew(shell))
    print("Modified: %s" % gitModified(shell))

class ParentUpdate(Thread):
    def __init__(self, vcs, branch, recursive):
        Thread.__init__(self)
        self.vcs = vcs
        self.branch = branch
        self.shell = recursive
    def run(self):
        if self.vcs == VCS.git:
            checkGitModifications(self.shell)
            gitPU(self.branch, self.shell)

class ThreadingSync(Thread):
    def __init__(self, vcs, branch, upstreambranch, recursive):
        Thread.__init__(self)
        self.vcs = vcs
        self.branch = branch
        self.upstreambranch = upstreambranch
        self.shell = recursive
    def run(self):
        if self.vcs == VCS.git:
            checkGitModifications(self.shell)
            gitSync(self.branch, self.upstreambranch, self.shell)
        elif self.vcs == VCS.git_git:
            gitgitSync(self.shell)
        elif self.vcs == VCS.git_mercurial:
            githgSync(self.shell)
        elif self.vcs == VCS.git_subversion:
            print ("can't sync git from subversion yet")
        elif self.vcs == VCS.hg_hg:
            hghgSync(self.shell)

def DoUpdate(vcs, branch, useub, haveparent, upstreambranch, parent, recursive):
    global success
    global error
    if not useub: upstreambranch = branch
    thrd = ThreadingSync(vcs,branch, upstreambranch, recursive)
    thrd.setDaemon(True)
    thrd.start()

    failed = True
    mustend = time.time() + 120
    while time.time() < mustend:
        if thrd.is_alive(): time.sleep(0.25)  
        else: 
            success+=1
            print(" --> successful synchronized :)")
            if haveparent:
                print(">>>>>>>>> Parent update: %s" % parent)
                os.chdir( parent.strip() )
                thrdp = ParentUpdate(vcs, branch, recursive)
                thrdp.setDaemon(True)
                thrdp.start()
                succp = True
                mustendp = time.time() + 120
                while time.time() < mustendp:
                    if thrdp.is_alive(): time.sleep(0.25)  
                    else: 
                        print(" --> %s : successful synchronized :)" % parent)
                        succp = False
                        break
                if succp: print(" --> %s : timed out :(" % parent)
            failed = False
            break
    if failed: 
        error+=1
        print(" --> %s : timed out :(" % r)

def SyncStarter(repo, recursive):
    global fst
    global total
    
    vcs = VCS.git
    useub = False
    haveparent = False
    branches = ''
    branch = 'master'
    parent = ''
    upstreambranch = ''

    r = repo.split(" -t")
    pth  = ((r[0]).split(" "))[0]

    print("------ Repository: %s ------" % pth)
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
        branches = branch.split(",")
    pb = repo.split(" -u") # <----- Upstream Branch
    if len(pb) > 1:
        useub = True
        upstreambranch = ((pb[1]).split(" ")[1])
    sbm = repo.split(" -p") # <----- Submodule Parents
    if len(sbm) > 1:
        haveparent = True
        parent = ((sbm[1]).split(" ")[1])

    if recursive:
        if fst: 
            fst = False
            os.chdir(pth)
        else:
            os.chdir("..")
            os.chdir(pth)
    else: os.chdir(pth)
        
    if len(branches) > 1:
        for b in branches:
            total += 1
            print("--> branch: %s" % b)
            DoUpdate(vcs, b, useub, haveparent, upstreambranch, parent, recursive)
    else:
        total += 1
        DoUpdate(vcs, branch, useub, haveparent, upstreambranch, parent, recursive)
    print("______________________________________________________________________")

def syncrepos(repos, recursive): 
    for r in repos.split("\n"): 
        if r: SyncStarter(r, recursive)

def sync(oz): 
    global sudo
    if oz == 'nt':
        config.readfp(open('repolist.conf'))
        syncrepos( config.get('Repos','user') , True)
    else:
        config.readfp(open('/etc/repolist.conf'))
        if os.geteuid() == 0:
            print("warning: running from root, only root repositories is syncing")
        else:
            user = config.get('Repos','user')
            syncrepos(user, False)
            sudo = True
        root = config.get('Repos','sudo')
        syncrepos(root, False)

print("=====================================================================================")
print("                     sync: Global repositories synchronizer v.2.6  ")
print("=====================================================================================")

config = ConfigParser()
sync(os.name)
print("  Statistics:  ")
print("-------------------------------------------------------------------------------------")
print("      total : %d" % total)
print("      success : %d" % success)
print("      errors : %d" % error)
print("=====================================================================================")