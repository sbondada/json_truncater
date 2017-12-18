# json_truncater

## File Structure

README.md - A markdown file explaining your approach, any technical challenges, potential improvements

truncate - The executable file

## Run Instructions

program takes two parameters
* The maximum number of bytes for each truncated object
* This is the maximum number of bytes of the resulting JSON encoded string to be written out

The filename to read JSON encoded objects from

## What the Program Does
1. The program reads JSON encoded objects from the file provided
2. JSON objects are separated by newlines
3. he program writes the resulting JSON encoded objects to standard output, separated by newline
4. The executable should be named “truncate”

Sample input
```
"hi every one I am as good as it gets"
{"hello": "world is a very happy place to live", "ram": { "har": "happy birthday"}}
{"some": {"nested":["objects are the best things invented",{}, 1234, "love is impossible", "lock the potential and the wealth"]}}
```
sample output for this command
> python2.7 json_truncater/src/truncate.py 64 json_truncater/resource/json_input.txt
```
"hi every one I am as good as it gets"
{"ram": {"har": "happy birthday"}, "hello": "world is a v..."}
{"some": {"nested": ["object...", {}, 1234, "lov...", "loc..."]}}
```

JSON objects are truncated with the following rules
* Structure is always maintained
* If the input contains a nested object within a list, the output should also contain a nested object within a list
* Key names should never be truncated
* Only strings get truncated
* runcated strings should have a trailing ellipses, E.g.: “Long string here....”
* Strings should never be truncated to less than 3 characters
* This means that the shortest truncated string would end up being a maximum of 6 characters long
E.g.: “Lon...”
Assume all input is ASCII
* If an object cannot be truncated, the result should be “<ERROR>”

## On Backlog
* Attempt to only truncate at word boundaries
* Truncate the middle of the string
E.g. “Some really long text here” → “Some really...here”
