Sync is util which will help you to keep your forks up to date!

all you need is: /etc/conf.d/repolist.conf

``` shell
[Repos]
user:
  /home/nen/contrib/portage
  /home/nen/contrib/uemacs
  /home/nen/contrib/hackport
  /home/nen/contrib/FAKE -t git -b develop
;  /home/nen/contrib/sync -t git hg
;  /home/nen/contrib/ctodo -t git hg
;  /home/nen/contrib/htodo -t git git
;  /home/nen/contrib/web/cynede -t git git
;  /home/nen -t git git
;  /home/nen/projects/ARMD/lib -t git git
sudo:
  /home/gamerlay
;  /home/nengraphy -t git git
  /home/nen/contrib/buildroot
  /home/gentoo-haskell
  /home/gentoo-kde
```

(git and master branch are defaults)

and run forks-sync. [not that it can't setup repos for you yet]

it will be look alike that:

``` shell
------ Repository:  /home/nen/contrib/hackport ------
Untracked: []
New: []
Modified: []
From github.com:Cynede/hackport
 * branch            master     -> FETCH_HEAD
From git://github.com/gentoo-haskell/hackport
 * branch            master     -> FETCH_HEAD
From git://github.com/gentoo-haskell/hackport
 * branch            master     -> FETCH_HEAD
Everything up-to-date
 -->  ['/home/nen/contrib/hackport'] : successful synchronized :)
______________________________________________________________________
------ Repository:  /home/nen/contrib/FAKE -t git -b develop ------
Untracked: []
New: []
Modified: []
From github.com:Cynede/FAKE
 * branch            develop    -> FETCH_HEAD
remote: Counting objects: 543, done.
remote: Compressing objects: 100% (231/231), done.
remote: Total 401 (delta 254), reused 301 (delta 156)
Receiving objects: 100% (401/401), 40.00 KiB, done.
Resolving deltas: 100% (254/254), completed with 69 local objects.
From git://github.com/fsharp/FAKE
 * branch            develop    -> FETCH_HEAD
From git://github.com/fsharp/FAKE
 * branch            develop    -> FETCH_HEAD
Counting objects: 543, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (133/133), done.
Writing objects: 100% (401/401), 40.00 KiB, done.
Total 401 (delta 254), reused 401 (delta 254)
To git@github.com:Cynede/FAKE.git
   d524537..b87f7d8  develop -> develop
 -->  ['/home/nen/contrib/FAKE ', ' git -b develop'] : successful synchronized :)
______________________________________________________________________
```

Installation
============

in gentoo you can install it from my overlay

``` shell
layman -a weirdo
emerge sync
```

