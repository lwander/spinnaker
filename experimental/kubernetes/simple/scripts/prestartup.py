from getpass import getpass

username = raw_input('DockerHub username: ')
password = getpass('DockerHub password: ')
image = raw_input('DockerHub image, ignoring username prefix [spin-kub-demo]: ')

if not image:
    image = 'spin-kub-demo'

contents = None
with open('config/clouddriver-local-gen.yml', 'r') as file:
    contents = file.read()

contents = contents.replace('{%username%}', username)
contents = contents.replace('{%password%}', password)
contents = contents.replace('{%image%}', image)

with open('config/clouddriver-local.yml', 'w') as file:
    file.write(contents)
