#TODO: Change to ItemTracker for final
#Author: Jana Haase
DATABASE = 'ItemTracker_test'

import sys, os
import site
site.addsitedir(r'B:\site-packages')

import pyodbc
from time import strftime

def Errorhandling(errormessage):
	global message
	message.append(errormessage)

def connectToDB(): # opens the connection to itemTracker#############################
	global conn, cursor
	try:
		conn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost;DATABASE=%s;UID=user;PWD=password' % DATABASE)
		cursor = conn.cursor()
	except:
		Errorhandling('Could not connect to ItemTracker')
		
def CommitChanges(): # commits changes and closes the connection #############################
	try:
		conn.commit()
		conn.close()
	except:		
		Errorhandling('Could not commit changes in ItemTracker')
		
def SelectFromDB(column,table,condition):

	sql = 'select %s from %s where %s ' % (column,table,condition)
	cursor.execute(sql)
	vals = cursor.fetchall()
	if len(vals):
		return vals
	else:
		Errorhandling('could not select %s from %s where %s' % (column,table,condition))
		
def SelectFromDBReturnNone(column,table,condition):

	sql = 'select %s from %s where %s ' % (column,table,condition)
	cursor.execute(sql)
	vals = cursor.fetchall()
	if len(vals):
		return vals
	else:
		return None	
	
def FillDict(dictionary,item):
	dictionary[item] = {}
	return dictionary[item]

def UpdateData(table,column,value,whereclause):
	try:
		sql = 'update %s set %s = %s where %s' %(table,column,repr(value),whereclause)
		cursor.execute(sql)
	except:	
		Errorhandling('could not update %s (%s) where %s' % (table,column,whereclause))

def InsertIntoDB(table,ColValDict):
	# ColValDict- columnnames is key
	try:
		sql = 'insert into %s (%s) values (%s)' % (table,', '.join(ColValDict.keys()),repr(ColValDict.values())[1:-1])
		cursor.execute(sql)
	except:
		Errorhandling('could not insert into %s values' % (table,ColValDict.values()))		
		
def GetDictionary(ItemIDs):
	global message, ItemProperties,ItemGroupDict
	message = []
	connectToDB()
	ItemProperties = {}
	FinalItemDict = {}
	ItemIDString = ''
	i = 0
	while i < len(ItemIDs):
		if ItemIDString == '':
			ItemIDString = 'ItemID = %d' % ItemIDs[i]
		else:
			ItemIDString = ItemIDString + ' or ItemID = %d' % ItemIDs[i]
		i = i+1

	Bacteria = SelectFromDBReturnNone('StrainID, AlternID,OriginalID,ItemID','ItemTable',ItemIDString)

	if Bacteria != None:
		BacteriaItemIDs = []
		for bacteriaitem in Bacteria:
			BacteriaItemIDs.append(bacteriaitem[3])
		if len(ItemIDs) > len(BacteriaItemIDs):#check if some itemIDs are not in ItemTracker
			for itemid in ItemIDs:
				if itemid not in BacteriaItemIDs: 
					Errorhandling('ItemID %s does not exist in ItemTracker' % itemid)
					
		for itemid in BacteriaItemIDs:
			ItemProperties[itemid] = {}	

		StrainIDString = ''
		
		for BacteriaItem in Bacteria:
			ItemProperties[BacteriaItem[3]]['AlternID'] = BacteriaItem[1]
			ItemProperties[BacteriaItem[3]]['StrainID'] =  (BacteriaItem[0]).encode()
			ItemProperties[BacteriaItem[3]]['OriginalID']= BacteriaItem[2]
			if StrainIDString == '':
				StrainIDString = "StrainID = '%s'" % ItemProperties[BacteriaItem[3]]['StrainID']
			else:
				StrainIDString = StrainIDString + " or StrainID = '%s'" % ItemProperties[BacteriaItem[3]]['StrainID']
	else:
		Errorhandling('None of the ItemIDs (%s) exists in ItemTracker :(' % ItemIDs)
		
	# get Item information for all items of bacteria items in list given to function "GetDictionary"
	# #### !!!!! don't change order of "ColumnNamesToSelect" !!!!!!!!!!!!!!! #####################
	ColumnNamesToSelect = 'ItemType,ItemID, ItemName, ParentCode, UserName, InputDate, LocationID, SalmonellaStatus,ListeriaStatus,FrozenStatus,DNAStatus,viabilityS,viabilityL,ViabilityF,AlternID,DNAconcentrationngul,Selected,SelectedBy,StrainID,VolumeFrozenStock,VolumeDNA'
	ItemList = SelectFromDBReturnNone(ColumnNamesToSelect,'ItemTable',StrainIDString+' order by StrainID')
	# sort out which item belongs to which bacteria
	Dict = {}
	Dict2 = {}
	for BacteriaItem in ItemProperties.keys():
		Dict[ItemProperties[BacteriaItem]['StrainID']] = []
		Dict2[ItemProperties[BacteriaItem]['StrainID']] = BacteriaItem
		for item in ItemList:
			if (item[18]).encode() == ItemProperties[BacteriaItem]['StrainID']:
				Dict[ItemProperties[BacteriaItem]['StrainID']].append(item)		
		
	for strain in Dict.keys():
		ItemID = Dict2[strain]
		SalmOrList = []
		FrozenStocks = []
		DNA = []
		ItemGroupDict = {}
		ItemDict = {}
		for item in Dict[strain]:
			# Salmonella, Listeria, Ecoli tubes
			if item[0] == 'Salmonella' or item[0] == 'Listeria' or item[0] == 'Ecoli':
				SalmOrList.append(item[1])
				FillPropertyDict(item)
			# frozen Stocks		
			if item[0] == 'Frozen Stock':
				FrozenStocks.append(item[1])
				FillPropertyDict(item)
			# DNA items
			if item[0] == 'DNA':
				DNA.append(item[1])
				FillPropertyDict(item)
			
		# sort out realtions between items
		for key in ItemGroupDict.keys(): # key is each item retrieved for this StrainID
			for item in ItemGroupDict.keys():
				if key == int(ItemProperties[item]['ParentCode']):
					ItemGroupDict[key].append((item))
						
		LastItems = []
		for key in ItemGroupDict.keys():
			if ItemGroupDict[key] == []:
				LastItems.append(key)
		
		for item in LastItems: # for each item without any child
			ItemDict[item] = []
			ItemOfQuestion = item
			parent = 0
			while parent != ItemID: 
				parent = int(ItemProperties[ItemOfQuestion]['ParentCode'])
				ItemDict[item].append(parent)
				ItemOfQuestion = parent
					
		for key in ItemDict.keys():
			i = len(ItemDict[key])
			try:
				FinalItemDict[ItemDict[key][i-1]]
			except:
				FinalItemDict[ItemDict[key][i-1]] = {}
				
			j = len(ItemDict[key])-2
			dictionary = FinalItemDict[ItemDict[key][i-1]]
			while j > -1:
				try:
					dictionary[ItemDict[key][j]]
					dictionary = dictionary[ItemDict[key][j]]
				except:
					dictionary = FillDict(dictionary,ItemDict[key][j])
				j = j-1
			try:
				dictionary[key]
			except:
				dictionary = FillDict(dictionary,key)

	conn.close() # close connection without commit changes (no changes happened)	
	return FinalItemDict,ItemProperties,message

def FillPropertyDict(item): # fills dictionary ItemProperties with data retrieved form ItemTracker
	ItemProperties[item[1]] = {}
	ItemProperties[item[1]]['ItemType'] = item[0]
	ItemProperties[item[1]]['ItemName']=item[2]
	ItemProperties[item[1]]['ParentCode']=item[3]		
	ItemProperties[item[1]]['UserName']=item[4]
	ItemProperties[item[1]]['InputDate']=item[5]
	if item[6] < 1:
		ItemProperties[item[1]]['TubePresent'] = '-'
		ItemProperties[item[1]]['Position'] = ''					
	else:
		ItemProperties[item[1]]['TubePresent']='+'
		Position = SelectFromDB('Freezer,Rack,Shelf,PlateRack,Position','LocationView','ItemID = %s' % item[1])
		ItemProperties[item[1]]['Position'] = Position[0]
	if item[7] != None: #status salmonella
		ItemProperties[item[1]]['Status']=item[7]
		ItemProperties[item[1]]['Viability']=item[11]
	elif item[8] != None: #status listeria
		ItemProperties[item[1]]['Status']=item[8]
		ItemProperties[item[1]]['Viability']=item[12]
	elif item[9] != None: # status frozens tock
		ItemProperties[item[1]]['Status']=item[9]
		ItemProperties[item[1]]['Viability']=item[13]
	elif item[10] != None: # status DNA
		ItemProperties[item[1]]['Status']=item[10]
		ItemProperties[item[1]]['Viability']=''

		
	else: # item has no status
		ItemProperties[item[1]]['Status']=''
		if item[11] != None:
			ItemProperties[item[1]]['Viability']=item[11]
		elif item[12] != None:
			ItemProperties[item[1]]['Viability']=item[12]
		elif item[13] != None:
			ItemProperties[item[1]]['Viability']=item[13]	
		else:
			ItemProperties[item[1]]['Viability']=''
			
	if item[2][0] == 'D': #item is DNA
		# volume DNA
		if item[20] != None:
			ItemProperties[item[1]]['Volume']= '% sul' % item[20]
		else:
			ItemProperties[item[1]]['Volume']= ''
	elif item[2][0] == 'F': #item is frozen stock
		# volume ForzenStock
		if item[19] != None:
			ItemProperties[item[1]]['Volume']='%s ul' % item[19]
		else:
			ItemProperties[item[1]]['Volume']= ''
		
	# item has no volume property (such as "salmonella")
	try:
		test = ItemProperties[item[1]]['Volume']
	except:
		ItemProperties[item[1]]['Volume'] = ''
			
	ItemProperties[item[1]]['AlternID']=item[14]
	if item[15] != None:
		ItemProperties[item[1]]['DNA concentration']= '%s ng/ul' % item[15]
	else:
		ItemProperties[item[1]]['DNA concentration']= ''
	if item[16] == '0':
		ItemProperties[item[1]]['Selected']='no'
		ItemProperties[item[1]]['SelectedBy']=item[17]
	elif item[16] == '1':
		ItemProperties[item[1]]['Selected']='yes'
		ItemProperties[item[1]]['SelectedBy']=item[17]
	else:
		ItemProperties[item[1]]['Selected'] = ''
		if item[17] != None:
			ItemProperties[item[1]]['SelectedBy'] = item[17]
		else:
			ItemProperties[item[1]]['SelectedBy'] = ''
	ItemGroupDict[item[1]] = []
	
def SelectItem(ItemID):
	global message
	message = []
	connectToDB()
	ItemInfo = SelectFromDB('ItemTypeID,SeqNo','Items','ItemID = %d' % ItemID)
	SeqNo = ItemInfo[0][1]
	if ItemInfo[0][0] == 6:
		message.append('Item %s is a Bacteria and can not be selected' % ItemID)
	if message == []:
		UpdateSelectedStatus(ItemID,SeqNo,1)
	if message == []:
		CommitChanges()
	else:
		conn.close()
	return message

def UnselectItem(ItemID):
	global message
	message = []
	connectToDB()
	ItemInfo = SelectFromDB('ItemTypeID,SeqNo','Items','ItemID = %d' % ItemID)
	SeqNo = ItemInfo[0][1]
	if ItemInfo[0][0] == 6:
		message.append('Item %s is a Bacteria and can not be unselected' % ItemID)
	if message == []:
		UpdateSelectedStatus(ItemID,SeqNo,0)
	if message == []:
		CommitChanges()
	else:
		conn.close()
	return message

def UpdateSelectedStatus(ItemID,SeqNo,UpdateValue):
	date = strftime("%Y-%m-%d %H:%M")	
	UserDict = {'jhaase':6,'ysong':4, 'vimal':7,'machtman':8,'rmurphy':14, 'bofarrell':12, 'jhale':13, 'elitrup':15}
	username = os.environ.get('USERNAME')
	Selected = SelectFromDBReturnNone('FieldValue','ItemValue','FieldID = 57 and ItemID = %s and SeqNo = %d' % (ItemID,SeqNo))
	if Selected != None:
		UpdateData('ItemValue','FieldValue',UpdateValue,'FieldID = 57 and ItemID = %s and SeqNo = %d' % (ItemID,SeqNo))
	else:
		PropertyDict1 = {'ItemID':ItemID, 'SeqNo':SeqNo, 'FieldID':57,'FieldValue':UpdateValue}
		InsertIntoDB('ItemValue',PropertyDict1)
	SelectedBy = SelectFromDBReturnNone('FieldValue','ItemValue','FieldID = 58 and ItemID = %s and SeqNo = %d' % (ItemID,SeqNo))
	if SelectedBy != None:
		UpdateData('ItemValue','FieldValue',username,'FieldID = 58 and ItemID = %s and SeqNo = %d' % (ItemID,SeqNo))
	else:
		PropertyDict1 = {'ItemID':ItemID, 'SeqNo':SeqNo, 'FieldID':58,'FieldValue':username}
		InsertIntoDB('ItemValue',PropertyDict1)
	#set update date and update last user
	UpdateData('Items','ChangeDate',date,'ItemID = %d' % ItemID)
	UpdateData('Items','UserID',UserDict[username],'ItemID = %d' % ItemID)
	
def SelectAllselectedEntries(ItemList):
	username = os.environ.get('USERNAME')
	connectToDB()
	StrainIDs = []
	if len(ItemList) == 1:
		StrainIDsItemList = SelectFromDB('StrainID','ItemTable','ItemID = %s' % (ItemList[0]))
	elif len(ItemList) > 1:
		StrainIDsItemList = SelectFromDB('StrainID','ItemTable','ItemID in %s' % (tuple(ItemList),))
	elif len(ItemList) == 0:
		StrainIDsItemList = []
	for item in StrainIDsItemList:
		StrainIDs.append(item[0])
	SelectedItemsPresentInBN = []
	data = []
	BactDict = {}
	BacteriItems = SelectFromDB('ItemID,StrainID','ItemTable',"ItemType = 'Bacteria'")
	for item in BacteriItems:
		BactDict[item[1]] = item[0]
	selecteditems = SelectFromDBReturnNone('ItemID,StrainID,ItemType,ItemName','ItemTable',"Selected = 1 and SelectedBy = '%s' order by ItemType" % username)
	conn.close()
	
	if selecteditems != None:
		for item in selecteditems:
			ItemInDatabase = item[1] in StrainIDs
			if ItemInDatabase == True:
				BacteriaItemID = BactDict[item[1]]
				if BacteriaItemID:
					data = []
					for selecteditem in item:
						data.append(selecteditem)
					data.append(BacteriaItemID)
					SelectedItemsPresentInBN.append(data)
				else:
					Errorhandling('No Bacteria with StrainID %s in ItemTracker' % item[1])
	
	
	return SelectedItemsPresentInBN
	
if __name__ == '__main__':
	global ItemProperties, ItemDict
	
	#ItemIDs = [8765,32131,32140,32137]
	#ItemIDs = [52213,52219,8765]
	#ItemIDs = [61619,77784,61687,61594,61686,61677,61623,61620,61685,9431]
	#SelectAllselectedEntries(ItemIDs)
	  # get item information/ children
	#ItemDict,ItemProperties,message = GetDictionary(ItemIDs)
	#print message
	  # update an Item
	#ItemID = 3866
	#result = SelectItem(ItemID)
	#result = UnselectItem(ItemID)
	#print result
	#Items = [1,2,3,4,17,8765,3865]
	#ListOFSelectedItems = SelectAllselectedEntries(Items)
	pass

