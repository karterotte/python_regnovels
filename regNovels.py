#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-12-11 09:08:19
# @Author  : Richard 
# @Link    : katerotte@gmail.com
# @Version : $2.0$
# @Function: Type set novels

import os
import sys
import re
import glob
import codecs
import inspect
from  xml.dom import  minidom

import re
import time
incode='utf8'
outcode='gbk'#'utf8'
try:
    import chardet
    from chardet.universaldetector import UniversalDetector
except ImportError:
    print u"需要安装模块'chardet'，否则txt文件编码检测可能不正确".encode(outcode)

try:
    import zh_wiki,langconv
except ImportError:
    print u"需要下载文件'zh_wiki.py'，'langconv.py',否则无法进行繁简转换".encode(outcode)

checkbianma=0#设为1使用chardet自动检测文章编码，非常耗时;
cataindex=1
catadict={}

def typenum_deco(func):
    def wrapper(cls):
        strcolock=round(time.clock(),3)
        res=func(cls)
        seccolock=round(time.clock(),3)-strcolock
        ss=u"-››%s调整数目：%s\t耗时：%ss"%(func.func_doc.ljust(13),str(res).ljust(5),"%.3f"%seccolock)
        print ss.encode(outcode,'ignore')
        return res
    return wrapper
def checkcode(checkobj):
    '''判断读取文章的编码'''
    if not 'chardet' in sys.modules or checkbianma==0:
        return 'mbcs'#默认只能编辑gbk/mbcs的文章，utf8的会出错
    code=''
    if (isinstance(checkobj,file)):
        detector=UniversalDetector()
        for line in checkobj.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        checkobj.close()
        code=detector.result["encoding"]
    elif (os.path.isfile(checkobj)):
        f=open(checkobj)
        code=checkcode(f)
    elif (isinstance(checkobj,str)):
        code=chardet.detect(checkobj)["encoding"]
    else:
        pass
    if code=="GB2312":
        code='mbcs'
    return code

class Novel_Input:

    def __init__(self):
        self._inputpath=""
        self._pathtype=0
        self._filepath=""
        self._folderpath=""

    def inputNovels(self):
        self.__init__()
        welcomestr=u'''\n欢迎使用txt小说排版系统，请输入数字以使用对应功能:
        1. 开始排版小说...
        2. 输出设置文件以进行配置（第一次运行程序时建议使用）...
        0. 退出程序\n'''
        while True:
            ans=raw_input(welcomestr.encode(outcode))
            if ans=='1':
                while True:
                    inputpath=""
                    inputpath=raw_input(u'请拖放或输入路径（txt文件或文件夹），或输入0（零）结束...\n'.encode(outcode))
                    if inputpath=='0':
                        break
                    if(inputpath.startswith('\"') and inputpath.endswith('\"')):
                        inputpath=inputpath[1:-1]
                    check=self.checkpath(inputpath)
                    if(check==0):
                        print u"路径可能含有空格或不正确，输入0（零）返回菜单...\n".encode(outcode)
                    else:
                        self._inputpath=inputpath
                        self._pathtype= check
                        if check==1:
                            self._filepath=inputpath
                        elif check==2:
                            self._folderpath=self._inputpath
                        break
                break    
            elif ans=='2':
                print 'wait...'
                con=RegexConfig()
                con.makeconfig()
            elif ans=='0':
                print 'see you...'
                return 0
            else:
                print 'Oh no!'
                continue

    def checkpath(self,inputpath):
        check=0
        if os.path.isfile(inputpath):
            if(os.path.splitext(inputpath)[1]=='.txt'):      
                check=1
            else:
                print 'need .txt format file... '
                check=0
        elif os.path.isdir(inputpath):
            check=2
        else:
            check=0
        return check

    def getnovels(self):
        if self._pathtype==1:
            return [self._filepath]
        elif self._pathtype==2:
            pathstr=os.path.join(self._folderpath,"*.txt")
            return glob.glob(pathstr)
        else:
            return []
class RegexConfig:
    u"""docstring for regexConfig """
    def __init__(self):
        self.configdict={
        u"编码检测":u"N",
        u"标点":u"半角",
        u"目标编码":u"GB",
        u"繁简体":u"简体",
        u"软回车删除":u"Y",
        u"段首空格":u"4",
        u"段间空行":u"1",
        u"非结段字符":ur"，「“；",
        u"非开段字符":ur"，：；！。？…·）」”～—",
        u"章节标识":u"Y",
        u"去除代码广告":u"Y"
        }
        self.refresh()
    def getcurrentpath(self):
        caller_file=os.path.split(inspect.stack()[1][1])[0]
        configpath=os.path.join(caller_file,'TypeSetConfig.xml')
        return configpath
    def refresh(self):
        configpath=self.getcurrentpath()
        if os.path.exists(configpath):
            try:
                self.readconfig(configpath)
            except Exception, e:
                print e
        else:
            ss= u"%s 文件不存在，采用默认设置"%configpath
            print ss.encode(outcode)
    def readconfig(self,path):
        doc = minidom.parse(path) 
        root = doc.documentElement
        itemnodes=root.getElementsByTagName('Config')
        if len(itemnodes)<1:
            ss= u"%s 文件格式不正确，请重新生成"%configpath
            print ss.encode(outcode)
            return 0
        config=itemnodes[0]
        for node in config.childNodes:#读取均为Unicode
            if node.nodeType == node.ELEMENT_NODE:
                name=node.nodeName
                value=node.childNodes[0].nodeValue
                dict={name:value}
                self.configdict.update(dict)
        if self.configdict[u"编码检测"]==u'Y':
            global checkbianma
            checkbianma=1
            print u'开启编码检测'.encode(outcode)
        ss= u"%s 配置文件加载成功"%config.getAttribute('Name')
        print ss.encode(outcode)
    def makeconfig(self):
        defaultstr='''<?xml version="1.0" encoding="utf-8"?>
        <TypeSetConfig>
          <Config Name="YY">
            <编码检测>N</编码检测><!-- 默认只能排版ANSI编码的txt，设置此项为Y则可以自动分辨UTF8及ANSI，但会显著降低排版速度 -->
            <标点>全角</标点>
            <目标编码>GB</目标编码>
            <繁简体>简体</繁简体>
            <软回车删除>Y</软回车删除>
            <段首空格>6</段首空格>
            <段间空行>1</段间空行>
            <非结段字符>，「“；</非结段字符>
            <非开段字符>，：；！。？…·）」”～—</非开段字符>
            <章节标识>N</章节标识><!-- 设置此项为Y则会在生成的文件开始处添加章节列表 -->
            <去除代码广告>Y</去除代码广告>
          </Config>
        </TypeSetConfig>'''
        configpath=self.getcurrentpath()
        f1=codecs.open(configpath,'w')
        f1.write(defaultstr)
        f1.close()
        print u"生成配置文件成功，若修改配置需要重新启动程序...".encode(outcode)
class Novel_Info:
    u"""docstring for novelInfo"""
    def __init__(self, novelpath):
        self.path = novelpath
        self.title=""
        self.size=""
        self.filecode=""
        self.content=""
        self.catalog=""
        self.readinfo()
        self.readfile()
    def readinfo(self):
        info=os.stat(self.path)
        self.title=os.path.split(os.path.splitext(self.path)[0])[1]
        self.size="%sKB"%int(info.st_size/1024)
        self.filecode=checkcode(self.path)
        print self.title,self.size,self.filecode
    def readfile(self):
        f=codecs.open(self.path,'rU')
        #读取文件，\r\n会统一替换为\n
        try:
            self.content=f.read()
            #这个步骤不可缺少，否则正则表达式无法匹配
            #读取ANSI文件内容，先转成mbcs或gbk的unicode，再转成utf8字符串（因为程序脚本的正则匹配字符串是utf8）
            self.content=self.content.decode(self.filecode)#.encode(incode)
        except Exception as e:
            raise e
        finally:
            f.close()
class DoTypeSet:
    """docstring for doTypeSet"""
    def __init__(self, regexconfig,novelinfo,output=None):
        self.config = regexconfig.configdict
        self.novel=novelinfo
        self.output=""
        self.catalog=""
        self.result=novelinfo.content
    def dotypeset(self):
        func01(self)
        func02(self)
        func03(self)
        func04(self)
        func05(self)
        func06(self)
        func07(self)
        # 
        func01fix(self)
    def doconvert(self,target='SimpleChinese'):
        if target=='SimpleChinese':
            self.result=langconv.Converter('zh-hans').convert(self.result)
        elif target=='TraditionChinese':
            self.result=langconv.Converter('zh-hant').convert(self.result)
        else:
            pass
    def makefile(self):
        base,fname=os.path.split(self.novel.path)
        if self.output is None or self.output=="":
            self.output=os.path.join(base,'fixed')
        if not os.path.exists(self.output):
            os.mkdir(self.output)
        self.output=os.path.join(self.output,fname)
        print "outputPath:%s "%self.output
        f1=codecs.open(self.output,'w',incode)
        if self.config[u"章节标识"]==u"Y":
            f1.write(self.catalog+'\r\n')
        f1.write(self.result)
        f1.close()

@typenum_deco
def func01(cls):
    u'''提取文章章节名'''
    patternobj=re.compile(ur'^[\s　]*(第.*[章节卷集].*$|^序章.*$)',re.M)
    res=patternobj.findall(cls.result)
    for item in res:
        #匹配得到的字符串是unicode，再转成mbcs或gbk输出（cmd为此格式）(IDE需要转成utf8)
        if len(item)>50:
            continue
        result=item
        print result.encode(outcode)
        cls.catalog+=result+"\r\n"
    #先进行替换处理，避免后续正则修改章节名称格式
    result = patternobj.sub(func01sp, cls.result)
    cls.result=result
    return len(res)
def func01sp(matchobj):#只接受一个match实例参数，如何能增加更多参数？
    global cataindex,catadict
    key=u"<cata%s>"%cataindex
    value=matchobj.group(1)
    catadict.update({key:value})
    cataindex+=1
    return key#需要返回一个被替换的字符串
def func01fix(cls):
    u'''恢复章节名称'''
    global catadict
    for item in catadict.keys():
        patternobj=re.compile(item,re.M)
        result = patternobj.sub('\r\n'+catadict[item], cls.result)
        cls.result=result
@typenum_deco
def func02(cls):
    u'''删除软回车调整'''
    chars=cls.config[u"非开段字符"]
    chare=cls.config[u"非结段字符"]
    #python的中文范围需要特别加注ur
    pattern =ur'''
    (?<=[\u4e00-\u9fa5]|[非结段字符]) #前面是汉字或非结段字符
    (?:\s*[\r\n]+\s*)                #段末空格、空行、段前空格
    (?=[\u4e00-\u9fa5]|[非开段字符])  #后面是汉字或非开段字符'''
    pattern=pattern.replace(u"非结段字符",chare)
    pattern=pattern.replace(u"非开段字符",chars)
    patternobj=re.compile(pattern,re.M|re.X|re.U)
    res=patternobj.findall(cls.result)
    result = patternobj.sub('', cls.result)
    cls.result=result
    return len(res)
@typenum_deco
def func03(cls):
    u'''段落内空格调整'''
    pattern =ur"(?<=\S)(?:[ 　]+)(?=\S)|(?<=\S)(?:[ 　]+)(?=$)|(?<=\S)(?:[ 　]+)(?=[\r\n])"
    patternobj=re.compile(pattern,re.M)
    res=patternobj.findall(cls.result)
    newstring=''
    result = patternobj.sub(newstring, cls.result)
    cls.result=result
    return len(res)
@typenum_deco
def func04(cls):
    u'''段落间空行调整'''
    pattern =ur"(?<=[\n\r])^(\s*$[\n\r])+"
    patternobj=re.compile(pattern,re.M)
    res=patternobj.findall(cls.result)
    #把读取文章转化的\n变回\r\n
    newstring='\r\n'*int(cls.config[u"段间空行"])
    result = patternobj.sub(newstring, cls.result)
    cls.result=result
    return len(res)
@typenum_deco
def func05(cls):
    u'''段落前缩进调整'''
    pattern =ur"^[ 　]*(?=\S)"
    patternobj=re.compile(pattern,re.M|re.U)
    res=patternobj.findall(cls.result)
    newstring=r' '*int(cls.config[u"段首空格"])
    result = patternobj.sub(newstring, cls.result)
    cls.result=result
    return len(res)
@typenum_deco
def func06(cls):
    u'''去除代码及广告'''
    pattern =ur"(?<=\S)(?:[ 　]+)(?=\S)|(?<=\S)(?:[ 　]+)(?=$)|(?<=\S)(?:[ 　]+)(?=[\r\n])"
    patternobj=re.compile(pattern,re.M|re.U)
    res=patternobj.findall(cls.result)
    newstring=''
    result = patternobj.sub(newstring, cls.result)
    cls.result=result
    return len(res)
@typenum_deco
def func07(cls):
    u'''修正不正确回车'''
    pattern =ur"(?<=[^\r])\n"
    patternobj=re.compile(pattern,re.M|re.U)
    res=patternobj.findall(cls.result)
    newstring='\r\n'
    result = patternobj.sub(newstring, cls.result)
    cls.result=result
    return len(res)
if __name__ == '__main__':
    rc=RegexConfig()
    a= Novel_Input()
    a.inputNovels()
    for nu,novel in enumerate(a.getnovels()):
        print str(nu+1).zfill(3),novel.split(os.path.sep)[-1]
        b=Novel_Info(novel)
        c=DoTypeSet(rc,b)
        c.dotypeset()
        c.doconvert()
        c.makefile()
