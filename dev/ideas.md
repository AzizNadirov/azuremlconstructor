# Main ideas for implemention

1. `init`, `build`, `run` modules required as before.
    Implement them as args of main `amlctor` module.

2. `amlctor` is separated, so you must  call `python -m amlctor run <path to pipe folder>` or
    `python -m amlctor run .` if pwd = target pipe dir.

3. Inputs:

    Generally:

        Remake `datastore_name` as `datastore` and check if it's string or DataStore object. So that users will be able to create `datastore` object and use it inside Input classes.

    FileInput:

        reimplement `filename: str` as `filenames: list`, so that make ability to load multiple files from a datastore. Look for new file types: json, txt, etc.

    PathInput:

        add `upload` method, which will take file and upload it to the remote path.

4. Add ability to create templates

5. Rename step or pipe.

    ```
    amlctor rename
        -f/--path <pipe path>  
        -o/--old <old name> 
        -n/--new <new name> 
        -s/--step 
        -p/--pipeline
    ```

`
6. Ability Updating:

        Look at `settings.py` file and detect new names. Add new ones without overwriting existing content.
        Just add names to modules.
        `amlctor update --step 'stepname'` apply changes only for the passed pipe step. Optional,
        `--step` or `-s` by default = whole pipeline.
