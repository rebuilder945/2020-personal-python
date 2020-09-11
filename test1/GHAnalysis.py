import json
import os
import argparse

class Data:
    def __init__(self, dict_address: int = None, reload: int = 0):  # 构造函数初始化
        if reload == 1:  # 支持重复查询，当一次运行完之后，data实例被销毁后，self.__4Events4PerP也消失，故下面要将数据存入json并在reload
            # 为0时不再分析整理数据，而是在下面直接赋值self.__4Events4PerP进行查询（因此查询函数中遍历的也是直接的self.__4Events4PerP）
            self.__init(dict_address)
        if dict_address is None and not os.path.exists('1.json') and not os.path.exists('2.json') and not os.path.exists('3.json'):
            raise RuntimeError('error: init failed')  # 若未初始化过，无分析后的json，而进行查询则报错
        # 赋值self.__4Events4PerP以支持查询
        x = open('1.json', 'r', encoding='utf-8').read()
        self.__4Events4PerP = json.loads(x)
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)

    # 建立数据库的过程（分析整理数据）
    def __init(self, dict_address: str):
        json_list = []
        for root, dic, files in os.walk(dict_address):
            for f in files:
                if f[-5:] == '.json':
                    json_path = f
                    x = open(dict_address+'\\'+json_path,
                             'r', encoding='utf-8').read()  # 读出目标文件的内容存在x中
                    str_list = [_x for _x in x.split('\n') if len(_x) > 0]
                    for i, _str in enumerate(str_list):
                        try:
                            json_list.append(json.loads(_str))
                        except:
                            pass
        records = self.__listOfNestedDict2ListOfDict(json_list)  # 将字符串列表转换为字典列表

        # 对整个数据的字典列表的分析整理，并输出到json文件
        self.__4Events4PerP = {}
        self.__4Events4PerR = {}
        self.__4Events4PerPPerR = {}
        for i in records:
            if not self.__4Events4PerP.get(i['actor__login'], 0):
                self.__4Events4PerP.update({i['actor__login']: {}})
                self.__4Events4PerPPerR.update({i['actor__login']: {}})
            self.__4Events4PerP[i['actor__login']][i['type']
                                         ] = self.__4Events4PerP[i['actor__login']].get(i['type'], 0)+1
            if not self.__4Events4PerR.get(i['repo__name'], 0):
                self.__4Events4PerR.update({i['repo__name']: {}})
            self.__4Events4PerR[i['repo__name']][i['type']
                                       ] = self.__4Events4PerR[i['repo__name']].get(i['type'], 0)+1
            if not self.__4Events4PerPPerR[i['actor__login']].get(i['repo__name'], 0):
                self.__4Events4PerPPerR[i['actor__login']].update({i['repo__name']: {}})
            self.__4Events4PerPPerR[i['actor__login']][i['repo__name']][i['type']
                                                          ] = self.__4Events4PerPPerR[i['actor__login']][i['repo__name']].get(i['type'], 0)+1

        # 分别创建json文件并将整理后的数据写入
        with open('1.json', 'w', encoding='utf-8') as f:  # open对象文件若就在同样目录则只要传入文件名，若文件不存在，自动创建该文件
            json.dump(self.__4Events4PerP,f)  # 写入
        with open('2.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR,f)
        with open('3.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR,f)

    # 嵌套字典的递归建立
    def __parseDict(self, d: dict, prefix: str):
        _d = {}
        for k in d.keys():
            if str(type(d[k]))[-6:-2] == 'dict':
                _d.update(self.__parseDict(d[k], k))
            else:
                _k = f'{prefix}__{k}' if prefix != '' else k
                _d[_k] = d[k]
        return _d

    # 将字符串列表转换为字典列表
    def __listOfNestedDict2ListOfDict(self, a: list):
        records = []
        for d in a:
            _d = self.__parseDict(d, '')
            records.append(_d)
        return records

    # 3种查询函数
    def getEventsUsers(self, username: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):  # 先查有无此人
            return 0
        else:
            return self.__4Events4PerP[username].get(event,0)  # 不用self.__4Events4PerP[username][event]原因是若事件查无则会出错

    def getEventsRepos(self, reponame: str, event: str) -> int:
        if not self.__4Events4PerR.get(reponame,0):  # 先查有无此仓库
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event,0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):  # 先查有无此人
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame,0):  # 再查有无此仓库
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()  # 创建命令行解析器
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):  # 初始化命令类型参数
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    # 匹配输入命令
    def analyse(self):
        if self.parser.parse_args().init:  # 初始化命令
            self.data = Data(self.parser.parse_args().init, 1)  # 建立data，创建json数据库
            return 0
        else:  # 查询命令
            if self.data is None:  # 重复查询的时候data已被销毁，应先建立data
                self.data = Data()  # 但此时的data不必再经历一次分析数据的过程
            if self.parser.parse_args().event:  # 事件的必要级最高
                if self.parser.parse_args().user:  # 其次用户
                    if self.parser.parse_args().repo:  # 查询类别1
                        res = self.data.getEventsUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo, self.parser.parse_args().event)
                    else:  # 查询类别2
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:  # 查询类别3
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -l or -c are required')  # 无用户也无仓库异常报错
            else:
                raise RuntimeError('error: argument -e is required')  # 无事件异常报错
        return res


if __name__ == '__main__':
    a = Run()