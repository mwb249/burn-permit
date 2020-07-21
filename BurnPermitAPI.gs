function createDocument(address, name, phone, date_issued, acres_yn) {
  var TEMPLATE_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
  var documentId = DriveApp.getFileById(TEMPLATE_ID).makeCopy().getId();

  drivedoc = DriveApp.getFileById(documentId);
  drivedoc.setName("Burn Permit - " + address);

  doc = DocumentApp.openById(documentId);

  var body = doc.getBody();

  body.replaceText('{address}', address);
  body.replaceText('{name}', name);
  body.replaceText('{phone}', phone);
  body.replaceText('{date_issued}', date_issued);
  body.replaceText('{date_expire}', date_expire);
  body.replaceText('{year}', year);
  body.replaceText('{acres_yn}', acres_yn);
  drivedoc.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.EDIT);

  return "https://docs.google.com/document/d/" + documentId + "/export?format=pdf";
}

function doGet(e) {
  var address = e.parameter.address;
  var name = e.parameter.name;
  var phone = e.parameter.phone;
  var date_issued = e.parameter.date_issued;
  var acres_yn = e.parameter.acres_yn;
  var url = createDocument(address, name, phone, date_issued, acres_yn);
  return ContentService.createTextOutput(url);
}
