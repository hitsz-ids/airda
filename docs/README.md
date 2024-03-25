# SQLAgent API docs

## Online docs

Typically, our [latest API document](https://data-agent.readthedocs.io/en/latest/) can be accessed via readthedocs.

## Build docs locally

You can build the docs on your own computer.

Step 1: Install docs dependencies

```
pip install -e .[docs]
```

Step 2: Build docs

```
cd docs && make html
```

Step 3 (Optional): deploy a local http server to view the docs

```
cd build/html && python -m http.server
```

Then access http://localhost:8000 for docs.
