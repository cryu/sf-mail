=====
Ideas
=====


The upload module consists of several components:

- The processor which takes incoming files and processes them, e.g. by creating thumbnails
- The media database, a mongoengine powered database for storing the asset metadata
- some store implementations to actually store the file contents. Defaults to filesystem.
- Some upload handler which takes the file and processes it. It also includes the valum drag and drop JS upload handler and some bootstrap compatible styles along with it.


Basic upload functionality
==========================

The most basic functionality is to take a file and store it somewhere. We assume that the app is getting a filepointer in ``fp`` and wants to
save the file. Then we can do something like this in a handler::

    # get this from some upload JS or whatever
    fp = self.request.files['file']
    name = self.request.form['name']
    filename = self.request.form['Filename']

    metadata = self.app.module_map.uploader.add(fp, 
        filename = filename,
        name = name)

    return metadata.filename


The ``name`` parameter here is actually a **kw keyword argument and will be simply copied to the metadata.
In this basic form it will also not store any metadata in some database. You have to do this yourself. 


Asset management
================

If you also want to use asset management then you need to connect a database with mongoengine.connect and configure
the module accordingly in your application class::

    import sfext.uploader as upl

    modules = [
        upl.upload_module(
            metadata_db = upl.metadata.MongoStore(db="...", user="...", ...)
        )
    ]

The metadata database will store content length, content type and any other metadata passed in (as a subdocument called ``metadata``). It will have a unique id which
you can use in your own app to link to that entry.

Upload will work as before but the returned metadata will also include an ``_id`` field which points to that metadata entry.



Different storages
==================

To configure the incluced filesystem storage or use a different one you can configure it as follows::

    modules = [
        upl.upload_module(
            store = upl.stores.FilesystemStore(base_path="/home/user/uploads"),
        )
    ]

A store will always store files under a UUID and not the real filename to prevent name collisions. By default this is the same id which the asset has.



Processors
==========

..info::

    This is for implementing later but the idea should be shown here

Processors can take an incoming file and do something with it like e.g. creating additional versions like scaled down images etc. 
This means that the metadata record will have additional fields such as a ``parent`` which holds the parent asset id. "Master" assets
will also contain a list if derived assets in the simple form as ``{'name' : 'id', ...}``.

Processors can be registered on the module. 


Handlers
========

We have some predefined handler for dealing with uploads. This is based on the ``valums file uploader`` (https://github.com/valums/file-uploader). 









