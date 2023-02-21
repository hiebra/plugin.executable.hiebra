import xbmcgui
import xbmcplugin
import web_pdb; web_pdb.set_trace()
import plugin
from urllib.parse import parse_qsl, urlencode

#<addon>
import xbmcaddon
addon = xbmcaddon.Addon()
def configure():
    id = addon.getAddonInfo('id')
    xbmc.executebuiltin(f'Addon.OpenSettings({id})')
def resource(path):
    resources = addon.getAddonInfo('path') + 'resources/' + path
#</addon>

def item():
    raise Exception('not implemented yet')

def branch(label, path = None, art = None):
    item = xbmcgui.ListItem(label)
    xbmcplugin.addDirectoryItem(handle, f'{base}?action={action}' if action else join(root, path), item, True)
    plugin.append(item)

call = {
    'configure': configure,
}

def leaf(label, path = None, action = None):
    item = xbmcgui.ListItem(label)
    item.setInfo('IsPlayable', 'false' if action else 'true')
    xbmcplugin.addDirectoryItem(handle, f'{base}?action={action}' if action else join(root, path), item, False)
    plugin.append(item)

leaf('Complete configuration...', action = 'configure')
videos()

"""
item.setArt({
    'icon': resources + 'icon.png',
    'thumb': resources + 'thumb.jpeg',
    'fanart': resources + 'fanart.jpg'
})
item.setInfo('video', {'plot': 'La aplicación no puede ejecutarse hasta que se haya configurado correctamente. Complete la configuración y vuelva a intentarlo'})
"""

xbmcplugin.setContent(handle, 'videos')

xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
