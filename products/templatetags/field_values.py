from django import template

register = template.Library()


@register.simple_tag
def get_field_value(instance, field_name):
    """
    returns value of field based on field name
    """
    if hasattr(instance, field_name):
        value = getattr(instance, field_name)
        if value == None:
            return '-'
        else:
            return value


@register.simple_tag
def get_dimension_match_width_length(instance, value):
    width = getattr(instance, 'inner_dim1')
    length = getattr(instance, 'inner_dim2')
    if value:
        value_width_match = (1 - (abs((value - width)) / width)) * 100
        value_length_match = (1 - (abs((value - length)) / length)) * 100

        if value_width_match >= value_length_match:
            return value_width_match
        else:
            return value_length_match
    else:
        return '-'


@register.simple_tag
def get_dimensions_match(instance, search_width, search_length, search_height, search_diameter):
    object_width = getattr(instance, 'inner_dim1')
    object_length = getattr(instance, 'inner_dim2')
    object_height = getattr(instance, 'inner_dim3')
    object_diameter = getattr(instance, 'diameter')
    object_min_height = getattr(instance, 'inner_variable_dimension_MIN')
    object_max_height = getattr(instance, 'inner_variable_dimension_MAX')

    def get_match(search_dim, object_dim):
        if search_dim and object_dim:
            return round((1 - (abs((search_dim - object_dim)) / object_dim)) * 100)
        return 0

    def get_var_match():
        if object_min_height is not None and object_max_height is not None:
            return 100

    swidth_width_match = get_match(search_width, object_width)
    swidth_length_match = get_match(search_width, object_length)
    slength_width_match = get_match(search_length, object_width)
    slength_length_match = get_match(search_length, object_length)
    sheight_height_match = get_match(search_height, object_height)
    sheight_varheight_match = get_var_match()
    sdiameter_diameter_match = get_match(search_diameter, object_diameter)

    if swidth_width_match >= slength_width_match:
        match1 = swidth_width_match
    else:
        match1 = slength_width_match

    if slength_length_match >= swidth_length_match:
        match2 = slength_length_match
    else:
        match2 = swidth_length_match

    if sheight_varheight_match:
        match3 = sheight_varheight_match
    else:
        match3 = sheight_height_match

    match4 = sdiameter_diameter_match

    all_matches = [match1, match2, match3, match4]
    found_matches = [match for match in all_matches if match > 0]
    if len(found_matches) > 0:
        overall_match = round(sum(found_matches) / len(found_matches))
    else:
        overall_match = 100

    if search_width and search_length:
        return match1, match2, match3, match4, overall_match

    else:
        if match1 > match2:
            match2 = 0
        else:
            match1 = 0
        return match1, match2, match3, match4, overall_match
