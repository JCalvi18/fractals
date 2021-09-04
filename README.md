###Installation:
It is assumed that python 3.5+ is installed.

For installing the Cairo and Gtk dependencies, for Linux/Arch users run:
```
sudo pacman -S python cairo pkgconf gobject-introspection gtk3
```
Other operating systems refer to: https://pygobject.readthedocs.io/en/latest/getting_started.html

To install additional libraries run inside the project folder:
```
pip install -r requirements.txt
```

To test if the installating was correct, run:
```
python cairo/sierpinski.py 8 --gtk

```
It should show a floating windows with the Sierpinski triangle
