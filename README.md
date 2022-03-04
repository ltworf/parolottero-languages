Parolottero
===========

Interactive game inspired by Passaparola (which I later learnt was inspired by Boggle).

Game modes
----------

You can either challenge yourself or other people.

To play against other people you will all need a device and will need to set the seed and timer to the same value, in order to obtain the same board.


Playing
-------

I think it's quite obvious :)


Installing
----------

The preferred mode is to install the .deb files.

There is one which contains the game code and data packages which contain the languages.


Building
--------

Refer to debian/control for the list of build-time and run-time dependencies.

You must do

```
mkdir build
cd build
qmake ../src
make -j
```

Game files
----------

The game files are contained in the dist .tar.gz file. But there is a Makefile with targets to regenerate them.


Contributing
------------

If you are contributing a new language, make sure the license of the word list allows it.

Contributions are welcome both via git send mail to tiposchi@tiscali.it or github pull requests.
