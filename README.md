Dynamic ansible inventory from Splunk search
============================================
A simple script for running search queries against Splunk to get a dynamic
inventory from the result set.

## How to write searches 
While not necessary, I recomend padding the searches to limit the amount of
data outputed from Splunk. Only the host field is used, so use rename.

```
 dedup host | fields host
 dedup host | table host
 dedup hostname | rename hostname as host | fields host
```

## How to use

```
ansible -i ./splunkinv.py all -m ping 
ansible-playbook -i ./splunkinv.py playbook.yml
```

## Configuration

