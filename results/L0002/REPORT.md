---
status: failed
---

## Command outputs

`echo shell-ok` (exit 0):

```text
shell-ok
```

`python -c "import pptx; print('pptx', pptx.__version__)"` (exit 1):

```text
python : The term 'python' is not recognized as the name of a cmdlet, function, script file, or operable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:2 char:1
+ python -c "import pptx; print('pptx', pptx.__version__)"
+ ~~~~~~
    + CategoryInfo          : ObjectNotFound: (python:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
```

## Notes

The shell command ran. The requested Python command could not run because `python` was not found in this shell session. No package was installed.
