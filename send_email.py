"""
The send_email module connects to a Web GIS, queries for unprocessed records in the specified burn permit feature
service, then processes those records by calling a GoogleAppsScript to generate a burn permit. A link to the burn
permit document is then emailed to the applicant. Finally it updates the feature service to indicate the record has
been processed. This module is meant to run as a stand-alone script at an interval of choice.
"""

import requests
import os
import smtplib
import datetime
import pytz
import yaml
import textwrap
from arcgis.gis import GIS


def format_phone(n):
    """Formats phone number."""
    return format(int(n[:-1]), ",").replace(",", "-") + n[-1]


def format_datetime(date):
    """Converts a unixtime object to a Python datetime object."""
    create = str(date)[0: 10]
    create_unixtime = float(create)
    create_datetime = datetime.datetime.fromtimestamp(create_unixtime, tz_utc)
    create_datetime = create_datetime.astimezone(tz_est)
    return create_datetime.replace(tzinfo=None)


def conn_portal(webgis_config):
    """Creates a connection to an ArcGIS Portal."""
    w_gis = None
    try:
        if cfg_webgis['profile']:
            w_gis = GIS(profile=webgis_config['profile'])
        else:
            w_gis = GIS(webgis_config['portal_url'], webgis_config['username'], webgis_config['password'])
    except Exception as connect_error:
        print(f'Error: {connect_error}')
        print('Exiting script: not able to connect to ArcGIS Portal.')
        exit()
    return w_gis


if __name__ == '__main__':
    # Set current working directory
    cwd = os.getcwd()

    # Open config file
    with open(cwd + '/config.yml', 'r') as yaml_file:
        cfg = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # Set variables based on values from config file
    cfg_webgis = cfg['webgis']
    cfg_pdf_api = cfg['gs_pdf_api']
    cfg_local_tz = cfg['local_tz']
    agency_name = cfg['agency']['name']
    agency_phone = cfg['agency']['phone']
    agency_url = cfg['agency']['url']
    agency_email = cfg['agency']['email']
    smtp_password = cfg['agency']['smtp_password']
    smtp_svr = cfg['agency']['smtp_server']
    smtp_port = cfg['agency']['smtp_port']

    # Set variables to timezones (datetime fields in GIS are in UTC timezone)
    tz_utc = pytz.timezone('UTC')
    tz_est = pytz.timezone(cfg_local_tz)

    # Connect to Web GIS
    gis = conn_portal(cfg_webgis)

    # Set feature layer
    flc_burnpermit = gis.content.get(cfg_webgis['portal_item'])
    fl_burnpermit = flc_burnpermit.layers[cfg_webgis['layer_num']]

    # Query feature layer, return feature set
    sql = "PROCESSED IS NULL AND APPLICANT_EMAIL IS NOT NULL"
    fset_burnpermit = fl_burnpermit.query(where=sql)

    # Empty list for to hold features to update
    features_to_update = []

    for bp in fset_burnpermit:
        # Set issue date and issue year variables
        issue_datetime = format_datetime(bp.attributes['issue_date'])
        issue_date_str = issue_datetime.strftime('%m/%d/%Y')
        issue_year_str = issue_datetime.strftime('%Y')

        # Set expire date variable
        expire_datetime = format_datetime(bp.attributes['expire_date'])
        expire_date_str = expire_datetime.strftime('%m/%d/%Y')

        # Format Phone Number
        phone = format_phone(bp.attributes['applicant_phone'])

        # Remove special characters from Applicant Name field
        rm_characters = [';', ':', '!', "*", "'", '"']
        name = bp.attributes['applicant_name']
        for i in rm_characters:
            name = name.replace(i, '')
        name.title()

        # Use title Casing on address field
        address = bp.attributes['site_address'].title()

        # Set parameters, submit request, receive PDF link
        params = {'address': address,
                  'name': name,
                  'phone': phone,
                  'date_issued': issue_date_str,
                  'date_expire': expire_date_str,
                  'year': issue_year_str,
                  'acres_yn': bp.attributes['burn_day_restriction']}
        response = requests.get(cfg_pdf_api, params=params, allow_redirects=True, timeout=10.0)
        response.encoding = 'utf-8'
        pdf_url = response.text

        # Set variable for recipient email address
        email = bp.attributes['applicant_email']

        # Email message body
        message = textwrap.dedent(f"""\
        From: Burn Permits <{agency_email}>
        To: {name} <{email}>
        Subject: {agency_name} Burn Permit {issue_year_str}
        
        Please click the link below to download your {issue_year_str} {agency_name} Burn Permit:
        {pdf_url}
        
        This link will remain active for 10 days.
        
        Your Burn Permit is kept on file with the {agency_name}, however, we recommend printing a copy for your records.
        
        For questions, please visit {agency_url} or call {agency_phone}.
        
        Thank you,
        
        The {agency_name} Staff""")

        # Set SMTP session
        s = smtplib.SMTP(smtp_svr, smtp_port)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(agency_email, smtp_password)
        # Send email and update processed attribute
        try:
            s.sendmail(agency_email, email, message)
            s.quit()
            bp.attributes['applicant_name'] = name
            bp.attributes['site_address'] = address
            bp.attributes['processed'] = 'Yes'
            features_to_update.append(bp)
        except Exception as e:
            print(e)

    # Update features
    fl_burnpermit.edit_features(updates=features_to_update)
