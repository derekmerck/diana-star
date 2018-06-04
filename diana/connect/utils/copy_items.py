from diana.connect.apis import OrthancEndpoint, SplunkEndpoint, FileEndpoint

def copy_item(item, source, destination, **kwargs):

    if type(source) == OrthancEndpoint:

        if kwargs.get('anonymize'):
            if kwargs.get('replacement_map'):
                replacement_map = kwargs.get('replacement_map')
            else:
                replacement_map = None
            anon = source.anonymize(item, replacement_map=replacement_map)
            source.remove(item)
            item = anon

        if type(destination) == OrthancEndpoint:
            source.send(item, destination)

        if type(destination) == SplunkEndpoint:
            source.get(item, view="tags")
            splunk_index = kwargs.get("splunk_index")
            destination.put(item, splunk_index=splunk_index)

        if type(destination) == FileEndpoint:
            source.get(item, view="file")
            destination.put(item)

    if type(source) == FileEndpoint:

        if type(destination) == OrthancEndpoint:
            source.get(item, view="file")
            destination.put(item)


def copy_items(worklist, source, destination, **kwargs):

    for item in worklist:
        copy_item( item, source, destination, **kwargs )


def copy_children(worklist, source, destination, **kwargs):

    single_item = kwargs.get('single_item', False)

    for item in worklist:
        res = source.get(item, view='meta')
        children = res.get( item.level.child_level() )
        # ie, for a series, it is the "instances: [..." array

        if single_item:
            children = children[0]

        for child in children:
            copy_item( child, source, destination, **kwargs)

