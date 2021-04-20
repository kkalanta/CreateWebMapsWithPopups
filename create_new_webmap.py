"""
Module for creating new web maps, adding feature layers to them,
and creating popups for desired map layers
"""

# import modules
from arcgis.gis import GIS
from arcgis.mapping import WebMap

# create connection to ArcGIS Enterprise/Portal
PORTAL_CONNECTION = GIS("portal_url", "username", "password")


def create_new_webmap(project_name, layer_names, *args):
    """
    creates a web map, adds feature layers to web map,
    and defines properties for layers and the web map

    Args:
        project_name (str): name of project
        layer_names (list): list of layer names to be added to web map

    Raises:
        TypeError: if project name is not type of string
        TypeError: if layer names is not type of list
        TypeError: if layer name is not type of string
    """
    if not isinstance(project_name, str):
        raise TypeError('expected project name to be type of str')

    if not isinstance(layer_names, list):
        raise TypeError('expected layer names to be type of list')

    for layer_name in layer_names:
        if not isinstance(layer_name, str):
            raise TypeError('expected layer name to be type of str')

    # get feature layers collection and update its properties
    feature_layers = get_feature_layers_collection(project_name)
    feature_layers_properties = get_properties_from_project(
        project_name=project_name,
        content_type='Feature Layer',
        project_additional_info=list(args)
    )
    feature_layers.update(item_properties=feature_layers_properties)
    protect_share_item(feature_layers)

    # create a new web map
    new_web_map = WebMap()
    print('creating a new web map')

    # add feature layers to the web map
    for feature_layer in feature_layers.layers:
        new_web_map.add_layer(layer=feature_layer)
    print('adding', feature_layers.title, 'to web map')

    # define properties for the web map
    web_map_properties = get_properties_from_project(
        project_name=project_name,
        content_type='WebMap',
        project_additional_info=list(args)
    )

    # create popups for map layers
    create_popups(
        web_map=new_web_map,
        project_name=project_name,
        layer_names=layer_names
    )

    # save the web map
    new_web_map.save(item_properties=web_map_properties)
    print('saving web map in portal')


def get_portal_item(portal_connection, item_name, item_type):
    """
    gets portal items, including feature layers collections,
    map image layers, and vector tile packages
    in ArcGIS Enterprise/Portal

    Args:
        portal_connection
        item_name (str): name of an item
        item_type (str): type of an item

    Returns:
        portal_item (arcgis.gis.Item): any item of feature, map image, and tile layer

    Raises:
        KeyError: if the specified search item is not found
        KeyError: if the specified portal item is not found
    """
    search_item = portal_connection.content.search(
        query='title:{} AND owner:{}'.format(item_name, portal_connection.users.me.username),
        item_type=item_type
    )

    if not search_item:
        raise KeyError('unable to find {}'.format(item_name))

    item = search_item[0]
    item_id = item.id
    portal_item = portal_connection.content.get(item_id)

    if not portal_item:
        raise KeyError("unable to find an item with id of '{}'".format(item_id))

    return portal_item


def get_feature_layers_collection(project_name):
    """
    gets feature layers collection of a project
    in ArcGIS Enterprise/Portal

    Args:
       project_name (str): project name

    Returns:
        feature_layer_collection or feature service (arcgis.gis.Item)
    """
    feature_layers_collection = get_portal_item(
        portal_connection=PORTAL_CONNECTION,
        item_name="{}_Map".format(project_name),
        item_type="Feature Layer"
    )

    return feature_layers_collection


def get_properties_from_project(project_name, content_type, project_additional_info):
    """
    gets properties of a project
    and applies them for portal contents

    Args:
        project_name (str): name of project
        content_type (str): type of portal item
        project_additional_info (list): list of additional information of a project
    """
    title_not_used = {'title'}
    item_title = "{}_{}".format(project_name, content_type)

    access_information = "Data Center"
    license_info = 'All rights reserved.'

    item_tags = [project_name] + project_additional_info
    item_snippet = ('This is a {} of {} project.').format(content_type, project_name)

    font_properties = '''<font color='#8b0000' size='4'><font style='font-family: inherit;'>'''
    item_description = (
        'This is a {} of {} project.').format(content_type, project_name)

    properties = {
        "title": item_title,
        "snippet": item_snippet,
        "description": font_properties + item_description,
        "tags": item_tags,
        "accessInformation": access_information,
        "licenseInfo": font_properties + license_info
    }

    if content_type != 'WebMap':
        item_properties = {key: properties[key] for key in properties if key not in title_not_used}
    else:
        item_properties = properties

    return item_properties


def protect_share_item(portal_item):
    """
    uses Python API methods to protect a portal item
    from deletion and shares it in organization

    Args:
        portal_item (arcgis.gis.item)
    """
    # protect portal item from deletion
    portal_item.protect(enable=True)
    print('protecting portal item of', portal_item.title, 'from deletion')

    # share portal item in the organization
    portal_item.share('org')
    print('sharing', portal_item.title, 'in organization')


def create_popups(web_map, project_name, layer_names):
    """
    creates popups for web map operational layers

    Args:
        web_map (arcgis.gis.Item)
        project_name (str): name of project
        layer_names (list): list of layer names to have popups
    """
    if layer_names:
        for layer_name in layer_names:
            # popup
            feature_layer_popup(
                map_service_name='{}_{}'.format(project_name, 'Map'),
                map_service_type='Feature Layer',
                web_map=web_map,
                layer_name=layer_name
            )
    else:
        print('No popup was defined for layers')


def feature_layer_popup(map_service_name, map_service_type, web_map, layer_name):
    """
    includes all steps to create and customize
    popups for both registered and hosted feature layers in a web map

    Args:
        map_service_name (str): name of feature layers on the portal
        map_service_type (str): type of feature layers on the portal
        web_map (ArcGIS item): created web map
        layer_name (str): name of each layer in a service
    """
    # get operational layer of a web map
    operational_layer = get_webmap_operational_layers(
        web_map=web_map,
        layer_name=layer_name
    )
    # get feature layer from feature layer collection
    target_layer = get_feature_layer_from_feature_service(
        map_service_name=map_service_name,
        map_service_type=map_service_type,
        layer_name=layer_name
    )

    # set popup info for the operational layer based on the type of services
    # hosted feature layer
    if operational_layer['popupInfo']:
        operational_layer_popup = operational_layer['popupInfo']

    # registered feature layer
    else:
        # set popup info
        operational_layer.update(popupInfo=target_layer['popupInfo'])
        operational_layer_popup = operational_layer['popupInfo']

    # set title for popup
    operational_layer_popup['title'] = layer_name

    # set description for popup
    layer_popup_description = customize_popup_description(
        operational_layer=operational_layer,
        map_service_type=map_service_type
    )
    operational_layer_popup['description'] = layer_popup_description

    # set decimal places and digit separators for numeric fields
    for field in operational_layer_popup['fieldInfos']:
        for fld in target_layer.properties.fields:
            # double
            if field['fieldName'] == fld.name and fld.type == "esriFieldTypeDouble":
                field.update({"format": {"places": 2, "digitSeparator": False}})
            # integer
            elif field['fieldName'] == fld.name and fld.type == "esriFieldTypeInteger":
                field.update({"format": {"places": 0, "digitSeparator": False}})

    print('customizing popup for', operational_layer['title'])


def customize_popup_description(operational_layer, map_service_type):
    """
    creates description for popups of layers by using
    an HTML format for font and fields information

    Args:
        operational_layer (dict): operational layer in a web map
        map_service_type (str): type of map service

    Returns:
        layer_popup_description (str): customized description for popup
    """
    layer_popup_description = '''<font color='#dc143c' face='Arial' size='2'>'''

    if map_service_type == 'Feature Layer':
        operational_layer_popup = operational_layer['popupInfo']
        for field in operational_layer_popup['fieldInfos']:

            # registered feature layers
            if any(letter.isupper() for letter in field['fieldName']) \
                    and not field['fieldName'] in NO_POPUP_FIELDS:
                field_name = split_uppercase(field['fieldName'])
                field_popup = '<b> %s :</b>  {%s}  <br /><br />' % (field_name, field['fieldName'])
                layer_popup_description += field_popup

            # hosted feature layers
            elif any(letter.isupper() for letter in field['label']) \
                    and not field['label'] in NO_POPUP_FIELDS:
                label = split_uppercase(field['label'])
                field_popup = '<b> %s :</b>  {%s}  <br /><br />' % (label, field['label'])
                layer_popup_description += field_popup

    print('customizing popup description for', operational_layer['title'])

    return layer_popup_description


def get_feature_layer_from_feature_service(map_service_name, map_service_type, layer_name):
    """
    gets a feature layer in feature layer collection

    Args:
        map_service_name (str): name of feature layers on the portal
        map_service_type (str): type of feature layers on the portal
        layer_name (str): name of each layer in a service
    """
    # access a feature service and gets its data
    feature_layers = get_portal_item(
        portal_connection=PORTAL_CONNECTION,
        item_name=map_service_name,
        item_type=map_service_type
    )
    feature_layer_data = feature_layers.get_data()

    # get index of a feature layer
    layer_index = get_feature_layer_index(feature_layers, layer_name)

    if not feature_layer_data:
        # get target layer in hosted feature service
        target_layer = feature_layers.layers[layer_index]
    else:
        # get target layer in registered feature service
        target_layer = feature_layer_data['layers'][layer_index]

    return target_layer


def get_feature_layer_index(feature_layer_collection, layer_name):
    """
    gets index of layers in a feature layer collection

    Args:
        feature_layer_collection (arcgis.gis.item): published feature layers
        layer_name (str): name of desired layer

    Returns:
        layer_index (int): index of a layer in a feature layer collection
    """
    for index, url in zip(range(len(feature_layer_collection.layers)),
                          feature_layer_collection.layers):
        if layer_name in feature_layer_collection.layers[index].properties.name:
            layer_index = index
            print('index of feature layer',
                  feature_layer_collection.layers[layer_index].properties.name, 'with url of',
                  url, 'is', layer_index)

    return layer_index


def get_webmap_operational_layers(web_map, layer_name):
    """
    gets operational layers of a web map

    Args:
        web map (arcgis item)
        layer_name (str): name of a layer

    Returns:
        operational_layer (dict): operational layer of web map, map property
    """
    web_map_definition = web_map.definition
    for layer in web_map_definition['operationalLayers']:
        if layer_name in layer['title']:
            operational_layer = layer

    return operational_layer


def split_uppercase(word):
    """
    splits strings that have uppercase

    Args:
        word (str): a word to be splitted
    """
    final_word = ''
    for i in word:
        final_word += ' %s' % i if i.isupper() else i

    return final_word.strip()


# list of fields that are not shown in popups of layers
NO_POPUP_FIELDS = [
    'OBJECTID', 'ORIG_FID', 'ORIG_FID_1', 'Shape.STArea()',
    'Shape.STLength()', 'Shape__Area', 'Shape__lenght', 'Shape'
]

if __name__ == "__main__":
    create_new_webmap("project_name", ['layer_one', 'layer_two'])
    print('End!')
