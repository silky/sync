Sync is util which will help you to keep your forks up to date!

Just, create config alike

``` shell
[Repos]
user: 
  /home/nen/contrib/portage -t git git
  /home/nen/contrib/paludis -t hg git
  /home/nen/contrib/uemacs
sudo:
  /home/nen/contrib/buildroot -t git git
  /home/gentoo-haskell
  /home/gentoo-kde
  /usr/src/kernel
```

(git git is default)

and run sync. [not that it can't setup repos for you yet]

it will be look alike that:

``` shell
/sync
Repo:  /home/nen/contrib/portage -t git
Untracked: []
New: []
Modified: []
From github.com:Ashlyn/portage
 * branch            master     -> FETCH_HEAD
From git://git.overlays.gentoo.org/proj/portage
 * branch            master     -> FETCH_HEAD
From git://git.overlays.gentoo.org/proj/portage
 * branch            master     -> FETCH_HEAD
Everything up-to-date
Repo:  /home/nen/contrib/paludis -t git
Untracked: []
New: []
Modified: []
From github.com:Ashlyn/paludis
 * branch            master     -> FETCH_HEAD
From git://git.exherbo.org/paludis/paludis
 * branch            master     -> FETCH_HEAD
From git://git.exherbo.org/paludis/paludis
 * branch            master     -> FETCH_HEAD
Everything up-to-date
```

Installation
============

in gentoo you can install it from my overlay + emerge sync
