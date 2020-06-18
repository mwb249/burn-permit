"""
The send_email module...
"""

import requests
import os
import smtplib
import datetime
import pytz
import yaml
import keyring
from arcgis.gis import GIS


def phone_format(n):
    """Formats phone number."""
    return format(int(n[:-1]), ",").replace(",", "-") + n[-1]


if __name__ == '__main__':
    # Set global variables
    global name, email, pdf_url, creation_year

    # Set current working directory
    cwd = os.getcwd()

    # Open config file
    with open(cwd + '/config.yml', 'r') as yaml_file:
        cfg = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # Set variables based on values from config file
    cfg_profile = cfg['webgis']['profile']
    cfg_portal_item = cfg['webgis']['portal_item']
    cfg_layer_num = cfg['webgis']['layer_num']
    cfg_pdf_api = cfg['pdf_api']
    cfg_local_tz = cfg['local_tz']
    cfg_agency_name = cfg['agency']['name']
    cfg_agency_phone = cfg['agency']['phone']
    cfg_agency_url = cfg['agency']['url']
    cfg_agency_email = cfg['agency']['email']
    cfg_smtp_svr = cfg['agency']['smtp_server']
    cfg_smtp_port = cfg['agency']['smtp_port']

    # Retrieve smtp password from keyring
    smtp_password = keyring.get_password('burn-permit', cfg_agency_email)

    # Email message body
    message = """From: Burn Permits <{6}>
    To: {0} <{1}>
    Subject: {3} Burn Permit {7}

    Please click the link below to download your {7} {3} Burn Permit:
    {2}

    This link will remain active for 10 days.

    Your Burn Permit is kept on file with the {3}, however, we recommend printing a copy for your records.

    For questions, please visit {5} or call {4}.

    Thank you,

    The {3} Staff
    """.format(name, email, pdf_url, cfg_agency_name, cfg_agency_phone, cfg_agency_url, cfg_agency_email, creation_year)

    # Set variables to timezones (datetime fields in GIS are in UTC timezone)
    tz_utc = pytz.timezone('UTC')
    tz_est = pytz.timezone(cfg_local_tz)

    # Connect to Web GIS
    gis = GIS(profile=cfg_profile)

    # Set feature layer
    flc_burnpermit = gis.content.get(cfg_portal_item)
    fl_burnpermit = flc_burnpermit.layers[cfg_layer_num]

    # Query feature layer, return feature set
    sql = 'PROCESSED IS NULL AND EMAIL IS NOT NULL'
    fset_burnpermit = fl_burnpermit.query(where=sql)

    # Empty list for to hold features to update
    features_to_update = []

    for bp in fset_burnpermit:
        # Format Creation Date
        create = str(bp.attributes['IssuedDate'])[0: 10]
        create_unixtime = float(create)
        create_datetime = datetime.datetime.fromtimestamp(create_unixtime, tz_utc)
        create_datetime = create_datetime.astimezone(tz_est)
        create_datetime = create_datetime.replace(tzinfo=None)
        creation_date = create_datetime.strftime('%m/%d/%Y')
        creation_year = create_datetime.strftime('%Y')

        # Format Phone Number
        phone = phone_format(bp.attributes['phone'])

        # Remove special characters from name field
        rm_characters = [';', ':', '!', "*", "'", '"']
        name = bp.attributes['name']
        for i in rm_characters:
            name = name.replace(i, '')

        # Set parameters, submit request, receive PDF link
        params = {'address': bp.attributes['address'],
                  'name': name,
                  'phone': phone,
                  'date_issued': creation_date,
                  'acres_yn': bp.attributes['followburncal']}
        response = requests.get(cfg_pdf_api, params=params, allow_redirects=True, timeout=10.0)
        response.encoding = 'utf-8'
        pdf_url = response.content
        pdf_url = str(pdf_url)

        # Set variable for recipient email address
        email = bp.attributes['email']

        # Set SMTP session
        s = smtplib.SMTP(cfg_smtp_svr, cfg_smtp_port)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(cfg_agency_email, smtp_password)
        # Send email and update processed attribute
        try:
            s.sendmail(cfg_agency_email, email, message)
            s.quit()
            bp.attributes['processed'] = 'Yes'
            features_to_update.append(bp)
        except Exception as e:
            print(e)

    # Update features
    fl_burnpermit.edit_features(updates=features_to_update)
