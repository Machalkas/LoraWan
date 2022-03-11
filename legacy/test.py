from http import client
import influxdb


client = influxdb.InfluxDBClient(host="192.168.0.123")
# client.create_database("stats")
print(client.get_list_database())
table="power"
print([i for i in client.query("select * from %s;"%table, database="stats").get_points(table)][0])
print(client.get_list_users())

client.close()