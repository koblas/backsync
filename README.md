backsync
========

BackboneJS + SockJS + Tornado

Back Story
----------

The real back story is that I was building an app that needed to emit log messages at the browser in a
console kind of fashion.  Realized that I wanted a "real-time" front end and of course stared looking
at using BackbonJS on a real project.  Now the problem with backbone is that it's a CRUD interface to
data, which isn't too hard to support - but isn't realtime.  Meteor is realtime, but of course it's a
whole different approach than the Python/Tornado backend that I had in place.

Given that I started looking at Backbone.IO, which after a bit of mucking around got the job done.  But,
it's not quite what I wanted in an interface, so looked at using SockJS instead of Socket.IO as the
transport, thus ended up having to drop Backbone.IO and build out something slightly different.

How It Works
------------

Upsert / Delete is the way everything communicates.

Client Changes
--------------

The premise is that instead of attaching everything on the save handler on the model object, it's handled 
at the Backbone.Collection level so you'll end up with code like this:

    var Message = Backbone.Model.extend({
         urlRoot : 'ChatMessage',
    });

    var Messages = Backbone.Collection.extend({
        url    : 'ChatMessage',
        model  : Message,

        initialize: function (model) {
            this.syncBind('upsert', this.serverUpsert, this);
            this.syncBind('delete', this.serverDelete, this);
        },

        serverUpsert: function(data) {
            var m = this.get(data.id);
            if (m) {
                m.set(data);
            } else {
                this.add(data);
            }
        },

        serverDelete: function(data) {
            var m = this.get(data.id);
            if (m)
                this.remove(m);
        }
    });


Protocol
--------

All messages are in JSON - It's 2012 after all.

    Message :=
        id    : TRANSACTION_ID      // Server only sends ID in response to a Client ID
        event : MODEL ':' METHOD
        data  : MODEL_DATA

    MODEL := 
        STRING identifier for the Client/Server Model Object
    
    METHOD :=
        read    - Triggered back a Backbone.collection.fetch() - Reads all objects
        upsert  - Update or Insert a record into the store
        delete  - Delete a record

Inspiration
-----------

* Meteor - https://github.com/meteor/meteor
* Chatty - https://github.com/liamks/Chatty
* Backbone.IO - http://alogicalparadox.com/backbone.iobind/
