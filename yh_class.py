import requests
from time import sleep, localtime, strftime, perf_counter
from json import loads, decoder
from random import sample, randint
from os import system
from user_agents import parse
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)


class YingHua:
    def __init__(self, login_username, login_password, user_agent, url):
        self.session = requests.Session()
        self.session.headers['user-agent'] = user_agent
        self.form_data = {}
        self.base_url = url
        self.username = login_username
        self.password = login_password

    def login(self):
        login_data = {
            "platform": "Android",
            "username": self.username,
            "password": self.password,
            "pushId": "140fe1da9e67b9c14a7",
            "school_id": "0",
            "imgSign": "533560501d19cc30271a850810b09e3e",
            "imgCode": "cryd",
        }

        login_url = self.base_url + "/api/login.json"
        response = self.session.post(login_url, data=login_data, verify=False)

        if response.status_code != 200:
            return False, "登录失败,请保持网络通畅与网址是否输入正确!"

        response_data = response.json()
        if response_data.get("_code") != 0:
            return False, response_data.get("msg")

        self.session.cookies = response.cookies

        token = response_data["result"]["data"]["token"]
        self.form_data['token'] = token

        return True, response_data['result']['data']

    def get_courses(self):
        courses_url = self.base_url + "/api/course.json"
        response = self.session.post(courses_url, data=self.form_data, verify=False)

        if response.status_code != 200:
            return False, "获取课程失败,请保持网络通畅!"

        response_data = response.json()
        if response_data.get("_code") != 0:
            return False, response_data.get("msg")

        return True, response_data['result']['list']

    def get_chapters(self, course_id):

        learned = {}
        not_completed = {}
        not_started = {}

        chapters_url = self.base_url + "/api/course/chapter.json"
        self.form_data["courseId"] = course_id
        response = self.session.post(chapters_url, data=self.form_data, verify=False)

        if response.status_code != 200:
            return False, "获取课程章节失败,请保持网络通畅!", 0, 0

        response_data = response.json()
        if response_data.get("_code") != 0:
            return False, response_data.get("msg"), 0, 0

        for data in response_data['result']['list']:
            learned[data['name']], not_completed[data['name']], not_started[data['name']] = [], [], []
            for i in data['nodeList']:
                learned[data['name']].append(i) if i["videoState"] == 2 and i['tabVideo'] is True else False
                not_completed[data['name']].append(i) if i["videoState"] == 1 and i['tabVideo'] is True else False
                not_started[data['name']].append(i) if i["videoState"] == 0 and i['tabVideo'] is True else False

        response_data_len = len(response_data['result']['list'])
        learned_sum = len([i for data in learned.values() for i in data])
        not_completed_sum = len([i for data in not_completed.values() for i in data])
        not_learned_sum = len([i for data in not_started.values() for i in data])

        return True, [response_data_len, learned_sum, not_completed_sum, not_learned_sum], not_completed, not_started

    def get_video_progress(self, node_id):
        video_url = self.base_url + "/api/node/video.json"
        self.form_data["nodeId"] = node_id
        response = self.session.post(video_url, data=self.form_data, verify=False)

        if response.status_code != 200:
            return False, "获取视频进度失败,请保持网络通畅!"

        response_data = response.json()
        if response_data.get("_code") != 0:
            return False, response_data.get("msg")

        return True, response_data['result']['data']

    def study_node(self, node_id, study_time, study_id):
        study_url = self.base_url + "/api/node/study.json"
        self.form_data["nodeId"] = node_id
        self.form_data["studyTime"] = str(study_time)
        self.form_data["studyId"] = str(study_id)
        response = self.session.post(study_url, data=self.form_data, verify=False)

        if response.status_code != 200:
            return False, "视频学习失败,请保持网络通畅!"

        response_data = response.json()
        if response_data.get("_code") != 0:
            return False, response_data.get("msg")

        return True, response_data["result"]["data"]['studyId']


class PineSeed:
    def __init__(self):
        self.yinghua = None
        self.course_serial = 0
        self.response_courses = None
        self.chapters_len, self.n_completed, self.n_started = None, None, None
        self.learned_this_time = 0
        self.learning_status = [False, 0]
        self.user_pass = False
        self.user_agent = False
        self.url = False
        try:
            with open('./yh_class.txt', 'r', encoding='utf-8') as f:
                yh_class = loads(str(f.read()))
            self.message = '已成功加载配置文件'
            if ('username' and 'password') in yh_class:
                self.username = yh_class['username']
                self.password = yh_class['password']
                self.user_pass = True
            if 'user_agent' in yh_class:
                self.user_agent_jsons = yh_class['user_agent']
                self.user_agent = True
                for key, value in self.user_agent_jsons.items():
                    user_agent_li = parse(value)
                    if user_agent_li.os.family == 'Other':
                        self.message = '配置文件中UserAgent有误,程序将以默认模式运行'
                        self.user_agent = False
                        break
            if 'url' in yh_class:
                self.url_cleaning(yh_class['url'])
        except FileNotFoundError:
            self.message = ''
        except decoder.JSONDecodeError:
            self.message = '配置文件内容有误,请以标准JSON格式进行配置,程序将以默认模式运行'

        if not self.user_agent:
            self.user_agent_jsons = loads('''{
                "红米Note 5": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; Redmi Note 5 Build/PKQ1.180904.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.10.8",
                "小米6": "Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.3 (Baidu; P1 9)",
                "华为Mate 20 X": "Mozilla/5.0 (Linux; Android 10; EVR-AL00 Build/HUAWEIEVR-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 baiduboxapp/11.0.5.12 (Baidu; P1 10)",
                "COR-TL10": "Mozilla/5.0 (Linux; Android 9; COR-TL10 Build/HUAWEICOR-TL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "华为nova4": "Mozilla/5.0 (Linux; Android 10; VCE-AL00 Build/HUAWEIVCE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 baiduboxapp/11.0.5.12 (Baidu; P1 10)",
                "华为P20 Pro": "Mozilla/5.0 (Linux; Android 10; CLT-AL00 Build/HUAWEICLT-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10) NABar/1.0",
                "黑鲨2游戏手机": "Mozilla/5.0 (Linux; Android 10; SKW-A0 Build/SKYW2001202CN00MQ0; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10)",
                "OPPO A5": "Mozilla/5.0 (Linux; Android 8.1.0; PBAM00 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0) NABar/2.0",
                "DUB-TL00": "Mozilla/5.0 (Linux; Android 8.1.0; DUB-TL00 Build/HUAWEIDUB-TL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0) NABar/2.0",
                "华为nova 2s": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; HWI-AL00 Build/HUAWEIHWI-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.1 Mobile Safari/537.36",
                "iPhone 13": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/13.0 MQQBrowser/10.1.1 Mobile/15B87 Safari/604.1 QBWebViewUA/2 QBWebViewType/1 WKType/1",
                "Redmi Note 7": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; Redmi Note 7 Build/PKQ1.180904.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.14",
                "HLK-AL10": "Mozilla/5.0 (Linux; Android 9; HLK-AL10 Build/HONORHLK-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "华为nova5 Pro": "Mozilla/5.0 (Linux; Android 10; SEA-AL10 Build/HUAWEISEA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10) NABar/1.0",
                "魅族 16s Pro": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; 16s Pro Build/PKQ1.190616.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/9.1 Mobile Safari/537.36",
                "vivo Z3": "Mozilla/5.0 (Linux; Android 9; V1813BT Build/PKQ1.181030.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/11.16 lite baiduboxapp/4.11.0.10 (Baidu; P1 9)",
                "OPPO A79k": "Mozilla/5.0 (Linux; Android 7.1.1; OPPO A79k Build/N6F26Q; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/11.15 baiduboxapp/11.15.0.12 (Baidu; P1 7.1.1)",
                "vivo X9s L": "Mozilla/5.0 (Linux; Android 8.1.0; vivo X9s L Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "RNE-AL00": "Mozilla/5.0 (Linux; Android 8.0.0; RNE-AL00 Build/HUAWEIRNE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.0.0)",
                "M2 E": "Mozilla/5.0 (Linux; Android 6.0.1; M2 E Build/MMB29U; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.2 (Baidu; P1 6.0.1)",
                "MI PLAY": "Mozilla/5.0 (Linux; Android 8.1.0; MI PLAY Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "NX606J": "Mozilla/5.0 (Linux; Android 8.1.0; NX606J Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "OPPO A57": "Mozilla/5.0 (Linux; U; Android 6.0.1; zh-cn; OPPO A57 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/9.1 Mobile Safari/537.36",
                "华为畅享9 Plus": "Mozilla/5.0 (Linux; Android 9; JKM-AL00a Build/HUAWEIJKM-AL00a; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "JNY-AL10": "Mozilla/5.0 (Linux; Android 10; JNY-AL10 Build/HUAWEIJNY-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10) NABar/2.0",
                "vivo X21": "Mozilla/5.0 (Linux; Android 9; vivo X21 Build/PKQ1.180819.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9) NABar/1.0",
                "华为Mate 9 Pro": "Mozilla/5.0 (Linux; U; Android 9; zh-CN; LON-AL00 Build/HUAWEILON-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.9.0.1070 Mobile Safari/537.36",
                "荣耀20": "Mozilla/5.0 (Linux; Android 10; YAL-AL00 Build/HUAWEIYAL-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10) NABar/2.0",
                "V1913A": "Mozilla/5.0 (Linux; Android 9; V1913A Build/P00610; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "CLT-TL01": "Mozilla/5.0 (Linux; Android 10; CLT-TL01 Build/HUAWEICLT-TL01; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10)",
                "三星Galaxy S10+": "Mozilla/5.0 (Linux; Android 10; SM-G9750 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 10)",
                "红米5 Plus": "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; Redmi 5 Plus Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/9.2 Mobile Safari/537.36",
                "iPhone 11": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 MQQBrowser/10.1.0 Mobile/15B87 Safari/604.1 QBWebViewUA/2 QBWebViewType/1 WKType/1",
                "一加6": "Mozilla/5.0 (Linux; Android 9; ONEPLUS A6000 Build/PKQ1.180716.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9) NABar/2.0",
                "OPPO_A59S": "Mozilla/5.0 (Linux; U; Android 4.4.2; zh-cn; OPPO_A59S Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36",
                "华为Mate10移动定制全网通版": "Mozilla/5.0 (Linux; Android 9; ALP-TL00 Build/HUAWEIALP-TL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "OPPO R15": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; PACT00 Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.1 Mobile Safari/537.36",
                "Redmi K20 Pro": "Mozilla/5.0 (Linux; U; Android 10; zh-cn; Redmi K20 Pro Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.14",
                "华为Mate 8": "Mozilla/5.0 (Linux; U; Android 7.0; zh-cn; HUAWEI NXT-AL10 Build/HUAWEINXT-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/9.0 Mobile Safari/537.36",
                "华为畅享10 Plus": "Mozilla/5.0 (Linux; Android 9; STK-AL00 Build/HUAWEISTK-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9) NABar/1.0",
                "红米6 Pro": "Mozilla/5.0 (Linux; Android 9; Redmi 6 Pro Build/PKQ1.180917.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "红米4X": "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 4X Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/11.12 baiduboxapp/11.12.3.2 (Baidu; P1 7.1.2)",
                "M1822": "Mozilla/5.0 (Linux; Android 8.1.0; M1822 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "iQOO Pro 5G": "Mozilla/5.0 (Linux; U; Android 9; zh-CN; V1916A Build/PKQ1.190714.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.8.2.1062 Mobile Safari/537.36",
                "PBDM00": "Mozilla/5.0 (Linux; Android 9; PBDM00 Build/PKQ1.190519.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 9)",
                "小米8": "Mozilla/5.0 (Linux; Android 9; MI 8 Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9) NABar/2.0",
                "V1836A": "Mozilla/5.0 (Linux; Android 9; V1836A Build/PKQ1.181030.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "荣耀8X": "Mozilla/5.0 (Linux; Android 9; JSN-AL00a Build/HONORJSN-AL00a; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9) NABar/1.0",
                "vivo X9s": "Mozilla/5.0 (Linux; Android 8.1.0; vivo X9s Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "vivo Y85A": "Mozilla/5.0 (Linux; Android 8.1.0; vivo Y85A Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/11.1 baiduboxapp/11.1.0.10 (Baidu; P1 8.1.0)",
                "华为Mate20": "Mozilla/5.0 (Linux; Android 10; HMA-AL00 Build/HUAWEIHMA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10) NABar/2.0",
                "1809-A01": "Mozilla/5.0 (Linux; Android 8.1.0; 1809-A01 Build/OPM1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 8.1.0)",
                "SM-A7050": "Mozilla/5.0 (Linux; Android 9; SM-A7050 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)",
                "小米5X": "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-CN; MI 5X Build/OPM1.171019.019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.2.992 Mobile Safari/537.36",
                "小米8 SE": "Mozilla/5.0 (Linux; Android 10; MI 8 SE Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.17 SP-engine/2.13.0 baiduboxapp/11.17.0.13 (Baidu; P1 10)",
                "Redmi 7": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; Redmi 7 Build/PKQ1.181021.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.14",
                "V1816A": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; V1816A Build/PKQ1.180819.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.1 Mobile Safari/537.36",
                "SM-C7010": "Mozilla/5.0 (Linux; Android 8.0.0; SM-C7010 Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.0.0)",
                "Redmi Note 8 Pro": "Mozilla/5.0 (Linux; U; Android 10; zh-cn; Redmi Note 8 Pro Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.14",
                "V1732A": "Mozilla/5.0 (Linux; Android 8.1.0; V1732A Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "华为Mate 10": "Mozilla/5.0 (Linux; Android 10; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10) NABar/2.0",
                "荣耀8青春版": "Mozilla/5.0 (Linux; Android 8.0.0; PRA-TL10 Build/HONORPRA-TL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.0.0)",
                "华为nova3i": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; INE-AL00 Build/HUAWEIINE-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.1 Mobile Safari/537.36",
                "华为Mate10 Pro": "Mozilla/5.0 (Linux; Android 10; BLA-TL00 Build/HUAWEIBLA-TL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 10)",
                "OPPO R11": "Mozilla/5.0 (Linux; Android 7.1.1; OPPO R11 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 7.1.1)",
                "小米2S": "Mozilla/5.0 (Linux; U; Android 10; zh-cn; MIX 2S Build/QKQ1.190828.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.14",
                "vivo Y71A": "Mozilla/5.0 (Linux; Android 8.1.0; vivo Y71A Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0)",
                "荣耀畅玩6X": "Mozilla/5.0 (Linux; Android 7.0; BLN-AL40 Build/HONORBLN-AL40; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045130 Mobile Safari/537.36 V1_AND_SQ_8.2.7_1334_YYB_D QQ/8.2.7.4410 NetType/4G WebP/0.3.0 Pixel/1080 StatusBarHeight/72 SimpleUISwitch/0",
                "华为 nova 3e": "Mozilla/5.0 (Linux; Android 9; ANE-AL00 Build/HUAWEIANE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)"
            }
                ''')
        self.user_agent_data = sample([key for key, value in self.user_agent_jsons.items()], 1)[0]

    def url_cleaning(self, url):
        if ('https://' or 'http://') not in url:
            url = 'https://' + url
        if '/' == url[-1]:
            url = url[:-1]
        self.url = url

    def start_print(self):
        system('cls')
        system('title YH Class V1.3 Beta')
        print(f'''
==========================================================================================
=                                                                                        =
=    * * * *   * * *   *      *   * * * *      * * * *   * * * *   * * * *   * * *       =
=    *     *     *     * *    *   *            *         *         *         *     *     =
=    * * * *     *     *  *   *   * * * *      * * * *   * * * *   * * * *   *      *    =
=    *           *     *    * *   *                  *   *         *         *     *     =
=    *         * * *   *      *   * * * *      * * * *   * * * *   * * * *   * * *       =
=                                                                                        =
=                   Wish everyone can obtain the knowledge they want!                    =
=                                                                                        =
==========================================================================================
=                         GithHub:https://github.com/Pine-Seed                           =
=                      CSDN:https://blog.csdn.net/weixin_44105042                        =
==========================================================================================

欢迎使用 YH Class V1.4 Beta  [当前模拟机型：{self.user_agent_data}]

注意事项:
1.当前为测试版,时间不够没有太过完善请多包涵
2.请在稳定的网络环境下运行(高延时没事,只要不把网络断开就行)
3.最小化窗口不会停止运行,要关闭就叉掉此窗口
4.程序会自动识别你自己的学习进度,不用担心会重新学习浪费时间

{self.message}''')

    def printf(self):
        system('cls')
        print(f'''
==========================================================================================
=                                                                                        =
=    * * * *   * * *   *      *   * * * *      * * * *   * * * *   * * * *   * * *       =
=    *     *     *     * *    *   *            *         *         *         *     *     =
=    * * * *     *     *  *   *   * * * *      * * * *   * * * *   * * * *   *      *    =
=    *           *     *    * *   *                  *   *         *         *     *     =
=    *         * * *   *      *   * * * *      * * * *   * * * *   * * * *   * * *       =
=                                                                                        =
=                   Wish everyone can obtain the knowledge they want!                    =
=                                                                                        =
==========================================================================================
=                         GithHub:https://github.com/Pine-Seed                           =
=                      CSDN:https://blog.csdn.net/weixin_44105042                        =
==========================================================================================

欢迎使用 YH Class V1.4 Beta | 正在运行中，把我挂着，你可以去做你自己的事情了

[当前模拟机型：{self.user_agent_data}]
[当前学习课程：《{self.response_courses[int(self.course_serial)]['name']}》]
[本次运行已学习：{self.learned_this_time} 节课]
                ''')
        print('-' * 10, f"[{strftime('%Y-%m-%d %H:%M:%S', localtime())}]", '-' * 10)
        print(f"本课程共有 {self.chapters_len[0]} 章 | 您已学: "
              f"{self.chapters_len[1]} 小节 | 未学完: {self.chapters_len[2]} 小节 | 未学: "
              f"{self.chapters_len[3]} 小节")

    def enter_account(self):
        if not self.url:
            self.url = input('请输入学校网址(域名)：')
            self.url_cleaning(self.url)
        while True:
            if not self.user_pass:
                self.username = input('请输入账号：')
                self.password = input('请输入密码：')
            self.yinghua = YingHua(self.username, self.password, self.user_agent_jsons[self.user_agent_data], self.url)
            err, response_user = self.yinghua.login()
            if err:
                break
            print(response_user)
            self.user_pass = False
        current_time()
        print("登录成功！")
        print(
            f"姓名：{response_user['name']}\n所在学院：{response_user['collegeName']}\n所在班级："
            f"{response_user['className']}")

    def retrieve_courses(self):
        current_time()
        print("正在检索课程,请稍后...")
        err, self.response_courses = self.yinghua.get_courses()
        if not err:
            print('检索课程出错啦！错误:', self.response_courses)
            input('\n按回车键退出程序')
            exit()
        current_time()
        print(f"共找到 {len(self.response_courses)} 门课程")
        print('=' * 20)
        for courses in self.response_courses:
            course_name = courses['name']
            course_progress = float(courses['progress']) * 100
            course_end_date = courses['endDate']
            print('序号:', self.response_courses.index(courses), '| 课程名:', course_name, '| 学习进度:',
                  course_progress,
                  '% | 结束时间:', course_end_date)
        print('=' * 20)

    def search_chapter(self):
        self.course_serial = input('请输入需要学习的课程序号：')
        course_ids = self.response_courses[int(self.course_serial)]['id']
        current_time()
        print(f"正在检索 {self.response_courses[int(self.course_serial)]['name']} 课程章节,请稍后...")
        err, self.chapters_len, self.n_completed, self.n_started = self.yinghua.get_chapters(course_ids)
        if not err:
            print('检索章节出错啦！错误:', self.chapters_len)
            input('\n按回车键退出程序')
            exit()
        current_time()
        wait = randint(1, 5)
        print(f"检索完毕！ {wait} 秒后开始学习")
        sleep(wait)

    def learning_unfinished_courses(self):
        self.learning_status = [False, 1]
        for key, values in self.n_completed.items():
            self.start_learning(key, values)

    def learning_unstudied_courses(self):
        self.learning_status = [False, 2]
        for key, values in self.n_started.items():
            self.start_learning(key, values)

    def start_learning(self, key, values):
        for value in values:
            self.learning_status[0] = True
            self.printf()

            value_id = value['id']
            value_name = value['name']
            try:
                value_duration = value['duration']
            except TypeError:
                value_duration = '未知'

            print(f'当前学习章节: 《{key}》')
            start_time = 1
            start_id = 0
            reckon_time_start = perf_counter()

            print(f'当前学习小节: 《{value_name}》 ,视频时长: [{value_duration}]')

            while True:
                err, response_video_progress = self.yinghua.get_video_progress(value_id)
                if not err:
                    print('检索视频出错啦！错误:', response_video_progress)
                    input('\n按回车键退出程序')
                    exit()
                try:
                    progress = response_video_progress['study_total']['progress']
                    state = response_video_progress['study_total']['state']
                except TypeError:
                    progress = '0.00'
                    state = 0
                err, response_study_node = self.yinghua.study_node(value_id, start_time, start_id)
                if not err:
                    print('学习课程出错啦！错误:', response_video_progress)
                    input('\n按回车键退出程序')
                    exit()
                reckon_time_stop = perf_counter() - reckon_time_start
                print("\r[进度:{:^3.0f}%][{}{}][已用时间: {:.2f} s]".format(
                    float(progress) * 100,
                    "*" * int((float(progress) * 100) // 2),
                    "." * int(50 - ((float(progress) * 100) // 2)),
                    reckon_time_stop), end='')
                start_time += 10
                start_id = response_study_node
                if int(state) == 2:
                    print("\r[进度:{:^3.0f}%][{}{}][已用时间: {:.2f} s]".format(
                        100, "*" * 50, "." * 0, reckon_time_stop))
                    break
                sleep(10)
            wait = randint(5, 10)
            self.learned_this_time += 1
            print(f'当前章节已学完,等待 {wait} 秒后继续')
            sleep(wait)

            if self.learning_status[0] and self.learning_status[1] == 1:
                self.chapters_len[2] -= 1
                self.chapters_len[1] += 1
            elif self.learning_status[0] and self.learning_status[1] == 2:
                self.chapters_len[3] -= 1
                self.chapters_len[1] += 1


def current_time():
    t = f"[{strftime('%Y-%m-%d %H:%M:%S', localtime())}] "
    print(t, end='')


if __name__ == "__main__":
    pineseed = PineSeed()
    pineseed.start_print()
    pineseed.enter_account()
    pineseed.retrieve_courses()
    pineseed.search_chapter()
    pineseed.learning_unfinished_courses()
    pineseed.learning_unstudied_courses()
    pineseed.printf()
    input('\n当前课程学习完毕!请按回车键退出')
