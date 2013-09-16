#!/usr/bin/env python
#_____________________________________________________________________________________________
''' Copyright (C)  2012-2013  Heather '''
#_____________________________________________________________________________________________
import os
import string
import time
from threading import Thread
#_____________________________________________________________________________________________
#Python 2x / 3x compatibility
try:  from configparser import ConfigParser 
except ImportError: 
    from ConfigParser import ConfigParser 

from subprocess import Popen, PIPE
#_____________________________________________________________________________________________
class VCS:
    git=0
    git_git=1
    git_mercurial=2
    git_subversion=3
    hg_hg=5
#_____________________________________________________________________________________________
sudo = False
fst = True
#_____________________________________________________________________________________________
#statistics global variables
total = 0
success = 0
error = 0
#_____________________________________________________________________________________________
class shellrunner():
    def __init__(self, shell):
        self.shell = shell
    def command(self, x):
        return str(Popen(x.split(' ')
            , stdout    = PIPE
            , shell     = self.shell).communicate()[0])
    def pretty(self, msg):
        ss = msg.split("\n")
        for s in ss: 
            if not s.startswith("b"): print(s)
    def cmd(self, q):
        if sudo: return self.command("sudo %s" % q)
        else:    return self.command(q)
    def sh(self, s): self.pretty(self.cmd(s))
#_____________________________________________________________________________________________
def gitSync(branch, upstream, upstreambranch, e):
    e.sh("git checkout %s" % branch)
    e.sh("git rebase --abort")
    e.sh("git pull origin %s" % branch)
    e.sh("git fetch %s %s" % (upstream, upstreambranch))
    e.sh("git pull --rebase %s %s" % (upstream, upstreambranch))
    e.sh("git push -f origin %s" % branch)
#_____________________________________________________________________________________________
def gitPU(branch, e):
    e.sh("git pull origin %s" % branch)
    e.sh("git commit -am submodule")
    e.sh("git push -f origin %s" % branch)
#_____________________________________________________________________________________________
def gitgitSync(e):
    e.sh("git pull origin master")
    e.sh("git fetch git master")
    e.sh("git push -f git master")
#_____________________________________________________________________________________________
def githgSync(e):
    e.sh("hg pull")
    e.sh("hg update")
    e.sh("hg push git")
#_____________________________________________________________________________________________
def hghgSync(e):
    e.sh("hg pull")
    e.sh("hg update")
    e.sh("hg push hg")
#_____________________________________________________________________________________________
def gitNew(e, status):
    return [x[14:] for x in status if x.startswith("#\tnew file:   ")]
#_____________________________________________________________________________________________
def gitModified(e, status):
    return [x[14:] for x in status if x.startswith("#\tmodified:   ")]
#_____________________________________________________________________________________________
def checkGitModifications(e):
    status = e.command("git status").split("\n")
    print("New: %s" % gitNew(e, status))
    print("Modified: %s" % gitModified(e, status))
#_____________________________________________________________________________________________
class ParentUpdate(Thread):
    def __init__(self, vcs, branch, shell):
        Thread.__init__(self)
        self.vcs = vcs
        self.branch = branch
        self.e = shellrunner(shell)
    def run(self):
        if self.vcs == VCS.git:
            checkGitModifications(self.e)
            gitPU(self.branch, self.e)
#_____________________________________________________________________________________________
class ThreadingSync(Thread):
    def __init__(self, vcs, branch, upstream, upstreambranch, shell):
        Thread.__init__(self)
        self.vcs = vcs
        self.branch = branch
        self.upstream = upstream
        self.upstreambranch = upstreambranch
        self.e = shellrunner(shell)
    def run(self):
        if self.vcs == VCS.git:
            checkGitModifications(self.e)
            gitSync(self.branch, self.upstream, self.upstreambranch, self.e)
        elif self.vcs == VCS.git_git:
            gitgitSync(self.e)
        elif self.vcs == VCS.git_mercurial:
            githgSync(self.e)
        elif self.vcs == VCS.git_subversion:
            print ("can't sync git from subversion yet")
        elif self.vcs == VCS.hg_hg:
            hghgSync(self.e)
#_____________________________________________________________________________________________
def DoUpdate(vcs, branch, useub, haveparent,upstream, upstreambranch, parent, shell):
    global success
    global error
    if not useub: upstreambranch = branch
    thrd = ThreadingSync(vcs,branch,upstream, upstreambranch, shell)
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
                thrdp = ParentUpdate(vcs, branch, shell)
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
#_____________________________________________________________________________________________
def SyncStarter(repo, shell):
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
    rpth = ((r[0]).split(" "))
    pth  = rpth[0]

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

    pdir = pth; upstream = 'upstream'
    if pth.startswith('git@'):
        if len(rpth) > 1:
            upstream = rpth[1]
            print(" --> upstream: %s" % upstream)
        else: 
            print(" --> %s : Failed to get upstream branch :(" % pth)
            return
        vcs = VCS.git
        if not shell:
            if not os.path.exists('/usr/share/sync/git'):
                os.makedirs('/usr/share/sync/git')
        gitp = (((r[0]).split("/"))[1].split("."))[0]
        pdir = { True: 'sync-%s'
               , False: '/usr/share/git/%s'} [shell] % gitp
        if not os.path.exists(pdir):
            e = shellrunner(shell)
            e.sh("git clone %s %s" % (pth, pdir))

    if shell:
        if fst: 
            fst = False
            os.chdir(pdir)
        else:
            os.chdir("..")
            os.chdir(pdir)
    else: os.chdir(pdir)
        
    if len(branches) > 1:
        for b in branches:
            total += 1
            print("--> branch: %s" % b)
            DoUpdate(vcs, b, useub, haveparent, upstream, upstreambranch, parent, shell)
    else:
        total += 1
        DoUpdate(vcs, branch, useub, haveparent, upstream, upstreambranch, parent, shell)
    print("______________________________________________________________________")
#_____________________________________________________________________________________________
def syncrepos(repos, shell): 
    for r in repos.split("\n"): 
        if r: SyncStarter(r, shell)
#_____________________________________________________________________________________________
print("======================================================================")
print("         sync: Global repositories synchronizer v.3.1  ")
print("======================================================================")
#_____________________________________________________________________________________________
config = ConfigParser()
if os.name == 'nt':
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
#_____________________________________________________________________________________________
print("  Statistics:  ")
print("----------------------------------------------------------------------")
print("      total : %d" % total)
print("      success : %d" % success)
print("      errors : %d" % error)
print("======================================================================")
#_____________________________________________________________________________________________