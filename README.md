# sanitise
Script to sanitise text/content based on a set of rules

## Configuration file options
The configuration options are defined as a YAML file. The following summaries current valid options to define in the file:
| Option | Description
|--------|------------
| file_extensions | A list of file extensions to scan
| rules | A list of rules to apply to files

### file_extensions
* This option currently assumes files with `*.gz` or `*.bz2` extensions are compressed files, using GZIP or BZIP2 respectively.
* Define the file extensions to scan for as a YAML list.

### rules
The list of supported rules will be added in time.
* `substitute` - replaces original text defined with `find:` with another text using `replace:` keys

## Sample config file
```
file_extensions:
- ".log"
- ".txt"
- ".gz"
- ".bz2"

rules:
- substitute:
    find: "example.com"
    replace: "mydomain"
- substitute:
    find: "test"
    replace: "mytest"
```
