import urllib.parse as parse
import getpass

f = open('pass.tmp', 'w')
encoded_pass = parse.quote_plus(getpass.getpass("Enter password: "))
f.write(encoded_pass)
