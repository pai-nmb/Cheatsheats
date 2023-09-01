### To delete the entire data
```
DELETE FROM opcua_data.test_server_data
```


### To delete data older than a day
```
DELETE FROM opcua_data.test_server_data
WHERE time < NOW() - INTERVAL '1 day';
```