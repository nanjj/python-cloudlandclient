================
Cloudland Client
================

Command Line
============

Create file ``~/cloudlandrc``::

  CLOUDLAND_USERNAME="<your username>"
  CLOUDLAND_PASSWORD="<your password>"
  CLOUDLAND_ENDPOINT="http://9.110.51.248/cloudland/api/"
  export CLOUDLAND_USERNAME CLOUDLAND_PASSWORD CLOUDLAND_ENDPOINT

Let's cloudland::

  source ~/cloudlandrc
  cloudland --help

Client API
==========
::

   from cloudlandclient.client import CloudlandClient

   cl = CloudlandClient(username, password, endpoint)
   cl.vm_list()


  


