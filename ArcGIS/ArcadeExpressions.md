### Permit - Print Request
{expression/expr0}
```javascript
// Google Apps Script - Deployment ID
var deployment_id = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX';

//Construct base URL
var baseurl = 'https://script.google.com/macros/s/' + deployment_id + '/exec?';

// Create variables for issue and expire months (Jan = 0)
var month_issue = Month($feature.issue_date) + 1;
var month_expire = Month($feature.expire_date) + 1;

// Create variables for attributes with proper formatting 
var phone_formatted = '(' + Left($feature.applicant_phone, 3) + ') ' + Mid($feature.applicant_phone, 3, 3) + '-' + 
Right($feature.applicant_phone, 4);
var issued = month_issue + '/' + Day($feature.issue_date) + '/' + Year($feature.issue_date);
var expire_mdy = month_expire + '/' + Day($feature.expire_date) + '/' + Year($feature.expire_date);
var expire_y = Year($feature.expire_date);

// Create parameters variable
var params = {
    address: Proper($feature['site_address']),
    name: Proper($feature['applicant_name']),
    phone: phone_formatted,
    date_issued: issued,
    date_expire: expire_mdy,
    year_expire: expire_y,
    acres_yn: $feature['burn_day_restriction']
}

// Return base URL with feature parameters
return baseurl  + UrlEncode(params);
```

### Status - RGB Color
{expression/expr1}
```javascript
If ($feature.permit_status == 'Active') {
    return '226,156,0';
} else if ($feature.permit_status == 'Revoked') {
    return '188,44,0';
} else {
    return '137,137,137';
}
```

### Phone - Formatted
{expression/expr2}
```javascript
return '(' + Left($feature.applicant_phone, 3) + ') ' + Mid($feature.applicant_phone, 3, 3) + '-' + 
Right($feature.applicant_phone, 4);
```

### Year - Formatted
{expression/expr3}
```javascript
// Used in pop-up title
return Text(Year($feature.expire_date));
```

### Expires / Expired
{expression/expr4}
```javascript
if ($feature.permit_status == 'Active' || $feature.permit_status == 'Revoked') {
    return 's';
}
return 'd';
```

### Follow Calendar - Yes/No
{expression/expr5}
```javascript
// Reverses the yes/no burn_day_restriction (Greater Than 3 Acres)
// field to indicate if the permit holder/parcel is required to
//follow the burn day calendar.

if ($feature.burn_day_restriction == 'Yes') {
    return 'No'
}
Return 'Yes'
```

### Condo - Asterisk
{expression/expr6}
```javascript
if ($feature.burn_day_restriction == 'No' && $feature.site_acreage >= 3.0) {
    return '*'
}
return ''
```

### Condo - Asterisk Notes
{expression/expr7}
```javascript
if ($feature.burn_day_restriction == 'No' && $feature.site_acreage >= 3.0) {
    return '*Site condominiums may display greater than 3 acres,\
    however, they are required to follow the burn day calendar.'
}
return ''
```
