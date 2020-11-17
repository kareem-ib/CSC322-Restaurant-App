''' Registration '''
# pre cond: application object sent in, must be have all fields fileld out
# post cond: applicant awaits approval
def RegisterApplicant(application):
    appDB = GetAppDB()
    appDB.add(application)

# pre cond: manager must have the proper credentials of a manger
# post cond: send back all pending applications
def getApplications(manager):
    appDB = GetAppDB()
    managerCredentials = manager.getCredentials()
    return appDB.retrieveApplications(managerCredentials)

# pre cond: manager must have proper credentials, application must be a valid applciation
# post cond: add to customer DB, remove applciation from DB, notify applicant
def approveApplication(manager, application):
    appDB = GetAppDB()
    customerDB = GetCustomerDB()

    if deposit(application.payment_method):
        appDB.remove(application, managerCredentials)
        customerDB.add(application)
        email(application.email, 'You got accepted son')
    else:
        rejectApplication(manager, application)

# pre cond: manager must have proper credentials, application must be a valid applciation
# post cond: remove applciation from DB, notify applicant
def rejectApplication(manager, application):
    appDB = GetAppDB()
    managerCredentials = manager.getCredentials()
    appDB.remove(application, managerCredentials)
    email(application.email, 'You got rejected son')

''' Quiting '''
# pre cond: customer must be a customer
# post cond: customer is added to quit DB to be approved by manager
def quitRequest(customer):
    quitDB = GetQuitDB()
    quitDB.add(customer)

# pre cond: manager is the manager
# post cond: all customer quit requests are returned
def getQuitRequests(manager):
    quitDB = GetQuitDB()
    managerCredentials = manager.getCredentials()
    return quitDB.retrieveQuitRequests(managerCredentials)

# pre cond: manager is a manager, customer is a customer with a quit request
# post cond: the customer is deregistered and removed from the DB
def acceptQuitRequest(manager, customer):
    quitDB = GetQuitDB()
    customerDB = GetCustomerDB()

    managerCredentials = manager.getCredentials()
    clearDeposit(customer, managerCredentials)
    customerDB.remove(customer)
    quitDB.remove(customer)

    email(customer.email, 'Bye :(')

# pre cond: manager is a manager, customer is a customer with a quit request
# post cond: customer is still a customer, their quit request is removed
def denyQuitRequest(manager, customer):
    quitDB - GetQuitDB()
    managerCredentials = manager.getCredentials()

    quitDB.remove(customer)
    email(customer.email, 'Nah')

''' Menu '''
# pre cond: desigChef is a designated chef, itemInfo has the name of the menu item, description, and picture
# post cond: itemInfo is added to the menu DB
def addMenuItem(desigChef, itemInfo):
    menuItem = createMenuItem(desigChef.id,
                              itemInfo.name,
                              itemInfo.desc,
                              itemInfo.picture)
    GetMenuDB.add(menuItem)

# pre cond: desigChef is a designated chef, itemID is a valid menu item
# post cond: itemID is removed from menu DB
def removeMenuItem(desigChef, itemID):
    GetMenuDB.remove(desigChef, itemID)

# Surfers
# pre cond: customer is not logged in i.e. surfer, menu exists
# post cond: returns a menu list with default featured items
def getMenu():
    menuDB = GetMenuDB()
    # Sets the default menu items to personalizedMenu
    personalizedMenu = Menu(menuDB)

    topThreeRatedDishes = menuDB.getTopRatedDishes()
    topThreeOrderedDishes = menuDB.getTopOrdereddDishes()
    personalizedMenu.setFeaturedDishes(topThreeRatedDishes,
                                       topThreeOrderedDishes)

    return personalizedMenu

# Customers
# pre cond: customer is logged in
# post cond: return a menu that is personalized to the customers orders
def getMenu(customer):
    ordersDB = GetOrdersDB()
    allCustomerOrders = ordersDB.getAllOrders(customer)
    # only allows unique dishes
    distinctOrders = set(allCustomerOrders.allCustomerDishes) 

    if distinctOrders.length < 3:
        return getMenu()
    
    menuDB = GetMenuDB()
    personalizedMenu = Menu(menuDB)

    topThreeDishes = set(allCustomerOrders.sortByRatings().allCustomerDishes())
    personalizedMenu.setFeaturedDishes(topThreeDishes)

    if customer.isVIP:
        personalizedMenu.setSpecials(menuDB.getSpecials())

    return personalizedMenu

''' Discussion Board '''
# pre cond: customer is a customer, postInfo has the subject and body of the post
# post cond: if no more than 3 taboo words, add the post to the discussion baord
def post(customer, postInfo):
    # Return a lsit of all taboo words
    tabooWords = scanTabooWords(postInfo)
    if tabooWords is not empty:
        customer.incrementWarnings()
        GetCustomerDB.update(customer)
        punishCustomer(customer)
        if tabooWords.length <= 3:
            replaceAllTabooWords(postInfo, '***')
        else:
            # Do not add post if too many bad words
            return
    
    postItem = createPostItem(customer,
                              postInfo.subject,
                              postInfo.body)
    GetPostDB().add(postItem)

# pre cond: customer is a customer, commentInfo has a body
# post cond: if no more than 3 taboo words, comment is posted to the post
def comment(customer, post, commentInfo):
    tabooWords = scanTabooWords(commentInfo)
    if tabooWords is not empty:
        customer.incrementWarnings()
        GetCustomerDB.update(customer)
        punishCustomer(customer)
        if tabooWords.length <= 3:
            replaceAllTabooWords(commentInfo, '***')
        else:
            # Do not add post if too many bad words
            return
    
    commentItem = createCommentItem(customer,
                              commentInfo.body)
    post.addComment(commentItem)
    GetPostDB().update(post)

# pre cond: customer is a customer with a warning
# post cond: if customer is VIP with >= 2 warnings, deregister to regular customer
#            if customer has >= 3 warnings, deregister customer to a surfer
def punishCustomer(customer):
    customerDB = GetCustomerDB()
    totalWarnings = customer.getWarnings()
    if customer.isVIP and totalWarnings >= 2:
        customer.unregisterVIP()
        customerDB.update(customer)
    else if totalWarnings >= 3:
        clearDeposit(customer)
        GetCustomerDB().remove(customer)
        customerDB.update(customer)
    

''' Reporting '''
# pre cond: customer is a customer, post is a valid post or comment on discussion board
# post cond: add report to reports database
def reportPost(customer, post):
    post.setSnitch(customer)
    GetReportsDB.add(post)

# pre cond: manager is a manager
# post cond: return all active reports to the manager
def getReports(manager):
    managerCredentials = manager.getCredentials()
    return GetReportsDB().getAllReports(managerCredentials)

# pre cond: manager is a manager, report is an active report, accepted is a boolean if the complainer's report is valid
# post cond: if accepted, complainee gets a warning, if snitch is VIP, then it is counted twice
#            else, snitch gets a warning
def managerAdjudicateReport(manager, report, accepted):
    reportsDB = GetReportsDB()
    customerDB = GetCustomerDB
    managerCredentials = manager.getCredentials()
    
    if accepted:
        if report.snitch.isVIP():
            report.poster.incrementWarnings()
            report.poster.incrementWarnings()
        else:
            report.poster.incrementWarnings()

        customerDB.update(report.poster)
        punishCustomer(report.poster)
    else:        
        report.snitch.incrementWarnings()
        customerDB.update(report.snitch)
        punishCustomer(report.snitch)

    reportsDB.remove(report)

''' Complaints '''
# dp = Delivery Person
# pre cond: complaint must have a complainee, snitch must be a customer or dp
#           if snitch is a customer, they must have had either dp or chef as the complainee
#           if snitch is a dp, they must have had the customer as the complainee
# post cond: a complaint for the complainee is added to the complaints DB
def complain(snitch, complaint):
    complaintItem = createComplaint(snitch,
                                    complaint.complainee,
                                    complaint.reason)
    GetComplaintsDB.add(complaintItem)

# pre cond: manager is a manager
# post cond: return all active complaints to the manager
def getAllComplaints(manager):
    managerCredentials = manager.getCredentials()
    return GetComplaintsDB.getComplaints()

# pre cond: compalinee must have complaint as active against them, reason must be a reason to dispute
# post cond: a dispute is added to complaint
def disputeComplaint(complainee, complaint, reason):
    disputeItem = createDispute(complainee,
                                reason)
    GetComplaintsDB().addDispute(complaint, disputeItem)

# pre cond: manager is a manager, compalaint must be an active complaint, accepted is a boolean if the complainer's complaint is valid
# post cond: if accepted, complainee gets a warning, if snitch is VIP, then it is counted twice
#            else, snitch gets a warning
#            person who gets the complaint gets punished
def managerAdjudicateComplaint(manager, complaint, accepted):
    complaintsDB = GetComplaintsDB()
    managerCredentials = manager.getCredentials()

    complaintsDB.remove(complaint)
    if accepted:
        if complaint.snitch.TYPE is Customer and complaint.snitch.isVIP():
            complaint.complainee.incrementWarnings()
            complaint.complainee.incrementWarnings()
        else:
            complaint.complainee.incrementWarnings()
        # getTypeDB() gets the complainee's specific database i.e. chef, delivery person, or customer
        getTypeDB(complaint.complainee.TYPE).update(complaint.complainee)
        if getTypeDB(complaint.complainee.TYPE) is Staff:
            punishStaff(complaint.complainee)
        else:
            punishCustomer(complaint.complainee)
    else:
        complaint.snitch.incrementWarnings()      
        getTypeDB(complaint.snitch.TYPE).update(complaint.snitch)
        if getTypeDB(complaint.snitch.TYPE) is Staff:
            punishStaff(complaint.snitch)
        else:
            punishCustomer(complaint.snitch)

# pre cond: staffMember must be a dp or chef
# post cond: if staffMember had >= 3 warnings, they get demoted, decreased salary, warnings set to 0
#            if staffMember had >= 2 demotions, they are fired and removed from the DB
def punishStaff(staffMember):
    staffDB = getTypeDB(staffMember.TYPE)
    totalWarnings = staffMember.getWarnings()

    if totalWarnings >= 3:
        staffMember.incrementDemotions()
        staffMember.decreaseSalary()
        # If over 3 complaints, set back to 0 complaints for another demotion
        staffMember.setWarningsZero()
        staffDB.update(staffMember)
    else if staffMember.getDemotions() >= 2:
        # This fires them
        GetFiredDB().add(staffMember)
        staffDB.remove(staffMember)

''' Rating '''
# pre cond: customer is a customer, menuItem is in the menu DB, rating is between 1-5
# post cond: rating is added to menuItem, if customer is VIP it's counted twice
#            check if the chef who added the menu item needs to be promoted/demoted
def rate(customer, menuItem, rating):
    if customer.isVIP():
        menuItem.incrementTotalRatings()
        menuItem.incrementTotalRatings()
        menuItem.addRating(2 * rating)
    else:
        menuItem.incrementTotalRatings()
        menuItem.addRating(rating)

    GetMenuDB().update(menuItem)
    checkChefMenuRatings(menuItem)

# pre cond: menuItem is in the menu DB
# post cond: if the chef has consistently high ratings (an average rating of >= 4 with 10 or more ratings), give promotion
#            if the chef has consistently low ratings (an average rating of <= 2 with 10 or more ratings), give demotion and punish
def checkChefMenuRatings(menuItem):
    chefDB = GetChefDB()
    desigChef = menuItem.assignedBy()
    totalRatings = menuItem.getTotalRatings()
    averageRating = menuItem.averageRating()
    if totalRatings >= 10 and averageRating >= 4:
        desigChef.incrementPromotions()
        desigChef.increaseSalary()
        chefDB.update(desigChef)
    else if totalRatings >= 10 and averageRating <= 2:
        desigChef.incrementDemotions()
        desigChef.decreaseSalary()
        chefDB.update(desigChef)
        punishStaff(desigChef)

''' Compliment '''
# pre cond: complimenter must be a customer or dp, compliment has a reason and a complimentee who is a dp or customer
#           complimenter and complimentee cannot be both dp and dp or both customer and customer
# post cond: if complimentee has warnings, remove them first before adding an official compliment
#            if complimentee is Staff with no warnings, give them an official compliment and reward
#            if the complimenter is a VIP, their compliment is counted twice
def giveCompliment(complimenter, compliment):
    complimentee = compliment.complimentee
    complimentItem = createCompliment(complimenter,
                                      complimentee
                                      compliment.reason)
    personDB = getTypeDB(complimentee.TYPE)
    
    if complimenter.TYPE is Customer and complimenter.isVIP():
        if complimentee.getWarnings() >= 2:
            complimentee.decrementWarnings()
            complimentee.decrementWarnings()
        else if complimentee.getWarnings() == 1:
            complimentee.decrementWarnings()
            complimentee.incrementCompliments()
            reward(complimentee)
        else:
            complimentee.incrementCompliments()
            complimentee.incrementCompliments()
            reward(complimentee)
    else:
        if complimentee.getWarnings() > 0:
            complimentee.decrementWarnings()
        else if complimentee is Staff:
            complimentee.incrementCompliments()
            reward(complimentee)
    
# pre cond: staffMember is a dp or chef with a newly added compliment
# post cond: if staffMember has >= 3 official compliments, give promotion, increase their salary, and reset their compliments to 0
def reward(staffMember):
    staffDB = getTypeDB(staffMember.TYPE)

    if staffMember.getCompliments() >= 3:
        staffMember.incrementPromotions()
        staffMember.increaseSalary()
        staffMember.setComplimentsZero()
        staffDB.update(staffMember)

''' Deposit '''
# pre cond: customer is a customer, payment type is either money or cryptocurrency, depositAmount is the total deposit in USD
# post cond: if paymentType is money, just check if their card has the funds to deposit and return whether or not it does
#            if paymentType is crypto, check if they have enough crypto (when converted to USD) to pay and return whether or not it does
def deposit(customer, paymentType, depositAmount):
    customerDB = GetCustomerDB()
    if paymentType == Money:
        if totalAmount(customer.card) >= depositAmount:
            withdraw(customer.card, depositAmount)
            customer.addMoney(depositAmount)
            customerDB.update(customer)
            return 'Deposit aproved.'
        else:
            return 'Deposit denied.'
    else:
        # Crypto Payment
        if convertToUSD(totalCryptoAmount(customer.card)) >= depositAmount:
            # Crypto network is Ethereum rinkeby
            withdrawFromCryptoNetwork(customer.card, depositAmount)
            customer.addMoney(depositAmount)
            customerDB.update(customer)
            return 'Deposit approved.'
        else:
            return 'Deposit denied.'

''' Orders '''
# pre cond: customer is a customer with a deposit, menuItems is a list of of items from the menu DB
# post cond: remove money from customers account, if VIP then apply a 10% discount
#            return True if the user has the proper deposit amount and false otherwise
def pay(customer, menuItems):
    # Get total price of all the orders
    totalPrice = menuItems.reduce(total, item => total + item.price)
    if customer.money() >= totalPrice:
        if customer.isVIP:
            customer.removeMoney(totalPrice * 0.90)
        else:
            customer.removeMoney(totalPrice)
        return True
    else:
        return False

# pre cond: time is a time to reserve tables, partyMembers are the total people in the reservation
# post cond: each table in the restaurant has two seats, if there exist enough tables for each member in the party at time, return True
#            otherwise there are not enough tables at time for the party, return False
def dineInTimeConflict(time, partyMembers):
    tables = GetTablesDB()
    tablesNeeded = ceil(totalSeats / 2)
    tablesOccupied = tables.tablesOccupiedAt(time)
    totalTablesInRestaurant = tables.getTotalTables()
    if tablesNeeded < totalTablesInRestaurant - tablesOccupied:
        tables.occupyMoreTables(time, tablesNeeded)
        return False
    else:
        return True

# pre cond: customer is a customer with a deposit, menuItems is a list of of items from the menu DB, time is a time to reserve tables, partyMembers are the total people in the reservation
# post cond: a success condition reserves the time for the party and a chef is assigned, checks if to make a customer a VIP
#            a fail condition tells the customer why it failed
def orderDineIn(customer, menuItems, time, partyMembers):
    if dineInTimeConflict(time, partyMembers):
        return "Time conflicts. Please choose another."
    else if pay(customer, menuItems):
        reserveTime(time, partyMembers)
        order = createOrderDineIn(customer,
                                  menuItems,
                                  time,
                                  partyMembers,
                                  randomChef())
        GetOrdersDB().add(order)
        if not customer.isVIP():
            checkIfNowVIP(customer)
        return "Order successful"
    else:
        return "Deposit more money please"

# pre cond: customer is a customer with a deposit, menuItems is a list of of items from the menu DB
# post cond: if the customer has enough deposit the order is placed and a chef is assigned, checks if to make a customer a VIP
def orderTakeout(customer, menuItems):
    if pay(customer, menuItems):
        order = createOrderTakeout(customer,
                                   menuItems,
                                   randomChef())
        GetOrdersDB().add(order)
        if not customer.isVIP():
            checkIfNowVIP(customer)
        return "Order successful."
    else:
        return "Order failed."

# pre cond: customer is a customer with a deposit, menuItems is a list of of items from the menu DB
# post cond: if the customer has enough deposit the order is placed and a dp is assigned, checks if to make a customer a VIP
def orderDelivery(customer, menuItems):
    if pay(customer, menuItems):
        order = createOrderDelivery(customer,
                                    menuItems,
                                    randomChef(),
                                    randomDP())
        GetOrdersDB().add(order)
        if not customer.isVIP():
            checkIfNowVIP(customer)
        return "Order successful."
    else:
        return "Order failed."
        
# pre cond: customer is a non VIP customer
# post cond: if the customer has >= $500 of orders placed or more than 50 orders placed then turn them into a VIP
def checkIfNowVIP(customer):
    customerOrders = GetOrdersDB().getCustomerOrders(customer)
    totalNumberOfOrders = customerOrders.length
    totalPriceOfAllOrders = customerOrders.reduce(total, order => total + order.price)

    if totalNumberOfOrders >= 50 or totalPriceOfAllOrders >= 500:
        customer.setVIPStatus()
        GetCustomerDB().update(customer)