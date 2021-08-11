

def get_hitmask(image_alpha):
    """Returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image_alpha.get_width()):
        mask.append([])
        for y in range(image_alpha.get_height()):
            mask[x].append(bool(image_alpha.get_at((x, y))[3]))
    return mask
