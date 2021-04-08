# Numworks-workshop.py

This project is a python wrapper for the numworks [workshop](workshop.numworks.com/).

## How to install ?

Just install the pypi [package](https://pypi.org/project/numworkshop/)

With pip :

```
pip install numworkshop
```

Or with poetry :

```
poetry add numworkshop
```

## How to use ?

```py
from numWorkshop import Script, Workshop

workshop = Workshop("email", "password")

toaster = Script(name="name",
                 description="description",
                 content="print('hello-world')",
                 public=True)

workshop.create_script(toaster)
toaster.content = "print('nsi.xyz')"

# Since we use the script name to get acess and edit your script, your should use the name parameter
# of the edit_script method, this will update the script at the end of the process and not break script
# Other parameter are updated throught Script object...
workshop.edit_script(toaster, name="namev2")
workshop.delete_script(toaster)

script = workshop.get_script("https://workshop.numworks.com/python/thierry-barry/annuite_constante")  # This return a script object.
print(script)
```

If you find a bug or want a new feature you can open an issue.

## Adding feature ?

First clone the project :

```
git clone https://github.com/LeGmask/numWorkshop.git
```

Install project with [poetry](https://python-poetry.org) :

```
poetry install
```

Then you're ready to go !
