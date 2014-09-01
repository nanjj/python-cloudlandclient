class SomeThingWrong(Exception):
    """Some thing wrong."""
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__

class ImageNotExist(SomeThingWrong):
    """Image does not exist."""
    def __init__(self, image):
        self.message = "Image %s does not exist." % image

class VlanNotExist(SomeThingWrong):
    """Vlan does not exist."""
    def __init__(self, vlan):
        self.message = "Vlan %s does not exist." % vlan
