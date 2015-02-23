"""Inkscape Gradient Cleaner"""
# Jeffrey N. Murphy
# Created: 2015.02.16

"""
Useful References:

* http://stackoverflow.com/questions/15857818/python-svg-parser
* https://docs.python.org/2/library/xml.dom.minidom.html
* https://wiki.python.org/moin/MiniDom
* http://www.tutorialspoint.com/python/python_xml_processing.htm
* http://www.bitpapers.com/2012/04/python-removing-node-from-dom-tree.html
* http://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
* https://wiki.python.org/moin/Tutorials%20on%20XML%20processing%20with%20Python
* http://stackoverflow.com/questions/2951071/editing-xml-file-content-with-python
* 
"""

from xml.dom import minidom
import os

xmldoc = minidom.parse('C:\Users\Jeffrey\Desktop\introductory figure 11p rec.svg')
output_filename = "introductory figure 11p rec clean.svg"
output = os.path.join("C:\Users\Jeffrey\Desktop",output_filename)

## for RECT & PATH
## Presumes format: style="fill:url(#linearGradient3775);fill-opacity:1;stroke:none"
def findAndReplace(style,dup_ids,dup_replace):
	a = style.split(";")
	lingrad = a[0][10:-1]
	match = 0
	for i in range(0,len(dup_ids)):
		if lingrad == dup_ids[i]:
			replace = dup_replace[i]
			i = len(dup_ids)
			match = 1
	if match:
		print(str(i) + " " + replace)
	else:
		print("no match")

def findAndReplaceXlink(xlink,dup_ids,dup_replace):
	lingrad = xlink[1:]
	match = 0
	for i in range(0,len(dup_ids)):
		if lingrad == dup_ids[i]:
			replace = dup_replace[i]
			i = len(dup_ids)
			match = 1
	if match:
		print(str(i) + " " + replace)
	else:
		print("no match")

def recursivetagsG(xmlsource,tags):
	items = []
	for t in tags:
		ti = xmlsource.getElementsByTagName(t)
		for i in ti:
			items.append(i)
	for g in xmlsource.getElementsByTagName("g"):
		recursivetagsG(g,tags)
	return items



itemlist = xmldoc.getElementsByTagName('linearGradient')

gradientduplicates = list(itemlist)
gradientswithstops = list(itemlist)
gradientkeepers = list(itemlist)
for i in range(0,len(gradientduplicates)):
	gradientduplicates[i] = i
	gradientswithstops[i] = len(itemlist[i].getElementsByTagName('stop'))
	gradientkeepers[i] = 0
gradientkeepers[0] = 1

"""
print(gradientduplicates)

print(len(itemlist))
for s in itemlist :
	print(s.attributes['id'].value)
	stop = s.getElementsByTagName('stop')
	for t in stop:
		print(t.attributes['offset'].value)
		print(t.attributes['style'].value)
"""

for i in range(0,len(itemlist)-1):
	stops_i = itemlist[i].getElementsByTagName('stop')
	if gradientswithstops[i] > 0:
		for j in range(i+1,len(itemlist)):
			if (gradientduplicates[j] == j) and (gradientswithstops[i] == gradientswithstops[j]): 					# checks to see if it's already been processed and found to be identical
				stops_j = itemlist[j].getElementsByTagName('stop')
				matches = 1
				for k in range(0,len(stops_i)):
					offset_i = stops_i[k].getAttribute("offset")
					offset_j = stops_j[k].getAttribute("offset")
					styles_i = stops_i[k].getAttribute("style")
					styles_j = stops_j[k].getAttribute("style")
					if (offset_i == offset_j) and (styles_i == styles_j):
						matches = matches
					else:
						matches = 0
				if matches:
					gradientduplicates[j] = i
					gradientkeepers[i] = gradientkeepers[i] + 1
				else:
					gradientkeepers[j] = 1



#print(itemlist[5].attributes['id'].value)	# just a test



#print(gradientduplicates)
#print(gradientswithstops)
#print(gradientkeepers)

gk = gradientkeepers
gd = gradientduplicates

gdc = 0 # gradient duplicate count
gkc = 0 # gradient keeper count
for i in range(0,len(gd)):
	if gk[i] > 1:
		gdc = gdc + gk[i] - 1
	if gk[i] > 0:
		gkc = gkc + 1
print("Gradient Keepers: " + str(gkc))
print("Gradient Duplicates: " + str(gdc))

""" Find the duplicates """ 

dups = [] # duplicates list
dup_ids = []
dup_replace = []

for i in range(0,len(gk)):
	if gk[i] > 1:
		for j in range(i+1,len(gk)):
			if gd[j] == i:
				dups.append(j)
				dup_ids.append(itemlist[j].attributes['id'].value)
				dup_replace.append(itemlist[i].attributes['id'].value)

print("Dups:")
print(dups)
print("Dup IDs:")
print(dup_ids)
print("Dup Replaceme:")
print(dup_replace)

""" Remove the duplicate gradients """ 

for i in range(0,len(dups)):
	p = itemlist[dups[i]].parentNode
	p.removeChild(itemlist[dups[i]])


"""Correct all remaining notes referencing the deleted gradients"""

#tags = ["rect","path","text"] - the problem isn't with these: they simply reference gradients which have specific coordinates.
# every gradient is actually 2 sets of stuff: (1) is the colour map & (2) is the coordinate map
# the problem is that (1) keeps getting duplicated for (2)
tags = ["linearGradient","radialGradient"]
grad_items = recursivetagsG(xmldoc,tags)

for entry in grad_items:
	if len(entry.getElementsByTagName('stop')) == 0:
 		style = entry.attributes['xlink:href'].value
 		for i in range(0,len(dup_ids)):
 			if style[1:] == dup_ids[i]:
 				#print("true " + style)
 				entry.setAttribute("xlink:href", "#" + dup_replace[i])


"""Remove unused gradients?"""

## Find all gradients used by the objects
tags = ["rect","path","text"]
svg_items = recursivetagsG(xmldoc,tags)
svg_items_grad_refs = []  # a list for every gradient referenced by the objects (rect, path, text)
svg_items_grad_entries = []

for entry in svg_items:
	style = entry.attributes['style'].value
	if len(style.split(";")[0]) > 12:
		svg_items_grad_refs.append(style.split(";")[0][10:-1])
		svg_items_grad_entries.append(entry)

print(svg_items_grad_refs)

## Find all reference-gradients listed: grad_items
print("")

grad_items_ids = []

for entry in grad_items:
	if len(entry.getElementsByTagName('stop')) == 0: ## only secondary gradients (no stops tags)
		match = 0
		entry_id = entry.attributes['id'].value
		#print(entry_id)
		grad_items_ids.append(entry_id)
		#for i in range(0,len(svg_items_grad_refs)):
		#	if 
print(grad_items_ids)


## Find all gradients that are not referneced:
unreferenced_gradients = []

for item in grad_items_ids:
	match = 0
	for obj in svg_items_grad_refs:
		if obj == item:
			match = 1
	if match == 0:
		#print(item + " not referenced")
		unreferenced_gradients.append(item)
print("\nGRADIENTS NOT REFERNECED")
print(unreferenced_gradients)

## Delete the nodes of unreferneced gradients:

for entry in grad_items:
	grad_id = entry.attributes['id'].value
	if grad_id in unreferenced_gradients:
		p = entry.parentNode
		p.removeChild(entry)


"""Simplify Names of Gradients"""


"1. Gradients"
tags = ["linearGradient","radialGradient"]
new_grad_items = recursivetagsG(xmldoc,tags)

#new grad items:
ngi_n = [] #no stops
ngi_n_ref = []
ngi_n_id = []
ngi_s = [] #stops
ngi_s_id = []

for entry in new_grad_items:
	if len(entry.getElementsByTagName('stop')) == 0:
 		ngi_n_ref.append(entry.attributes['xlink:href'].value[1:])
 		ngi_n_id.append(entry.attributes['id'].value)
 		ngi_n.append(entry)
 	else:
 		ngi_s_id.append(entry.attributes['id'].value)
 		ngi_s.append(entry)

print("\nGRADIENTS REFERNECED")
print("Stops:")
print(ngi_s_id)
print("No Stops:")
print(ngi_n_id)

"2. Objects"
"Most of this is already done"
#tags = ["rect","path","text"]
#svg_items = recursivetagsG(xmldoc,tags)
#svg_items_grad_refs = []  # a list for every gradient referenced by the objects (rect, path, text)

"3. Map"


ngi_map = [-1]*len(ngi_n_id)
svg_items_map = [-1]*len(svg_items_grad_refs)

"svg object --> no stops:"
for i in range(0,len(svg_items_grad_refs)):
	for j in range(0,len(ngi_n_id)):
		if svg_items_grad_refs[i] == ngi_n_id[j]:
			svg_items_map[i] = j

print("no stops --> main gradients")
for i in range(0,len(ngi_n_ref)):
	for j in range(0,len(ngi_s_id)):
		if ngi_n_ref[i] == ngi_s_id[j]:
			ngi_map[i] = j


print("\nGRADIENTS REFERNECED:")
print("svg object --> no stops:")
print(svg_items_map)
print("no stops --> main gradients")
print(ngi_map)


"4. Assign new names"

new_original_gradients = [0]*len(ngi_s_id)
new_nostop_gradients = [0]*len(ngi_n_id)

for i in range(0,len(new_original_gradients)):
	value = ngi_s_id[i][0:14] + str(1000 + i)
	new_original_gradients[i] = value
	count = 1
	print(new_original_gradients[i])
	for j in range(0,len(ngi_map)):
		if ngi_map[j] == i:
			value = new_original_gradients[i] + "-" + str(count)
			new_nostop_gradients[j] = value
			count = count + 1
			print(new_nostop_gradients[j])


"5. Rename everything"

"Orginal Gradients [stops]"
for i in range(0, len(ngi_s)):
	entry = ngi_s[i]
	entry.setAttribute("id",new_original_gradients[i])

"NoStop Gradients [no stops]"
for i in range(0, len(ngi_n)):
	entry = ngi_n[i]
	entry.setAttribute("id",new_nostop_gradients[i])
	entry.setAttribute("xlink:href", "#" + new_original_gradients[ngi_map[i]])

"SVG Items"
for i in range(0, len(svg_items_grad_entries)):
	entry = svg_items_grad_entries[i]
	style = entry.attributes['style'].value
	if style[10:16] == "radial" or style[10:16] == "linear":
		style = style.replace(svg_items_grad_refs[i],new_nostop_gradients[svg_items_map[i]]) #ref: http://www.tutorialspoint.com/python/string_replace.htm
		entry.setAttribute("style",style)


""" old code:
for entry in svg_items:
	style = entry.attributes['style'].value
	if len(style.split(";")[0]) > 12:
		svg_items_grad_refs.append(style.split(";")[0][10:-1])
		svg_items_grad_entries.append(entry)

svg_items_grad_refs.append(style.split(";")[0][10:-1])
"""


# How to Save: http://stackoverflow.com/questions/9912578/how-to-save-an-xml-file-to-disk-with-python
# https://docs.python.org/2/library/xml.dom.minidom.html
# http://stackoverflow.com/questions/18533621/creating-a-new-text-file-with-python

f = open(output,'w') 
xmldata = xmldoc.toxml()
f.write(xmldata)
f.close()

xmldoc.unlink()


"""
Limitations:
1. It presumes that all "stroke" values are solid. Hence it will likely mess-up if a stroke has a gradient. (easy to fix, but no time now)

"""