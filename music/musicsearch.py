# coding=utf-8

import os
import sys
from xlrd import open_workbook
import xlwt
from xlutils.copy import copy
import requests
import ConfigParser
import time
import hashlib
import logging
import re
import json
# from pyh import *
from pyh2 import *


class Logger():
    def __init__(self, logname, logger):
        """
           指定日志文件的路径，日志级别
           将日志存入到指定的文件，同时在控制台中显示
        """
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlog(self):
        return self.logger


class UnifiedSearch():
    def __init__(self):
        self.querytext_index = None  # 搜索词序号
        self.expect_index = None  # 期望词序号
        self.expect_song_index = None  # 期望歌曲序号
        self.expect_singer_index = None  # 期望歌手序号
        self.ranking_index = None  # 排名序号
        self.score_index = None  # 得分序号
        self.sourceWb = None  # xlrd读取excel
        self.targetWb = None  # xlutils.copy转化后可操作excel
        self.targetWs = None  # sheet内数据
        self.unified_search = {"musicsearch": "咪咕音乐", "searchlyric": "歌词搜索", "searchalbum": "专辑搜索",
                               "searchsong": "歌曲搜索",
                               "searchsinger": "歌手搜索", "searchmv": "mv搜索", "suggest": "智能提示",
                               "searchsong&singer": "歌曲+歌手", "searchplaylist": "歌单搜索",
                               "searchconcert": "演唱会搜索", "searchbestshow": "最佳显示位搜索"}

        self.re_querytext = re.compile(u"\s*搜索词|查询串\s*")
        self.re_expect = re.compile(u"\s*预期词|期望词\s*")
        self.re_song = re.compile(u"\s*预期歌曲名\s*")
        self.re_singer = re.compile(u"\s*预期歌手名\s*")
        self.re_ranking = re.compile(u"\s*返回位置|排名\s*")
        self.re_score = re.compile(u"\s*得分\s*")

        # 设置样式
        self.alignment = xlwt.Alignment()
        self.alignment.horz = xlwt.Alignment.HORZ_CENTER  # 设置行居中
        self.alignment.vert = xlwt.Alignment.VERT_CENTER  # 设置列居中
        self.style = xlwt.XFStyle()
        self.style.alignment = self.alignment

        # 初始化日志
        if os.path.exists('musicsearch.log'):
            os.remove('musicsearch.log')
        self.logger = Logger(logname='musicsearch.log', logger="musicsearch").getlog()

    def unifiedsearch(self, searchfile):
        """
        统一搜索效果测试
        输入：效果测试搜索词表格
        输出：效果测试得分报告+html统计报告
        """
        self.cf = ConfigParser.ConfigParser()
        self.cf.read('musicsearch.ini')  # 读取配置文件
        # os.path.splitext：将文件名与扩展名分开===>('musicsearch'，'.xls')
        if os.path.exists(os.path.splitext(searchfile)[0] + '_report' + os.path.splitext(searchfile)[1]):
            os.remove(os.path.splitext(searchfile)[0] + '_report' + os.path.splitext(searchfile)[1])
        if os.path.exists(os.path.splitext(searchfile)[0] + '_report.html'):
            os.remove(os.path.splitext(searchfile)[0] + '_report.html')

        self.logger.info(u"%s效果测试", self.unified_search[os.path.splitext(searchfile)[0]].decode('utf-8'))
        self.sourceWb = open_workbook(searchfile, formatting_info=True)  # xlrd读取excel（不可操作）
        self.targetWb = copy(self.sourceWb)  # xlutils.copy将读取的excel变成可操作的excel

        # 获取sheet名列表
        sheet_names = self.sourceWb.sheet_names()
        # 遍历获取各个sheet及对应的配置请求信息
        for sheet_name in sheet_names:
            self.targetWs = self.targetWb.get_sheet(sheet_name)
            try:
                self.logger.info(u"%s", self.unified_search[sheet_name].decode('utf-8'))  # 获取到的sheet添加到日志
            except KeyError, error:
                self.logger.error(error.message)
                self.logger.info("%s", sheet_name)

            try:
                searchjson = json.loads(self.cf.get("musicsearch", sheet_name))  # 将对应配置文件json==>dict
            except ConfigParser.NoOptionError, error:
                self.logger.error(error.message)
            except ConfigParser.NoSectionError, error:
                self.logger.error(error.message)
            else:
                self.music_search(sheet_name, searchjson)  # 调用搜索请求
        # 文件保存musicsearch_report.xls
        self.targetWb.save(os.path.splitext(searchfile)[0] + '_report' + os.path.splitext(searchfile)[1])
        self.html_report(searchfile)  # 写入报告

    def html_report(self, searchfile):
        # 生成html统计报告
        page = PyH('统一搜索效果测试统计结果')
        tab = table(cellspacing="0", cellpadding="4", border="1", align="center")
        tab << tr(td(self.unified_search[os.path.splitext(searchfile)[0]] + '效果测试统计结果',
                     style="text-align:center; font-weight:bold", colspan="5"), bgcolor="#F3F3F3")
        tab << tr(
            td('搜索维度', style="width:150px") + td('搜索词数量', style="width:150px") + td('总得分', style="width:150px") + td(
                '百分制得分', style="width:150px") + td('备注', style="width:100px"), style="font-weight:bold",
            bgcolor="#F3F3F3")
        # 读取excel报告
        self.sourceWb = open_workbook(os.path.splitext(searchfile)[0] + '_report' + os.path.splitext(searchfile)[1],
                                      formatting_info=True)
        sheet_names = self.sourceWb.sheet_names()
        total_score = float(0)
        total_querywords = 0
        for sheet_name in sheet_names:
            sheet = self.sourceWb.sheet_by_name(sheet_name)
            if sheet_name == 'searchsong&singer':
                self.get_index_music(sheet)  # 获取搜索词、预期歌曲名、预期歌手名、返回位置、得分所在列
            else:
                self.get_index(sheet)  # 获取搜索词、预期词、返回位置、得分所在的列
            total_querywords = total_querywords + sheet.nrows - 1
            score_temp = float(0)
            except_temp = 0
            not_exist_temp = 0
            for i in range(1, sheet.nrows):
                score = sheet.cell_value(i, self.score_index)
                if score == u'异常' or score == '':
                    except_temp += 1
                elif score == u'无资源':
                    not_exist_temp += 1
                else:
                    score_temp += float(score)
            if except_temp > 0 and not_exist_temp > 0:
                tab << tr(td(self.unified_search[sheet_name]) + td(sheet.nrows - 1) + td(score_temp) + td(
                    score_temp / (sheet.nrows - 1) * 100) + td(
                    '异常' + str(except_temp) + '次\n' + '无资源' + str(not_exist_temp) + '次'), bgcolor="#F3F3F3")
            elif except_temp > 0 and not_exist_temp == 0:
                tab << tr(td(self.unified_search[sheet_name]) + td(sheet.nrows - 1) + td(score_temp) + td(
                    score_temp / (sheet.nrows - 1) * 100) + td('异常' + str(except_temp) + '次'), bgcolor="#F3F3F3")
            elif except_temp == 0 and not_exist_temp > 0:
                tab << tr(td(self.unified_search[sheet_name]) + td(sheet.nrows - 1) + td(score_temp) + td(
                    score_temp / (sheet.nrows - 1) * 100) + td('无资源' + str(not_exist_temp) + '次'), bgcolor="#F3F3F3")
            else:
                tab << tr(td(self.unified_search[sheet_name]) + td(sheet.nrows - 1) + td(score_temp) + td(
                    score_temp / (sheet.nrows - 1) * 100) + td(' '), bgcolor="#F3F3F3")
            total_score += score_temp

        tab << tr(
            td('合计') + td(total_querywords) + td(total_score) + td(total_score / total_querywords * 100) + td(' '),
            style="font-weight:bold", bgcolor="#F3F3F3")
        page << tab
        page.printOut(os.path.splitext(searchfile)[0] + '_report.html')

    def music_search(self, sheet_name, searchjson):
        """
        咪咕音乐搜索请求
        """
        sheet = self.sourceWb.sheet_by_name(sheet_name)  # 获取原表格sheet数据
        self.targetWs = self.targetWb.get_sheet(sheet_name)  # 获取目标表格sheet数据
        # 歌曲+歌手作为搜索条件，包含两个预期结果的分支
        if sheet_name == 'searchsong&singer':
            self.get_index_music(sheet)  # 获取搜索词、预期歌曲名、预期歌手名、返回位置、得分所在列
        else:
            self.get_index(sheet)  # 获取搜索词、预期词、返回位置、得分所在的列
        # 获取请求url所需字段
        url = searchjson['url']
        uri = searchjson['uri']
        headers = searchjson['headers']
        params = searchjson['params']
        appkey = searchjson['appkey']
        appid = params['appId']
        if sheet_name == 'searchbestshow':
            params['searchSwitch'] = json.dumps(params['searchSwitch'])

        for i in range(1, sheet.nrows):
            querytext = sheet.cell_value(i, self.querytext_index)  # 遍历获取搜索词所在列数据
            # 歌曲+歌手作为搜索条件，包含两个预期结果的分支
            if sheet_name == 'searchsong&singer':  # 获取期望词数据
                expect_song = sheet.cell_value(i, self.expect_song_index)
                expect_singer = sheet.cell_value(i, self.expect_singer_index)
            else:
                expect = sheet.cell_value(i, self.expect_index)
            # 构造鉴权数据
            timestamp = str(int(time.time()))[0:10]
            token = self.toMd5(appid + appkey + timestamp)
            params['token'] = token
            params['timestamp'] = timestamp
            params['text'] = querytext

            ranking = 0
            score = 0

            self.logger.info(u"搜索词：%s", querytext)
            try:
                response = requests.get(url + uri, params=params, headers=headers)
            except IOError, error:
                self.logger.error(error.message)  # 请求异常写入ranking和score
                self.targetWs.write(i, self.ranking_index, u'异常', self.style)
                self.targetWs.write(i, self.score_index, u'异常', self.style)
            else:
                self.logger.info(u"搜索结果：%s", response.text)
                try:
                    if sheet_name == 'suggest':
                        result = json.loads(response.text)['data']
                    elif sheet_name == 'searchbestshow':
                        result = json.loads(response.text)['data']['bestShowResultTone']['data']['result']
                    else:
                        result = json.loads(response.text)['data']['result']
                except KeyError, error:
                    self.logger.error(u"响应报文没有result属性！")
                else:
                    # 歌曲+歌手作为搜索条件，包含两个预期结果的分支
                    if sheet_name == 'searchsong&singer':
                        for j in range(0, len(result)):
                            song_name = result[j]['name']
                            if len(result[j]['singers']) == 0:
                                singer_name = "歌曲无歌手"
                            else:
                                singer_name = result[j]['singers'][0]['name']
                            if (song_name == expect_song or song_name.startswith(
                                    expect_song + u'(') or song_name.startswith(
                                expect_song + u' (') or song_name.startswith(
                                expect_song + u'.') or song_name.startswith(expect_song + u'（') or song_name.startswith(
                                expect_song + u' （')) and singer_name == expect_singer:
                                ranking = j + 1
                                score = self.get_score(ranking)
                                break
                            else:
                                continue
                    elif sheet_name == 'searchbestshow':
                        for j in range(0, len(result)):
                            name = result[j]['singername']
                            if type(expect) is int or type(expect) is float:
                                expect = str(expect)
                            if name == expect or name.startswith(expect + u'(') or name.startswith(
                                    expect + u' (') or name.startswith(expect + u'.') or name.startswith(
                                expect + u'（') or name.startswith(expect + u' （'):
                                ranking = j + 1
                                score = self.get_score(ranking)
                                break
                            else:
                                continue
                    elif sheet_name == 'suggest':
                        for j in range(0, len(result)):
                            if result[j]['type'] == 'singerSong' or result[j]['type'] == 'song' or \
                                    result[j]['type'] == 'songSinger':
                                name = result[j]['data'].get('songName', '未获取到相应数据')
                            else:
                                name = result[j]['data'].get('singerName', '未获取到相应数据')
                            if type(expect) is int or type(expect) is float:
                                expect = str(expect)
                            if name == expect or name.startswith(expect + u'(') or name.startswith(
                                    expect + u' (') or name.startswith(expect + u'.') or name.startswith(
                                expect + u'（') or name.startswith(expect + u' （'):
                                ranking = j + 1
                                score = self.get_score(ranking)
                                break
                            else:
                                continue
                    else:
                        for j in range(0, len(result)):
                            name = result[j]['name']
                            if type(expect) is int or type(expect) is float:
                                expect = str(expect)
                            if name == expect or name.startswith(expect + u'(') or name.startswith(
                                    expect + u' (') or name.startswith(expect + u'.') or name.startswith(
                                expect + u'（') or name.startswith(expect + u' （'):
                                ranking = j + 1
                                score = self.get_score(ranking)
                                break
                            else:
                                continue

                if ranking != 0:
                    if sheet_name == 'searchsong&singer':
                        self.logger.info(u'匹配到预期歌曲+预期歌手：%s+%s，排名：%s，得分：%s', expect_song, expect_singer, ranking, score)
                    else:
                        self.logger.info(u'匹配到预期词：%s，排名：%s，得分：%s', expect, ranking, score)
                    # 目标excel写入排名和得分
                    self.targetWs.write(i, self.ranking_index, ranking, self.style)
                    self.targetWs.write(i, self.score_index, score, self.style)
                else:
                    if sheet_name == 'searchsong&singer':
                        self.logger.warn(u'未匹配到预期词：%s %s，使用预期歌曲名进行二次搜索', expect_song, expect_singer)
                        params['text'] = expect_song.strip()
                    else:
                        self.logger.warn(u'未匹配到预期词：%s，使用预期词进行二次搜索', expect)
                        params['text'] = expect
                    try:
                        if sheet_name == 'searchlyric':
                            searchsong_json = json.loads(self.cf.get("musicsearch", "searchsong"))
                            searchsong_url = searchsong_json["url"]
                            searchsong_uri = searchsong_json["uri"]
                            searchsong_headers = searchsong_json["headers"]
                            searchsong_params = searchsong_json["params"]
                            searchsong_params['token'] = params['token']
                            searchsong_params['timestamp'] = params['timestamp']
                            searchsong_params['text'] = params['text']
                            response = requests.get(searchsong_url + searchsong_uri, params=searchsong_params,
                                                    headers=searchsong_headers)
                        else:
                            response = requests.get(url + uri, params=params, headers=headers)
                    except IOError, error:
                        self.logger.error(error.message)
                        self.targetWs.write(i, self.ranking_index, u'异常', self.style)
                        self.targetWs.write(i, self.score_index, u'异常', self.style)
                    else:
                        self.logger.info(u"二次搜索结果：%s", response.text)
                        try:
                            if sheet_name == 'suggest':
                                result = json.loads(response.text)['data']
                            else:
                                result = json.loads(response.text)['data']['result']
                        except KeyError, error:
                            self.logger.error(u"响应报文没有result属性！")
                            self.targetWs.write(i, self.ranking_index, u'无资源', self.style)
                            self.targetWs.write(i, self.score_index, u'无资源', self.style)
                        else:
                            self.targetWs.write(i, self.ranking_index, u'无资源', self.style)
                            self.targetWs.write(i, self.score_index, u'无资源', self.style)
                            # 歌曲+歌手作为搜索条件，包含两个预期结果的分支
                            if sheet_name == 'searchsong&singer':
                                for j in range(0, len(result)):
                                    song_name = result[j]['name']
                                    if len(result[j]['singers']) == 0:
                                        singer_name = '数据无歌手'
                                    else:
                                        singer_name = result[j]['singers'][0]['name']

                                    if (song_name == expect_song or song_name.startswith(
                                            expect_song + u'(') or song_name.startswith(
                                        expect_song + u' (') or song_name.startswith(
                                        expect_song + u'.') or song_name.startswith(
                                        expect_song + u'（') or song_name.startswith(
                                        expect_song + u' （')) and singer_name == expect_singer:
                                        self.targetWs.write(i, self.ranking_index, u'无', self.style)
                                        self.targetWs.write(i, self.score_index, '0', self.style)
                                        break
                                    else:
                                        continue
                            elif sheet_name == 'searchbestshow':
                                for j in range(0, len(result)):
                                    name = result[j]['singername']
                                    if type(expect) is int or type(expect) is float:
                                        expect = str(expect)
                                    if name == expect or name.startswith(expect + u'(') or name.startswith(
                                            expect + u' (') or name.startswith(expect + u'.') or name.startswith(
                                        expect + u'（') or name.startswith(expect + u' （'):
                                        ranking = j + 1
                                        score = self.get_score(ranking)
                                        self.targetWs.write(i, self.ranking_index, u'无', self.style)
                                        self.targetWs.write(i, self.score_index, '0', self.style)
                                        break
                                    else:
                                        continue
                            elif sheet_name == 'suggest':
                                for j in range(0, len(result)):
                                    if result[j]['type'] == 'singerSong' or result[j]['type'] == 'song' or result[j][
                                        'type'] == 'songSinger':
                                        name = result[j]['data'].get('songName', '未获取到相应数据')
                                    else:
                                        name = result[j]['data'].get('singerName', '未获取到相应数据')
                                    if type(expect) is int or type(expect) is float:
                                        expect = str(expect)
                                    if name == expect or name.startswith(expect + u'(') or name.startswith(
                                            expect + u' (') or name.startswith(expect + u'.') or name.startswith(
                                        expect + u'（') or name.startswith(expect + u' （'):
                                        ranking = j + 1
                                        score = self.get_score(ranking)
                                        self.targetWs.write(i, self.ranking_index, u'无', self.style)
                                        self.targetWs.write(i, self.score_index, '0', self.style)
                                        break
                                    else:
                                        continue
                            else:
                                for j in range(0, len(result)):
                                    name = result[j]['name']
                                    if name == expect or name.startswith(expect + u'(') or name.startswith(
                                            expect + u' (') or name.startswith(expect + u'.') or name.startswith(
                                        expect + u'（') or name.startswith(expect + u' （'):
                                        self.targetWs.write(i, self.ranking_index, u'无', self.style)
                                        self.targetWs.write(i, self.score_index, '0', self.style)
                                        break
                                    else:
                                        continue

    def toMd5(self, key):
        """
        对key进行md5加密
        """
        keyMd5 = hashlib.md5()
        keyMd5.update(key)
        keyMd5 = keyMd5.hexdigest()
        return keyMd5

    def get_score(self, ranking):
        """
        根据排名计算得分，规则如下：
        排名为1得1分，排名为2~5得0.5分，排名为6~10得0.25分，排名在10以后或者无匹配结果得0分
        """
        if ranking == 1:
            score = 1
        elif ranking >= 2 and ranking <= 5:
            score = 0.5
        elif ranking >= 6 and ranking <= 10:
            score = 0.25
        else:
            score = 0
        return score

    def get_index(self, sheet):
        """
        获取搜索词、预期词、返回位置、得分所在的列
        """
        self.querytext_index = self.expect_index = self.ranking_index = self.score_index = None
        for i in range(0, sheet.ncols):
            if self.re_querytext.search(sheet.cell_value(0, i)):
                self.querytext_index = i
            elif self.re_expect.search(sheet.cell_value(0, i)):
                self.expect_index = i
            elif self.re_ranking.search(sheet.cell_value(0, i)):
                self.ranking_index = i
            elif self.re_score.search(sheet.cell_value(0, i)):
                self.score_index = i
        if self.querytext_index is None:
            raise IOError(u"数据文件缺少搜索词列！")
            return
        if self.expect_index is None:
            raise IOError(u"数据文件缺少预期词列！")
            return
        if self.ranking_index is None:
            raise IOError(u"数据文件缺少返回位置列！")
            return
        if self.score_index is None:
            raise IOError(u"数据文件缺少得分列！")
            return

    def get_index_music(self, sheet):
        """
        获取搜索词、预期歌曲名、预期歌手名、返回位置、得分所在列
        """
        self.querytext_index = self.expect_singer_index = self.expect_song_index = self.ranking_index = self.score_index = None
        for i in range(0, sheet.ncols):
            if self.re_querytext.search(sheet.cell_value(0, i)):
                self.querytext_index = i
            elif self.re_song.search(sheet.cell_value(0, i)):
                self.expect_song_index = i
            elif self.re_singer.search(sheet.cell_value(0, i)):
                self.expect_singer_index = i
            elif self.re_ranking.search(sheet.cell_value(0, i)):
                self.ranking_index = i
            elif self.re_score.search(sheet.cell_value(0, i)):
                self.score_index = i
        if self.querytext_index is None:
            raise IOError(u"数据文件缺少搜索词列！")
            return
        if self.expect_song_index is None:
            raise IOError(u"数据文件缺少预期歌曲列！")
            return
        if self.expect_singer_index is None:
            raise IOError(u"数据文件缺少预期歌手列！")
            return
        if self.ranking_index is None:
            raise IOError(u"数据文件缺少返回位置列！")
            return
        if self.score_index is None:
            raise IOError(u"数据文件缺少得分列！")
            return


if __name__ == "__main__":
    test_object = UnifiedSearch()
    test_object.unifiedsearch(sys.argv[1])
