import datetime

get_time = datetime.datetime.now() 
print(get_time)
get_time_strip = get_time.strftime("%B %d, %Y, %I:%M:%S %p")
f_get = open("start_time.txt", 'w')
f_get.writelines(get_time_strip)
f_get.close()
