from bs4 import BeautifulSoup

def get_fedconnect_soup():
    content = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

    <html xmlns="http://www.w3.org/1999/xhtml" >

    <head id="Head1"><title>
        FedConnect:  Opportunity Summary
    </title><link href="Common/Stylesheets/Style_Master.css" rel="stylesheet" type="text/css" /><link href="Common/Stylesheets/Style_MessageCenter.css" rel="stylesheet" type="text/css" /><link href="Common/Stylesheets/Style_OpportunityAward.css" rel="stylesheet" type="text/css" /><link href="Common/Stylesheets/Style_WebZonePage.css" rel="stylesheet" type="text/css" /><style type="text/css">
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 { text-decoration:none; }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1 { color:Black;font-family:Tahoma;font-size:100%; }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2 { padding:2px 2px 2px 2px; }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_3 {  }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_4 { font-weight:normal; }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_5 {  }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_6 {  }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_7 { background-color:#B5B5B5;padding:0px 0px 0px 0px; }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_8 { color:#6666AA;text-decoration:underline; }
        .WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_9 { color:#6666AA;text-decoration:underline; }
        .WebPartZone1_0 { border-color:Black;border-width:1px;border-style:None; }
        .WebPartZone1_1 {  }
        .WebPartZone1_2 { color:#001E4C;font-size:120%;font-weight:bold; }
        .WebPartZone1_3 { border-color:Silver;border-width:1px;border-style:Outset; }
        .WebPartZone2_0 { border-color:Black;border-width:1px;border-style:None; }
        .WebPartZone2_1 {  }
        .WebPartZone2_2 { color:#001E4C;font-size:120%;font-weight:bold; }
        .WebPartZone2_3 { border-color:Silver;border-width:1px;border-style:Outset; }

    </style></head>

    <body>
    <form method="post" action="PublicPages/PublicSearch/Public_OpportunitySummary.aspx?ReturnUrl=%2fFedConnect%2f%3fdoc%3d28321319RI0000024%26agency%3dSSA&amp;doc=28321319RI0000024&amp;agency=SSA" id="form1">
    <div class="aspNetHidden">
    <input type="hidden" name="__WPPS" id="__WPPS" value="s" />
    <input type="hidden" name="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ExpandState" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ExpandState" value="eennennn" />
    <input type="hidden" name="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_SelectedNode" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_SelectedNode" value="" />
    <input type="hidden" name="__EVENTTARGET" id="__EVENTTARGET" value="" />
    <input type="hidden" name="__EVENTARGUMENT" id="__EVENTARGUMENT" value="" />
    <input type="hidden" name="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_PopulateLog" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_PopulateLog" value="" />
    <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUKMTEzODcxND" />
    </div>

    <script type="text/javascript">
    //<![CDATA[
    var theForm = document.forms['form1'];
    if (!theForm) {
        theForm = document.form1;
    }
    function __doPostBack(eventTarget, eventArgument) {
        if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
            theForm.__EVENTTARGET.value = eventTarget;
            theForm.__EVENTARGUMENT.value = eventArgument;
            theForm.submit();
        }
    }
    //]]>
    </script>


    <script src="/FedConnect/WebResource.axd?d=ldpgsa9POskOYV5Fxgemz_lt7M4VdzNKriTVZZaCMxSYWT5IQ48Ac_ZI81RYAX9DM0EW8cgmcsMPirRU0&amp;t=636765211280000000" type="text/javascript"></script>


    <script src="/FedConnect/WebResource.axd?d=ObQeOXcRBagrVWoTChxaa-nQPVOXjUNXVg5Ag5QJMBjbokFA-l_SNCkn09E0ueuMVPhYbLHxNiYqyJnE0&amp;t=636765211280000000" type="text/javascript"></script>
    <script type="text/javascript">
    //<![CDATA[

        function TreeView_PopulateNodeDoCallBack(context,param) {
            WebForm_DoCallback(context.data.treeViewID,param,TreeView_ProcessNodeData,context,TreeView_ProcessNodeData,false);
        }
    var WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data = null;//]]>
    </script>

    <div class="aspNetHidden">

        <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="5EDCDEAE" />
        <input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="/wEdAAgUg/A2hYFMGhij3SfcS+dW6TIbCOn0GagHpgjvVpB3c+x15iJ5pDYy7yXruP/4hDoIxWujEltJMIGO4LxiyJdMUUIn+FdIMvBEzjK+ouhTycI/hTzlyzT41JiKIpMJRdcMHq8F/UvCiflmVyMB013K84c3O9MomIJfADP/6Pn/xp2uE5gDBffy0URd/ekZVHFzf0kL" />
    </div> 
        
        <h1 class="h1_oppawdsumamry">
            <table cellspacing="0" summary="This table is for formatting purposes only." id="FormView_DocDescription" style="width:100%;border-collapse:collapse;">
        <tr>
            <td colspan="2">     
                        Opportunity: Print Certification and Inventory Solution
                </td>
        </tr>
    </table>           
    </h1>        
        
        <p class="p_button_return">
        </p>      
        
        
        
        <div id="Panel_WebParts">
            
            
        
            
                
            
                <div id="div_WebPart_MainContent">    
                    <div id="vsuErrorText" style="display:none;">

        </div> 
                    
                    <table cellpadding="0" cellspacing="0" width="100%" >
                        <tr>
                            <td id="td_leftcolumn1" class="td_webpart_left" >
                            
                            
                    
                            
                                <table cellspacing="0" cellpadding="0" border="0" id="WebPartZone1" style="width:100%;">
            <tr>
                <td style="height:100%;"><table cellspacing="0" cellpadding="2" border="0" style="width:100%;height:100%;">
                    <tr>
                        <td><table class="WebPartZone1_0" cellspacing="0" cellpadding="2" border="0" style="width:100%;">
                            <tr>
                                <td class="WebPartZone1_3"><table cellspacing="0" cellpadding="0" border="0" style="width:100%;">
                                    <tr>
                                        <td style="width:100%;white-space:nowrap;"><span class="WebPartZone1_2" title="Description">Description</span>&nbsp;</td>
                                    </tr>
                                </table></td>
                            </tr><tr>
                                <td style="background-color:White;padding:5px;"><table cellspacing="0" summary="This table is for formatting purposes only." id="WebPartManager1_gwpCTRL_DocDescription1_CTRL_DocDescription1_FormView_DocDescription" style="border-collapse:collapse;">
                                    <tr>
                                        <td colspan="2">
                <p style="height: 100px; width: 100%; overflow: auto; ">
                    provide additional information to potential respondents.
                </p>
            </td>
                                    </tr>
                                </table>
        
    
        
        </td>
                            </tr>
                        </table></td>
                    </tr><tr>
                        <td><table class="WebPartZone1_0" cellspacing="0" cellpadding="2" border="0" style="width:100%;">
                            <tr>
                                <td class="WebPartZone1_3"><table cellspacing="0" cellpadding="0" border="0" style="width:100%;">
                                    <tr>
                                        <td style="width:100%;white-space:nowrap;"><span class="WebPartZone1_2" title="Overview">Overview</span>&nbsp;</td>
                                    </tr>
                                </table></td>
                            </tr><tr>
                                <td style="background-color:White;padding:5px;"><table class="table_bordercollapse" cellspacing="0" summary="This table is for formatting purposes only." id="WebPartManager1_gwpCTRL_DocInfo1_CTRL_DocInfo1_FormView_DocInfo" style="border-collapse:collapse;">
                                    <tr>
                                        <td colspan="2">
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Reference number:                       
                            </td>
                            <td class="datacolumn">
                                28321319RI0000024 
                            </td>                      
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Issue date:                       
                            </td>
                            <td class="datacolumn">
                                11/23/2018
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Response due:                       
                            </td>
                            <td class="datacolumn">
                            12/17/2018 05:00 PM US/Eastern  
                            </td>                      
                        </tr>
                    
                        <tr>
                            <td colspan="2">
                                <hr />
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Set Aside:
                            </td>
                            <td class="datacolumn">
                                N/A
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                NAICS:
                            </td>
                            <td class="datacolumn">
                                511210-Software Publishers
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                            PSC / FSC:
                            </td>
                            <td class="datacolumn">
                                7030-ADP SOFTWARE
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <hr />
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Agency:
                            </td>
                            <td class="datacolumn">
                                Social Security Administration
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <hr />
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Contracting office:
                                <br /><br />
                            </td>
                            <td class="datacolumn">
                            
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            Social Security Administration
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            Office of Acquisition and Grants
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            1540 Robert M. Ball Building
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            6401 Security Blvd
                            </td>
                        </tr>
                    <tr>
                            <td class="datacolumn_indent" colspan="2">
                            
                            </td>
                        </tr>
                    
                        <tr>                       
                            <td class="datacolumn_indent" colspan="2">
                                Baltimore, MD 21235
                                <br /><br />
                            </td>    
                        </tr>
                        <tr>
                            <td colspan="2">
                                <hr />
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Place of Performance:
                                <br /><br />
                            </td>
                            <td class="datacolumn">
                            
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            Headquarters
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            
                            </td>
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                            
                            </td>
                        </tr>
                    <tr>
                            <td class="datacolumn_indent" colspan="2">
                            
                            </td>
                        </tr>
                    
                        <tr>                       
                            <td class="datacolumn_indent" colspan="2">
                                
                                <br /><br />
                            </td>    
                        </tr>
                        <tr>
                            <td colspan="2">
                                <hr />
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Contact:
                            </td>
                            <td class="datacolumn">
                                ROGER  TWIGG
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Phone:
                            </td>
                            <td class="datacolumn">
                                
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Fax:
                            </td>
                            <td class="datacolumn">
                                
                            </td>
                        </tr>
                    <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Email:
                            </td>
                            <td class="datacolumn">
                                ROGER.TWIGG@SSA.GOV
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <hr />
                            </td>
                        </tr>                         
                        
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Vendors conference:                       
                            </td>
                            <td class="datacolumn">
                                <br />
                            
                            </td>  
                        
                        </tr>
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                                <br />                        
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top">
                                Location:       
                                <br /><br />                
                            </td>
                            <td class="datacolumn">
                            
                            </td> 
                        </tr> 
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                                
                                <br /><br />                
                            </td>
                        </tr>
                        <tr>
                            <td class="td_fieldlabel_nowrap_top" >
                                Details:       
                                <br /><br />                            
                            </td>
                            <td class="datacolumn">
                            
                            </td> 
                        </tr> 
                        <tr>
                            <td class="datacolumn_indent" colspan="2">
                                <p style="height: 100px; width: 100%; overflow: auto; ">
                                    
                                </p>
                                <br /><br />                
                            </td>
                        </tr>
                                
                
                </td>
                                    </tr>
                                </table>







    
    </td>
                            </tr>
                        </table></td>
                    </tr><tr>
                        <td style="padding:0;height:100%;"></td>
                    </tr>
                </table></td>
            </tr>
        </table>
                                
                                
                                                        
                            </td>
                
                            <td class="td_webpart_center"  rowspan="2" >  
                                                                
                                    <div class="div_whatdoido">
                                        <span id="LBL_WhatDoIDo" class="span_whatdoido">What do I do now?</span>
                                    </div>
                                    
                                    
                                    <div class='div_teammessage'>This is the opportunity summary page.  To the left you will see a description and an overview of this opportunity.  
                                        To the right you will see a list of the attached documentation.  To view any of the attachments, simply click the attachment name.
                                        <br /><br /><br /><br />
                                        
                                        <span style="font-weight: bold;">Registered Users</span>
                                        <br />
                                        To register interest in this opportunity or to electronically respond, you must first sign in.  Click the Sign In button below.<br />
                                        <br />
                                        <input type="submit" name="LogIn" value="Sign In" id="LogIn" class="button" />
                                        <br /><br /><br /><br />
                                        
                                        
                                        
                                        <span style="font-weight: bold;">Non Registered Users</span>
                                        <br />        
                                        You can view this or any other public opportunity. However, registered users have numerous added benefits including the ability to submit questions to the agency, 
                                        receive emails concerning updates and amendments, create and manage a response team and submit responses directly through this site.
                                        <br /><br />
                                        Becoming a registered user is fast, free and takes only a few minutes.  To get started, click the Register Now button below.
                                        <br /><br />
                                        <input type="submit" name="btn_Register" value="Register Now" id="btn_Register" class="button" />&nbsp;&nbsp;
                                    <br /><br />
                                <hr />
                                    </div>
                                                        
                                
                                    <div class="div_whatdoido">
                                    <br /><br />
                                    <input type="submit" name="btn_Return" value="Return to Public Opportunity List" id="btn_Return" class="button" />
        
                                    </div>
                                </td>
                            <td class="td_webpart_right" >

                                <table cellspacing="0" cellpadding="0" border="0" id="WebPartZone2" style="width:100%;">
            <tr>
                <td style="height:100%;"><table cellspacing="0" cellpadding="2" border="0" style="width:100%;height:100%;">
                    <tr>
                        <td><table class="WebPartZone2_0" cellspacing="0" cellpadding="2" border="0" style="width:100%;">
                            <tr>
                                <td class="WebPartZone2_3"><table cellspacing="0" cellpadding="0" border="0" style="width:100%;">
                                    <tr>
                                        <td style="width:100%;white-space:nowrap;"><span class="WebPartZone2_2" title="Documentation">Documentation</span>&nbsp;</td>
                                    </tr>
                                </table></td>
                            </tr><tr>
                                <td style="background-color:White;padding:5px;">


    <div id="div_attachments"  class="div_attachmentlist">
        
        
        
        
        <a href="#WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_SkipLink"><img alt="Skip attachment list." src="/FedConnect/WebResource.axd?d=1Qy8WEZnhB8RQWawlAOs_qiEXPwFUvqAL2t_Jz6LByI_EAv-8F4BCMnZkG5LHFGKSU4db5ViQuiC4oRH0&amp;t=636765211280000000" width="0" height="0" style="border-width:0px;" /></a><div id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments" title="Attachments">
                                    <table cellpadding="0" cellspacing="0" style="border-width:0;">
                                        <tr>
                                            <td><a id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn0" href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,0,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn0&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn0Nodes&#39;))"><img src="/FedConnect/WebResource.axd?d=rDupnbnRxxLouEMydiW2Eejt9sDWCiaga446F1FF_uS40DXNzXTCiCrs7c_3jBa13SvjENAYW5T8npHkd_UHQSMODeTqtc3ah1xpzp-Aa8579yq-0&amp;t=636765211280000000" alt="Collapse 28321319RI0000024" style="border-width:0;" /></a></td><td><a href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst0&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst0i" tabindex="-1"><img src="Common/Images/TreeLineImages/folder.gif" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_3" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1" href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst0&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst0">28321319RI0000024</a></td>
                                        </tr><tr style="height:0px;">
                                            <td></td>
                                        </tr>
                                    </table><div id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn0Nodes" style="display:block;">
                                        <table cellpadding="0" cellspacing="0" style="border-width:0;">
                                            <tr style="height:0px;">
                                                <td></td>
                                            </tr><tr>
                                                <td><div style="width:15px;height:1px"></div></td><td><a id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1" href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,1,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1Nodes&#39;))"><img src="/FedConnect/WebResource.axd?d=rDupnbnRxxLouEMydiW2Eejt9sDWCiaga446F1FF_uS40DXNzXTCiCrs7c_3jBa13SvjENAYW5T8npHkd_UHQSMODeTqtc3ah1xpzp-Aa8579yq-0&amp;t=636765211280000000" alt="Collapse Solicitation" style="border-width:0;" /></a></td><td><a href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,1,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1Nodes&#39;))" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst1i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=egrZcX-XiWmRmBq72DCDOwY5rlvrCAFSJvnui-tRf1aLk5Ej2j0KuLIVKR08ZdGk_HpZKhHFBAm8-eRN0-lmDd2ICaNPoe4HEsJ8uuCKt2QO2oJJ0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_5" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_4" href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,1,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1Nodes&#39;))" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst1">Solicitation</a></td>
                                            </tr><tr style="height:0px;">
                                                <td></td>
                                            </tr>
                                        </table><div id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn1Nodes" style="display:block;">
                                            <table cellpadding="0" cellspacing="0" style="border-width:0;">
                                                <tr style="height:0px;">
                                                    <td></td>
                                                </tr><tr>
                                                    <td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><img src="/FedConnect/WebResource.axd?d=IuDw3BwrXsU5_SXtFpqFWC3qKu-QKSApFA5zQEk64cjVdv0ZL9_CzGOUBjxJOlvaeG28GjpKtWyR8_sKRlU-d-RxTM83BY1zBNvBysEEe0CiDkLJ0&amp;t=636765211280000000" alt="" /></td><td><a href="javascript:void window.open(&#39;/FedConnect/PublicPages/PublicSearch/Public_OpportunityDescription.aspx?id=108888&#39;,&#39;Opportunity&#39;,&#39;width=400, height=700,toolbar=0, menubar=0, status=0, scrollbars=1, resizable=1&#39;)" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst2i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=36m8VhGkCDmsJNpPQdzclulQiF_g41vnGTfdqYmq4z1EHri_gx6rLmkT93y0pkjS843S1W2E6iO4lR-SquWIJ-XUffnstaokS3YjLRmKnTIo7d4V0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1" href="javascript:void window.open(&#39;/FedConnect/PublicPages/PublicSearch/Public_OpportunityDescription.aspx?id=108888&#39;,&#39;Opportunity&#39;,&#39;width=400, height=700,toolbar=0, menubar=0, status=0, scrollbars=1, resizable=1&#39;)" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst2">Overview</a></td>
                                                </tr><tr style="height:0px;">
                                                    <td></td>
                                                </tr>
                                            </table><table cellpadding="0" cellspacing="0" style="border-width:0;">
                                                <tr style="height:0px;">
                                                    <td></td>
                                                </tr><tr>
                                                    <td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><img src="/FedConnect/WebResource.axd?d=IuDw3BwrXsU5_SXtFpqFWC3qKu-QKSApFA5zQEk64cjVdv0ZL9_CzGOUBjxJOlvaeG28GjpKtWyR8_sKRlU-d-RxTM83BY1zBNvBysEEe0CiDkLJ0&amp;t=636765211280000000" alt="" /></td><td><a href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024\\108888\\SUPPORTDOC,1685647&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst3&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst3i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=36m8VhGkCDmsJNpPQdzclulQiF_g41vnGTfdqYmq4z1EHri_gx6rLmkT93y0pkjS843S1W2E6iO4lR-SquWIJ-XUffnstaokS3YjLRmKnTIo7d4V0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1" href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024\\108888\\SUPPORTDOC,1685647&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst3&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst3">RFI Print Certification and Inventory - 2nd posting</a></td>
                                                </tr><tr style="height:0px;">
                                                    <td></td>
                                                </tr>
                                            </table><table cellpadding="0" cellspacing="0" style="border-width:0;">
                                                <tr style="height:0px;">
                                                    <td></td>
                                                </tr><tr>
                                                    <td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><a id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4" href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,4,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4Nodes&#39;))"><img src="/FedConnect/WebResource.axd?d=rDupnbnRxxLouEMydiW2Eejt9sDWCiaga446F1FF_uS40DXNzXTCiCrs7c_3jBa13SvjENAYW5T8npHkd_UHQSMODeTqtc3ah1xpzp-Aa8579yq-0&amp;t=636765211280000000" alt="Collapse Amendment 1" style="border-width:0;" /></a></td><td><a href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,4,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4Nodes&#39;))" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst4i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=egrZcX-XiWmRmBq72DCDOwY5rlvrCAFSJvnui-tRf1aLk5Ej2j0KuLIVKR08ZdGk_HpZKhHFBAm8-eRN0-lmDd2ICaNPoe4HEsJ8uuCKt2QO2oJJ0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_5" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_4" href="javascript:TreeView_ToggleNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data,4,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4&#39;),&#39; &#39;,document.getElementById(&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4Nodes&#39;))" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst4">Amendment 1</a></td>
                                                </tr><tr style="height:0px;">
                                                    <td></td>
                                                </tr>
                                            </table><div id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentsn4Nodes" style="display:block;">
                                                <table cellpadding="0" cellspacing="0" style="border-width:0;">
                                                    <tr style="height:0px;">
                                                        <td></td>
                                                    </tr><tr>
                                                        <td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><img src="/FedConnect/WebResource.axd?d=IuDw3BwrXsU5_SXtFpqFWC3qKu-QKSApFA5zQEk64cjVdv0ZL9_CzGOUBjxJOlvaeG28GjpKtWyR8_sKRlU-d-RxTM83BY1zBNvBysEEe0CiDkLJ0&amp;t=636765211280000000" alt="" /></td><td><a href="javascript:void window.open(&#39;/FedConnect/PublicPages/PublicSearch/Public_OpportunityDescription.aspx?id=109257&#39;,&#39;Opportunity&#39;,&#39;width=400, height=700,toolbar=0, menubar=0, status=0, scrollbars=1, resizable=1&#39;)" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst5i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=36m8VhGkCDmsJNpPQdzclulQiF_g41vnGTfdqYmq4z1EHri_gx6rLmkT93y0pkjS843S1W2E6iO4lR-SquWIJ-XUffnstaokS3YjLRmKnTIo7d4V0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1" href="javascript:void window.open(&#39;/FedConnect/PublicPages/PublicSearch/Public_OpportunityDescription.aspx?id=109257&#39;,&#39;Opportunity&#39;,&#39;width=400, height=700,toolbar=0, menubar=0, status=0, scrollbars=1, resizable=1&#39;)" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst5">Overview</a></td>
                                                    </tr><tr style="height:0px;">
                                                        <td></td>
                                                    </tr>
                                                </table><table cellpadding="0" cellspacing="0" style="border-width:0;">
                                                    <tr style="height:0px;">
                                                        <td></td>
                                                    </tr><tr>
                                                        <td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><img src="/FedConnect/WebResource.axd?d=IuDw3BwrXsU5_SXtFpqFWC3qKu-QKSApFA5zQEk64cjVdv0ZL9_CzGOUBjxJOlvaeG28GjpKtWyR8_sKRlU-d-RxTM83BY1zBNvBysEEe0CiDkLJ0&amp;t=636765211280000000" alt="" /></td><td><a href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024\\108888\\109257\\SUPPORTDOC,1690028&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst6&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst6i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=36m8VhGkCDmsJNpPQdzclulQiF_g41vnGTfdqYmq4z1EHri_gx6rLmkT93y0pkjS843S1W2E6iO4lR-SquWIJ-XUffnstaokS3YjLRmKnTIo7d4V0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1" href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024\\108888\\109257\\SUPPORTDOC,1690028&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst6&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst6">28321319RI0000024</a></td>
                                                    </tr><tr style="height:0px;">
                                                        <td></td>
                                                    </tr>
                                                </table><table cellpadding="0" cellspacing="0" style="border-width:0;">
                                                    <tr style="height:0px;">
                                                        <td></td>
                                                    </tr><tr>
                                                        <td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><div style="width:15px;height:1px"></div></td><td><img src="/FedConnect/WebResource.axd?d=IuDw3BwrXsU5_SXtFpqFWC3qKu-QKSApFA5zQEk64cjVdv0ZL9_CzGOUBjxJOlvaeG28GjpKtWyR8_sKRlU-d-RxTM83BY1zBNvBysEEe0CiDkLJ0&amp;t=636765211280000000" alt="" /></td><td><a href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024\\108888\\109257\\SUPPORTDOC,1690027&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst7&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst7i" tabindex="-1"><img src="/FedConnect/WebResource.axd?d=36m8VhGkCDmsJNpPQdzclulQiF_g41vnGTfdqYmq4z1EHri_gx6rLmkT93y0pkjS843S1W2E6iO4lR-SquWIJ-XUffnstaokS3YjLRmKnTIo7d4V0&amp;t=636765211280000000" alt="" style="border-width:0;" /></a></td><td class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_2" onmouseover="TreeView_HoverNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this)" onmouseout="TreeView_UnhoverNode(this)" style="white-space:nowrap;"><a class="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_0 WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_1" href="javascript:__doPostBack(&#39;WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments&#39;,&#39;s28321319RI0000024\\108888\\109257\\SUPPORTDOC,1690027&#39;)" onclick="TreeView_SelectNode(WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data, this,&#39;WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst7&#39;);" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst7">Amendment #1</a></td>
                                                    </tr><tr style="height:0px;">
                                                        <td></td>
                                                    </tr>
                                                </table>
                                            </div>
                                        </div>
                                    </div>
                                </div><a id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_SkipLink"></a>

        
        

    </div></td>
                            </tr>
                        </table></td>
                    </tr><tr>
                        <td style="padding:0;height:100%;"></td>
                    </tr>
                </table></td>
            </tr>
        </table>
                            </td>
                        </tr>
                        
                    </table>
                                
                    <div id="CTRL_FooterBar1_Panel_FooterRuleLine">
            
        <hr id="hr_footerbar_rule"/>

        </div>


                                    
    <div id="div_footerbar_main">
        <table class="tbl_footerbar_main"  summary="This table is for formatting purposes only." >
            <tr>
                <td style="width: 400px; ">
                    <!--<a id="CTRL_FooterBar1_hypCopyright" title="Copyright Information" href="PublicPages/Copyright.aspx"> -->
                            <abbr title="Copyright">©</abbr> 2019 Compusearch Software Systems, Inc.    All rights reserved.
                    <!--</a> -->
                </td>
                <td style="text-align: center;">
                    <a id="CTRL_FooterBar1_hypTerms" title="View Terms of Service and Use" href="PublicPages/TOS_ReadOnly.aspx"> 
                            Terms of Service and Use
                    </a>
                </td>
                <td class="td_about_ViP" >
                    <a id="CTRL_FooterBar1_Link_About" title="About FedConnect" href="PublicPages/About.aspx">About FedConnect</a>    
                </td>
            </tr>
        </table>
    </div>

                    
                </div>
        
        
            
    </div>
        
        
        
    
        
    
        
        
        
        
            

    <link href="../../Common/Stylesheets/Style_Master.css" rel="stylesheet" type="text/css" />
    <div id="div_bannerbar">
        <div id="div_bannerbar_main" >
                <table id="table_banner">
                    <tr>
                        <td class="td_banner_title" style="white-space: nowrap; ">
                            
                            
                                
                        </td>
                        <td style="width: 100%; text-align: right;">
                            
                        </td>
                    </tr>            
                </table> 
        </div>
    </div> 
                

    <div id="div_logobar_main" >
    
        <div id="div_logobar_logo">
            <img id="CTRL_LogoBar1_MasterLogo" src="Common/Images/Logos/logo.gif" alt="FedConnect logo" />
        </div>

        <div id="div_logobar_toolbar">
            
            
            
                


            
            
            
            <a id="CTRL_LogoBar1_VidioLink" title="Video Library" class="a_logobar_toolbar" href="Videos/videolibrary.htm" target="_blank">              
                    Videos
            </a>   
            
            <span id="CTRL_LogoBar1_IMGBTN_Home_Divider" class="spacer">|</span>        

            <a id="CTRL_LogoBar1_Master_Help" title="Help" class="a_logobar_toolbar" href="Help/welcome_to_the_fedconnect_online_help.htm" target="_blank">              
                    Help
            </a>  
        
                    
                
            
                
            
            
            
            
            
                
            
            
    
    </div>
        
    </div>

    
        
    
    
        
                
            
    
    <script type="text/javascript">
    //<![CDATA[
    var WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ImageArray =  new Array('Common/Images/TreeLineImages/folder.gif', '/FedConnect/WebResource.axd?d=egrZcX-XiWmRmBq72DCDOwY5rlvrCAFSJvnui-tRf1aLk5Ej2j0KuLIVKR08ZdGk_HpZKhHFBAm8-eRN0-lmDd2ICaNPoe4HEsJ8uuCKt2QO2oJJ0&t=636765211280000000', '/FedConnect/WebResource.axd?d=36m8VhGkCDmsJNpPQdzclulQiF_g41vnGTfdqYmq4z1EHri_gx6rLmkT93y0pkjS843S1W2E6iO4lR-SquWIJ-XUffnstaokS3YjLRmKnTIo7d4V0&t=636765211280000000', '/FedConnect/WebResource.axd?d=IuDw3BwrXsU5_SXtFpqFWC3qKu-QKSApFA5zQEk64cjVdv0ZL9_CzGOUBjxJOlvaeG28GjpKtWyR8_sKRlU-d-RxTM83BY1zBNvBysEEe0CiDkLJ0&t=636765211280000000', '/FedConnect/WebResource.axd?d=l4g1-nQW8AuGW8RH5AV-QFf0hVFnkMs70MC03VmwcPmnZ5k6jWDSJrDiIVRG-nRKNmpt-Wdm3TQ1-PqWvxcqIDn9AprVwNXf_T-pSWpkLuQyJRAl0&t=636765211280000000', '/FedConnect/WebResource.axd?d=rDupnbnRxxLouEMydiW2Eejt9sDWCiaga446F1FF_uS40DXNzXTCiCrs7c_3jBa13SvjENAYW5T8npHkd_UHQSMODeTqtc3ah1xpzp-Aa8579yq-0&t=636765211280000000');
    var Page_ValidationSummaries =  new Array(document.getElementById("vsuErrorText"));
    //]]>
    </script>

    <script type="text/javascript">
    //<![CDATA[
    var vsuErrorText = document.all ? document.all["vsuErrorText"] : document.getElementById("vsuErrorText");
    vsuErrorText.headertext = "Following issues have been identified.Please address before proceeding.";
    //]]>
    </script>


    <script type="text/javascript">
    //<![CDATA[
    var __wpmExportWarning='This Web Part Page has been personalized. As a result, one or more Web Part properties may contain confidential information. Make sure the properties contain information that is safe for others to read. After exporting this Web Part, view properties in the Web Part description file (.WebPart) by using a text editor such as Microsoft Notepad.';var __wpmCloseProviderWarning='You are about to close this Web Part.  It is currently providing data to other Web Parts, and these connections will be deleted if this Web Part is closed.  To close this Web Part, click OK.  To keep this Web Part, click Cancel.';var __wpmDeleteWarning='You are about to permanently delete this Web Part.  Are you sure you want to do this?  To delete this Web Part, click OK.  To keep this Web Part, click Cancel.';
    var callBackFrameUrl='/FedConnect/WebResource.axd?d=DN2kktcy0OgX1guLEKeS5vp-Jn2ZlDEBddwZJ0JqxIOmyK4Mj3C77m2f08QCsNimRLEp5Nux9DCaeATJ0&t=636765211280000000';
    WebForm_InitCallback();var WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data = new Object();
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.images = WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ImageArray;
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.collapseToolTip = "Collapse {0}";
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.expandToolTip = "Expand {0}";
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.expandState = theForm.elements['WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ExpandState'];
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.selectedNodeID = theForm.elements['WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_SelectedNode'];
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.hoverClass = 'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_9';
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.hoverHyperLinkClass = 'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_8';
    (function() {
    for (var i=0;i<6;i++) {
    var preLoad = new Image();
    if (WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ImageArray[i].length > 0)
        preLoad.src = WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ImageArray[i];
    }
    })();
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.lastIndex = 8;
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.populateLog = theForm.elements['WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_PopulateLog'];
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.treeViewID = 'WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments';
    WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data.name = 'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_Data';
    //]]>
    </script>
    </form>
    
    
    
    
        
    </body>
    </html>'''
    soup = BeautifulSoup(content, 'html.parser')

    return soup

def get_a_tag():
    html = r'''<a href="javascript:__doPostBack('WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments','s28321319RI0000024\\108888\\109257')" id="WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst4"><font color="Black" face="Tahoma">Amendment 1</font></a>'''
    soup = BeautifulSoup(html, 'html.parser')
    a_tag = soup.find('a')   

    return a_tag 


expected_payload = {'__WPPS': 's', 
                    '__VIEWSTATE': '/wEPDwUKMTEzODcxND',
                    '__VIEWSTATEGENERATOR': '5EDCDEAE', 
                    '__EVENTVALIDATION': '/wEdAAgUg/A2hYFMGhij3SfcS+dW6TIbCOn0GagHpgjvVpB3c+x15iJ5pDYy7yXruP/4hDoIxWujEltJMIGO4LxiyJdMUUIn+FdIMvBEzjK+ouhTycI/hTzlyzT41JiKIpMJRdcMHq8F/UvCiflmVyMB013K84c3O9MomIJfADP/6Pn/xp2uE5gDBffy0URd/ekZVHFzf0kL',
                    'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_SelectedNode': 'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachmentst4', 
                    'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_ExpandState': 'eennennn', 
                    '__EVENTTARGET': 'WebPartManager1$gwpCTRL_AttachmentTree1$CTRL_AttachmentTree1$Tree_Attachments', 
                    '__EVENTARGUMENT': 's28321319RI0000024\\108888\\109257', 
                    'WebPartManager1_gwpCTRL_AttachmentTree1_CTRL_AttachmentTree1_Tree_Attachments_PopulateLog': '',
                    '__SCROLLPOSITIONX': 123,
                    '__SCROLLPOSITIONY': 0}