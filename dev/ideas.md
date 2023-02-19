## Main ideas for implemention

1. `init`, `build`, `run` modules required as before.
    Implement them as args of main `amlctor` module.

2. Add rename ability as:
    `python -m amlctor [--rename <pipe path>] [--old <old step or pipe name>] [--new <new name>]`. If there are more than one items(pipes or steps) with old names, then show interactive menu, that user should be able to choose number and define which item will be renamed.

2. `amlctor` is separated, so you must  call `python -m amlctor run <path to pipe folder>` or `python -m amlctor run .` if pwd = target pipe dir.

3. Inputs: 
    Generally:
        Remake `datastore_name` as `datastore` and check if it's string or DataStore object. So that users will be able to create `datastore` object and use it inside Input classes.

    FileInput: 
        reimplement `filename: str` as `filenames: list`, so that make ability to load multiple files from a datastore. Look for new file types: json, txt, etc.

    PathInput: 
        add `upload` method, which will take file and upload it to the remote path.
