import asyncio
import nest_asyncio
import random
import pyzeebe
import json
import time

nest_asyncio.apply()

async def main():
	channel = pyzeebe.create_camunda_cloud_channel(client_id="rBNAuQ9b9w3_wQYrNn.nHp6kC762XRGB", 
													client_secret="C7QWOBgT_R5Hbs4RrA1vLnxJrmG6QxghzxlHG3S5FtdKEBRiGicUDmkvRsZj0p0V",
													cluster_id="c8192281-1489-423b-8f9e-bd82cfd54dbb",
													region="dsm-1"

	)
	print("channel created")
	worker = pyzeebe.ZeebeWorker(channel)
	print("worker connected")

	def saveDBfile():
		with open('lib_db.json', 'w') as ofile:
			json.dump(db, ofile, indent = 4)
		return

	#Prepare local db and overwrite old entries. RUN THIS CODE ONCE IF FILE DOES NOT EXIST YET, or if you want to everwrite
	# db = {}
	# c_id = 0
	# firstName = 'Jane'
	# lastName = 'Doe'
	# customer = {
	# 		"customerID" : c_id,
	# 		"firstName" : firstName,
	# 		"lastName" : lastName,
	# 		"gender" : "other",
	# 		"email" : f"{firstName.lower()}{'.' if len(firstName) > 0 else ''}{lastName.lower()}@hu-berlin.de"
	# 	}
	
	# booklist = []
	# db[c_id] = {'c_data' : customer, 'booklist' : booklist}
	# saveDBfile()


	with open('lib_db.json') as json_file:
		db = json.load(json_file)

	@worker.task(task_type="getCustomerByID")
	def getCustomerByID(customerID: int):
		return db[customerID]['c_data']

	@worker.task(task_type="getCustomerByName")
	def getCustomerByName(lastName: str, firstName: str):
		for c_id in db:
			if db[c_id]['c_data']['firstName'] == firstName and db[c_id]['c_data']['lastName'] == lastName:
				print('HIT')
				return db[c_id]['c_data']
		# in case of wrong input make sure to return any
		return db[c_id]['c_data']

	@worker.task(task_type="saveNewCustomer", single_value=True, variable_name="customerID")
	def saveNewCustomer(lastName: str, firstName: str, gender: str, email: str) -> int:
		c_id = int(list(db.keys())[-1])+1
		customer = {
				"customerID" : c_id,
				"firstName" : firstName,
				"lastName" : lastName,
				"gender" : gender,
				"email" : f"{firstName.lower()}{'.' if len(firstName) > 0 else ''}{lastName.lower()}@hu-berlin.de"
			}
	
		db[c_id] = {'c_data' : customer, 'booklist' : []}
		print(db[c_id])
		saveDBfile()
		return c_id

	@worker.task(task_type="checkBookLimit", single_value=True, variable_name="limitReached")
	def checkBookLimit(customerID: int, bookList: str):
		bookList = bookList.split(";")
		return len(bookList) > 5

	@worker.task(task_type="updateLendingDatabase")
	def updateLendingDatabase(customerID: int, bookList: str):
		bookList = bookList.split(";")
		epoch = str(time.time())
		for i, book in enumerate(bookList):
			# book str -> title:lending time:overdue bool
			bookList[i] = f'{book}:{epoch}:{0}'
		db[str(customerID)]['booklist'] += bookList
		print(db[str(customerID)])
		saveDBfile()
		return 

	@worker.task(task_type="sendLimitReached")
	def sendLimitReached(customerID: int):
		# send message
		return 

	@worker.task(task_type="generateFeeReceipt", single_value=True, variable_name="receiptID")
	def generateFeeReceipt(bookReturnList:str):
		print('generating damage report')
		damagedBooks = 0

		bookReturnList_scope = bookReturnList.split(';')
		for book in bookReturnList_scope:
			if int(book.split(':')[-1]) == 1:
				damagedBooks += 1
		
		# generate fee receipt and send message
		receiptID = random.randint(0,100)
		if damagedBooks > 0:
			print(f'You have damaged {damagedBooks} books. You total fee sums up to {damagedBooks*10}€, receipt ID {receiptID}')
		return f"{receiptID}"
	
	@worker.task(task_type="calcLendingTime", single_value=True, variable_name="booksOverdue")
	def calcLendingTime(bookReturnList:str):
		overdueFees = False
		bookReturnList_scope = bookReturnList.split(';')

		for i, book in enumerate(bookReturnList_scope):
			bookReturnList_scope[i] = book.split(":")[0]
		
		
		for key in db:
			for book in bookReturnList_scope:
				c_booklist = [c_book.split(':')[0] for c_book in db[key]['booklist']]
				for i, c_book in enumerate(c_booklist):
					if book == c_book:
						if db[key]['booklist'][i].split(':')[-1] == "1":
							print(f'BookID {book} is overdue!')
							overdueFees = True

		if not overdueFees:
			print("No overdue fees")
		return overdueFees
	
	@worker.task(task_type="checkOverdueCost", single_value=True, variable_name="overdueReceiptID")
	def checkOverdueCost(bookReturnList:str):
		receiptID = random.randint(0,100)
		print(f"Generating overdue cost receipt with ID {receiptID}")
		return f'{receiptID}'
	
	@worker.task(task_type="returnBookUpdate")
	def returnBookUpdate(bookReturnList:str):
		bookReturnList_scope = bookReturnList.split(';')

		for i, book in enumerate(bookReturnList_scope):
			bookReturnList_scope[i] = book.split(":")[0]
		
		
		for key in db:
			for book in bookReturnList_scope:
				c_booklist = [c_book.split(':')[0] for c_book in db[key]['booklist']]
				for i, c_book in enumerate(c_booklist):
					if book == c_book:
						del db[key]['booklist'][i]

		print(f"You have successfully returned: {bookReturnList_scope}")
		saveDBfile()
		return

	print("tasks added\n...running...")
	await worker.work()

asyncio.run(main())
print("done")

# TODO
# Add Date to book
# Add overdue bool to book
# abc:0;def:1;