# -*- coding: utf-8 -*-
'''
Created on Mar 28, 2013

@author: timmahrt

Common HTML snippets
'''

import os
import Cookie

from functools import partial

from lmeds import loader

choice = """<input type="radio" name="radio">"""
img = """<img src="data/%s">"""
txtBox = """<input type="text" name="%s" value=""/>"""
radioButton = """<input type="radio" name="radio" value="%s">"""

pg2HTML = """
%%(explain)s<br /><br />
%(choiceA)s %%(consent)s\n
<br /><br />\n
%(choiceB)s %%(dissent)s
""" % {"choiceA":radioButton % "consent",
       "choiceB":radioButton % "dissent"
       }


formTemplate = """
<form class="submit" name="languageSurvey" method="POST" action="%(source_cgi_fn)s" onsubmit="return processSubmit();">
%(html)s

<input TYPE="hidden" name="page" value="%(page)s"> 
<input TYPE="hidden" name="pageNumber" value="%(pageNumber)d"> 
<input TYPE="hidden" name="cookieTracker" value="%(cookieTracker)s"> 
<input TYPE="hidden" name="user_name" value="%(user_name)s"> 
<input TYPE="hidden" name="num_items" value="%(num_items)d">
<input TYPE="hidden" name="task_duration" id="task_duration" value="0">
<input TYPE="hidden" name="audioFilePlays0" id="audioFilePlays0" value="0" />
<input TYPE="hidden" name="audioFilePlays1" id="audioFilePlays1" value="0" />
<br /><br />
<input id="submit" TYPE="submit" value="%(submit_button_text)s">
</form>
"""

# This is more or less a HACK 
# -- we needed to hide the submit button, but only in a single situation
# -- (it reappears after someone clicks another button--handled via javascript)
formTemplate2 = """
<form class="submit" name="languageSurvey" method="POST" action="%(source_cgi_fn)s" onsubmit="return processSubmit();">
%(html)s

<div id="HiddenForm" style="DISPLAY: none">
<input TYPE="hidden" name="page" value="%(page)s"> 
<input TYPE="hidden" name="pageNumber" value="%(pageNumber)d"> 
<input TYPE="hidden" name="cookieTracker" value="%(cookieTracker)s"> 
<input TYPE="hidden" name="user_name" value="%(user_name)s"> 
<input TYPE="hidden" name="num_items" value="%(num_items)d">
<input TYPE="hidden" name="task_duration" id="task_duration" value="0">
<input TYPE="hidden" name="audioFilePlays0" id="audioFilePlays0" value="0" />
<input TYPE="hidden" name="audioFilePlays1" id="audioFilePlays1" value="0" />
<br /><br />
<input id="submit" TYPE="submit" value="%(submit_button_text)s">
</div>
</form>
"""

taskDurationCode = """
<script type="text/javascript">

var start = new Date().getTime();

function calcDuration() {
    var time = new Date().getTime() - start;

    var seconds = Math.floor(time / 100) / 10;
    var minutes = Math.floor(seconds / 60);
    seconds = seconds - (minutes * 60);
    if(Math.round(seconds) == seconds) { 
        seconds += '.0'; 
    }
    var param1 = minutes.toString();
    var param2 = Number(seconds).toFixed(1);
    document.getElementById("task_duration").value = param1 + ":" + param2;
}
</script>
"""


def createChoice(textList, i, checkboxFlag=False):
    
    widgetTemplate = """<input type="radio" name="%s" id="%s" value="%s">"""
    if checkboxFlag:
        widgetTemplate = """<input type="checkbox" name="%s" id="%s" value="%s">"""
        
    choiceList = []
    for text in textList:
        newRadioButton = widgetTemplate % (str(i), str(i), text)
        choiceList.append("%s %s" % (text, newRadioButton))
    
    txtSeparator = "&nbsp;" * 4
    
    return "%s" %  txtSeparator.join(choiceList), i + 1


def createChoicebox(textList, i):
    
    widgetTemplate = """<option value="%s">%s</option>"""
    
#     textList = ["",] + textList # Default value is blank
    
    choiceList = []
    for j, text in enumerate(textList):
        newChoice = widgetTemplate % (str(j), text)
        choiceList.append(newChoice)
        
    returnTxt = """<select name="%s" id="%s">%%s</select>""" % (str(i), str(i))
    returnTxt %= "\n".join(choiceList)
    
    return returnTxt, i + 1


def createTextbox(i):
    txtBox = """<input type="text" name="%s" id="%s" value=""/>"""
    return txtBox % (str(i), str(i)), i + 1


def createTextfield(i, argList):
    width = argList[0] # Units in number of characters
    numRows = argList[1]
    return """<textarea name="%s" id="%s" rows="%s" cols="%s"></textarea>""" % (str(i), str(i), numRows, width), i + 1

    
def createWidget(widgetType, argList, i):

    elementDictionary = {"Choice":createChoice,
                         "Item_List":partial(createChoice, checkboxFlag=True),
                         "Choicebox":createChoicebox,
                         }
    
    if widgetType == "Textbox":
        widgetHTML, i = createTextbox(i)
    elif widgetType == "Multiline_Textbox":
        widgetHTML, i = createTextfield(i, argList)
    else:
        widgetHTML, i = elementDictionary[widgetType](argList, i)
        
    return widgetHTML, i


def surveyPage(surveyFN):
    surveyItemList = survey.parseSurveyFile(surveyFN)
    i = 0
    itemHTMLList = []
    
    choiceBoxIndexList = []
    for item in surveyItemList:
        
        itemElementList = []
        for dataTuple in item.widgetList:
            elementType, argList = dataTuple
            widget = createWidget(elementType, argList, i)[0]
            itemElementList.append(widget)
        
            if elementType == "Choicebox":
                choiceBoxIndexList.append(i)
            i += 1
        
        
        
        elementHTML = " ".join(itemElementList)
        
        itemHTML = "%s) %s<br />%s" % (item.enumStrId, item.text, elementHTML)
        
        if item.depth == 1:
            itemHTML = "<div id='indentedText'>%s</div>" % itemHTML
        elif item.depth > 1:
            itemHTML = "<div id='doubleIndentedText'>%s</div>" % itemHTML
        
        itemHTMLList.append(itemHTML)
    
    surveyHTML = "<br /><br />\n".join(itemHTMLList)
    
    javascript = """document.getElementById("%d").selectedIndex = -1;"""
    javascriptList = [javascript % i for i in choiceBoxIndexList]

        
    embedTxt = """\n<script type="text/javascript">\nfunction setchoiceboxes() {
    %s
    }
    window.addEventListener("load", setchoiceboxes);\n</script>\n""" % "\n".join(javascriptList)
    
    return "<div id='longText'>%s</div>" % surveyHTML, embedTxt
        
        

def getProgressBar():
    progressBarText = "- %s - <br />" % loader.getText("progress")
    
    progressBarTemplate = progressBarText + """
    <dl class="progress">
        <dt>Completed:</dt>
        <dd class="done" style="width:%(percentComplete)s%%%%"><a href="/"></a></dd>
    
        <dt >Left:</dt>
        <dd class="left" style="width:%(percentUnfinished)s%%%%"><a href="/"></a></dd>
    </dl>
    """
    
    return progressBarTemplate


def validateAndUpdateCookie(pageNum):
    '''
    Tracks the progress of pages.  If a page is reloaded, terminate execution.
    
    In order to implement this, the pageNum must always increase by an
    arbitrary amount with each new page.  If the pageNum is less than or equal
    to what it was before, this indicates the reloading of an older page.
    
    Terminating the test prevents users from hitting /back/ and then /forward/
    to wipe page-variables like num-of-times-audio-file-played.
    '''
    oldPageNum = -1
    try:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        oldPageNum = int(cookie["lastPage"].value)
    except(Cookie.CookieError, KeyError):
        if pageNum != 0:
            print "\n\nERROR: Page number is %d according to index.cgi but no cookies found" % pageNum
            exit(0)
    else:
        if pageNum <= oldPageNum and pageNum != 0:
            print "\n\nERROR: Back button or refresh detected", pageNum, oldPageNum
            exit(0)
    
#    # Set expiration five minutes from now
#    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    cookie = Cookie.SimpleCookie()
    cookie["lastPage"] = pageNum
    
    return cookie, oldPageNum, pageNum


def printCGIHeader(pageNum, disableRefreshFlag):
    '''
    This header must get printed before the website will render new text as html
    
    A double newline '\n\n' indicates the end of the header.
    '''
    print 'Content-Type: text/html'
    
    if disableRefreshFlag:
        print "Pragma-directive: no-cache"
        print "Cache-directive: no-cache"
        print "Cache-Control: no-cache, no-store, must-revalidate"
        print "Pragma: no-cache"
        print "Expires: 0"
        cookieStr= validateAndUpdateCookie(pageNum)[0]
        print cookieStr
    print "\n\n"


def firstPageHTML():
    txtBox = """<input type="text" name="%s" value=""/>"""
    productNote = """%s <br /> 
<b><i>%s</i></b><br /><br />\n\n""" % (loader.getText('experiment header'),
                                       constants.softwareName)
    
    title = """<div><p id="title">%s</p></div>\n\n""" % loader.getText('title')
    
    backButtonWarning = loader.getText('back button warning')
    pg0HTML = loader.getText('user name text') + "<br /><br />"
    pg0HTML += (txtBox % 'user_name_init') + "<br /><br />" + backButtonWarning
    
    unsupportedWarning = '''<div id="unsupported_warning"><br /><br /><font color="blue"><b>
    The web browser you are using does not support features required by LMEDS.  
    Please update your software
    or download a modern modern such as Chrome or Firefox.</b></font></div>'''
     
    return productNote + title + pg0HTML + unsupportedWarning
    

def firstPageErrorHTML():
    
    pg0HTML = firstPageHTML()
    pg0HTML = pg0HTML

    textKey = 'error user name exists'
    userNameErrorTxt = loader.getText(textKey)

    if '%s' not in userNameErrorTxt:
        errorMsg = "Please add a '%s' for the user name in the text associated with this key"
        raise loader.BadlyFormattedTextError(errorMsg, textKey)
    
    pg0HTML += "<br />" + userNameErrorTxt

    return pg0HTML


def instructionPageHTML():
    
    instructionText = """Instruction Page<br/><br/>In this study, you will...
    <br/><br/>Each sound file is playable twice.  After listening to the audio, 
    make your judgements and move on to the next page."""
    
    return instructionText


def breakPageHTML():

    return loader.getText('section finished')

  
def audioTestPageHTML():
    
    audioTestPageHTML
    
    consentText = "\n\n<hr /><br /><br />%s" % loader.getText("audioTest text")

    consentButton = radioButton % "consent"
    dissentButton = radioButton % "dissent"

    consentChoice = '%s %s\n<br /><br />%s %s' % (consentButton, 
                                                  loader.getText("audioTest affirm"),
                                                  dissentButton,
                                                  loader.getText("audioTest reject"))

    consentHTML = consentText + "<br /><br />%s<br /><br />" + consentChoice

    return consentHTML
  
    
def consentPageHTML(consentName=None):
    
    if consentName == None:
        consentName = "text"
    
    consentText = open(join(constants.htmlSnippetsDir, "consent.html"), "r").read()
    consentText %= (loader.getText("title"),
                    loader.getText("consent title"),
                    loader.getText("consent %s" % consentName))
    
    consentText += "\n\n<hr /><br /><br />%s" % loader.getText("consent query")

#    radioButton = """<input type="radio" name="radio" value="%s">"""

    consentButton = radioButton % "consent"
    dissentButton = radioButton % "dissent"

    consentChoice = '%s %s\n<br /><br />%s %s' % (consentButton, 
                                                  loader.getText("consent"),
                                                  dissentButton,
                                                  loader.getText("dissent"))

    consentHTML = consentText + "<br /><br />" + consentChoice

    return consentHTML


def consentEndPageHTML():
    
    consentErrorHTML = ""
    
    return consentErrorHTML


def axbPageHTML():
    
    radioButton = '<p><input type="radio" name="axb" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """%s<br /><br /><br />
%s<br /> <br />
%%s<br /> <br />
<table class="center">
<tr><td>%s</td><td>%s</td></tr>
<tr><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>"""
    html %= (loader.getText("axb query"),
             loader.getText("axb x"),
             loader.getText("axb a"),
             loader.getText("axb b"),
             radioButton % {'id':'0'}, 
             radioButton % {'id':'1'})
    
#     html %= ('<p><input type="radio" value="A" id="A" name="gender" /> <label for="A">Male</label></p>',
#             '<p><input type="radio" value="B" id="B" name="gender" /> <label for="B ">Female</label></p>')
    
    return html


def audioDecisionPageHTML():
    
    radioButton = '<p><input type="radio" name="abn" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """
    %%s
<table class="center">
<tr><td>%%s</td><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td></tr>
</table>""" 
    
    return html % (radioButton % {'id':'0'},
                   radioButton % {'id':'1'},
                   radioButton % {'id':'2'})


def sameDifferentPageHTML():
    
    radioButton = '<p><input type="radio" name="same_different" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """
    <br /><br />%%s %%s<br /><br />
<table class="center">
<tr><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>""" 
    
    return html % (radioButton % {'id':'0'},
                   radioButton % {'id':'1'})

def abPageHTML():
    
    radioButton = '<p><input type="radio" name="ab" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """Write statement about how the user should select (A) or (B).<br /><br />
<table class="center">
<tr><td>A</td><td>B</td></tr>
<tr><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>"""
    html %= (radioButton % {'id':'0'}, 
             radioButton % {'id':'1'})
    
    return html    


def constructCheckboxTable(wordList, doBreaks, doProminence, offsetNum):
    

    breakSign = "|" 
    breakHTML = '<p><input type="checkbox" name="b" value="%(num)d" id="%(num)d"/> <label for="%(num)d">.</label></p>\n'
    prominenceHTML = '<p><input type="checkbox" name="p" value="%(num)d" id="%(num)d"/> <label for="%(num)d">.</label></p>\n'
    
    
    # Set the prominence marks
    row1List = wordList
    bCheckboxList = []
    pCheckboxList = [prominenceHTML % {'num':i+offsetNum} for i, word in enumerate(wordList)]
    
    # Set the breaks
    if doBreaks:
        
        row1ListCopy = []
        pCheckboxListCopy = []
        
#        row1List = [breakSign,]
        bCheckboxList = []
        for i, wordTuple in enumerate( zip(row1List,pCheckboxList) ):
            word, pCheckbox = wordTuple
            
            row1ListCopy.append(word)
            row1ListCopy.append(breakSign)
            
            bCheckboxList.append("")
            bCheckboxList.append(breakHTML % {'num':i})
            
            pCheckboxListCopy.append(pCheckbox)
            pCheckboxListCopy.append("")
        
        row1List = row1ListCopy[:-1]
        pCheckboxList = pCheckboxListCopy[:-1]
        bCheckboxList = bCheckboxList[:-1]
        
    textRow = "</td><td>".join(row1List)

    
    rowHTML = "<tr><td>%s</td></tr>"
    
    allRows = ""
    allRows += rowHTML % textRow
    
    if doBreaks:
        bCheckboxRow = "</td><td>".join(bCheckboxList)
        allRows += rowHTML % bCheckboxRow 
    
    if doProminence:
        pCheckboxRow = "</td><td>".join(pCheckboxList)
        allRows += rowHTML % pCheckboxRow   
    
    html = '<table class="center">%s</table>' % allRows

    return html


def makeTogglableWord(testType, word, idNum, boundaryToken):
    
    tokenTxt = ""
    if boundaryToken != None:
        tokenTxt = """<span class="hidden">%s</span>""" % boundaryToken
    
    html = """
<label for="%(idNum)d">
                <input type="checkbox" name="%(testType)s" id="%(idNum)d" value="%(idNum)d"/>
                %(word)s""" + tokenTxt + """\n</label>\n\n"""

    return html % {"testType":testType,"word":word, "idNum":idNum}


def getTogglableWordEmbed(numWords, boundaryMarking):
    

    boundaryMarkingCode_showHide = """
            $("#"+x).closest("label").css({ borderRight: "3px solid #000000"});
            $("#"+x).closest("label").css({ paddingRight: "0px"});
    """
    
    boundaryMarkingCode_toggle = """    
    $(this).closest("label").css({ borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"});
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});"""
    if boundaryMarking != None:
        boundaryMarkingCode_toggle = """
        $(this).next("span").css({ visibility: this.checked ? "visible":"hidden"});
        """
        boundaryMarkingCode_showHide = """
        $("#"+x).next("span").css({ visibility: "visible"});
        """
    
    

    
    javascript = """
<script type="text/javascript" src="jquery.min.js"></script>
    
<script>
function ShowHide()
{
var didPlay = verifyFirstAudioPlayed();

if(didPlay == true) {
    document.getElementById("ShownDiv").style.display='none';
    document.getElementById("HiddenDiv").style.display='block';
    document.getElementById("HiddenForm").style.display='block';
    for (e=0;e<%(numWords)d;e++) {
        var x = e+%(numWords)d;

        if (document.getElementById(e).checked==true) {
%(boundaryMarkingCode_showHide)s
            }
        }
    }
}
</script>
    
<style type="text/css">
           /* Style the label so it looks like a button */
           label {
                border-right: 0px solid #FFFFFF;
                position: relative;
                z-index: 3;
                padding-right: 3px;
                padding-left: 3px;
           }
           /* CSS to make the checkbox disappear (but remain functional) */
           label input {
                position: absolute;
                visibility: hidden;
           }
</style>
    
    
<script>
$(document).ready(function(){
  $('input[type=checkbox]').click(function(){
    
    if (this.value < %(numWords)d)
    {
    /* Boundary marking */
%(boundaryMarkingCode_toggle)s
    }
    else
    {
    /* Prominence marking */
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    }
  });
});
</script>"""

    return javascript % {"numWords":numWords, "boundaryMarkingCode_toggle":boundaryMarkingCode_toggle,
                         "boundaryMarkingCode_showHide":boundaryMarkingCode_showHide}


def getProminenceOrBoundaryWordEmbed(isProminence):
    
    boundaryEmbed = """
    $(this).closest("label").css({ borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"});
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});
    """
    
    prominenceEmbed = """
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    """
    
    javascript = """
<script type="text/javascript" src="jquery.min.js"></script>

    
<style type="text/css">
           /* Style the label so it looks like a button */
           label {
                border-right: 0px solid #FFFFFF;
                position: relative;
                z-index: 3;
                padding-right: 3px;
                padding-left: 3px;
           }
           /* CSS to make the checkbox disappear (but remain functional) */
           label input {
                position: absolute;
                visibility: hidden;
           }
</style>
    
    
<script>
$(document).ready(function(){
  $('input[type=checkbox]').click(function(){
%s
  });
});
</script>
"""
    
    if isProminence:
        javascript %= prominenceEmbed
    else:
        javascript %= boundaryEmbed

    return javascript


def getProcessSubmitHTML(pageType):
    '''
    processSubmit() is a javascript function whose job is only to launch
    other javascript functions.  These functions need to be registered with
    a page in order to receive that functionality.
    '''
    
    baseHTML = """
<script  type="text/javascript">
function processSubmit()
{
calcDuration();
var returnValue = true;

%s
return returnValue;    
}
</script>
"""
    
    funcList = []
    # Ensure the subject has listened to all audio files
    if pageType in ['axb', 'prominence', 'boundary', 'boundary_and_prominence',
                    'oldProminence', 'oldBoundary', 'abn', 'audio_test']:
        funcList.append("verifyAudioPlayed")
        
    # Ensure all required forms have been filled out
    if pageType in ['login', 'login_bad_user_name', 'consent', 'audio_test', 'axb', 'ab', 'abn']:
        funcList.append("validateForm")
    
    htmlList = []
    for func in funcList:
        htmlList.append("returnValue = returnValue && %s();" % func)
    
    htmlTxt = "\n".join(htmlList)
    
    return baseHTML % htmlTxt


if __name__ == "__main__":
    loader.initTextDict("../english.txt")
    print firstPageErrorHTML()

