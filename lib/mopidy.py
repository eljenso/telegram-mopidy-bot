import json
from urllib.request import urlopen

__host = ''

def __makeRequest(command):
    response = urlopen('http://%s/mopidy/rpc' % (__host) , json.dumps(command).encode())
    result = json.loads(response.read().decode())['result']
    return result

def __executeMethod(method, params={}):
    command = {
      "method": method,
      "jsonrpc": "2.0",
      "params": params,
      "id": 1
    }
    return __makeRequest(command)


def __queueUri(uri):
    return __executeMethod('core.tracklist.add', { "uri": uri })

def __getState():
    return __executeMethod('core.playback.get_state')

def __clearPlaylist():
    return __executeMethod('core.tracklist.clear')

def __play():
    return __executeMethod('core.playback.play')

def __resume():
    return __executeMethod('core.playback.resume')


def queue(host, uri):
    global __host
    __host = host

    currentState = __getState()
    if currentState == 'stopped':
        __clearPlaylist()
    __queueUri(uri)
    if currentState == 'stopped':
        __play()
    elif currentState == 'paused':
        __resume()
