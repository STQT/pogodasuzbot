import motor.motor_asyncio
import pprint

client = motor.motor_asyncio.AsyncIOMotorClient('127.0.0.1', 27017)
db = client.test_collection
collusers = db.collusers


# async def do_insert():
#     document = {'key': 'value'}
#
#     result = await db.test_collection.insert_one(document)
#
#     print('result %s' % repr(result.inserted_id))
#
# import asyncio
#
# loop = client.get_io_loop()
#
# loop.run_until_complete(do_insert())

# async def do_insert():
#
#     result = await db.test_collection.insert_many(
#
#         [{'i': i} for i in range(2000)])
#
#     print('inserted %d docs' % (len(result.inserted_ids),))
#
# loop = client.get_io_loop()
#
# loop.run_until_complete(do_insert())


# async def do_find():
#
#     cursor = db.test_collection.find({'i': {'$lt': 5}}).sort('i')
#
#     for document in await cursor.to_list(length=100):
#
#         pprint.pprint(document)
#
#
# loop = client.get_io_loop()
#
# loop.run_until_complete(do_find())

async def get_current_user_col(user_id):
    document = await collusers.find_one({'_id': user_id})
    return document


async def insert_new_user(user_id):
    await collusers.insert_one(
        {'_id': user_id,
         'city': "Tashkent",
         'notify_hours': 6,
         'active': True
         }
    )


async def update_notify_hours_by_user_id(user_id, notify_hours):
    await collusers.update_one({'_id': user_id}, {'$set': {'notify_hours': notify_hours}})


async def update_city_hours_by_user_id(user_id, city):
    await collusers.update_one({'_id': user_id}, {'$set': {'city': city}})


async def get_all_active_users():
    cursor = collusers.find({"active": True})
    count = await collusers.count_documents({"active": True})
    users = []
    for document in await cursor.to_list(length=count):
        users.append(document)
    return users


async def get_all_active_users_with_hour(hour):
    filtering = {"active": True, "notify_hours": hour}
    cursor = collusers.find(filtering)
    count = await collusers.count_documents(filtering)
    users = []
    for document in await cursor.to_list(length=count):
        users.append(document)
    return users

async def do_delete_one():
    coll = db.collusers
    n = await coll.count_documents({})

    print('%s documents before calling delete_one()' % n)

    result = await collusers.delete_one({'_id': 390736292})
    print(result)
    print('%s documents after' % (await coll.count_documents({})))

# loop = client.get_io_loop()
# print("LOOP")
# loop.run_until_complete(do_delete_one())

async def user_counts():
    count = await db.collusers.count_documents({})
    return count
