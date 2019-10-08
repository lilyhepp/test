#---------pyppeteer.py

import sys,os
import random
import datetime
import asyncio
import traceback
from   pyppeteer        import *
from   pyppeteer.errors import *

sys.path.append("..")
sys.path.append(".")

from   log.logger     import *
from   struct_def     import *

#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
class PyteerEx(object):
    def __init__(self,logInfos,logExceptions):
        self.logInfo      = logInfos
        self.logException = logExceptions
        
    #-----------------------------------------------------------------
    #
    def printLogInfo(self,msg,level= LogLevel.Debug):
        if self.logInfo is not None:
            self.logInfo.show(msg)
    
    #-----------------------------------------------------------------
    #
    def printExcepInfo(self,msg):
        if self.logException is not None:
            self.logException.show(msg)
    
    #-----------------------------------------------------------------
    #
    async def get_cookie(self,page):
        cookies_list = await page.cookies()
        cookies = ''
        for cookie in cookies_list:
            str_cookie = '{}={}={};'
            str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'),cookie.get('url'))
            cookies += str_cookie
        self.printLogInfo(cookies)  

    #-----------------------------------------------------------------------------------------------------
    #
    async def closePage(self,page):
        if page is not None:
            try:
                await page.close()
            except  PageError as e:
                self.printExcepInfo("PyteerEx->closePage():exception->PageError ")
                self.printExcepInfo(e)
            except PyppeteerError as e:
                self.printExcepInfo("PyteerEx->closePage(): Exception = PyppeteerError")
                self.printExcepInfo(e)
            
                
    #-----------------------------------------------------------------------------------------------------
    #
    async def closeBrower(self,browser):
        if browser is not None:
            for _page in await browser.pages():
                try:
                    await _page.close()
                except  PageError as e:
                    self.printExcepInfo("PyteerEx->closeBrower():exception->PageError ")
                    self.printExcepInfo(e)
                    continue
                except PyppeteerError as e:
                    self.printExcepInfo("PyteerEx->closeBrower(): Exception = PyppeteerError")
                    self.printExcepInfo(e)
                    continue
    #-----------------------------------------------------------------------------------------------------
    #刷新当前页面
    async  def  refreshPage(self,page) :
        ret = RetVal.Fail.value
        try:
            await page.reload()
        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->refreshPage():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->refreshPage():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->refreshPage():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->refreshPage(): Exception = PyppeteerError")
            self.printExcepInfo(e)   
        return ret    
    #-----------------------------------------------------------------------------------------------------
    #输入文本
    async def inputText(self,page,selector,inputText,delayMin=15,delayMax=30) :
        
        ret,element = await self.getElement(page,selector)
        if ret == RetVal.Suc.value:
            try:
                await page.type(selector, inputText, {'delay': random.randint(delayMin, delayMax) })
            except  PageError as e:
                ret  = RetVal.ExceptPageError.value
                self.printExcepInfo("PyteerEx->inputText():exception->PageError ")
                self.printExcepInfo(e) 
            except PyppeteerError as e:
                self.printExcepInfo("PyteerEx->inputText(): Exception = PyppeteerError")
                self.printExcepInfo(e)
                  

        return ret
    
    #-----------------------------------------------------------------------------------------------------
    #查找关键字
    async def searchNavigate(self,objPage,searchText,strEditWndCss,strBtnWndCss,editDelayMin,editDelayMax,
                          waitTimeoutMs=20000,waitUntilList=["load","domcontentloaded"]) :
        
        self.printLogInfo("PyteerEx->searchNavigate():enter ")
        
        ret,element = await self.getElement(objPage,strEditWndCss)
        if ret != RetVal.Suc.value:
            return ret

        waitOption = {"timeout":waitTimeoutMs,"waitUntil":waitUntilList}
        ret = await self.inputText(objPage,strEditWndCss,searchText,editDelayMin,editDelayMax)
        if ret == RetVal.Suc.value:
           #time1 = datetime.datetime.now()
           ret = await self.dealClickNavigate(objPage,strBtnWndCss,waitOption)
           #self.printLogInfo("PyteerEx->searchNavigate():use time={}ms ".format((datetime.datetime.now()-time1).seconds))
        
        self.printLogInfo("PyteerEx->searchNavigate():exit ")
        
        return ret

    #-----------------------------------------------------------------------------------------------------
    #等待browser创建新page
    #delay:second
    #allPageNum: browser创建的page个数(包含新page)
    async def waitCreateNewPage(self,browser,allPageNum,delay):  

        ret      =  RetVal.Fail.value
        maxCount =  delay*10
        count    =   0
        pageBuf  =  []

        while  count < maxCount:
            count += 1
            pageBuf =  await browser.pages()

            if len(pageBuf) >= allPageNum:
                ret = RetVal.Suc.value
                break

            await asyncio.sleep(0.1)
        
        return ret,pageBuf
    #-----------------------------------------------------------------------------------------------------
    #查找关键字,在一个新的page中加载搜索结果
    async def searchNavigateNewPage(self,browser,page,searchText,strEditWndCss,strBtnWndCss,editDelayMin,editDelayMax,
                          waitTimeoutMs=20000,waitUntilList=["load","domcontentloaded"]) :
        
        self.printLogInfo("PyteerEx->searchNavigateNewPage():enter ")

        newPage = None
        ret     = RetVal.Fail.value
        pageBuf = []
        waitOption = {"timeout":waitTimeoutMs,"waitUntil":waitUntilList}

        while True:
            #----input text
            ret1 = await self.inputText(page,strEditWndCss,searchText,editDelayMin,editDelayMax)
            if ret1 != RetVal.Suc.value:
                break
            #----click button
            ret1 = await self.clickHoverElement(page,strBtnWndCss,1,1)
            if ret1 != RetVal.Suc.value:
                break

            #----wait new page
            ret1,pageBuf = await self.waitCreateNewPage(browser,2,10)
            if ret1 != RetVal.Suc.value:
                break

            self.printLogInfo("PyteerEx->searchNavigateNewPage():get a new page ")
            #----
            curCount = 0
            for item in pageBuf:
                curCount += 1

                if (curCount == len(pageBuf)) and (item != page):
                    self.printLogInfo("PyteerEx->searchNavigateNewPage():get a new page1 ")
                    newPage = item
                    ret = RetVal.Suc.value
                    break
            """
            #----
            if newPage is  None:
                break
            #----
            
            self.printLogInfo("PyteerEx->searchNavigateNewPage():get a new page3 ")
            done = await newPage.waitForNavigation(waitOption)
            self.printLogInfo("PyteerEx->searchNavigateNewPage():get a new page2 ")
            if done is not None:
                ret = RetVal.Suc.value
                break
            
            #----------------------------
            """
            break
        #------------------------------------------------------------
        self.printLogInfo("PyteerEx->searchNavigateNewPage():exit ")
        
        return ret,newPage
    #-----------------------------------------------------------------------------------------------------
    #出现页面更新的click
    async def clickNavigate(self,objPage,strBtnWndCss,waitTimeoutMs=20000,waitUntilList=["load","domcontentloaded"]) :

        self.printLogInfo("PyteerEx->clickNavigate():enter ")

        waitOption = {"timeout":waitTimeoutMs,"waitUntil":waitUntilList}

        #time1 =  datetime.datetime.now()
        ret   =  await self.dealClickNavigate(objPage,strBtnWndCss,waitOption)
        
        #self.printLogInfo("PyteerEx->clickNavigate():use time={}ms ".format((datetime.datetime.now()-time1).seconds))
        self.printLogInfo("PyteerEx->clickNavigate():exit ")
        
        return ret


    #-----------------------------------------------------------------------------------------------------
    #
    async def  dealClickNavigate(self,page,clkSelector,waitOption):

        self.printLogInfo("PyteerEx->dealClickNavigate():enter ")
        
        ret,element = await self.getElement(page,clkSelector)
        if ret != RetVal.Suc.value:
            return ret

        ret = RetVal.Fail.value
        
        finishCount  = 0
        try:
            done,pending = await asyncio.wait([
                                              page.waitForNavigation(waitOption),
                                              page.click(clkSelector),
                                              
                                             ])
        
            for doing in done: 
                if doing is not None:
                   finishCount += 1     
                   self.printLogInfo("PyteerEx->dealClickNavigate(): doing result={}".format(doing.result()))
             
            if finishCount > 0:
             ret = RetVal.Suc.value
         
        except  TimeoutError as e:
           ret = RetVal.ExceptTimeout.value
           self.printExcepInfo("PyteerEx->dealClickNavigate():exception = TimeoutError")
           self.printExcepInfo(e)

        except  PageError as e:
           ret = RetVal.ExceptPageError.value
           self.printExcepInfo("PyteerEx->dealClickNavigate():exception = PageError")
           self.printExcepInfo(e)
        except PyppeteerError as e:
           self.printExcepInfo("PyteerEx->dealClickNavigate(): Exception = PyppeteerError")
           self.printExcepInfo(e)   
       
        self.printLogInfo("PyteerEx->dealClickNavigate():exit ret={} finishcout={}".format(ret,finishCount))

        return ret

    #-----------------------------------------------------------------------------------------------------
    #等待page中单个元素出现,超时以秒为单位
    async  def  waitPage(self,ObjPage,strSelector:str,timeoutSec=5) :

        self.printLogInfo("PyteerEx->waitPage():enter ")
        
        ret = RetVal.Fail.value
        
        count   = timeoutSec + 1
        element = None
        while True:

            ret,element = await self.getElement(ObjPage,strSelector)
               
            if ret == RetVal.Suc.value:
                break
            elif ret > RetVal.ExceptElement.value:
                break
               
            if count <= 1:
               ret = RetVal.Fail.value
               self.printExcepInfo("PyteerEx->waitPage():time out")
               break
           
            count -=1
            await asyncio.sleep(1)
        
        self.printLogInfo("PyteerEx->waitPage():exit ")

        return ret
    #-----------------------------------------------------------------------------------------------------
    #等待page中多个元素的某一个出现，
    async  def  waitPageAll(self,ObjPage,selectList,timeoutSec=5) :

        self.printLogInfo("PyteerEx->waitPageAll():enter ")
        
        ret = RetVal.Fail.value
        
        isBreak = 0
        count   = timeoutSec + 1
        element = None

        while True:
            isBreak = 0
            
            for cssItem in selectList:
                ret,element = await self.getElement(ObjPage,cssItem)

                if ret == RetVal.Suc.value:
                    isBreak = 1
                    break
                elif ret > RetVal.ExceptElement.value:
                    isBreak = 0
                    continue
                   
            if isBreak == 1:
                break

            if count <= 1:
                ret = RetVal.Fail.value
                self.printExcepInfo("PyteerEx->waitPageAll():time out")
                break
           
            count -=1
            await asyncio.sleep(1)
        
        self.printLogInfo("PyteerEx->waitPageAll():exit ")

        return ret
    
    #------------------------------------------------------------------------------------------------------
    #滚动到底部
    async  def  scroolBottom(self,ObjPage) -> int:

        self.printLogInfo("PyteerEx->scroolBottom():enter ")
        
        ret = RetVal.Suc.value
        try:
            height     = await ObjPage.evaluate('document.body.clientHeight') 
            top        = await ObjPage.evaluate('document.documentElement.scrollTop')
            lastpos = top
            newpos  = height
            await ObjPage.evaluate(f'window.scrollTo({lastpos},{newpos})')  
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->scroolBottom(): Exception")
            self.printExcepInfo(e)

        self.printLogInfo("PyteerEx->scroolBottom():exit ")

        return ret
    
    #------------------------------------------------------------------------------------------------------
    #滚动到顶部
    async  def  scroolTop(self,ObjPage) -> int:

        self.printLogInfo("PyteerEx->scroolTop():enter ")
        
        ret = RetVal.Suc.value
        try:
            #height     = await ObjPage.evaluate('document.body.clientHeight') 
            top        = await ObjPage.evaluate('document.documentElement.scrollTop')
            lastpos = top
            newpos  = 0
            await ObjPage.evaluate(f'window.scrollTo({lastpos},{newpos})')  
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->scroolTop(): Exception")
            self.printExcepInfo(e)

        self.printLogInfo("PyteerEx->scroolTop():exit ")

        return ret
    
    #------------------------------------------------------------------------------------------------------
    #
    async  def  forbidInfoJs(self,ObjPage):
        
        self.printLogInfo("PyteerEx->forbidInfoJs():enter ")
        ret = RetVal.Suc.value

        try:
           await ObjPage.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
           await ObjPage.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
           await ObjPage.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
           await ObjPage.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
           
         #await ObjPage.evaluate('navigator.webdriver')
        except PyppeteerError as e:
           ret = RetVal.ExceptPyppeteer.value
           self.printExcepInfo("PyteerEx->forbidInfoJs(): Exception")
           self.printExcepInfo(e)
        
        self.printLogInfo("PyteerEx->forbidInfoJs():exit ")

        return ret
    #------------------------------------------------------------------------------------------------------
    #          
    async  def  forbidInfoJsEx(self,ObjPage): 

        self.printLogInfo("PyteerEx->forbidInfoJsEx():enter ")

        ret = RetVal.Suc.value

        try:
           await ObjPage.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                              '{ webdriver:{ get: () => false } }) }')
        except PyppeteerError as e:
           ret = RetVal.ExceptPyppeteer.value
           self.printExcepInfo("PyteerEx->forbidInfoJsEx(): Exception")
           self.printExcepInfo(e)
        
        self.printLogInfo("PyteerEx->forbidInfoJsEx():exit ")

        return ret    
    #-----------------------------------------------------------------------------------------------------
    #---获取滚动条当前的位置
    async def getScrollCurPos(self,page):
        
        scrollTop = 0
        ret = RetVal.Suc.value
        #document.documentElement.scrollTop
        #document.body.scrollTop
        try:
            scrollTop = await page.evaluate('document.documentElement.scrollTop')
            scrollTop = int(scrollTop)
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getScrollCurPos(): Exception")
            self.printLogInfo("PyteerEx->getScrollCurPos(): Exception ",LogLevel.Fail)
            scrollTop = 0
        
        return ret,scrollTop   
    #-----------------------------------------------------------------------------------------------------
    #---获取滚动条是否已滑动到底
    async def getScrollIsBottom(self,page):

        ret = RetVal.Fail.value

        try:
            scrollTop    = await page.evaluate('document.documentElement.scrollTop')
            scrollBottom = await page.evaluate('document.body.scrollHeight')
            self.printLogInfo("PyteerEx->getScrollCurPos(): scrollTop={} scrollBottom={} ".format(scrollTop,scrollBottom))
            if scrollTop >= scrollBottom:
                ret = RetVal.Suc.value

        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getScrollIsBottom(): Exception")
            self.printLogInfo("PyteerEx->getScrollIsBottom(): Exception ",LogLevel.Fail)
        
        return ret

    #------------------------------------------------------------------------------------------------------
    #自动滚动-从顶到底
    async  def  autoScroll(self,page,oneStep = 50) -> int:

        self.printLogInfo("PyteerEx->scrollAuto():enter ")

        ret = RetVal.Suc.value
        try:

            await page.evaluate('''async(oneStep) => {
                                    await new Promise((resolve,reject)=> {
                                    let totalHeight = 0;
                                    let  distance = oneStep;

                                    let  timer = setInterval( () => {
                                        let scrollHeight = document.body.scrollHeight;
                                        if(totalHeight <= 0)
                                        { window.scrollTo(0,0); }
                                        window.scrollBy(0,distance);
                                        totalHeight += distance;
                                        if(totalHeight >= scrollHeight){
                                            clearInterval(timer);
                                            resolve();
                                        }

                                    },100);

                                });

                               }''',oneStep)
           
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->scrollAuto(): Exception")
            self.printExcepInfo(e)

        self.printLogInfo("PyteerEx->scrollAuto():exit ")

        return ret
    #------------------------------------------------------------------------------------------------------
    #自动滚动-从当前位置到底
    """
    if (totalHeight >distance)
                                    { totalHeight = totalHeight-distance;  }
                                    else
                                    { totalHeight = 0; }
    """
    async  def  autoScrollCur(self,page,oneStep = 50) -> int:

        self.printLogInfo("PyteerEx->scrollAutoCur():enter ")

        ret = RetVal.Suc.value
        try:

            await page.evaluate('''async(oneStep) => {
                                    await new Promise((resolve,reject)=> {
                                    let  totalHeight = document.documentElement.scrollTop;
                                    let  distance = oneStep;
                                    let scrollHeight = document.body.scrollHeight;
                                    

                                    let  timer = setInterval( () => {
                                        if(totalHeight <= 0)
                                        { window.scrollTo(0,0); }
                                        window.scrollBy(0,distance);
                                        totalHeight += distance;
                                        if(totalHeight >= scrollHeight){
                                            clearInterval(timer);
                                            resolve();
                                        }

                                    },100);

                                });

                               }''',oneStep)
           
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->scrollAutoCur(): Exception")
            self.printExcepInfo(e)

        self.printLogInfo("PyteerEx->scrollAutoCur():exit ")

        return ret

    #------------------------------------------------------------------------------------------------------
    #---移动指针到指定的元素 -已找到元素
    async  def  hovers(self,ObjElement,delay=1) -> int:

        self.printLogInfo("PyteerEx->hovers():enter ")

        ret = RetVal.Fail.value

        try:
            if ObjElement is not None:
                
                await ObjElement.hover()
                if delay > 0:
                    await asyncio.sleep(delay)
                ret = RetVal.Suc.value

        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->hovers():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->hovers():exception = PageError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptPageError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->hovers(): Exception = PyppeteerError")
            self.printExcepInfo(e)
            
        
        self.printLogInfo("PyteerEx->hovers():exit ")

        return ret
    #------------------------------------------------------------------------------------------------------
    #---需要判断元素是否存在
    #@staticmethod
    async  def  hoverElement(self,ObjElement,selector,delay) -> int:
        
        self.printLogInfo("PyteerEx->hoverElement():enter ")
        
        ret = RetVal.Fail.value

        try:
            element = await ObjElement.querySelector(selector)
            if element is not None:
                
                await element.hover()
                if delay > 0:
                    await asyncio.sleep(delay)
                ret = RetVal.Suc.value

        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->hoverElement():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->hoverElement():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->hoverElement():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->hoverElement(): Exception = PyppeteerError")
            self.printExcepInfo(e)
        
        self.printLogInfo("PyteerEx->hoverElement():exit ")

        return ret

    #------------------------------------------------------------------------------------------------------
    #---移到指定元素上，并click
    async  def  clickHoverElement(self,ObjElement,selector,clickDelay=1,hoverDelay=1) -> int:
        
        self.printLogInfo("PyteerEx->clickHoverElement():enter ")

        ret  = RetVal.Fail.value

        try:
            element = await ObjElement.querySelector(selector)
            if element is not None:
                
                await element.hover()
                
                if hoverDelay > 0:
                    await asyncio.sleep(hoverDelay)
                
                #click
                await element.click()
                
                if clickDelay > 0:
                    await asyncio.sleep(clickDelay)

                ret = RetVal.Suc.value
                
        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->clickHoverElement():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->clickHoverElement():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->clickHoverElement():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->clickHoverElement(): Exception = PyppeteerError")
            self.printExcepInfo(e)
        
        self.printLogInfo("PyteerEx->clickHoverElement():exit ")

        return ret
    
    #------------------------------------------------------------------------------------------------------
    #------模拟点击------这个方法假定元素已存在，当异常时，重试,
    #------只针对element对象,
    async  def  click(self,ObjElement) -> int:

        self.printLogInfo("PyteerEx->click():enter ")

        count = 3
        ret   = RetVal.Fail.value

        while count > 0:
            count -= 1
            try:
                if ObjElement is not None:
                    await ObjElement.click()
                    ret = RetVal.Suc.value
                    break

            except  ElementHandleError as e:
                self.printExcepInfo("PyteerEx->click():exception = ElementHandleError")
                self.printExcepInfo(e)
                ret = RetVal.ExceptElement.value
                continue
            except  PageError as e: 
                self.printExcepInfo("PyteerEx->click():exception = PageError")
                self.printExcepInfo(e)
                ret = RetVal.ExceptPageError.value
                break
            except  NetworkError as e:
                self.printExcepInfo("PyteerEx->clickHoverElement():exception = NetworkError")
                self.printExcepInfo(e)
                ret = RetVal.ExceptNetError.value
            except PyppeteerError as e:
                ret = RetVal.ExceptPyppeteer.value
                self.printExcepInfo("PyteerEx->click(): Exception=PyppeteerError")
                self.printExcepInfo(e)
                break

            self.printExcepInfo("PyteerEx->click():click repeat={}".format(count))
         
        self.printLogInfo("PyteerEx->click():exit ")

        return ret
    

    #------------------------------------------------------------------------------------------------------
    #---模拟点击------需要判断元素是否存在
    async  def  clickElement(self,ObjElement,selector) -> int:

        self.printLogInfo("PyteerEx->clickElement():enter ")

        count = 3
        ret   = RetVal.Fail.value
        while count > 0:
            count -= 1
            try:
                elementSub  = await  ObjElement.querySelector(selector)

                if elementSub is not None:
                    await elementSub.click()
                    ret  = RetVal.Suc.value
                    break
                else:
                    continue

            except  ElementHandleError as e:
                self.printExcepInfo("PyteerEx->clickElement():exception = ElementHandleError")
                self.printExcepInfo(e)
                ret  = RetVal.ExceptElement.value
                continue
            except  PageError as e: 
                self.printExcepInfo("PyteerEx->clickElement():exception = PageError")
                self.printExcepInfo(e)
                ret  =  RetVal.ExceptPageError.value
                break
            except  NetworkError as e:
                self.printExcepInfo("PyteerEx->clickElement():exception = NetworkError")
                self.printExcepInfo(e)
                ret = RetVal.ExceptNetError.value
                break
            except PyppeteerError as e:
                ret = RetVal.ExceptPyppeteer.value
                self.printExcepInfo("PyteerEx->clickElement(): Exception = PyppeteerError")
                self.printExcepInfo(e)
                break
           
        self.printLogInfo("PyteerEx->clickElement():exit ")

        return ret
    #------------------------------------------------------------------------------------------------------
    #---click元素并延迟
    async  def  clickElementDelay(self,ObjElement,selector,delay,isRepeat=False) -> int:
        
        self.printLogInfo("PyteerEx->clickElementDelay():enter ")

        count = 3
        ret   = RetVal.Fail.value
        
        while count > 0:
            count -= 1
            try:
                elementSub  = await  ObjElement.querySelector(selector)
                if elementSub is not None:
                    await elementSub.click()
                    ret  = RetVal.Suc.value
                    break
                else:
                    if isRepeat:
                        continue
                    else:
                        break
            
            except  ElementHandleError as e:
                self.printExcepInfo("PyteerEx->clickElement():exception = ElementHandleError")
                self.printExcepInfo(e)
                ret  = RetVal.ExceptElement.value
                continue
            except  PageError as e: 
                self.printExcepInfo("PyteerEx->clickElement():exception = PageError")
                self.printExcepInfo(e)
                ret  =  RetVal.ExceptPageError.value
                break
            except  NetworkError as e:
                self.printExcepInfo("PyteerEx->clickElement():exception = NetworkError")
                self.printExcepInfo(e)
                ret = RetVal.ExceptNetError.value
                break
            except PyppeteerError as e:
                ret = RetVal.ExceptPyppeteer.value
                self.printExcepInfo("PyteerEx->clickElement(): Exception = PyppeteerError")
                self.printExcepInfo(e)
                break

        if ret == RetVal.Suc.value and delay > 0:
            await asyncio.sleep(delay)
        
        self.printLogInfo("PyteerEx->clickElementDelay():exit ")

        return ret
    
    #------------------------------------------------------------------------------------------------------
    # load, domcontentloaded,networkidle0,networkidle2
    async  def  gotoUrl(self,ObjPage,url,timeoutSec,strWaitUntill) -> int:

        self.printLogInfo("PyteerEx->gotoUrl():enter ")

        ret = RetVal.Fail.value
        option = {"timeout":timeoutSec,"waitUntil":strWaitUntill }
        
        try:
            element = await ObjPage.goto(url,option)
            if element is not None:
                ret = RetVal.Suc.value

        except PageError as e:
            self.printExcepInfo("PyteerEx->gotoUrl():exception = PageError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptPageError.value
            #traceback.print_exc()
        except PyppeteerError as e:
                ret = RetVal.ExceptPyppeteer.value
                self.printExcepInfo("PyteerEx->gotoUrl(): Exception = PyppeteerError")
                self.printExcepInfo(e)
                
        self.printLogInfo("PyteerEx->gotoUrl():exit ")

        return ret

    #------------------------------------------------------------------------------------------------------
    #
    async  def  navigateUrl(self,ObjPage,timeoutSec) -> int:
        
        self.printLogInfo("PyteerEx->navigateUrl():enter ")

        ret = RetVal.Fail.value
        try:
            element = await ObjPage.waitForNavigation()
            if not element is None:
                ret = RetVal.Suc.value
        except PageError as e:
            self.printExcepInfo("PyteerEx->navigateUrl():exception = PageError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptPageError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->navigateUrl(): Exception = PyppeteerError")
            self.printExcepInfo(e)
            
        
        self.printLogInfo("PyteerEx->navigateUrl():exit ")

        return ret
    
    #------------------------------------------------------------------------------------------------------
    #
    async  def  getPropertyJs(self,jsHandle,propertyName) :
        
        self.printLogInfo("PyteerEx->getPropertyJs():enter ")

        ret = RetVal.Fail.value
        strPorperty = ""

        try:
            item = await jsHandle.getProperty(propertyName)
            if item is not None:
                strPorperty = await item.jsonValue()
                ret = RetVal.Suc.value
        except PageError as e:
            self.printExcepInfo("PyteerEx->getPropertyJs():exception = PageError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptPageError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getPropertyJs(): Exception = PyppeteerError")
            self.printExcepInfo(e)
        
        self.printLogInfo("PyteerEx->getPropertyJs():exit ")

        return ret,strPorperty
    
    #------------------------------------------------------------------------------------------------------
    #---查找指定的元素
    #---主要用于判断page,当异常或找不到时，重试
    async  def  findElement(self,ObjElement,strCssValue,loop=3) :
        
        self.printLogInfo("PyteerEx->findElement():enter ")

        ret     = RetVal.Fail.value
        element = None
        count   = loop

        while count > 0:
            count -= 1
            try:
                element = await ObjElement.querySelector(strCssValue)
                if element is not None:
                    ret = RetVal.Suc.value
                    break
            except  ElementHandleError as e:
                self.printExcepInfo("PyteerEx->findElement():exception = ElementHandleError")
                self.printExcepInfo(e)
                self.printLogInfo("PyteerEx->findElement():exception = ElementHandleError")
                ret  = RetVal.ExceptElement.value
                continue
            except  PageError as e: 
                self.printExcepInfo("PyteerEx->findElement():exception = PageError")
                self.printExcepInfo(e)
                self.printLogInfo("PyteerEx->findElement():exception = PageError")
                ret  =  RetVal.ExceptPageError.value
                break
            except  NetworkError as e:
                self.printExcepInfo("PyteerEx->findElement():exception = NetworkError")
                self.printLogInfo("PyteerEx->findElement():exception = NetworkError")
                self.printExcepInfo(e)
                ret = RetVal.ExceptNetError.value
                break
            except PyppeteerError as e:
                ret = RetVal.ExceptPyppeteer.value
                self.printExcepInfo("PyteerEx->findElement(): Exception = PyppeteerError")
                self.printLogInfo("PyteerEx->findElement(): Exception = PyppeteerError")
                self.printExcepInfo(e)
                break

            await asyncio.sleep(1)
        
        self.printLogInfo("PyteerEx->findElement():exit ")

        return ret

    #------------------------------------------------------------------------------------------------------
    #获取指定的element
    async  def  getElement(self,ObjElement,strCssValue) :
        
        ret     = RetVal.Fail.value
        element = None

        try:
            element = await ObjElement.querySelector(strCssValue)
            if not element is None:
                ret = RetVal.Suc.value
        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->getElement():exception = ElementHandleError")
            self.printLogInfo("PyteerEx->getElement():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->getElement():exception = PageError")
            self.printLogInfo("PyteerEx->getElement():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->getElement():exception = NetworkError")
            self.printLogInfo("PyteerEx->getElement():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getElement(): Exception = PyppeteerError")
            self.printLogInfo("PyteerEx->getElement():exception = PyppeteerError")
            self.printExcepInfo(e)
                
        return ret,element
    
    #------------------------------------------------------------------------------------------------------
    #
    async  def  getElementAll(self,ObjElement,strCssValue) :

        ret         = RetVal.Fail.value
        elementList = []

        try:
            elementList = await ObjElement.querySelectorAll(strCssValue)
            if len(elementList) > 0:
                ret = RetVal.Suc.value
        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->getElementAll():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->getElementAll():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->getElementAll():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getElement(): Exception = PyppeteerError")
            self.printExcepInfo(e)
                
        return ret,elementList
  
    #------------------------------------------------------------------------------------------------------
    #获取指定的href链接
    async  def  getElementHref(self,page,strCssValue="") :
        ret,val = await self.getElementProperty(page,"href",strCssValue)
        return ret,val

    #------------------------------------------------------------------------------------------------------
    #获取文本
    async  def  getElementContext(self,page,strCssValue="") :
        ret,val = await self.getElementProperty(page,"textContent",strCssValue)
        return ret,val
    
    #------------------------------------------------------------------------------------------------------
    #获取id值
    async  def  getElementId(self,page,strCssValue="") :
        ret,val = await self.getElementProperty(page,"id",strCssValue)
        return ret,val
    
    #------------------------------------------------------------------------------------------------------
    #获取指定的属性
    # strCssValue是空字符串时，表示获取对象本身的属性
    async  def  getElementProperty(self,page,strProperty,strCssValue) :

        ret = RetVal.Fail.value
        retProperty = ""
        element = None

        try:
            if len(strCssValue) > 0:
                element  = await page.querySelector(strCssValue )
            else:
                element  = page
            

            if element is not None:
                item = await element.getProperty(strProperty)       
                if item is not None:
                    retProperty = await item.jsonValue()
                    if retProperty is not None:
                        ret = RetVal.Suc.value
                    else:
                        ret = RetVal.Fail.value
                        retProperty = ""
                        

        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->getElementProperty():exception = ElementHandleError")
            self.printLogInfo("PyteerEx->getElementProperty():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->getElementProperty():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->getElementProperty():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getElementProperty(): Exception = PyppeteerError")
            self.printExcepInfo(e)
        
        return ret,retProperty

    #------------------------------------------------------------------------------------------------------
    #获取自定义的属性
    # strCssValue是空字符串时，表示获取对象本身的属性
    async  def  getElementProDef(self,page,elementSub,strProperty,strCssValue="") :
        
        ret          = RetVal.Fail.value
        propertyVal  = ""
        element      = None
        strEva       = ' (els) => els.getAttribute("{}") '.format(strProperty)
        

        try:
            if len(strCssValue) > 0:
                element  = await elementSub.querySelector(strCssValue )
            else:
                element  = elementSub
            

            if element is not None:
                propertyVal = await page.evaluate(strEva ,element) 
                ret = RetVal.Suc.value

        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->getElementProDef():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->getElementProDef():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->getElementProDef():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getElementProDef(): Exception = PyppeteerError")
            self.printExcepInfo(e)
        
        return ret,propertyVal

    #------------------------------------------------------------------------------------------------------
    #获取全部定义的属性
    # strCssValue是空字符串时，表示获取对象本身的属性
    async  def  getElementAllProDef(self,page,elementSub,strProperty,strCssValue) :
        
        ret = RetVal.Fail.value
        propertyBuf  = []
        element      = None
        strEva       = ' (els) => els.getAttribute("{}") '.format(strProperty)
        
        try:
            elementList = await elementSub.querySelectorAll(strCssValue )
            
            for item in elementList:
                propertyVal = await page.evaluate(strEva ,item) 
                propertyBuf.append(propertyVal )

        except  ElementHandleError as e:
            self.printExcepInfo("PyteerEx->getElementAllProDef():exception = ElementHandleError")
            self.printExcepInfo(e)
            ret  = RetVal.ExceptElement.value
        except  PageError as e: 
            self.printExcepInfo("PyteerEx->getElementAllProDef():exception = PageError")
            self.printExcepInfo(e)
            ret  =  RetVal.ExceptPageError.value
        except  NetworkError as e:
            self.printExcepInfo("PyteerEx->getElementAllProDef():exception = NetworkError")
            self.printExcepInfo(e)
            ret = RetVal.ExceptNetError.value
        except PyppeteerError as e:
            ret = RetVal.ExceptPyppeteer.value
            self.printExcepInfo("PyteerEx->getElementAllProDef(): Exception = PyppeteerError")
            self.printExcepInfo(e)
        
        if len(propertyBuf) > 0:
            ret = RetVal.Suc.value

        return ret,propertyBuf
    