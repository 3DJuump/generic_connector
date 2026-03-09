{
	"$schema": "./connector_conf.schema.json",
	"directoryNickName": "thedirectory",
	"cacheFolder": "./cache",
	"indexer": {
		"serveforever": false,
		"enabledocumentvalidation": true,
		"httpport": 8687
	} | {"elasticsearchurl":"http://127.0.0.1:9200"},
	"infiniteCliExe": "../../Server/GENERATED/DELIVERY/MSVC18_x64/3dJuumpInfiniteCli.d/3dJuumpInfiniteCli.d.exe",
	"maxWorkerCount": 12,
	"maxRamMB": 16000,
	"logLevel": "DEBUG"
}