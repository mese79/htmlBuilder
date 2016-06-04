htmlBuilder
===========

This script will help you to make a build out of your html project. In other words this will minify and merge all of your javascript and css files by running a command. Also the built html file will be modified to have new links to the minified/merged files.

##### Requirements #####
- python 3.x (been tested on python 3.4 and 3.5)
- [lxml](http://lxml.de/index.html) library
- [slimit](https://github.com/rspivak/slimit), [ply](http://www.dabeaz.com/ply) and [csscompressor](https://travis-ci.org/sprymix/csscompressor) libraries(included)
- a build config file.  

##### Config file #####
Build config file is a json file which specifies how js and css files should get minified and merged.
For exmple:
```
    {
        "buildPath": "../build",
        "timeStamp": true,
        "minify": "all",
        "obfuscate": true
        "merge": {
            "libs/libs.js": ["jquery.min.js", "jquery.dataTables.js", "semantic.js"],
            "js/app.js": ["js/**", "other-js/*"]
        },
        "exclude": ["js/temp/**"]
    }
```

**Options:**
- `buildPath`: sets build folder path.
- `timeStamp`:   if it's true script will add a time-stamp at the end of build path.
- `minify`:      sets which type of files should be minified. options are: `js`, `css` and `all`.
- `obfuscate`:   if it's true then javascript files will be obfuscated.
- `merge`:       this option specifies which files must be merged into what. it will accept an object which keys will be taken as final merged file path and values are arrays of files desired to be minified and merged together.
- `exclude`: array of files need to be excluded from built project.

**Notes:**
- use `*` at the end of the path to include all files in a directory 
- use `**` at the end of a path to include all files in a directory and all sub-directories of that directory.
- If you have an already minified file in your path, file name must end to `.min.js` or `.min.css`. Else it will be minified again by the script. in that case probably it will fail.

##### Commandline #####
    python html_builder.py -c path/to/config-file.json path/to/index.html
    # for commandline help see:
    python html_builder.py --help
