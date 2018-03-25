
from copy import deepcopy as copy
from PyQt5 import QtCore
from lxml import etree as ET

def as_unicode(x):
    if isinstance(x,unicode):
        return x
    if isinstance(x,str):
        return unicode(x)
    if isinstance(x,QtCore.QVariant):
        return unicode(x.toString())
    return unicode(x)

class Meta(object):
    """Trivial List-based implementation of ordered Dict"""
    def __init__(self, list=None):
        if list is None:
            self._list = []
        else:
            self._list = copy(list)

    def copy(self):
        return Meta(self._list)

    def keys(self):
        return [k for k,v in self._list]

    def key(self, idx):
        if idx < len(self._list):
            return self._list[idx][0]
        else:
            return ""

    def value(self, idx):
        if idx < len(self._list):
            return self._list[idx][1]
        else:
            return ""

    def setKey(self, idx, new_key):
        if idx < len(self._list):
            k,v = self._list[idx]
            self._list[idx] = (new_key, v)
        else:
            self._list.append((new_key, u""))

    def remove(self, idx):
        if idx < len(self._list):
            del self._list[idx]

    def get(self, key, default=None):
        for k, v in self._list:
            if k == key:
                return v
        return default
    
    def set(self, key, value):
        new_list = []
        found = False
        for k, v in self._list:
            if k == key:
                new_list.append((key, value))
                found = True
            else:
                new_list.append((k,v))
        if not found:
            new_list.append((key,value))
        self._list = new_list

    def size(self):
        return len(self._list)

    def add(self, key, value):
        self._list.append((key, value))

    def items(self):
        return self._list

    def dict(self):
        return dict([(as_unicode(k), as_unicode(v)) for k,v in self._list])

    def to_xml(self):
        xml = ET.Element("metainfo")
        for key, value in self.items():
            meta = ET.SubElement(xml, "meta", name=key)
            meta.text = value
        return ET.tostring(xml, encoding='utf-8')

    def set_from_xml(self, data):
        xml = ET.fromstring(data)
        for meta in xml.findall('meta'):
            key = meta.attrib['name']
            value = meta.text
            self[key] = value
    
    @staticmethod
    def from_xml(self, data):
        result = Meta()
        result.set_from_xml(data)
        return result
    
    def __getitem__(self, key):
        return self.get(key, None)
    
    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __len__(self):
        return self.size()

    def __repr__(self):
        return repr(self.dict())

    def __str__(self):
        return str(self.dict())

