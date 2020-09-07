# simple-json-server

Deploy a local JSON server in a matter of seconds from a JSON file with data and endpoint definitions. No extra dependencies required, just Python.

This project was inspired by [tipycode's json-server](https://github.com/typicode/json-server).

It currently supports only `GET` and `POST` methods.

## Usage

```
usage: server.py [-h] [-p PORT] [-f FILE] [-u URL]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Specify the desired port, defaults to port 80
  -f FILE, --file FILE  File from which to extract routing and data, defaults to db.json
  -u URL, --url URL     Set a fake url for the server, defaults to localhost
```

As stated above, the default values are `80` for the port, `localhost` for the hostname and `db.json` as the configuration file.

### Examples

To specify a hostname, port and JSON file from where to extract data and endpoints:

```sh
$ python server.py -u climbers-climbers.com -p 5000 -f db.json
```

Assuming [this file](https://github.com/juangallostra/simple-json-server/blob/master/db.json) is the one used for configuring the server:

## Configuration

### Routing and data

A single `JSON` file provides both the server endpoints and the data that will be accessed through that endpoint. The file should contain a single `JSON` object. For each name/value pair, the name will be an accessible endpoint and the value the data accessed through that endpoint. All endpoints accept, by default, GET requests. However, only endpoints whose value is a list of objects will accept POST requests.

A full example of a configuration file can be found [here](https://github.com/juangallostra/simple-json-server/blob/master/db.json).

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

Then querying `[...]/api/metadata` will return the value associated with the name. It is also possible to specify a list of objects as the data to be returned instead of a single object. **The endpoints whose value is a list of objects are the only ones that will accept and process POST requests**. For example:

```JSON
{
  "api/customers": [
    {
      "id": 1,
      "name": "Alex Honnold",
      "email": "ahonnold@climber.com",
      "address": "his van"
    },
    {
      "id": 2,
      "name": "Adam Ondra",
      "email": "aondra@sport-climber.com",
      "address": "always traveling"
    },
    {
      "id": 3,
      "name": "Jimmy Webb",
      "email": "jwebb@boulderer.com",
      "address": "Looking for nice boulders"
    }
  ]
}
```

Then querying `[...]/api/customers` will return the whole list of customers.

### Parameters

For the routes that return a list of objects it is possible to specify a parameter in the configuration file. To do so, `[...]/path/to/endpoint/:param`. When the parameter value is set, only those objects that match the parameter value will be returned. 

```JSON
{
  "api/customers/:id": [
    {
      "id": 1,
      "name": "Alex Honnold",
      "email": "ahonnold@climber.com",
      "address": "his van"
    },
    {
      "id": 2,
      "name": "Adam Ondra",
      "email": "aondra@sport-climber.com",
      "address": "always traveling"
    },
    {
      "id": 3,
      "name": "Jimmy Webb",
      "email": "jwebb@boulderer.com",
      "address": "Looking for nice boulders"
    }
  ]
}
```

`[...]/api/customers` will return the full list of objects while `[...]/api/customers/2` will return the customer whose `id` is 2.

### Errors and Exceptions

When an error or exception is raised, the server reply will be in the form:

```JSON
{
  "result": {
    "code": "ERROR_CODE",
    "message": "ERROR_MESSAGE",
    "description": "ERROR_DESCRIPTION"
  }
}
```

### Running Multiple instances
