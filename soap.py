import zeep
import logging
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
import pandas as pd
import pdb
USERNAME = 'jack.dwyer@blastam.com'
PASSWORD = 'Blast6020'
authentication_dict = {"Username":USERNAME,
   "Password":PASSWORD}
client = zeep.Client(wsdl = 'https://ws.campaigner.com/2013/01/contactmanagement.asmx?WSDL')

xml = "<contactssearchcriteria><version major=\"2\" minor=\"0\" build=\"0\" revision=\"0\"/>" +\
"<set>Partial</set><evaluatedefault>True</evaluatedefault>" +\
"<group><filter><filtertype>EmailAction</filtertype>" +\
"<campaign><anycampaign/></campaign>" +\
"<action><status>Do</status><operator>Open</operator></action>" +\
"<operator>Anytime</operator></filter>" +\
"</group></contactssearchcriteria>"

runreport = client.service.RunReport(authentication = authentication_dict, xmlContactQuery = xml)
print runreport
ticket = runreport['body']['RunReportResult']['ReportTicketId']

response = client.service.DownloadReport(authentication = authentication_dict,
reportTicketId=ticket, fromRow=2, toRow=5, reportType='rpt_Summary_Campaign_Results')['body']['DownloadReportResult']['ReportResult']
dict_list = []
for i in response:
   dict_list.append(i['_attr_1'])
my_dict = zeep.helpers.serialize_object(dict_list)
campaigns_df = pd.DataFrame(my_dict)
print campaigns_df
#
# runids = campaigns_df.CampaignRunId.unique()
# client = zeep.Client(wsdl = 'https://ws.campaigner.com/2013/01/campaignmanagement.asmx?WSDL')
# for id in runids:
#     id = str(id)
#     temp_zeep = client.service.GetTrackedLinkSummaryReport(authentication = authentication_dict, campaignRunId = id)['body']['GetTrackedLinkSummaryReportResult']['TrackedLinkSummaryData']
#     temp_dict = zeep.helpers.serialize_object(temp_zeep)
#     temp_df = pd.DataFrame(temp_dict)
#     summary_df1 = pd.DataFrame()
#     if summary_df1.empty:
#         summary_df1 = temp_df.copy()
#         break
#     else:
#         summary_df1.append(temp_df)
#         break
# print summary_df1
#
# client = zeep.Client(wsdl = 'https://ws.campaigner.com/2013/01/campaignmanagement.asmx?WSDL')
# zeep_dict = client.service.ListCampaigns(authentication = authentication_dict)['body']['ListCampaignsResult']['CampaignDescription']
# my_dict = zeep.helpers.serialize_object(zeep_dict)
# campaigns_df = pd.DataFrame(my_dict)
#
#
# campaigns = campaigns_df.Id.unique()
#
# for id in campaigns:
#     id = str(id)
#     temp_zeep = client.service.ListTrackedLinksByCampaign(authentication = authentication_dict, campaignIds = id)['body']['ListTrackedLinksByCampaignResult']['TrackedLinkDescription']
#     #print temp_zeep
#     temp_dict = zeep.helpers.serialize_object(temp_zeep)
#     temp_df = pd.DataFrame(temp_dict)
#     summary_df2 = pd.DataFrame()
#     if summary_df2.empty:
#         summary_df2 = temp_df.copy()
#         break
#     else:
#         summary_df2.append(temp_df)
#         break
# print summary_df2
#
# #
# #
# client = zeep.Client(wsdl = 'https://ws.campaigner.com/2013/01/contactmanagement.asmx?WSDL')
#
#
# xml = "<contactssearchcriteria><version major=\"2\" minor=\"0\" build=\"0\" revision=\"0\"/>" +\
#     "<set>Partial</set><evaluatedefault>True</evaluatedefault>" +\
#     "<group><filter><filtertype>EmailAction</filtertype>" +\
#     "<campaign><anycampaign/></campaign>"+\
#     "<action><status>Do</status><operator>ClickAnyLink</operator></action>" +\
#     "<operator>PastNDay</operator><value>1</value></filter>" +\
#     "</group></contactssearchcriteria>"
#
#
#
#
# runreport = client.service.RunReport(authentication = authentication_dict, xmlContactQuery = xml)
# print runreport
# ticket = runreport['body']['RunReportResult']['ReportTicketId']
#
# response = client.service.DownloadReport(authentication = authentication_dict,
# reportTicketId=ticket, fromRow=2, toRow=5, reportType='rpt_Summary_Campaign_Results')#['body']['DownloadReportResult']['ReportResult']
# print response
# dict_list = []
# for i in response:
#     dict_list.append(i['_attr_1'])
# my_dict = zeep.helpers.serialize_object(dict_list)
# campaigns_df = pd.DataFrame(my_dict)
# print campaigns_df
