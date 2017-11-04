# coding: utf-8
from werkzeug.local import Local, LocalManager

local = Local()
local_manager = LocalManager([local])
