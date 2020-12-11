// Global variables
var address = null;
var name = null;
var phone = null;
var date_issued = null;
var date_expire = null;
var year_expire = null;
var acres_yn = null;

function doGet(e) {
  address = e.parameter.address;
  name = e.parameter.name;
  phone = e.parameter.phone;
  date_issued = e.parameter.date_issued;
  date_expire = e.parameter.date_expire;
  year_expire = e.parameter.year_expire;
  acres_yn = e.parameter.acres_yn;
  return HtmlService
      .createTemplateFromFile('Index')
      .evaluate();
}
