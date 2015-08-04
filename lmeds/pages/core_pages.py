'''
Created on Mar 1, 2014

@author: tmahrt

Core pages may appear in any LMEDS tests, regardless of what kind of
experiment it is.  Pages that provide information to users, get their
 user name or consent, error pages, etc.
'''

from os.path import join

from lmeds.pages import abstract_pages

from lmeds.io import loader
from lmeds.utilities import constants
from lmeds.code_generation import html
from lmeds.code_generation import audio

checkboxValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["radio"])==true)
    {
    alert("%s");
    return false;
    }
return true;
"""


class LoginPage(abstract_pages.NonRecordingPage):
    
    pageName = "login"
    
    def __init__(self, *args, **kargs):
        
        super(LoginPage, self).__init__(*args, **kargs)

        # Strings used in this page
        txtKeyList = ['experiment_header', 'title', 'back_button_warning',
                      'user_name_text', 'unsupported_warning',
                      'error_blank_name']
        self.textDict.update(loader.batchGetText(txtKeyList))

        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = ["validateForm", ]

    def _getHTMLTxt(self):
        txtBox = """<input type="text" name="%s" value=""/>"""
        productNote = "%s <br /><b><i>%s</i></b><br /><br />\n\n"
        productNote %= (self.textDict['experiment_header'],
                        constants.softwareName)
        
        title = '<div><p id="title">%s</p></div>\n\n' % self.textDict['title']
        
        backButtonWarning = self.textDict['back_button_warning']
        pg0HTML = self.textDict['user_name_text'] + "<br /><br />"
        pg0HTML += (txtBox % 'user_name_init') + "<br /><br />"
        pg0HTML += backButtonWarning
        
        unsupportedWarning = self.textDict['unsupported_warning']
         
        return productNote + title + pg0HTML + unsupportedWarning

    def getValidation(self):
        loginValidation = ('var y=document.forms["languageSurvey"];'
                           ''
                           'if (textBoxValidate(y["user_name_init"])==1)'
                           '{'
                           'alert("%s");'
                           'return false;'
                           '}'
                           'return true;'
                           )
        
        txt = self.textDict['error_blank_name']
        txt = txt.replace('"', "'")
        retPage = loginValidation % txt
        
        return retPage
        
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
    
        embedTxt = html.checkForAudioTag()
    
        return htmlText, pageTemplate, {'embed': embedTxt}


class LoginErrorPage(LoginPage):
    
    pageName = "login_bad_user_name"
        
    def __init__(self, userName, *args, **kargs):
        
        super(LoginErrorPage, self).__init__(*args, **kargs)
        
        self.userName = userName
        
        # Strings used in this page
        txtKeyList = ['error user name exists', ]
        self.textDict.update(loader.batchGetText(txtKeyList))
        
    def _getHTMLTxt(self):

        pg0HTML = super(LoginErrorPage, self)._getHTMLTxt()
        pg0HTML = pg0HTML
        
        textKey = 'error user name exists'
        userNameErrorTxt = self.textDict[textKey]
    
        if '%s' not in userNameErrorTxt:
            # A warning to the developer, not the user
            errorMsg = ("Please add a '%s' for the user name in the text "
                        "associated with this key")
            raise loader.BadlyFormattedTextError(errorMsg, textKey)
        
        pg0HTML += "<br />" + userNameErrorTxt
    
        return pg0HTML
    
    def getHTML(self):
        htmlText = self._getHTMLTxt() % self.userName
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
        
        return htmlText, pageTemplate, {}


class ConsentPage(abstract_pages.NonRecordingPage):
    
    pageName = "consent"
    
    def __init__(self, consentName, *args, **kargs):
        
        super(ConsentPage, self).__init__(*args, **kargs)
        
        if consentName is None:
            consentName = "text"
            
        self.consentName = consentName
    
        # Strings used in this page
        txtKeyList = ["title", "consent_title",
                      "consent_%s" % self.consentName,
                      "consent_query", "consent", "dissent",
                      'error_consent_or_dissent', ]
        self.textDict.update(loader.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = ["validateForm", ]
    
    def _getHTMLTxt(self):
        
        consentText = open(join(constants.htmlSnippetsDir, "consent.html"),
                           "r").read()
        consentText %= (self.textDict["title"],
                        self.textDict["consent_title"],
                        self.textDict["consent_%s" % self.consentName])
        
        consentText += "\n\n<hr /><br /><br />"
        consentText += self.textDict["consent_query"]
    
        consentButton = html.radioButton % "consent"
        dissentButton = html.radioButton % "dissent"
    
        consentButtonTxt = self.textDict["consent"]
        dissentButtonTxt = self.textDict["dissent"]
        consentChoice = '%s %s\n<br /><br />%s %s'
        consentChoice %= (consentButton, consentButtonTxt,
                          dissentButton, dissentButtonTxt)
    
        consentHTML = consentText + "<br /><br />" + consentChoice
        
        return consentHTML
    
    def getValidation(self):
        txt = self.textDict['error_consent_or_dissent']
        txt = txt.replace('"', "'")
        retPage = checkboxValidation % txt
        
        return retPage
    
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
    
        return htmlText, pageTemplate, {}

    
class ConsentEndPage(abstract_pages.NonValidatingPage):
    
    pageName = "consent_end"
    
    def __init__(self, *args, **kargs):

        super(ConsentEndPage, self).__init__(*args, **kargs)
    
        # Strings used in this page
        txtKeyList = ["consent_opt_out", ]
        self.textDict.update(loader.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def getHTML(self):
        htmlText = self.textDict['consent_opt_out']
        pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
    
        return htmlText, pageTemplate, {}


class TextPage(abstract_pages.NonValidatingPage):

    pageName = "text_page"
    
    def __init__(self, textName, *args, **kargs):

        super(TextPage, self).__init__(*args, **kargs)
        self.textName = textName
    
        # Strings used in this page
        txtKeyList = ['title', self.textName]
        self.textDict.update(loader.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def _getHTMLTxt(self):
        
        htmlText = ('<p id="title">'
                    '%s'
                    '</p><br /><br />'
                    ''
                    '<div id="longText">'
                    ''
                    '%s'
                    '</div><br />')

        htmlText %= (self.textDict['title'], self.textDict[self.textName])
        
        return htmlText

    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {}


class TextAndAudioPage(abstract_pages.NonValidatingPage):
    
    pageName = "text_and_audio_page"
    
    def __init__(self, textName, audioList, *args, **kargs):
        
        super(TextAndAudioPage, self).__init__(*args, **kargs)
        self.textName = textName
        self.audioList = audioList
        self.wavDir = self.webSurvey.wavDir
        
        # Strings used in this page
        txtKeyList = [self.textName, 'title']
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(loader.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        self.numAudioButtons = len(audioList)
        self.processSubmitList = []
    
    def getHTML(self):
    
        audioNameList = [name.strip() for name in self.audioList]
        audioButtonList = [audio.generateAudioButton(name, i, 0, False)
                           for i, name in enumerate(audioNameList)]
        
        tmpTxt = self.textDict[self.textName] % tuple(audioButtonList)
        htmlText = ('<p id="title">'
                    '%s'
                    '</p><br /><br />'
                    ''
                    '<div id="longText">'
                    ''
                    '%s'
                    ''
                    '</div><br />')
        htmlText %= (self.textDict['title'], tmpTxt)
        
        embedTxt = audio.getPlaybackJS(True, len(audioNameList), -1, 1)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, audioNameList)
        
        pageTemplate = join(constants.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class AudioTestPage(abstract_pages.NonRecordingPage):
    
    pageName = "audio_test"
    
    def __init__(self, wavName, *args, **kargs):
        super(AudioTestPage, self).__init__(*args, **kargs)
        self.wavName = wavName
        self.wavDir = self.webSurvey.wavDir
    
        # Strings used in this page
        txtKeyList = ["audioTest_text", "audioTest_affirm",
                      "audioTest_reject", 'error_verify_audio']
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(loader.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = ["validateForm", "verifyAudioPlayed"]
    
    def _getHTMLTxt(self):
        
        consentText = "\n\n<hr /><br /><br />"
        consentText += self.textDict["audioTest_text"]
    
        consentButton = html.radioButton % "consent"
        dissentButton = html.radioButton % "dissent"
    
        audioTestAffirm = self.textDict["audioTest_affirm"]
        audioTestReject = self.textDict["audioTest_reject"]
        consentChoice = '%s %s\n<br /><br />%s %s' % (consentButton,
                                                      audioTestAffirm,
                                                      dissentButton,
                                                      audioTestReject)
    
        consentHTML = consentText + "<br /><br />%s<br /><br />"
        consentHTML += consentChoice
    
        return consentHTML
    
    def getValidation(self):
        
        txt = self.textDict['error_verify_audio']
        txt = txt.replace('"', "'")
        retPage = checkboxValidation % txt
        
        return retPage
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
        
        htmlText %= audio.generateAudioButton(self.wavName, 0, 0, False)
        htmlText += "<br />"
        
        embedTxt = audio.getPlaybackJS(True, 1, -1, 1, listenPartial=True)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.wavName, ])
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class AudioTestEndPage(abstract_pages.NonValidatingPage):
    
    pageName = "audio_test_end"
    
    def __init__(self, *args, **kargs):
        super(AudioTestEndPage, self).__init__(*args, **kargs)
        
        # Strings used in this page
        txtKeyList = ['audioTest_no_audio', ]
        self.textDict.update(loader.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def getHTML(self):
        htmlText = self.textDict['audioTest_no_audio']
        pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
        
        return htmlText, pageTemplate, {}


class EndPage(abstract_pages.NonValidatingPage):
    
    pageName = "end"
    
    def __init__(self, *args, **kargs):
        super(EndPage, self).__init__(*args, **kargs)
        
        # Strings used in this page
        txtKeyList = ["test_complete"]
        self.textDict.update(loader.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
        
    def getHTML(self):
        htmlText = self.textDict['test_complete']
        pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
    
        return htmlText, pageTemplate, {}