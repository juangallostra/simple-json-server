# simple-json-server

Deploy a local JSON server in a matter of seconds from a JSON file with data and endpoint definitions. No extra dependencies required, just Python.

This project was inspired by [tipycode's json-server](https://github.com/typicode/json-server).

It currently supports only `GET` and `POST` methods.

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

## Configuration

### Routing and data

A single `JSON` file provides both the server endpoints and the data that will be accessed through that endpoint. The file should contain a single `JSON` object. For each name/value pair, the name will be an accessible endpoint and the value the data accessed through that endpoint.

As an example, if the following was defined inside the `JSON` file:

```JSON
{
  "/api/metadata": {
    "info": "Provides customer and product info",
    "version": "0.1",
    "endpoints": [
      {
        "route": "/api/customers",
        "params": "id",
        "description": "Get customers"
      },
      {
        "route": "/api/products",
        "params": "normalized_name",
        "description": "Get products"
      }
    ]
  }
}
```

Then querying `[...]/api/metadata` would return the value associated with the name. 

### Parameters

### Running Multiple instances
