Sync is util which will help you to keep your forks up to date!

all you need is: /etc/conf.d/repolist.conf

``` shell
[Repos]
user:
  /home/nen/contrib/portage
  /home/nen/contrib/uemacs
  /home/nen/contrib/sync -t git hg
  /home/nen/contrib/ctodo -t git hg
  /home/nen/contrib/web/cynede -t git git
  /home/nen -t git git
  /home/nen/projects/ARMD/lib -t git git
sudo:
  /home/steam-overlay
  /home/nengraphy -t git git
  /home/nen/contrib/buildroot
  /home/gentoo-haskell
  /home/gentoo-kde
```

(git is default)

and run forks-sync. [not that it can't setup repos for you yet]

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
