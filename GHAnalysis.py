import json
import os
import argparse

class Data:

    def __init__(self, jsonAddress: str = None, ifload: int = 0):

        if ifload == 1:
            self._init(jsonAddress)
            return  # 优化
        if jsonAddress is None and not os.path.exists("1.json") and not os.path.exists("2.json") and not os.path.exists("3.path"):
            raise RuntimeError("error: init failed")
            
        x = open('1.json', 'r', encoding='utf-8').read()  
        self.__4Events4PerP = json.loads(x)
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)

    def _init(self, jsonAddress):

        self.__4Events4PerP = {}
        self.__4Events4PerR = {}
        self.__4Events4PerPPerR = {}

        for root, dic, files in os.walk(jsonAddress):
            for f in files:
                if f[-5:] == '.json':
                    with open(jsonAddress + '\\' + f, 'r', encoding = 'UTF-8') as f:  # 优化
                        while True:
                            i = f.readline()
                            if not i:
                                break
                            line = json.loads(i)
                            rType = line['type']
                              # 控制仅读入4种关注事件
                            if rType == 'PushEvent' or rType == 'IssueCommentEvent' or \
                                rType == 'IssueEvent' or rType == 'PullRequestEvent':
                                self._eventNumAdd(line)

        with open('./1.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerP, f)  # 写入
        with open('./2.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR, f)
        with open('./3.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR, f)

    def _eventNumAdd(self, dic: dict):  # 结构优化
        rId = dic['actor']['login']
        rRepo = dic['repo']['name']
        rType = dic['type']

        if not self.__4Events4PerP.get(rId, 0):  # *
            self.__4Events4PerP.update({rId: {}})
            self.__4Events4PerPPerR.update({rId: {}})
        self.__4Events4PerP[rId][rType] \
            = self.__4Events4PerP[rId].get(rType, 0) + 1

        if not self.__4Events4PerR.get(rRepo, 0):
            self.__4Events4PerR.update({rRepo: {}})
        self.__4Events4PerR[rRepo][rType] \
            = self.__4Events4PerR[rRepo].get(rType, 0) + 1

        if not self.__4Events4PerPPerR[rId].get(rRepo, 0):
            self.__4Events4PerPPerR[rId].update({rRepo: {}})
        self.__4Events4PerPPerR[rId][rRepo][rType] \
            = self.__4Events4PerPPerR[rId][rRepo].get(rType, 0) + 1

    def getPerP_EventNum(self, username, event):

        if not self.__4Events4PerP.get(username, 0):  # 先查有无此人
            return 0
        else:
            return self.__4Events4PerP[username].get(event, 0)

    def getPerR_EventNum(self, reponame, event):

        if not self.__4Events4PerR.get(reponame, 0):  # 先查有无此仓库
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event, 0)

    def getPerPperR_EventNum(self, username, reponame, event):

        if not self.__4Events4PerP.get(username, 0):  # 先查有无此人
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame, 0):  # 再查有无此仓库
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event, 0)


class Run:

    def __init__(self):

        self.parser = argparse.ArgumentParser()
        self.data = None
        self._parserInit()
        print(self._command())


    def _parserInit(self):

        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def _command(self):

        cmd = self.parser.parse_args()

        if cmd.init:
            self.data = Data(cmd.init, 1)
            return 'inited'
        else:

            self.data = Data()

            if cmd.user:
                if cmd.repo:
                    res = self.data.getPerPperR_EventNum(cmd.user, cmd.repo, cmd.event)
                else:
                    res = self.data.getPerP_EventNum(cmd.user, cmd.event)
            elif cmd.repo:
                res = self.data.getPerR_EventNum(cmd.repo, cmd.event)
            else:
                raise RuntimeError('error: argument -r or -u is required')
        return res


if __name__ == '__main__':
    a = Run()
