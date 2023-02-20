from kodi import *
import re
import mimetypes
mimetypes.init()

root = getSetting('root')

def configuration():
    if not getParameter('fixing') == 'true':
        description = 'La aplicación no ha podido arrancar con normalidad. Vuelva a intentarlo una vez establecida la configuración solicitada'
        add('Ajustar la configuración', f'{base}?fixing=true', False, description = description, playable = False, art = {
            'icon': resource('icon.png'),
            'fanart': resource('fanart.jpg')
        })
        finished('videos')
    else:
        xbmc.executebuiltin(f'Addon.OpenSettings({id})')

def matches(contentType, fileName):
    global subtype
    subtype = mimetypes.guess_type(fileName)[0]
    return subtype.startswith(contentType + '/')

def contains(contentType, directory):
    if contentType == 'videos':
        subdirectories, files = listDirectory(directory)
        for name in files:
            if matches('video', name):
                return True
        for name in subdirectories:
            if contains(contentType, directory + name):
                return True
        return False
    else:
        return True

def parse(indexable):
    match = re.search('^([1-9])+\. (.+)$', indexable)
    if match:
        return int(match.group(1)), match.group(2)
    else:
        return 0, indexable

def url(**query):
    query = {key: value for key, value in query.items() if value is not None}
    return '{0}?{1}'.format(base, urlencode(query))

def isSpecial(pathType, name):
    return startsWith('000.metadata', name) if pathType == 'directory' else name == 'folder.jpg'

def getMetadata(directory):
    metadata = directory + '000.metadata/'
    description = metadata + 'description.txt'
    description = read(description) if existsPath(description) else None
    menu = metadata + 'menu/'
    if not existsPath(menu):
        menu = None
    thumb = icon = fanart = None
    subdirectories, files = listDirectory(metadata)    
    for name in files:
        image = metadata + name
        if startsWith('thumb.', name):
            thumb = image
        elif startsWith('icon.', name):
            icon = image
        elif startsWith('fanart.', name):
            fanart = image
    if not thumb and existsPath(directory + 'folder.jpg'):
        thumb = directory + 'folder.jpg'
    return thumb, icon, fanart, description, menu

def path(index, contentType, relativePath, breadcrum, menuPath):
    return url(index = index, content_type = contentType, relativePath = relativePath, breadcrum = breadcrum, menuPath = menuPath)

def buildSubdirectory(absolutePath, name, contentType, relativePath, breadcrum):
    if isSpecial('directory', name):
        return None
    subdirectory = absolutePath + name + '/'
    if not contains(contentType, subdirectory):
        return None
    item = {}
    index, label = parse(name)
    item['label'] = label
    if not contentType == 'menu':
        itemRelativePath = (name if not relativePath else relativePath + name) + '/'
    itemBreadcrum = label if not breadcrum else breadcrum + ' / ' + label
    item['index'] = index
    item['isSubdirectory'] = True
    thumb, icon, fanart, item['description'], menu = getMetadata(subdirectory)
    if not thumb:
        thumb, icon, fanart, item['description'], previousMenu = getMetadata(absolutePath)
    if menu and not contentType == 'menu':
        item['path'] = path(index, 'menu', itemRelativePath, itemBreadcrum, menu)
    elif existsPath(contentTypeFile := subdirectory + 'content-type.txt'):
        item['path'] = path(index, read(contentTypeFile), relativePath, itemBreadcrum, None)
    elif contentType == 'menu':
        item['path'] = path(index, 'menu', relativePath, itemBreadcrum, subdirectory)
    else:
        nextContentType = 'executable' if contentType == 'resume' else contentType
        item['path'] = path(index, nextContentType, itemRelativePath, itemBreadcrum, None)
    item['isPlayable'] = 'false'
    item['art'] = {'icon': icon, 'thumb': thumb, 'fanart': fanart}
    return item

def buildFile(name, absolutePath, lateBinding):
    if isSpecial('file', name):
        return None
    item = {'label': parse(name)[1]}
    relative = absolutePath[len(root):] + name
    if lateBinding:
        item['path'] = url(file = relative)
        item['isPlayable'] = 'false'
    else:
        item['path'] = root + relative
        item['isPlayable'] = 'true'
    item['isSubdirectory'] = False
    return item

def render(items, lateBinding):
    for item in items:
        view = xbmcgui.ListItem(label=item['label'])
        view.setProperty('IsPlayable', item['isPlayable'])
        view.setProperty('ForceResolvePlugin', 'true' if lateBinding else 'false')
        if item['isSubdirectory']:
            view.setArt(item['art'])
            view.setInfo('video', {'plot': item['description']})
        xbmcplugin.addDirectoryItem(handle, item['path'], view, item['isSubdirectory'])
    setMediaType('abstract')
    #xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_FULLPATH)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmc.executebuiltin('Container.SetViewMode(55)')
    if xbmc.getInfoLabel('Container.SortOrder') == 'Descending':
        xbmc.executebuiltin('Container.SetSortDirection')
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)

def buildDirectory(contentType, relativePath, breadcrum, menuPath):
    if contentType == 'menu':
        absolutePath = menuPath
    else:
        absolutePath = root + relativePath if relativePath else root
        if not contentType == 'resume':
            testPath = absolutePath + '000.metadata/menu/'
            if existsPath(testPath):
                return buildDirectory('menu', relativePath, breadcrum, testPath)
    subdirectories, files = listDirectory(absolutePath)
    if breadcrum:
        setPath(breadcrum)
    items = []
    for name in subdirectories:
        item = buildSubdirectory(absolutePath, name, contentType, relativePath, breadcrum)
        if item:
            items.append(item)
    lateBinding = getSetting('lateBinding')
    if not contentType == 'menu':
        for name in files:
            item = buildFile(name, absolutePath, lateBinding)
            if item:
                items.append(item)
    if len(items) == 1 and item['isSubdirectory'] and getSetting('autoroot') == 'true':
        cut = len(label) + 3
        buildDirectory(contentType if not menu else 'menu', itemRelativePath, itemBreadcrum[:-cut], menu)
    else:
        render(items, lateBinding)

def noRoot():
    id = addon.getAddonInfo('id')
    xbmc.executebuiltin(f'Addon.OpenSettings({id})')
    item = xbmcgui.ListItem(label='Álbum familiar')
    item.setProperty('IsPlayable', 'false')
    resources = addon.getAddonInfo('path') + 'resources/'
    item.setArt({'icon': resources + 'icon.png', 'fanart': resources + 'fanart.jpg'})
    item.setInfo('video', {'plot': 'La aplicación no ha podido arrancar con normalidad. Vuelva a intentarlo una vez establecida la configuración solicitada'})
    setMediaType('files')
    i = getParameter('index')
    i = i + '1' if i else '0'
    xbmcplugin.addDirectoryItem(handle, f'{base}?content_type=executable&index={i}', item, True)
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)

