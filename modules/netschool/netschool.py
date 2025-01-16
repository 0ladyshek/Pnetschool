from aiohttp import ClientSession, TCPConnector, CookieJar, ClientResponse
from typing import Union, Optional
from yarl import URL
from hashlib import md5
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs4
from base64 import b64decode
from json import loads
from .errors import NetSchoolAPIError

class NetSchool:
    def __init__(self, url: str, username: str, password: str, school: Union[int, str] = 0) -> None:
        if not url.startswith("http"): url = f"http://{url}"
        if not url.endswith("/"): url = f"{url}/"
        self.url = url
        
        self.username = username
        self.password = password
        self.school = school
        
        self.client = ClientSession(trust_env = True, connector=TCPConnector(verify_ssl=False), base_url=URL(self.url), headers={"referer": self.url}, cookie_jar=CookieJar(unsafe=True),)
        
        self._year_id = None
        self._start_term = None
        self._end_term = None
        self._class_id = None

    async def login(self) -> list:
        
        login_meta = await self.requester("/webapi/auth/getdata", method = "POST")
        ver = login_meta.get("ver")
        salt = login_meta.get("salt")
        lt = login_meta.get("lt")

        encoded_password = md5(self.password.encode('windows-1251')).hexdigest() 
        encoded_password = md5(f"{salt}{encoded_password}".encode()).hexdigest() 
        password = encoded_password[:len(self.password)]

        login_response = await self.requester("/webapi/login", method = "POST", data={
            "LoginType": 1, 
            "sft": "2", 
            "scid": f"{self.school}", 
            "un": self.username, 
            "pw": password,
            "pw2": encoded_password,
            "lt": lt, 
            "ver": ver
        })
            
        self.access_token = login_response.get("at", None)
        if not self.access_token: raise NetSchoolAPIError(login_response)
        self.ver = ver

        self.client.headers.add("at", self.access_token)
        
        self._student_id = login_response['accountInfo']['user']['id']

        self._school_id = login_response['accountInfo']['currentOrganization']['id']
    
        #self._info_period = await self.period()
        #self._student_id = self._info_period['filterSources'][0]['defaultValue']
        #self._user_id = login_response['accountInfo']['user']['id']

        #year_response = await self.requester("/webapi/years/current")
        #self._year_id = year_response.get("id")

        return login_response
    
    async def context(self) -> dict:
        return (await self.requester(f"/webapi/context"))
    
    async def sessions(self) -> list:
        return (await self.requester("/webapi/context/activeSessions"))

    async def school_info(self, school_id: Optional[int] = 0) -> dict:
        return (await self.requester(f"/webapi/schools/{school_id if school_id else self.school}"))

    async def school_card(self, school_id: Optional[int] = 0) -> dict:
        return (await self.requester(f"/webapi/schools/{school_id if school_id else self.school}/card"))

    async def years(self) -> list:
        return (await self.requester(f"/webapi/mysettings/yearlist"))

    async def classes(self) -> list:
        return (await self.requester(f"/webapi/classes?expand=chiefs&expand=using&expand=room&expand=educPrograms"))

    async def classmeetings(self, class_id: Optional[int] = 0, start: Optional[datetime] = None, end: Optional[datetime] = None, student_id: Optional[int] = None) -> list:
        
        if not start: start = datetime.now()
        if not end: end = start
        
        params = {"start": start.strftime("%FT%X.%fZ"), "end": end.strftime("%FT%X.%fZ")}
        
        if class_id:
            params['classId'] = class_id
        
        if student_id:
            params['studentId'] = student_id

        return (await self.requester("/webapi/schedule/classmeetings", params = params))

    async def times(self) -> list:
        return (await self.requester(f"/webapi/schedule/times"))

    async def terms(self, class_id: Optional[int] = 0, start: Optional[datetime] = None, end: Optional[datetime] = None) -> list:
        
        if not start: start = datetime.now()
        if not end: end = start
        
        json = {"startPeriod": start.strftime("%FT%X.%fZ"), "endPeriod": end.strftime("%FT%X.%fZ")}
        
        if class_id:
            json['classIds'] = [class_id]

        return (await self.requester("/webapi/terms/search", method = "POST", json = json))

    async def state(self) -> dict:
        return (await self.requester(f"/webapi/context/state"))

    async def rooms(self) -> list:
        return (await self.requester(f"/webapi/rooms"))

    async def subjects(self, student_id: Optional[int] = 0, class_id: Optional[int] = 0) -> list:
        params = {"expand": "name", "expand": "terms", "expand": "class"}
        
        if student_id:
            params['studentId'] = student_id
        
        if class_id:
            params['iupClassId'] = f"{class_id}_0"

        return (await self.requester(f"/webapi/subjectgroups", params = params))

    async def birthdays(self, month: Optional[int] = 0, class_id: Optional[int] = -1) -> list:
        if not month: month = datetime.now().month
        
        return (await self.requester(f"/webapi/schedule/month/birthdays", params = {"classId": class_id, "month": month}))

    async def holidays(self, month: Optional[int] = 0, class_id: Optional[int] = 0, year: Optional[int] = 0) -> list:
        if not month: month = datetime.now().month
        if not year: year = datetime.now().year
        
        return (await self.requester(f"/webapi/schedule/month/events", params={"month": month, "year": year, "classId": class_id}))
    
    async def school_events(self, size: Optional[int] = 100, page: Optional[int] = 1, class_id: Optional[int] = 0) -> list:
        
        json = {
            "filterContext":
                {
                    "selectedData":
                        [
                            {
                                "filterId": "EventFilter",
                                "filterValue": "1",
                            },
                        ],
                        "params": None
                },
                "fields": 
                    [
                        "date","name","room","periodicity"
                    ],
                "page": page,
                "pageSize": size,
                "search": None,
                "order": None
        }
        
        if class_id:
            json['filterContext']['selectedData'].append({
                "filterId": "ClassFilter",
                "filterValue": str(class_id),
            })
        
        return (await self.requester(f"/webapi/school/events/registry", method = "POST", json = json))
        
        
    async def class_events(self, size: Optional[int] = 100, page: Optional[int] = 1, class_id: Optional[int] = 0) -> list:
        if not class_id: 
            class_id = await self.my_class_id()
        
        return (await self.requester(f"/webapi/school/events/registry", method = "POST", json = {
            "filterContext":
                {"selectedData":
                    [
                        {
                            "filterId": "EventFilter",
                            "filterValue": "2",
                        },
                        {
                            "filterId": "ClassFilter",
                            "filterValue": str(class_id),
                        },
                    ],
                    "params": None
                },
                "fields":
                    [
                        "date","name","room","class",
                    ],
                "page": page,
                "pageSize": size,
                "search": None,
                "order": None
        }))
        
    async def vacations(self, size: Optional[int] = 50, page: Optional[int] = 1, class_id: Optional[int] = 0) -> list:
            
        json = {
            "filterContext":
                {
                    "selectedData":
                        [
                            {
                                "filterId": "EventFilter",
                                "filterValue": "3",
                            },
                        ],
                        "params": None
                },
                "fields": 
                    [
                        "date","name","periodicity"
                    ],
                "page": page,
                "pageSize": size,
                "search": None,
                "order": None
        }
        
        if class_id:
            json['filterContext']['selectedData'].append({
                "filterId": "ClassFilter",
                "filterValue": str(class_id),
            })
        
        return (await self.requester(f"/webapi/school/events/registry", method = "POST", json = json))
        
    async def diary(self, start: Optional[datetime] = None, end: Optional[datetime] = None, year_id: Optional[int] = None) -> list:
        if not year_id: 
            if not self._year_id:
                self._year_id = await self.year_id()
            year_id = self._year_id
        if not start: start = datetime.now() - timedelta(days=datetime.now().weekday())
        if not end: end = start + timedelta(days=5)
        
        return (await self.requester("/webapi/student/diary", params = {
            "weekStart": start.strftime("%Y-%m-%d"),
            "weekEnd": end.strftime("%Y-%m-%d"),
            "studentId": self._student_id,
            "yearId": year_id,
            "schoolId": self._school_id
        }))
        
    async def attachments_diary(self, assignments: list) -> list:
        return (await self.requester("/webapi/student/diary/get-attachments", params = {"studentId": self._student_id}, method = "POST", json = {"assignId": assignments}))
    
    async def attachment(self, attachment_id: int) -> bytes:
        return (await self.requester(f"/webapi/attachments/{attachment_id}", output = "content"))
    
    async def assign_info(self, assign_id: int) -> dict:
        return (await self.requester(f"/webapi/student/diary/assigns/{assign_id}", params = {"studentId": self._student_id}))
    
    async def year_id(self) -> int:
        return (await self.requester("/webapi/years/current"))['id']
        
    async def info(self) -> bytes:
        return (await self.requester(f"/webapi/sysinfo", output="raw"))

    async def class_info(self, class_id: Optional[int] = 0, info: bool = True) -> list:
        if info: info = await self.requester(f"/webapi/classes/{class_id}?expand=room&expand=chiefs&expand=hasClassNotWorkingTeacher")
        students = await self.requester(f"/webapi/users/studentlist", params = {"classId": class_id})
        return info, students
    
    async def advanced_schedule(self, class_id: Optional[list] = [], teacher_id: Optional[int] = 0, start: Optional[datetime] = None, end: Optional[datetime] = None):
        params = {}
        if class_id:
            params['classId'] = class_id
        if teacher_id:
            params['teacherId'] = teacher_id
            params['teacherStatus'] = 2
        if not start: start = datetime.now() - timedelta(days=datetime.now().weekday())
        if not end: end = start + timedelta(days=5)
        params['start'] = start.strftime("%Y-%m-%dT00:00:00")
        params['end'] = end.strftime("%Y-%m-%dT00:00:00")
        return (await self.requester(f"/webapi/schedule/classmeetings", params = params))
  
    async def past_mandatory(self, start: Optional[datetime] = None, end: Optional[datetime] = None, year_id: Optional[int] = None) -> list:
        if not year_id: 
            if not self._year_id:
                self._year_id = await self.year_id()
            year_id = self._year_id
        if not start: start = await self.start_term()
        if not end: end = await self.end_term()
        
        return (await self.requester("/webapi/student/diary/pastMandatory", params = {
            "weekStart": start.strftime("%Y-%m-%d"),
            "weekEnd": end.strftime("%Y-%m-%d"),
            "studentId": self._student_id,
            "yearId": year_id,
            "schoolId": self._school_id
        }))
        
    async def subjects_class(self, class_id: Optional[int] = 0) -> list:
        if not class_id:
            class_id = await self.my_class_id()
        return (await self.requester(f"/webapi/subjectgroups", params = {"classId": class_id, "expand": "name"}))
        
    async def annouchements(self) -> list:
        return (await self.requester("/webapi/announcements"))
        
    async def mail(self, box: str = "Inbox", page: Optional[int] = 1, size: Optional[int] = 100) -> list:
        '''
        "Inbox", "Draft", "Sent", "Deleted"
        '''
        return (await self.requester(f"/webapi/mail/registry", "POST", json = {
            "filterContext": 
                {
                    "selectedData":
                        [
                            {
                                "filterId": "MailBox",
                                "filterValue": box,
                            }
                        ],
                    "params": None,
                },
                "fields": ["author","subject","sent"],
                "page": page,
                "pageSize": size,
                "search": None,
                "order": None
            }))
        
    async def message(self, message_id: str) -> dict:
        return (await self.requester(f"/webapi/mail/messages/{message_id}/read", params = {"userId": self._student_id}))
        
    async def forum(self, page: Optional[int] = 1, size: Optional[int] = 100) -> list:
        return (await self.requester("/webapi/forum/registry", "POST", json = {
            "filterContext":
                {
                    "selectedData": [],
                    "params": None
                },
                "fields": ["subject","author","moderators","replies","lastMessage"],
                "page": page,
                "pageSize": size,
                "search": None,
                "order": None
            }))
        
    async def topic(self, topic_id: str, page: Optional[int] = 1, size: Optional[int] = 100) -> list:
        return (await self.requester(f"/webapi/forum/topics/{topic_id}/registry", "POST", json = {
            "filterContext": {
                "selectedData": [
                    {
                        "filterId": "topicId",
                        "filterValue": topic_id,
                    }
                ],
                "params": None
            },
            "fields": ["author","message"],
            "page": page,
            "pageSize": size,
            "search": None,
            "order": None}))
        
    async def start_term(self) -> datetime:
        if self._start_term: return self._start_term
        
        term = await self.terms()
        
        self._start_term = datetime.strptime(term[0]['startDate'], "%Y-%m-%dT%H:%M:%S")
        return self._start_term
        
    async def end_term(self) -> datetime:
        if self._end_term: return self._end_term
        
        term = await self.terms()
        
        self._end_term = datetime.strptime(term[0]['endDate'], "%Y-%m-%dT%H:%M:%S")
        return self._end_term
        
    async def find_class_id(self, class_id: int) -> str:
        classes = await self.requester("/webapi/classes")
        classes = dict(zip([class_['id'] for class_ in classes], [class_['name'] for class_ in classes]))
        return classes[class_id]

    async def my_class_id(self) -> str:
        if self._class_id: return self._class_id
        self._class_id =  int((await self.requester(f"/webapi/school/events/registry/filter", "POST", json = {
            "selectedData": 
                [
                    {
                        "filterId": "EventFilter",
                        "filterValue": "2",
                    }
                ],
                "params": None
        }))[0]['defaultValue'])
        return self._class_id
    
    async def settings(self, photo: Optional[bool] = False) -> dict:
        user = await self.requester(f"/webapi/mysettings")
        
        if not photo: return user
        
        if user.get("existsPhoto"):
            photo = await self.requester("/webapi/users/photo", output = "content", params = {
                "AT": self.access_token,
                "userId": self._student_id,
                "ver": self.ver
            })
        else:
            photo = await self.requester("images/common/photono.jpg", output = "content")
        return user, photo

    async def regions(self) -> list:
        return (await self.requester("/webapi/prepareloginform"))

    async def subjects_class(self, class_id: Optional[int] = 0) -> list:
        return (await self.requester(f"/webapi/subjectgroups", params = {"classId": class_id, "expand": "name"}))
    
    async def school_search(self, name: Optional[str] = "") -> list:
        params = {}
        if name:
            params['name'] = name
        return (await self.requester(f"/webapi/schools/search", params = params))
    
    async def cities(self, disctrict: int, state: int, country: int) -> list:
        cities = await self.requester("/webapi/loginform", params = {
            "cid": country,
            "sid": state,
            "pid": disctrict,
            "LASTNAME": "pid"
        })
        return cities
    
    async def teachers(self) -> dict:
        classes = await self.classes()
        result = {}
        for class_ in classes:
            for chief in class_['chiefs']:
                result[chief['id']] = chief['name']
        result = dict(sorted(result.items(), key=lambda item: item[1]))
        return result
    
    async def logout(self) -> bool:
        await self.requester("/webapi/auth/logout", method = "POST", data = {"at": self.access_token, "ver": self.ver}, output = "raw")
        await self.client.close()
        return True

    async def requester(self, url: str, method: str = "GET",params: dict = {}, data: dict = {}, json: dict = {}, output: str = 'json') -> Union[str, dict, bytes]:
        if data:
            async with self.client.request(method, url, params=params, data=data) as response:
                return (await self.requester_response(response, output))
        else:
            async with self.client.request(method, url, params=params, json=json) as response:
                return (await self.requester_response(response, output))
            
    async def requester_response(self, response: ClientResponse, output: str = 'json') -> Union[str, dict, bytes]:
        if output == "json":
            return (await response.json())
        elif output == "raw":
            return (await response.text())
        elif output == "content":
            return await (response.read())
        elif output == "cookies":
            return self.client.cookie_jar
        elif output == "status":
            return True if response.status == 200 else False
        
    async def __aenter__(self, *args):
        if self.school:
            await self.login()
    
    async def __aexit__(self, *args):
        if self.school:
            await self.logout()
        return True
