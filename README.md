Dynamic ansible inventory from Splunk search
============================================
A simple script for running search queries against Splunk to get a dynamic
inventory from the result set. Yields an overhead of 100-200ms per search on the most basic datasets. 
Assume larger overhead with larger datasets.

## How to write searches 
While not necessary, I recomend padding the searches to limit the amount of
data outputed from Splunk. Only the host field is used, so use rename.

```
 dedup host | fields host
 dedup host | table host
 dedup hostname | rename hostname as host | fields host
```

## How to use
This is used as any other ansible inventory file. However, search input is
needed. There are three ways to provide this.
- Environment variables
- Script argument
- Search in file


### Environment variable (recomended)
```
    SQ='search index=_internal | dedup host | fields host' ansible-playbook -i ./splunkinv.py all -m ping
```

### Script argument (Only for testing)
I have not found a way of running this inline with the ansible command.

```
    ./splunkinv.py 'search index=_internal...' 
```

### Search in a file
Requires a file named _splunk.search_ in the current working directory.
If no other option is passed to the script, this will be used when the file is
available.

### Test it out with the following command

```
    SQ='search index=_internal | dedup host | fields host' ansible -i ./splunkinv.py all -m ping 
```

## Configuration
A sample configuration is provided _splunkinv.conf.sample_. Copy this to one of
the following locations and provide the correct information to get started.
 - ~/.config/splunkinv.conf
 - $(pwd)/splunkinv.conf
 - /path/of/script/splunkinv.conf

## Requirements
_requests_ is a non optional requirement.
Tested with Ansible 2.2.0 and Splunk 6.5.0.
