# Mo3jam

Mo3jam is field specific community dictionary, currently under developmet. Both `docker` and manuall installation are 
supported.

## Running Guide

### Docker installation 

First you need to make sure that `docker` and `docker-compose` are installed in your system, then the application can 
be simply started using:

`sudo docker-compose -f docker-compose.dev.yaml up`

If 5000 is already in use in your labtop, you can change the port to any port you want:

```
  webserver:
    ...
    ports:
      - "<your_port>:80"
      - "443:443"

```

### Manual installation

First you need to have `python` installed >= 3.6, then you need to have `ElasticSearch` and `MongoDB` installed on 
your labtop.

Then you need to install your dependencies using:

`pip install -r requirements.txt`

Then you can run the application:

`python run.py`

## Usage

The API currently is on version `1.0` and it contains the following resources:

* users
* unregistered-users
* terminologies 
* domains
* dictionaries 
* terminologies/<terminology_uid>/translations
* terminologies/<terminology_uid>/notes
* roles
* search

Examples:

```
POST /api/v1.0/unregistered-users/

{
	"name": "adnan",
	"email": "adnan@ex.com"
}

```

```
POST /api/v1.0/terminologies/

{
 	"term": "sync",
 	"creator": "40c4fb05-e1d8-4878-b7fa-7e9fefa82b0e",
 	"domain": "68532105-1aea-4114-960f-90019674bc86",
 	"translations": [
 		{
			"value": "sol",
			"creator": "40c4fb05-e1d8-4878-b7fa-7e9fefa82b0e",
			"author": "40c4fb05-e1d8-4878-b7fa-7e9fefa82b0e",
			"notes": "first note",
			"source": null
        }
 	],
 	"notes": [
 		{
			"value": "a note",
			"creator": "40c4fb05-e1d8-4878-b7fa-7e9fefa82b0e"
        }
 	],
 	"language": "en"
}

```

```
DELETE /api/v1.0/terminologies/c9372296-ee07-4dcb-bc50-f27a51dabf71/translations/d6776b58-177f-411b-adaf-3bddf066ebb7

```


## Notes

Currently authorization is turned off for simplicity, but expect this to change in the future.




