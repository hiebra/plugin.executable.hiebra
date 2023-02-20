import web_pdb
import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import xbmc
from urllib.parse import parse_qsl, urlencode

script = {
    'base': sys.argv[0][:-1],
    'handle': int(sys.argv[1]),    
    'parameters': dict(parse_qsl(sys.argv[2][1:])),
    'addon': xbmcaddon.Addon()
}

externalStorage = xbmcgui.Window(10000)

def getExternalStorage(property):
    return externalStorage.getProperty(script['base'] + property)

def setExternalStorage(property, value):
    externalStorage.setProperty(script['base'] + property, value)

def parameter(name):
    return script['parameters'].get(name, None)


def parameters(*names):
    values = []
    for name in names:
        values.append(parameter(name))
    return values

def getContentType():
    contentType = getParameter('content_type')
    return contentType if contentType else getParameter('contentType')

def getSetting(name):
    return script['addon'].getSetting(name)

def run(action):
    xbmc.executebuiltin(action)

def debug():
    web_pdb.set_trace()

def setDirectoryMediaType(mediaType):
    xbmcplugin.setContent(handle, mediaType)

def setPath(path):
    xbmcplugin.setPluginCategory(handle, path)

def listDirectory(path):
    return xbmcvfs.listdir(path)

def existsPath(path):
    return xbmcvfs.exists(path)

def read(file):
    file = xbmcvfs.File(file)
    return file.read().rstrip()

def startsWith(starting, string):
    return string.startswith(starting)

def setPlot(item, plot):
    item.setInfo('video', {'plot': 'La aplicación no ha podido arrancar con normalidad. Vuelva a intentarlo una vez establecida la configuración solicitada'})

def newItem(label, isPlayable = True):
    item = xbmcgui.ListItem(label=label)
    item.setProperty('IsPlayable', 'true' if isPlayable else 'false')
    return item

def path(*nodes):
    path = ''
    for node in nodes:
        if startsWith('/', node):
            node = node[1:]
        if endsWith('/', node):
            node = node[:-1]
        path += '/' + node
    return path

def resolve(*nodes):
    xbmcplugin.setResolvedUrl(script['handle'], True, xbmcgui.ListItem(path = path(nodes)))
    
def getResource(path):
    return addon.getAddonInfo('path') + 'resources/' + path
