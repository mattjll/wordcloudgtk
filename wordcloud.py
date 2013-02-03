#!/usr/bin/env python2
import gtk
import os, sys, re, random, time
from collections import Counter, defaultdict
from ConfigParser import SafeConfigParser
import nltk
import datetime

commonwords = ""
workingdir = os.getcwd()
config_file = "/home/matt/Installs/wordcounter.cfg"
default_common = "ignore"
default_save = os.getenv("HOME")
if not os.path.exists(config_file):
	confcreate = open(config_file, "w")
	confcreate.write(default_common + "\n" + default_save)
	confcreate.close()
#also create imagefldr
imagefldr = "/tmp/wordcloudimge/"
posfldr = "/tmp/wordcloudpos/"
if not os.path.exists(imagefldr):
	os.makedirs(imagefldr)
if not os.path.exists(posfldr):
	os.makedirs(posfldr)

#window create
window = gtk.Window()
window.connect("delete-event", gtk.main_quit)
window.set_default_size(650, 400)
window.set_title("WordCloud")
window.set_icon_from_file("wordcloud.png")

#functions
#remove common words
def listrm(thelist, val):
	return [value for value in thelist if value != val]


def progress_changed(amount):
	progress.set_fraction(amount)
	
#spawns the file chooser (for text file analysis)
def get_choosefile(filechoose_but):
	chooser = gtk.FileChooserDialog("Chooser", action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL , gtk.RESPONSE_CANCEL , gtk.STOCK_OPEN , gtk.RESPONSE_OK))
	if chooser.run() == gtk.RESPONSE_OK:
		global chooser_result
		chooser_result = chooser.get_filename()
		statusbar.push(context_id, "File \'" + chooser_result + "\' is selected!")
	chooser.destroy()
	
def get_commonfile(common_but):
	common_choose = gtk.FileChooserDialog("Commonwords File Chooser", action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL , gtk.RESPONSE_CANCEL , gtk.STOCK_OPEN , gtk.RESPONSE_OK))
	if common_choose.run() == gtk.RESPONSE_OK:
		global common_result
		common_result = common_choose.get_filename()
		# write result to the config file
		parser = SafeConfigParser()
		parser.read(config_file)
		parser.set('general', 'common', common_result)
		with open(config_file, 'wb') as parserfile:
			parser.write(parserfile)
		#set label - but this can't see the label object
		common_txt.set_text(common_result)
		
	common_choose.destroy()

def get_savefldr(savefldr_but):
	savefldr_choose = gtk.FileChooserDialog("Save Folder Chooser", action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL , gtk.RESPONSE_CANCEL , gtk.STOCK_OPEN , gtk.RESPONSE_OK))
	if savefldr_choose.run() == gtk.RESPONSE_OK:
		global savefldr_result
		savefldr_result = savefldr_choose.get_filename()
		# write result to the config file
		parser = SafeConfigParser()
		parser.read(config_file)
		parser.set('general', 'savefldr', savefldr_result)
		with open(config_file, 'wb') as parserfile:
			parser.write(parserfile)
		savefldr_txt.set_text(savefldr_result)
		
	savefldr_choose.destroy()


def settings_open(settings_but):
	
	settings_win.show_all()



#then main wordcounter image gen stuff
def imgen_activate(imgen_but):
	
	try:
		print chooser_result
		statusbar.remove_all(context_id)
	except NameError:
		statusbar.push(context_id, "Please Choose a file!")
	
	#gui stuff
	imgen_image.clear()
	statusbar.push(context_id, "Making your word cloud!")
	
	#define list of common words from file
	print "Checking for common words!"
	commonwords = open('/home/matt/Installs/Projects/wordcounter/commonwords.txt').read()
	commonwords = commonwords.lower()
	commonwords = re.findall(r'\w+', commonwords)
	
	# read main text file
	print "Reading your input text!"
	filetxt = open(chooser_result).read()
	filetxt = filetxt.lower()
	#sort by whitespace
	sep = re.findall(r'\w+', filetxt)
	
	#do for i in commonwords - remove those words from sep
	for i in commonwords:
		sep = listrm(sep, i)
	
	#count all the words in sep
	cnt = Counter(sep)

	#make dict with words and counts
	freqword = defaultdict(list)
	for word, freq in cnt.items():
		freqword[freq].append(word)
	
		
	#print in order
	print "Making initial images!"
	occ = freqword.keys()
	occ.sort()
	for freq in occ:
		freqword[freq].sort() # sort into list
		print "count {}: {}".format(freq, freqword[freq])
		#make image per word based on its frequency between 1 and 100
		freqrange = range(2, 100)
		for e in freqrange:
			if freq == e:
				#print e
				#print "count {}: {}".format(freq, freqword[freq])
				estring = str(e)
				#print estring
				for i in freqword[freq]:
					#print i
					fontsize = e + e + 10
					fontsize = str(fontsize)
					os.system("convert -font Courier  -density 80  -pointsize " + fontsize +  " label:" + i + " +append " +  imagefldr + estring + "-" + i + ".jpg")
	
	
	#make a final large image with all the word images
	print "Making the final big image!"
	imagelist = os.listdir(imagefldr)
	imagestring = " ".join(imagelist)
	os.chdir(imagefldr)
	print imagestring
	
	uhome = os.getenv("HOME")
	#check for existing montage.png and add date
	img_outname = "montage.png"
	uhomelist = os.listdir(uhome)
	if "montage.png" in uhomelist:
		ctime = datetime.datetime.now()
		ctime = ctime.strftime("%d-%m-%Y_%H:%M")
		
		img_outname = "montage-" + ctime + ".png"
	os.system("montage " + imagestring + " -tile 10x -geometry +5+5 $HOME/" + img_outname)
	#remove small images
	for i in imagelist:
		if i != "montage.jpg":
			os.remove(i)
	print "DONE"
	os.chdir(workingdir)
	statusbar.push(context_id, "Done making your word cloud!")
	
	newmontage = gtk.gdk.pixbuf_new_from_file(uhome + "/" + img_outname)

	pbx,pby = newmontage.get_width(),newmontage.get_height()
	if pbx > 2000 or pby > 2000:
		newmontage = newmontage.scale_simple(int(pbx/2.5),int(pby/2.5),gtk.gdk.INTERP_BILINEAR)
		pbx,pby = newmontage.get_width(),newmontage.get_height()
	if pbx > 1000:
		newmontage = newmontage.scale_simple(int(pbx/1.5),int(pby/1.5),gtk.gdk.INTERP_BILINEAR)
		pbx,pby = newmontage.get_width(),newmontage.get_height()
	if pby > 800:
		newmontage = newmontage.scale_simple(int(pbx/1.5),int(pby/1.5),gtk.gdk.INTERP_BILINEAR)
		pbx,pby = newmontage.get_width(),newmontage.get_height()
	if pby > 700:
		newmontage = newmontage.scale_simple(int(pbx/1.3),int(pby/1.3),gtk.gdk.INTERP_BILINEAR)
		pbx,pby = newmontage.get_width(),newmontage.get_height()
	
	imgen_image.set_from_pixbuf(newmontage)
	print "x: ",pbx,"y: ",pby
	imgenset = True
	return imgenset

def posgen_activate(pos_but):
	os.chdir(workingdir)
	poscommon = [",", "."]
	
	statusbar.push(context_id, "Making your POS cloud!")
	
	# read main text file
	print "Reading your input text!"
	filetxt = open(chooser_result).read()
	#make lowercase
	filetxt = filetxt.lower()
	
	#nltk!
	#tokens
	tokens = nltk.word_tokenize(filetxt)
	print tokens
	
	#pos
	tagged = nltk.pos_tag(tokens)
	print tagged
	taglist = []
	for i in tagged:
		print i[1]
		taglist.append(i[1])
	for i in poscommon:
		taglist = listrm(taglist, i)
	
	poscnt = Counter(taglist)
	freq_pos = defaultdict(list)
	for word, freq in poscnt.items():
		freq_pos[freq].append(word)
	occ = freq_pos.keys()
	occ.sort()
	for freq in occ:
		freq_pos[freq].sort() # sort into list
		print "count {}: {}".format(freq, freq_pos[freq])
		#works so far
		freqrange_pos = range(1, 200)
		for e in freqrange_pos:
			if freq == e:
				#print e
				#print "count {}: {}".format(freq, freqword[freq])
				estring = str(e)
				#print estring
				for i in freq_pos[freq]:
					#print i
					fontsize = e + 10
					fontsize = str(fontsize)
					os.system("convert -font Courier  -density 80  -pointsize " + fontsize +  " label:" + i + " +append " +  posfldr + estring + "-" + i + ".jpg")
	
	print "Making the final big image!"
	imagelist_pos = os.listdir(posfldr)
	random.shuffle(imagelist_pos)
	imagestring_pos = " ".join(imagelist_pos)
	os.chdir(posfldr)
	
	uhome = os.getenv("HOME")
	#check for existing montage.png and add date
	uhomelist = os.listdir(uhome)
	pos_outname = "montage_pos.png"
	if "montage_pos.png" in uhomelist:
		ctime = datetime.datetime.now()
		ctime = ctime.strftime("%d-%m-%Y_%H:%M")
		pos_outname = "montage_pos-" + ctime + ".png"
	
	print imagestring_pos
	os.system("montage " + imagestring_pos + " -tile 6x -geometry +5+5 $HOME/" + pos_outname)
	#works but the sizes for the first images needs tweaking!
	
	print "posDONE"
	os.chdir(workingdir)
	statusbar.push(context_id, "Done making your POS cloud!")

	newposmontage = gtk.gdk.pixbuf_new_from_file(uhome + "/" + pos_outname)
	pbmx,pbmy = newposmontage.get_width(),newposmontage.get_height()
	if pbmx > 2000 or pbmy > 2000:
		newposmontage = newposmontage.scale_simple(int(pbmx/2.5),int(pbmy/2.5),gtk.gdk.INTERP_BILINEAR)
		pbmx,pbmy = newposmontage.get_width(),newposmontage.get_height()
	if pbmx > 1000:
		newposmontage = newposmontage.scale_simple(int(pbmx/1.5),int(pbmy/1.5),gtk.gdk.INTERP_BILINEAR)
		pbmx,pbmy = newposmontage.get_width(),newposmontage.get_height()
	if pbmy > 800:
		newposmontage = newposmontage.scale_simple(int(pbmx/1.5),int(pbmy/1.5),gtk.gdk.INTERP_BILINEAR)
		pbmx,pbmy = newposmontage.get_width(),newposmontage.get_height()
	if pbmy > 700:
		newposmontage = newposmontage.scale_simple(int(pbmx/1.3),int(pbmy/1.3),gtk.gdk.INTERP_BILINEAR)
		pbmx,pbmy = newposmontage.get_width(),newposmontage.get_height()
	
	pos_image.set_from_pixbuf(newposmontage)
	print "x: ",pbmx,"y: ",pbmy
	
#settings window setup
settings_win = gtk.Window()
settings_win.set_default_size(300, 200)
settings_win.set_resizable(False)
settings_win.set_title("WordCloud Settings")
settings_win.set_icon_from_file("wordcloud.png")
settings_win.set_destroy_with_parent(True)

#parser
parser = SafeConfigParser()
parser.read(config_file)
common_value = parser.get('general', 'common')
savefldr_value = parser.get('general', 'savefldr')

#set commonwords file
common_but = gtk.Button("Commonwords")
common_but.set_size_request(125, -1)
common_but.connect("clicked", get_commonfile)
common_txt = gtk.Label("Filename here.")
common_txt.set_text(common_value)
common_hbox = gtk.HBox()
common_hbox.pack_start(common_but, False)
common_hbox.pack_start(common_txt, False)

#set image save folder
savefldr_but = gtk.Button("Save Folder")
savefldr_but.set_size_request(125, -1)
savefldr_but.connect("clicked", get_savefldr)
savefldr_txt = gtk.Label("Filename here.")
savefldr_txt.set_text(savefldr_value)
savefldr_hbox = gtk.HBox()
savefldr_hbox.pack_start(savefldr_but, False)
savefldr_hbox.pack_start(savefldr_txt, False)

#set on/off word instances in small images
count_but = gtk.CheckButton(label="Show wordcount?")
count_hbox = gtk.HBox()
count_hbox.pack_start(count_but, False)


settings_vbox = gtk.VBox(homogeneous=True)
sett_hsep1 = gtk.HSeparator()
sett_hsep2 = gtk.HSeparator()
common_label = gtk.Label("Set the text file to read common words from:")
savefldr_label = gtk.Label("Set the folder to save the final files to:")
count_label = gtk.Label("Check to show wordcounts in the final image:")

settings_vbox.pack_start(common_label, False)
settings_vbox.pack_start(common_hbox, False)
settings_vbox.pack_start(sett_hsep1, False)
settings_vbox.pack_start(savefldr_label, False)
settings_vbox.pack_start(savefldr_hbox, False)
settings_vbox.pack_start(sett_hsep2, False)
settings_vbox.pack_start(count_label, False)
settings_vbox.pack_start(count_hbox, False)

settings_win.add(settings_vbox)

############

#widgets
hbox1 = gtk.HBox()
vbox1 = gtk.VBox()
toolbar = gtk.Toolbar()
imgen_image = gtk.Image() # add in imgen_file later
imgen_image.set_from_file("wordcloud.png")
pos_image = gtk.Image()

#imgen button
imgen_but = gtk.Button()
imgen_but.connect("clicked", imgen_activate)
imgen_icon = gtk.Image()
imgen_icon.set_from_stock(gtk.STOCK_OK, gtk.ICON_SIZE_SMALL_TOOLBAR)
imgen_label = gtk.Label()
imgen_label.set_text(" Generate Word Cloud!")
imgen_hbox = gtk.HBox()
imgen_hbox.pack_start(imgen_icon)
imgen_hbox.pack_start(imgen_label)
imgen_but.add(imgen_hbox)

#filechoose button
filechoose_but = gtk.Button()
filechoose_but.connect("clicked", get_choosefile)
filechoose_icon = gtk.Image()
filechoose_icon.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_SMALL_TOOLBAR)
filechoose_label = gtk.Label()
filechoose_label.set_text(" Pick text file!")
filechoose_hbox = gtk.HBox()
filechoose_hbox.pack_start(filechoose_icon)
filechoose_hbox.pack_start(filechoose_label)
filechoose_but.add(filechoose_hbox)

#POS button
pos_but = gtk.Button()
pos_but.connect("clicked", posgen_activate)
pos_icon = gtk.Image()
pos_icon.set_from_stock(gtk.STOCK_OK, gtk.ICON_SIZE_SMALL_TOOLBAR)
pos_label = gtk.Label()
pos_label.set_text(" Generate POS Cloud!")
pos_hbox = gtk.HBox()
pos_hbox.pack_start(pos_icon)
pos_hbox.pack_start(pos_label)
pos_but.add(pos_hbox)

#settings button
settings_but = gtk.Button(stock=gtk.STOCK_PREFERENCES)
settings_but.connect("clicked", settings_open)


#separator and bar
hsep = gtk.HSeparator()
statusbar = gtk.Statusbar()
context_id = statusbar.get_context_id("Statusbar")
progress = gtk.ProgressBar()

#boxes
hbox1.pack_start(toolbar)
vbox1.pack_start(hbox1, False)
vbox1.pack_start(hsep, False)
vbox1.pack_start(imgen_image)
vbox1.pack_start(pos_image)
vbox1.pack_start(statusbar, False)
#vbox1.pack_start(progress, False)
toolbar.add(filechoose_but)
toolbar.add(imgen_but)
toolbar.add(pos_but)
toolbar.add(settings_but)

#windowadd
window.add(vbox1)
#show all widgets
window.show_all()
#main call for gtk
gtk.main()
