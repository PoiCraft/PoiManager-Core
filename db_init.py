from database.database import create_db
from database.ConfigHelper import init, print_and_edit


print('Creating database...')
create_db()
print('>>done')
print('Configuring with default values...')
init()
print('>>done')

print('For most cases, the default can meet the needs, without modification.')
print('If you want to modify the config, please read the wiki.')

print('The default values are:')
print_and_edit()
print('')
print('You can run \'python3 edit_config.py\' to modify the config.')
