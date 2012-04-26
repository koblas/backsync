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

TODO -
    Sample Client changes
    Sample Server
    Protocol

Inspiration
-----------

* Meteor - https://github.com/meteor/meteor
* Chatty - https://github.com/liamks/Chatty
* Backbone.IO - http://alogicalparadox.com/backbone.iobind/

