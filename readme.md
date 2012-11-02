Sync is which will help you to keep your forks up to date!

Just, create config alike

``` shell
[Repos]
user: 
  /home/nen/contrib/portage -t git
  /home/nen/contrib/paludis -t git
  /home/nen/contrib/uemacs -t git
sudo:
  /home/nen/contrib/buildroot -t git
  /home/gentoo-haskell -t git
  /home/gentoo-kde -t git
  /usr/src/kernel -t git
```

adn run sync.

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
