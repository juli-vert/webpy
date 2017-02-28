import web
from web import form
import sys
import time
from pyzabbix import ZabbixAPI
from datetime import datetime

render = web.template.render('templates/')
urls = (
    '/', 'index'
)

class results:
    valors = []
    sum = 0

    def __init__(self):
	self.sum = 0
    def addvalue(self,v):
	self.valors.append(v)
    def getvalues(self):
	return self.valors
    def setsum(self,s):
	self.sum = s
    def getsum(self):
	return self.sum 

# ~~ function to get data
def getdata(item,time_from,time_till,user,password):
    if item == "lumbar":
        item = "41334"
    elif item == "knee":
        item = "41333"

    z = ZabbixAPI("https://zabbix.telemedicineclinic.com/zabbix")
    z.login(user,password)
    h = z.history.get(itemids=[item],time_from=time_from,time_till=time_till,output='extend',limit='5000',)
    res = results()
    sum = 0
    for e in h:
        res.addvalue(str(e['value']))
        sum += int(e['value'])
    res.setsum(str(sum))    
    return res

app = web.application(urls, globals())
zabs = form.Form(
    form.Textbox('username'),
    form.Password('password'),
    form.Textbox('number_of_days'),
    form.Dropdown('Sort_of_cases', [('knee','knee'),('lumbar','lumbar')]),
    #form.Button('Submit'),
    validators = [form.Validator("Option not valid", lambda i: i.Sort_of_cases == "knee" or i.Sort_of_cases == "lumbar")]
)


class index:
    def GET(self):
	form = zabs()
        return render.formtest(form)
    def POST(self):
	form = zabs()
	if not form.validates():
	    return render.formtest(form)
	else:
	    dat = results()
	    ndays = int(form['number_of_days'].value)
	    time_till = time.mktime(datetime.now().timetuple())
    	    time_from = time_till - 60*60*24*ndays
	    dat = getdata(form['Sort_of_cases'].value,time_from,time_till,form['username'].value,form['password'].value)
	    out = ""
            for n in dat.getvalues():
		iday = datetime.fromtimestamp(time_till - 60*60*24*int(ndays)).strftime("%Y-%m-%d")
		out = '{0}{1}{2}{3} {4}{5}'.format(out,"\n","Day: ",iday,str(n)," cases")
		ndays -= 1
	    out = '{0}{1}{2}{3}'.format(out,"\n","The total number of cases is: ",str(dat.getsum()))
	    return out

if __name__ == "__main__":
    web.internalerror = web.debugerror
    app.run()


