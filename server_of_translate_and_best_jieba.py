import jieba,requests,re
from pprint import pprint
from flask import Flask
from flask import request
from urllib.parse import quote
from flask_cors import CORS


app=Flask(__name__)

CORS(app)

@app.route('/',methods=['GET'])
def init():
	return 'init'

@app.route('/testpost',methods=['POST'])
def testpost():
	return 'testpost'

@app.route('/trans',methods=['POST'])
def get_all_trans():
	data=request.data.decode()
	data=data.split('\n\n')
	data=[re.sub(r'\s+',' ',i).strip() for i in data]
	dot_lst=split_by_dot(data)
	trans_lst=get_all_trans(dot_lst)
	#  [st,ed] trans
	trans_len=len(trans_lst)
	res=[]
	for i in range(trans_len):
		if i==trans_len-1:
			ed=len(data)-1
		else:
			ed=trans_lst[i+1][0]-1
		st=trans_lst[i][0]
		tmp=split_trans(st, ed, trans_lst[i][1], data)
		for j in tmp:
			res.append(j)
	res=runse_trans(res)
	return '\n\n'.join(res)

def runse_trans(trans_set):
	len_set=len(trans_set)
	for i in range(len_set):
		mat=re.findall(r'^([\!\！\.\?\。\？\]\】\,\，])',trans_set[i])
		if mat and i!=0:
			trans_set[i-1]+=mat[0]
			trans_set[i]=trans_set[i][len(mat[0]):]
	return trans_set


def split_trans(st, ed, trans, data):
	_2=list(jieba.cut(trans))
	str=''
	pre_cut=0
	total_str_len=len(' '.join(data[st:ed+1]))
	res=[]
	for i in range(st,ed+1):
		now_cut=int(len(' '.join(data[st:i+1]))/total_str_len*len(_2)+0.520)
		res.append(''.join(_2[pre_cut:now_cut]))
		pre_cut=now_cut
	return res

def get_all_trans(dot_lst):
	# 减少调用get_trans的次数
	trans=''
	cur=0
	trans_lst=[]
	for dot in dot_lst:
		if len(dot[1])+2+len(trans)<5000:
			if trans=='':
				trans=dot[1]
			else:
				trans+='\n\n'+dot[1]
		else:
			# 注意未翻译当前的句子
			trans=get_trans(trans)
			trans=trans.split('\n\n')
			for tran in trans:
				trans_lst.append([dot_lst[cur][0],tran])
				cur=cur+1
			trans=dot[1]
	if len(trans)>5000:
		trans=trans.split('\n\n')
		for tran in trans:
			trans_lst.append([dot_lst[cur][0],tran])
			cur=cur+1
	elif len(trans)!=0:
		trans=get_trans(trans)
		trans=trans.split('\n\n')
		for tran in trans:
			trans_lst.append([dot_lst[cur][0],tran])
			cur=cur+1
	return trans_lst

def split_by_dot(data):
	trans=''
	data_len=len(data)
	dot_lst=[]
	pre=0
	for i in range(data_len):
		if trans=='':
			trans=data[i]
		else:
			trans+=' '+data[i]
		if i==data_len-1 or re.findall(r'[\!\！\.\?\。\？\]\】]\s*$',trans):
			dot_lst.append([pre,trans])
			pre=i+1
			trans=''
	return dot_lst

def get_trans(str):
	trans=''
	r=requests.get('https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh&dt=t&q='+quote(str),
		headers={
		'user-agent':'from python'
		}).json()
	for ii in r[0]:
		trans+=ii[0]
	return trans

if __name__=='__main__':
	app.run('0.0.0.0',5020,debug=True, ssl_context='adhoc')
