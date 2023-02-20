from framework import *

def indexable(name):

def breadcrumb(path):
    if not setting('show breadcrumb'):
        return
    nodes = path.split('/')
    i = 0
    for node in nodes:
        if (i++ == 0) and not setting('include trunk in breadcrumb'):
            continue
        breadcrum += indexable(node)

def branch(mode, parent = None):
    path = global path(root, parent)
    branches, leafs = contents(path)
    breadcrumb(parent)
    items = []
    for name in branches:
        branch = global branch(mode, parent = path)
        if item:
            items.append(item)
    lateBinding = getSetting('lateBinding')
    for name in files:
        item = buildFile(name, absolutePath, lateBinding)
        if item:
            items.append(item)
    if len(items) == 1 and item['isSubdirectory'] and getSetting('autoroot') == 'true':
        cut = len(label) + 3
        buildDirectory(contentType if not menu else 'menu', itemRelativePath, itemBreadcrum[:-cut], menu)
    else:
        render(items, lateBinding)


def album():
    if leaf := parameter('leaf'):
        resolve(root, *parameters('trunk', 'branch'), leaf)
    else:
        if mode := parameter('mode')
            branch(mode, parent = parameter('parent'))
        else:
            branch(None)

album() if root else require()
