# Websocket Server

This server, created using FastAPI, acts as a middleman between two long-running scripts (one which retrieves current schedule, one which processes audio for color values on front end) and the front end.  It receives values through the process method and then decides what type they are based on the top-level key within their dictionary data structure, before handling accordingly.
