#coding=utf8

def has_style(tag):
	return tag.has_attr('style')

def has_class(tag):
	return tag.has_attr('class')

def clean(soup):
	if soup.name == 'br' or soup.name == 'img' or soup.name == 'p' or soup.name == 'div':
		return
	try:
		ll = 0
		for j in soup.strings:
			ll += len(j.replace('\n', ''))
		if ll == 0:
			soup.decompose()
		else:
			for child in soup.children:
				clean(child)
	except Exception as e:
		pass
		
def dfs(soup, v):
	if soup.name == 'a' or soup.name == 'br':
		return
	try:
		lt = len(soup.get_text())
		ls = len(str(soup))
		a = soup.find_all('a')
		at = 0
		for j in a:
			at += len(j.get_text())
		lvt = lt - at
		v.append((soup, lt / ls * lvt))
		for child in soup.children:
			dfs(child, v)
	except Exception as e:
		pass

def extract(soup, text_only = True, remove_img = True):
	filt = ['script', 'noscript', 'style', 'embed', 'label', 'form', 'input', 'iframe', 'head', 'meta', 'link', 'object', 'aside', 'channel']
	if remove_img:
		filt.append('img')
	for ff in filt:
		for i in soup.find_all(ff):
			i.decompose()
	for tag in soup.find_all(has_style):
		del tag['style']
	for tag in soup.find_all(has_class):
		del tag['class']
	clean(soup)
	LVT = len(soup.get_text())
	for i in soup.find_all('a'):
		LVT -= len(i.get_text())
	v = []
	dfs(soup, v)
	mij = 0
	for i in range(len(v)):
		if v[i][1] > v[mij][1]:
			mij = i
	if text_only:
		res = v[mij][0].get_text()
	else:
		res = str(v[mij][0])
	return res, v[mij][1] / LVT if LVT > 0 else v[mij][1]

