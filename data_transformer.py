'''
{
    "mailID": 123456,
    "title": "xxx",
    "topicContent": "xxx",
    "topicAuthorLogin": "xxx",
    "topicAuthorEmail": "xxx",
    "replyAuthor": "xxx",
    "replyAuthorEmail": "xxx",
    "replyTime": "xxxx",
    "replyContent": "xxxx"
}

'''
import os
import email 
import json

# 可以解析mbox中的内容。
'''
    mailboxname = "mbox/m.__0712eKRIM.Hsm5VzCXCAAJ"
    # m._5nvtE9_qy0.ysUgEMm7AAAJ
    mailboxname = "mbox/m._5nvtE9_qy0.ysUgEMm7AAAJ"
    worker = data_tran_for_item(mailboxname)
    worker.extractItem()

    print(worker.mailID)
    print(worker.title)
    print(worker.Email)
    print(worker.Time)
    # print(worker.topicContent)
    print( email.utils.mktime_tz(email.utils.parsedate_tz(worker.Time)))    
'''

class data_tran_for_item:
    def __init__(self,mailboxname):
        self.mailboxname = mailboxname

        self.mailID = 0
        self.title = 'xxx' # Subject
        self.topicContent = 'msg maybe lost!'
        self.Login = 'xxx'
        self.Email = 'xxx'
        # print( email.utils.mktime_tz(email.utils.parsedate_tz(worker.Time)))    
        self.Time = 'Wed, 19 Sep 3000 02:41:19 -0700 (PDT)'

    def extractContent(self, part):
        cur = part.get_content_type()
        if part['Content-Transfer-Encoding'] != None:
            cur += '[' + part["Content-Transfer-Encoding"] + ']\t\n' 
        else:
            cur += '[ None ]\t\n'
        if part.is_multipart():
            for p in part.get_payload():
                res = cur + self.extractContent(p)
        else :
            res = cur + part.get_payload()
        return res


    def extractItem(self):
        with open(self.mailboxname) as fp:
            msg = fp.read()
        
        headers = email.message_from_string(msg)
        # 目前就是login没有解决。
        self.mailID = '/'.join(self.mailboxname.split('.')[-2:])

        if headers["Date"] != None:
            self.title = headers["Subject"]
            self.Email = headers["From"]
            self.Time = headers["Date"]
            self.topicContent = self.extractContent(headers)
        '''
            mix
                alternative
                    text
                    html
                attachment 
        '''
       
class data_tran:
    def __init__(self, mailgroupname):
        self.mailboxworkers = []
        with open(mailgroupname, 'r') as f:
            for line in f:
                line = line.strip('\n')
                if '/msg/' in line:
                    tmp_mailboxnames = '.'.join(line.split('/')[-2:])
                    tmp_mailboxnames = 'mbox/m.' + tmp_mailboxnames
                    worker = data_tran_for_item(tmp_mailboxnames)
                    worker.extractItem()
                    self.mailboxworkers.append(worker)
    
    def create_date(self,worker):
        return  email.utils.mktime_tz(email.utils.parsedate_tz(worker.Time))

    def worker2dict(self, worker):
        res = {}
        res['mailID'] = worker.mailID
        res['title'] = worker.title
        res['Email'] = worker.Email
        res['Time'] = worker.Time
        res['topicContent'] = worker.topicContent
        return res


    def extract(self):
        '''
        {
            "mailID": 123456,
            "title": "xxx",
            "topicContent": "xxx",
            "topicAuthorLogin": "xxx",
            "topicAuthorEmail": "xxx",
            "replyAuthor": "xxx",
            "replyAuthorEmail": "xxx",
            "replyTime": "xxxx",
            "replyContent": "xxxx"
        }

        ''' 
        self.mailboxworkers.sort(key=self.create_date)
        res = self.worker2dict(self.mailboxworkers[0])
        res["replyMail"] = []
        for mbox in self.mailboxworkers[1:]:
            res["replyMail"].append(self.worker2dict(mbox))
        return res
        

if __name__ == "__main__":
    all_msg = []
    # mailgroupname = 'msgs/m.__0712eKRIM.0'
    # mailgroupname = 'msgs/m.zi5UWdfRdXc.0'
    # mailgroupname = 'msgs/m.ZzyYL2ov3S4.0'
    base = 'msgs/'
    for root, ds, fs in os.walk(base):
        for f in fs:
            if f.startswith('.'):
                continue
            print(f)
            mailgroupname = base + f
            msg_tran = data_tran(mailgroupname)
            all_msg.append(msg_tran.extract())
    
    print("finished!")
    with open('mailinglist_msg.json', 'w') as f:
        json.dump(all_msg, f , indent=2)