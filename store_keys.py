import keyring
import getpass
from arcgis.gis import GIS

if __name__ == '__main__':
    print('Enter the Portal or ArcGIS Online Organization URL:')
    webgis_url = input('> ')

    print('Enter the Portal or ArcGIS Online Organization Username:')
    webgis_user = input('> ')

    print('Enter the the Portal or ArcGIS Online Organization Password:')
    webgis_pass = getpass.getpass(prompt='Enter the the Portal or ArcGIS Online Organization Password:')

    print('Choose a name for the Portal or ArcGIS Online Organization Profile:')
    webgis_profile = input('> ')

    try:
        GIS(webgis_url, webgis_user, webgis_pass, profile=webgis_profile)
        print('Successfully stored credentials in the OS keyring. Store the profile name in the config.yml file.')
    except Exception as e:
        print(e)

    print('Enter the sending email address:')
    email_add = input('> ')

    print()
    smtp_pass = getpass.getpass(prompt='Enter the SMTP password:')

    try:
        keyring.set_password('burn_permit', email_add, smtp_pass)
        print('Successfully stored password in the OS keyring.')
    except Exception as e:
        print(e)
