# simple-json-server

Deploy a local JSON server in a matter of seconds from a JSON file with data and endpoint definitions. No extra dependencies required, just Python.

This project was inspired by [tipycode's json-server](https://github.com/typicode/json-server).

## Usage

```
usage: server.py [-h] [-p PORT] [-f FILE] [-u URL]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Specify the desired port
  -f FILE, --file FILE  File from which to extract routing and data
  -u URL, --url URL     Set a fake url for the server
```

### Examples

To specify a hostname, port and JSON file from where to extract data and endpoints:

```sh
$ python server.py -u my-fake-website.com -p 5000 -f db.json
```

### Running Multiple instances

