from sys import argv
from random import choice
import string

project = argv[1]

bucket = raw_input('Pick a (globally) unique GCS bucket name [empty defaults to random]: ')

if not bucket:
    bucket = ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(16))

contents = None
with open('config/spinnaker-local-gen.yml', 'r') as file:
    contents = file.read()

contents = contents.replace('{%project%}', project)
contents = contents.replace('{%bucket%}', bucket)

with open('config/spinnaker-local.yml', 'w') as file:
    file.write(contents)
