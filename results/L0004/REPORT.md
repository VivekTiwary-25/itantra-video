---
status: failed
---

## Command outputs

`echo shell-ok`

```text
shell-ok
```

`python -c "import pptx; print('pptx', pptx.__version__)"`

```text
python : The term 'python' is not recognized as the name of a cmdlet, function, script file, or operable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:3 char:1
+ python -c "import pptx; print('pptx', pptx.__version__)"
+ ~~~~~~
    + CategoryInfo          : ObjectNotFound: (python:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
```

## Notes

The shell ran, but Python was not available by the command name required by the task, so the pptx import could not be checked.
