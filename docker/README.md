This docker image packages 3D Juump Infinite Cli, generic_connector.py and meta_connector.py

To use this image

 - mount a persistent volume/folder to `/connector`
 - set env `CONNECTOR_MODE` to **sleep**, **oneshot** or **daemon**

meta_connector.py will initialize content of `/connector/_scripts`
content of `/connector/_scripts` will be update/override when using a new container

# register your directory

You have to register your directory by running `3dJuumpInfiniteCli directory register... --location .` from `/connector/_scripts`
Directory nickname should be **thedirectory** and conf location should be in **/connector/_scripts**

# sleep

In this mode the container will wait for ever, allowing to run a bash in it to interact with the directory throught cli. You may restore/dump evojuumps.
docker exec -it CONTAINER_NAME /bin/bash

# oneshot

In this mode, for each top folders of `/connector` (except for folders whose name starts with a `_`), the container will :

 - copy customization files if it does not contains `project_custo.py` and `project_conf.json`
 - run generic_connector.py on the folder

# daemon

Same as oneshot but executed periodically. Note that a folder will be processed only if it was not modified recently (few minutes) to avoid processing folder during a data copy