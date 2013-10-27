# -*- coding: ISO-8859-15 -*-

import os
import tempfile
from lxml import etree

def get_tempdir():
    """Helper function to get tempdir"""
    return '%s%s%s' % (tempfile.gettempdir(), os.sep, 'wmo-cmp-ts')

def validate_iso_xml(xml):
    """Perform XML Schema validation of ISO XML Metadata"""
    tempdir = get_tempdir()
    if not os.path.exists(tempdir):
        raise IOError('%s does not exist' % tempdir)
    xsd = os.path.join(tempdir, 'schema', 'gmd', 'gmd.xsd')
    LOGGER.info('Validating %s against schema %s', xml, xsd)
    schema = etree.XMLSchema(etree.parse(xsd))
    schema.assertValid(etree.fromstring(xml))
