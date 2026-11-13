# Working on ComRAD public tools

- Keep the tools compatible with Python 3.12 and the standard library.
- Run `python3 -m unittest discover -s tests -v` after code changes.
- Use local mock servers for client tests. Do not start paid inference or download model weights for tests.
- Preserve release filenames, exact sizes, checksums, and source URLs unless updating to a separately verified release.
- Never commit credentials, private data, model weights, or files from outside this repository.
- Describe measured evaluation scope accurately. Do not infer full benchmark scores from pilots.
