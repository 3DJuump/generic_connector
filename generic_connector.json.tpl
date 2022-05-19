{
	"converter3dji":{
		"proxyApiUrl":"https://xxxx:yyyy@host:443/proxy",
		"projectId":"prj_xxxx",
		"cacheFolder":"./cache",
		"clearConnectorIndex":false,
		"reprocessCacheErrors":false,
		"copyBeforeLoad":true,
		"httpProxy":null,
		"verifySSL":true,
		"reprocessDocFromCache":false
	},
	"psconverter":{
		"workerCount": 12,
		"maxRamPerWorkerMB": 2048,
		"maxTimePerWorkerSec" : 360,
		"psConverterExe": "./PsConverter/PsConverter.exe",
		"directoryApiUrl":"https://xxxx:yyyy@host:443/directory"
	},
	"rootfolder": "./source",
	"tags":["GenericConnector"],
	"removeinstanciationandbakexforms":false,
    "scalefactortomillimeters":1
}
